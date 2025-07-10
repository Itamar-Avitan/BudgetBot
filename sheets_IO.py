import google.auth
from googleapiclient.discovery import build
import json
import os
import time
from google.oauth2 import service_account
from typing import Dict, List, Optional, Union

class SheetsIO:
    """
    Enhanced SheetsIO for Budget Bot v2.0 with separate Budget and Tracker sheets.
    
    Architecture:
    1. Budget Sheet (BUDGET_SPREADSHEET_ID): 
       - Columns: קטגוריה, תקציב, כמה יצא, כמה נשאר
       - Contains __configs sheet for configuration
    
    2. Tracker Sheet (TRACKER_SPREADSHEET_ID):
       - Columns: קטגוריה, פירוט, מחיר, תאריך
       - Contains individual expense transactions
    """
    
    def __init__(self, budget_spreadsheet_id: str, tracker_spreadsheet_id: str):
        # Load Google credentials - try environment first, then file
        try:
            # Try to load from environment variable (for production)
            if os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
                creds = service_account.Credentials.from_service_account_file(
                    os.getenv('GOOGLE_APPLICATION_CREDENTIALS'),
                    scopes=["https://www.googleapis.com/auth/spreadsheets"]
                )
            elif os.getenv('GOOGLE_SERVICE_ACCOUNT_JSON'):
                # Load from JSON string environment variable
                json_str = os.getenv('GOOGLE_SERVICE_ACCOUNT_JSON')
                if json_str:
                    sa_info = json.loads(json_str)
                    creds = service_account.Credentials.from_service_account_info(
                        sa_info,
                        scopes=["https://www.googleapis.com/auth/spreadsheets"]
                    )
                else:
                    raise ValueError("GOOGLE_SERVICE_ACCOUNT_JSON is empty")
            else:
                # Fall back to file for local development
                with open('credits/google_creds.json', 'r') as f:
                    sa_info = json.load(f)
                creds = service_account.Credentials.from_service_account_info(
                    sa_info,
                    scopes=["https://www.googleapis.com/auth/spreadsheets"]
                )
        except Exception as e:
            raise RuntimeError(f"Failed to load Google credentials: {e}")
        
        self.budget_spreadsheet_id = budget_spreadsheet_id
        self.tracker_spreadsheet_id = tracker_spreadsheet_id
        self.service = build("sheets", "v4", credentials=creds)
        
        # Cache for working sheet name to reduce API calls
        self._working_sheet_cache = None
        self._cache_timestamp = 0
        self._cache_ttl = 300  # 5 minutes cache

    def _execute_with_retry(self, api_call, max_retries=3, delay=1):
        """Execute API call with retry logic for network resilience."""
        for attempt in range(max_retries):
            try:
                return api_call.execute()
            except Exception as e:
                if attempt == max_retries - 1:  # Last attempt
                    raise e
                print(f"API call failed (attempt {attempt + 1}/{max_retries}): {e}")
                time.sleep(delay * (attempt + 1))  # Exponential backoff
        return None

    def get_config_value(self, key: str) -> str:
        """Get configuration value from __configs sheet on budget spreadsheet."""
        try:
            config_range = "__configs!A:B"
            response = self._execute_with_retry(
                self.service.spreadsheets().values().get(
                    spreadsheetId=self.budget_spreadsheet_id,
                    range=config_range
                )
            )
            
            values = response.get('values', []) if response else []
            if not values:
                raise ValueError("No configuration data found")
                
            # Find the key-value pair
            for row in values:
                if len(row) >= 2 and row[0] == key:
                    return row[1]
            
            raise ValueError(f"Configuration key '{key}' not found")
            
        except Exception as e:
            print(f"Error reading config: {e}")
            # Return special indicator for config failure
            raise ConfigurationError(f"Could not read config for key '{key}': {e}")

    def set_config_value(self, key: str, value: str) -> None:
        """Set configuration value in __configs sheet on budget spreadsheet."""
        try:
            config_range = "__configs!A:B"
            
            # Get current config data
            response = self._execute_with_retry(
                self.service.spreadsheets().values().get(
                    spreadsheetId=self.budget_spreadsheet_id,
                    range=config_range
                )
            )
            
            values = response.get('values', []) if response else []
            
            # Find if key exists
            key_row = None
            for i, row in enumerate(values):
                if len(row) >= 1 and row[0] == key:
                    key_row = i + 1  # 1-based for sheets
                    break
            
            if key_row:
                # Update existing key
                update_range = f"__configs!B{key_row}"
                self._execute_with_retry(
                    self.service.spreadsheets().values().update(
                        spreadsheetId=self.budget_spreadsheet_id,
                        range=update_range,
                        valueInputOption="RAW",
                        body={"values": [[value]]}
                    )
                )
            else:
                # Add new key-value pair
                append_range = "__configs!A:B"
                self._execute_with_retry(
                    self.service.spreadsheets().values().append(
                        spreadsheetId=self.budget_spreadsheet_id,
                        range=append_range,
                        valueInputOption="RAW",
                        insertDataOption="INSERT_ROWS",
                        body={"values": [[key, value]]}
                    )
                )
            
            print(f"Set config value: {key} = {value}")
            
        except Exception as e:
            print(f"Error setting config value: {e}")
            raise

    def get_working_sheet_name(self) -> str:
        """Get the current working sheet name from configuration with caching."""
        current_time = time.time()
        
        # Check if cache is still valid
        if (self._working_sheet_cache and 
            current_time - self._cache_timestamp < self._cache_ttl):
            return self._working_sheet_cache
        
        try:
            # Get from API and cache
            sheet_name = self.get_config_value("working_sheet")
            self._working_sheet_cache = sheet_name
            self._cache_timestamp = current_time
            return sheet_name
        except Exception as e:
            # If config read fails, try to use cached value
            if self._working_sheet_cache:
                print(f"Using cached working sheet name due to config error: {e}")
                return self._working_sheet_cache
            # If no cache, raise the error
            raise e

    def get_budget_categories(self) -> List[str]:
        """Get all available categories from budget sheet."""
        try:
            working_sheet = self.get_working_sheet_name()
            data_range = f"{working_sheet}!A:A"
            response = self._execute_with_retry(
                self.service.spreadsheets().values().get(
                    spreadsheetId=self.budget_spreadsheet_id,
                    range=data_range
                )
            )
            
            values = response.get('values', []) if response else []
            if not values:
                return []
            
            # Skip header row and extract categories
            categories = []
            for row in values[1:]:  # Skip header
                if row and row[0].strip():  # Skip empty rows
                    categories.append(row[0].strip())
            
            return categories
            
        except Exception as e:
            print(f"Error getting categories: {e}")
            return ["קניות", "אוכל בחוץ", "תחבורה", "בידור", "בריאות", "חשבונות"]  # Default fallback

    def add_expense_to_tracker(self, expense_data: Dict[str, Union[str, float]]) -> None:
        """Add expense to tracker sheet."""
        try:
            working_sheet = self.get_working_sheet_name()
            
            # Map the expense data to match tracker columns
            tracker_data = {
                "קטגוריה": expense_data.get("קטגוריה", ""),
                "פירוט": expense_data.get("פירוט", ""),
                "מחיר": expense_data.get("מחיר", 0),
                "תאריך": expense_data.get("תאריך", "")
            }
            
            # Get headers from tracker sheet
            header_range = f"{working_sheet}!A1:Z1"
            header_resp = self._execute_with_retry(
                self.service.spreadsheets().values().get(
                    spreadsheetId=self.tracker_spreadsheet_id,
                    range=header_range
                )
            )
            headers = header_resp.get("values", [[]])[0] if header_resp else []
            
            # Build row in correct order
            row = [tracker_data.get(h, "") for h in headers]
            
            # Append to tracker sheet
            append_range = f"{working_sheet}!A:Z"
            self._execute_with_retry(
                self.service.spreadsheets().values().append(
                    spreadsheetId=self.tracker_spreadsheet_id,
                    range=append_range,
                    valueInputOption="RAW",
                    insertDataOption="INSERT_ROWS",
                    body={"values": [row]}
                )
            )
            
            print(f"Added expense to tracker: {tracker_data}")
            
        except Exception as e:
            print(f"Error adding expense to tracker: {e}")
            raise

    def update_budget_sheet(self, category: str) -> bool:
        """Update budget sheet by recalculating expenses for a category. Returns success status."""
        try:
            working_sheet = self.get_working_sheet_name()
            
            # Get total spent for this category from tracker
            total_spent = self._calculate_category_total(category)
            
            # Find the category row in budget sheet
            budget_range = f"{working_sheet}!A:Z"
            response = self._execute_with_retry(
                self.service.spreadsheets().values().get(
                    spreadsheetId=self.budget_spreadsheet_id,
                    range=budget_range
                )
            )
            
            values = response.get('values', []) if response else []
            if not values:
                return False
            
            headers = values[0]
            data_rows = values[1:]
            
            # Find column indices
            category_col = headers.index("קטגוריה") if "קטגוריה" in headers else 0
            budget_col = headers.index("תקציב") if "תקציב" in headers else 1
            spent_col = headers.index("כמה יצא") if "כמה יצא" in headers else 2
            remaining_col = headers.index("כמה נשאר") if "כמה נשאר" in headers else 3
            
            # Find category row
            for row_idx, row in enumerate(data_rows):
                if len(row) > category_col and row[category_col] == category:
                    # Get budget amount
                    budget_amount = float(row[budget_col]) if len(row) > budget_col and row[budget_col] else 0
                    remaining_amount = budget_amount - total_spent
                    
                    # Update the budget sheet
                    sheet_row = row_idx + 2  # +1 for header, +1 for 0-based index
                    
                    # Update spent amount
                    spent_range = f"{working_sheet}!{chr(65 + spent_col)}{sheet_row}"
                    self._execute_with_retry(
                        self.service.spreadsheets().values().update(
                            spreadsheetId=self.budget_spreadsheet_id,
                            range=spent_range,
                            valueInputOption="RAW",
                            body={"values": [[total_spent]]}
                        )
                    )
                    
                    # Update remaining amount
                    remaining_range = f"{working_sheet}!{chr(65 + remaining_col)}{sheet_row}"
                    self._execute_with_retry(
                        self.service.spreadsheets().values().update(
                            spreadsheetId=self.budget_spreadsheet_id,
                            range=remaining_range,
                            valueInputOption="RAW",
                            body={"values": [[remaining_amount]]}
                        )
                    )
                    
                    print(f"Updated budget for {category}: spent={total_spent}, remaining={remaining_amount}")
                    return True
            
            print(f"Category '{category}' not found in budget sheet")
            return False
            
        except Exception as e:
            print(f"Error updating budget sheet for {category}: {e}")
            return False

    def _calculate_category_total(self, category: str) -> float:
        """Calculate total spent for a category from tracker sheet."""
        try:
            working_sheet = self.get_working_sheet_name()
            data_range = f"{working_sheet}!A:Z"
            response = self._execute_with_retry(
                self.service.spreadsheets().values().get(
                    spreadsheetId=self.tracker_spreadsheet_id,
                    range=data_range
                )
            )
            
            values = response.get('values', []) if response else []
            if not values:
                return 0.0
            
            headers = values[0]
            data_rows = values[1:]
            
            # Find column indices
            category_col = headers.index("קטגוריה") if "קטגוריה" in headers else 0
            price_col = headers.index("מחיר") if "מחיר" in headers else 2
            
            total = 0.0
            for row in data_rows:
                if (len(row) > category_col and 
                    row[category_col] == category and 
                    len(row) > price_col):
                    try:
                        price = float(row[price_col]) if row[price_col] else 0
                        total += price
                    except ValueError:
                        continue
            
            return total
            
        except Exception as e:
            print(f"Error calculating category total for {category}: {e}")
            return 0.0

    def refresh_all_budgets(self) -> Dict:
        """Refresh all budget categories with optimized batch operations."""
        try:
            working_sheet = self.get_working_sheet_name()
            categories = self.get_budget_categories()
            
            if not categories:
                return {
                    "success": False,
                    "error": "לא נמצאו קטגוריות לעדכון",
                    "updated_count": 0,
                    "failed_categories": []
                }
            
            print(f"🚀 Starting optimized batch refresh for {len(categories)} categories...")
            
            # API Call #1: Read tracker sheet ONCE
            print("📖 Reading tracker sheet (all data)...")
            tracker_range = f"{working_sheet}!A:Z"
            tracker_response = self._execute_with_retry(
                self.service.spreadsheets().values().get(
                    spreadsheetId=self.tracker_spreadsheet_id,
                    range=tracker_range
                )
            )
            
            # API Call #2: Read budget sheet ONCE
            print("📊 Reading budget sheet (all data)...")
            budget_range = f"{working_sheet}!A:Z"
            budget_response = self._execute_with_retry(
                self.service.spreadsheets().values().get(
                    spreadsheetId=self.budget_spreadsheet_id,
                    range=budget_range
                )
            )
            
            # Process data in memory
            tracker_data = tracker_response.get('values', []) if tracker_response else []
            budget_data = budget_response.get('values', []) if budget_response else []
            
            if not tracker_data or not budget_data:
                return {
                    "success": False,
                    "error": "לא נמצא מידע בגיליונות",
                    "updated_count": 0,
                    "failed_categories": []
                }
            
            # Get headers
            tracker_headers = tracker_data[0] if tracker_data else []
            budget_headers = budget_data[0] if budget_data else []
            
            # Find column indices
            try:
                tracker_cat_col = tracker_headers.index("קטגוריה") if "קטגוריה" in tracker_headers else 0
                tracker_price_col = tracker_headers.index("מחיר") if "מחיר" in tracker_headers else 2
                
                budget_cat_col = budget_headers.index("קטגוריה") if "קטגוריה" in budget_headers else 0
                budget_amt_col = budget_headers.index("תקציב") if "תקציב" in budget_headers else 1
                spent_col = budget_headers.index("כמה יצא") if "כמה יצא" in budget_headers else 2
                remaining_col = budget_headers.index("כמה נשאר") if "כמה נשאר" in budget_headers else 3
            except ValueError as e:
                return {
                    "success": False,
                    "error": f"לא נמצאו עמודות נדרשות: {e}",
                    "updated_count": 0,
                    "failed_categories": []
                }
            
            # Calculate totals for all categories in memory (FAST!)
            print("🧠 Processing all categories in memory...")
            category_totals = {}
            for row in tracker_data[1:]:  # Skip header
                if len(row) > max(tracker_cat_col, tracker_price_col):
                    cat = row[tracker_cat_col] if tracker_cat_col < len(row) else ""
                    price_str = row[tracker_price_col] if tracker_price_col < len(row) else "0"
                    
                    if cat and price_str:
                        try:
                            price = float(price_str)
                            category_totals[cat] = category_totals.get(cat, 0) + price
                        except ValueError:
                            continue
            
            # Prepare batch updates
            print("📝 Preparing batch updates...")
            batch_updates = []
            updated_count = 0
            failed_categories = []
            
            budget_rows = budget_data[1:] if len(budget_data) > 1 else []
            for row_idx, row in enumerate(budget_rows, start=2):  # Start from row 2 (1-based)
                if len(row) > budget_cat_col:
                    category = row[budget_cat_col]
                    if category in categories:  # Only update categories we track
                        try:
                            spent = category_totals.get(category, 0)
                            budget_amt = float(row[budget_amt_col]) if budget_amt_col < len(row) and row[budget_amt_col] else 0
                            remaining = budget_amt - spent
                            
                            # Prepare update for this row (spent and remaining columns)
                            spent_cell = f"{working_sheet}!{chr(65 + spent_col)}{row_idx}"
                            remaining_cell = f"{working_sheet}!{chr(65 + remaining_col)}{row_idx}"
                            
                            batch_updates.extend([
                                {
                                    "range": spent_cell,
                                    "values": [[spent]]
                                },
                                {
                                    "range": remaining_cell,
                                    "values": [[remaining]]
                                }
                            ])
                            
                            updated_count += 1
                            print(f"   ⚡ Prepared update for {category}: spent={spent}, remaining={remaining}")
                            
                        except Exception as e:
                            print(f"   ❌ Failed to prepare update for {category}: {e}")
                            failed_categories.append(category)
            
            # API Call #3: Execute batch update (ONE CALL FOR ALL CATEGORIES!)
            if batch_updates:
                print(f"📤 Executing batch update for {len(batch_updates)} cells...")
                batch_body = {
                    "valueInputOption": "RAW",
                    "data": batch_updates
                }
                
                self._execute_with_retry(
                    self.service.spreadsheets().values().batchUpdate(
                        spreadsheetId=self.budget_spreadsheet_id,
                        body=batch_body
                    )
                )
                
                print(f"✅ Batch update completed successfully!")
            
            # Return result in expected format
            if updated_count == 0:
                return {
                    "success": False,
                    "error": "לא עודכנו קטגוריות",
                    "updated_count": 0,
                    "failed_categories": failed_categories
                }
            elif failed_categories:
                return {
                    "success": True,
                    "partial": True,
                    "updated_count": updated_count,
                    "failed_categories": failed_categories,
                    "message": f"עודכנו {updated_count} קטגוריות, {len(failed_categories)} נכשלו"
                }
            else:
                return {
                    "success": True,
                    "updated_count": updated_count,
                    "message": f"עודכנו בהצלחה {updated_count} קטגוריות בשיטה מהירה!"
                }
                
        except Exception as e:
            print(f"❌ Error in optimized batch refresh: {e}")
            return {
                "success": False,
                "error": f"שגיאה כללית ברענון: {e}",
                "updated_count": 0,
                "failed_categories": []
            }

    def get_recent_transactions(self, limit: int = 20) -> List[Dict]:
        """Get recent transactions from tracker sheet."""
        try:
            working_sheet = self.get_working_sheet_name()
            data_range = f"{working_sheet}!A:Z"
            response = self._execute_with_retry(
                self.service.spreadsheets().values().get(
                    spreadsheetId=self.tracker_spreadsheet_id,
                    range=data_range
                )
            )
            
            values = response.get('values', []) if response else []
            if not values:
                return []
            
            headers = values[0]
            data_rows = values[1:]
            
            # Get recent transactions
            recent_rows = data_rows[-limit:] if len(data_rows) > limit else data_rows
            
            transactions = []
            for row in recent_rows:
                if len(row) > 0:  # Skip empty rows
                    transaction = {}
                    for i, header in enumerate(headers):
                        transaction[header] = row[i] if i < len(row) else ""
                    transactions.append(transaction)
            
            return transactions
            
        except Exception as e:
            print(f"Error getting recent transactions: {e}")
            return []

    def get_budget_summary(self) -> List[Dict]:
        """Get budget summary from budget sheet."""
        try:
            working_sheet = self.get_working_sheet_name()
            data_range = f"{working_sheet}!A:Z"
            response = self._execute_with_retry(
                self.service.spreadsheets().values().get(
                    spreadsheetId=self.budget_spreadsheet_id,
                    range=data_range
                )
            )
            
            values = response.get('values', []) if response else []
            if not values:
                return []
            
            headers = values[0]
            data_rows = values[1:]
            
            summary = []
            for row in data_rows:
                if len(row) > 0 and row[0].strip():  # Skip empty rows
                    budget_item = {}
                    for i, header in enumerate(headers):
                        budget_item[header] = row[i] if i < len(row) else ""
                    summary.append(budget_item)
            
            return summary
            
        except Exception as e:
            print(f"Error getting budget summary: {e}")
            return []

    def get_category_budget_info(self, category: str) -> Optional[Dict]:
        """Get budget information for a specific category."""
        try:
            summary = self.get_budget_summary()
            for item in summary:
                if item.get("קטגוריה") == category:
                    return {
                        "תקציב": float(item.get("תקציב", 0)) if item.get("תקציב") else 0,
                        "כמה יצא": float(item.get("כמה יצא", 0)) if item.get("כמה יצא") else 0,
                        "כמה נשאר": float(item.get("כמה נשאר", 0)) if item.get("כמה נשאר") else 0
                    }
            return None
            
        except Exception as e:
            print(f"Error getting category budget info: {e}")
            return None

    def process_expense(self, expense_data: Dict[str, Union[str, int, float]]) -> Dict:
        """Complete expense processing: add to tracker and update budget."""
        try:
            category = str(expense_data.get("קטגוריה", ""))
            
            # 1. Add to tracker sheet
            self.add_expense_to_tracker(expense_data)
            
            # 2. Update budget sheet
            self.update_budget_sheet(category)
            
            # 3. Get updated budget info
            budget_info = self.get_category_budget_info(category)
            
            return {
                "success": True,
                "category": category,
                "budget_info": budget_info,
                "expense": expense_data
            }
            
        except Exception as e:
            print(f"Error processing expense: {e}")
            return {
                "success": False,
                "error": str(e),
                "expense": expense_data
            }

    # ------------------------------------------------------------------
    # Budget Building Pipeline Methods
    # ------------------------------------------------------------------
    
    def create_new_budget_sheets(self, sheet_name: str) -> Dict:
        """Create new budget sheets in both spreadsheets with proper headers."""
        try:
            results = {"budget_sheet": False, "tracker_sheet": False}
            
            # Create budget sheet
            budget_headers = ["קטגוריה", "תקציב", "כמה יצא", "כמה נשאר"]
            if not self.sheet_exists(self.budget_spreadsheet_id, sheet_name):
                self._create_sheet_with_headers(self.budget_spreadsheet_id, sheet_name, budget_headers)
                results["budget_sheet"] = True
            
            # Create tracker sheet  
            tracker_headers = ["קטגוריה", "פירוט", "מחיר", "תאריך"]
            if not self.sheet_exists(self.tracker_spreadsheet_id, sheet_name):
                self._create_sheet_with_headers(self.tracker_spreadsheet_id, sheet_name, tracker_headers)
                results["tracker_sheet"] = True
            
            return {"success": True, "created": results}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _create_sheet_with_headers(self, spreadsheet_id: str, sheet_name: str, headers: List[str]) -> None:
        """Create a new sheet with RTL support and headers."""
        # Create the sheet
        req = [{"addSheet": {"properties": {"title": sheet_name, "rightToLeft": True}}}]
        response = self._execute_with_retry(
            self.service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body={"requests": req}
            )
        )
        
        # Check if response is valid
        if not response or not response.get("replies"):
            raise Exception(f"Failed to create sheet '{sheet_name}' - no response from API")
        
        sheet_id = response["replies"][0]["addSheet"]["properties"]["sheetId"]
        
        # Add headers
        header_range = f"{sheet_name}!A1:Z1"
        self._execute_with_retry(
            self.service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=header_range,
                valueInputOption="RAW",
                body={"values": [headers]}
            )
        )
        
        print(f"Created sheet '{sheet_name}' with headers in spreadsheet {spreadsheet_id}")
    
    def sheet_exists(self, spreadsheet_id: str, sheet_name: str) -> bool:
        """Check if sheet exists in specific spreadsheet."""
        try:
            # Get spreadsheet metadata
            metadata = self.service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
            sheets = metadata.get('sheets', []) if metadata else []
            
            for sheet in sheets:
                if sheet.get('properties', {}).get('title') == sheet_name:
                    return True
            return False
        except Exception:
            return False
    
    def update_working_sheet_config(self, new_sheet_name: str) -> Dict:
        """Update the working_sheet value in __configs sheet."""
        try:
            # First, read the entire __configs sheet to find the correct row
            config_range = "__configs!A:B"
            response = self._execute_with_retry(
                self.service.spreadsheets().values().get(
                    spreadsheetId=self.budget_spreadsheet_id,
                    range=config_range
                )
            )
            
            values = response.get('values', []) if response else []
            if not values:
                # If no config exists, create it
                self._execute_with_retry(
                    self.service.spreadsheets().values().update(
                        spreadsheetId=self.budget_spreadsheet_id,
                        range="__configs!A1:B1",
                        valueInputOption="RAW",
                        body={"values": [["working_sheet", new_sheet_name]]}
                    )
                )
                return {"success": True, "updated_to": new_sheet_name, "action": "created"}
            
            # Find the row with working_sheet key
            for row_idx, row in enumerate(values):
                if len(row) >= 1 and row[0] == "working_sheet":
                    # Update the value in the same row, column B
                    update_range = f"__configs!B{row_idx + 1}"
                    self._execute_with_retry(
                        self.service.spreadsheets().values().update(
                            spreadsheetId=self.budget_spreadsheet_id,
                            range=update_range,
                            valueInputOption="RAW",
                            body={"values": [[new_sheet_name]]}
                        )
                    )
                    
                    print(f"Updated working_sheet config from '{row[1] if len(row) > 1 else 'undefined'}' to '{new_sheet_name}'")
                    return {"success": True, "updated_to": new_sheet_name, "action": "updated"}
            
            # If working_sheet key not found, append it
            next_row = len(values) + 1
            self._execute_with_retry(
                self.service.spreadsheets().values().update(
                    spreadsheetId=self.budget_spreadsheet_id,
                    range=f"__configs!A{next_row}:B{next_row}",
                    valueInputOption="RAW",
                    body={"values": [["working_sheet", new_sheet_name]]}
                )
            )
            
            return {"success": True, "updated_to": new_sheet_name, "action": "appended"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_previous_month_categories(self) -> List[Dict[str, Union[str, float]]]:
        """Get categories and budgets from current month for template."""
        try:
            current_summary = self.get_budget_summary()
            categories = []
            
            for item in current_summary:
                category = item.get("קטגוריה", "")
                budget = item.get("תקציב", 0)
                if category and budget:
                    categories.append({
                        "קטגוריה": category,
                        "תקציב": float(budget) if budget else 0
                    })
            
            return categories
            
        except Exception as e:
            print(f"Error getting previous categories: {e}")
            return []
    
    def setup_budget_categories(self, sheet_name: str, categories: List[Dict[str, Union[str, float]]]) -> Dict:
        """Set up budget categories in the new budget sheet."""
        try:
            # Prepare data rows
            rows = []
            for cat in categories:
                category = cat.get("קטגוריה", "")
                budget = float(cat.get("תקציב", 0))
                spent = 0.0  # Start with 0
                remaining = budget  # Initially all budget remains
                
                rows.append([category, budget, spent, remaining])
            
            # Write to budget sheet
            if rows:
                data_range = f"{sheet_name}!A2:D{len(rows) + 1}"  # Start from row 2 (after headers)
                self._execute_with_retry(
                    self.service.spreadsheets().values().update(
                        spreadsheetId=self.budget_spreadsheet_id,
                        range=data_range,
                        valueInputOption="RAW",
                        body={"values": rows}
                    )
                )
            
            return {"success": True, "categories_added": len(rows)}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def complete_budget_setup(self, sheet_name: str, categories: List[Dict[str, Union[str, float]]]) -> Dict:
        """Complete budget setup: create sheets, setup categories, update config."""
        try:
            results = {"steps": []}
            
            # Step 1: Create sheets
            create_result = self.create_new_budget_sheets(sheet_name)
            results["steps"].append(f"📋 Created sheets: {create_result}")
            if not create_result["success"]:
                return {"success": False, "error": "Failed to create sheets", "details": results}
            
            # Step 2: Setup categories
            setup_result = self.setup_budget_categories(sheet_name, categories)
            results["steps"].append(f"📊 Setup categories: {setup_result}")
            if not setup_result["success"]:
                return {"success": False, "error": "Failed to setup categories", "details": results}
            
            # Step 3: Update config
            config_result = self.update_working_sheet_config(sheet_name)
            results["steps"].append(f"⚙️ Updated config: {config_result}")
            if not config_result["success"]:
                return {"success": False, "error": "Failed to update config", "details": results}
            
            return {
                "success": True, 
                "sheet_name": sheet_name,
                "categories_count": len(categories),
                "details": results
            }
            
        except Exception as e:
            return {"success": False, "error": str(e), "details": results}

    def get_available_sheets(self) -> List[str]:
        """Get all available sheet names (excluding system sheets)."""
        try:
            meta = self._execute_with_retry(
                self.service.spreadsheets().get(
                    spreadsheetId=self.budget_spreadsheet_id,
                    fields="sheets.properties"
                )
            )
            
            if not meta:
                return []
            
            sheets = []
            for sheet in meta.get("sheets", []):
                sheet_name = sheet["properties"]["title"]
                # Skip system sheets
                if not sheet_name.startswith("__"):
                    sheets.append(sheet_name)
            return sheets
        except Exception as e:
            print(f"Error getting available sheets: {e}")
            return []

class ConfigurationError(Exception):
    """Raised when configuration cannot be read."""
    pass

# Legacy compatibility class for existing code
class Sheets_analyzer:
    """Legacy compatibility wrapper for budget analysis."""
    
    def __init__(self, spreadsheet_id: str):
        self.spreadsheet_id = spreadsheet_id
        self.sheets_io = None  # Will be set from whatsapp.py
    
    def summary_as_dicts(self, sheet_name: str) -> List[Dict]:
        """Return budget summary as list of dicts for GPT processing."""
        if self.sheets_io:
            return self.sheets_io.get_budget_summary()
        return []
    
    def get_remaining_budget(self, sheet_name: str, category: str) -> Optional[float]:
        """Get remaining budget for a specific category."""
        if self.sheets_io:
            budget_info = self.sheets_io.get_category_budget_info(category)
            if budget_info:
                return budget_info.get("כמה נשאר")
        return None
    
    def analyze_sheet(self, sheet_name: str, category: Optional[str] = None) -> Dict:
        """Legacy method for backward compatibility."""
        if self.sheets_io:
            if category:
                budget_info = self.sheets_io.get_category_budget_info(category)
                if budget_info:
                    return {category: budget_info}
                return {}
            else:
                summary = self.sheets_io.get_budget_summary()
                analysis: Dict = {}
                if summary:  # Check if summary is not None or empty
                    for item in summary:
                        cat = item.get("קטגוריה", "")
                        if cat:
                            analysis[cat] = {
                                "תקציב": float(item.get("תקציב", 0)) if item.get("תקציב") else 0,
                                "כמה יצא": float(item.get("כמה יצא", 0)) if item.get("כמה יצא") else 0,
                                "כמה נשאר": float(item.get("כמה נשאר", 0)) if item.get("כמה נשאר") else 0
                            }
                return analysis
        return {}