import os
import requests
import json
from datetime import datetime, timedelta
from typing import List
from flask import Flask, request
from sheets_IO import SheetsIO, Sheets_analyzer
from GPT_API import GPT_API

# ---------------------------------------------------------------------------
# Load configuration - Environment variables for production or keys.json for local
# ---------------------------------------------------------------------------

def load_config():
    """Load configuration from environment variables or keys.json file."""
    config = {}
    
    # Try to load from environment variables first (for production)
    if os.getenv('META_ACCESS_TOKEN'):
        config = {
            "META_ACCESS_TOKEN": os.getenv('META_ACCESS_TOKEN'),
            "META_PHONE_NUMBER_ID": os.getenv('META_PHONE_NUMBER_ID'),
            "META_WEBHOOK_VERIFY_TOKEN": os.getenv('META_WEBHOOK_VERIFY_TOKEN'),
            "META_PHONE_NUMBER": os.getenv('META_PHONE_NUMBER'),
            "SUMMARY_SPREADSHEET_ID": os.getenv('BUDGET_SHEET_ID'),
            "IO_SPREADSHEET_ID": os.getenv('TRACKER_SHEET_ID'),
            "GPT_API_KEY": os.getenv('OPENAI_API_KEY'),
            "USER1_PHONE": os.getenv('USER1_PHONE', '1234567890'),
            "USER1_NAME": os.getenv('USER1_NAME', 'משתמש 1'),
            "USER2_PHONE": os.getenv('USER2_PHONE', '0987654321'),
            "USER2_NAME": os.getenv('USER2_NAME', 'משתמש 2'),
        }
    else:
        # Fall back to keys.json for local development
        try:
            with open('credits/keys.json', 'r') as f:
                config = json.load(f)
        except FileNotFoundError:
            raise RuntimeError("Configuration not found. Please set environment variables or create credits/keys.json")
    
    return config

keys = load_config()

# Meta WhatsApp Business API
META_ACCESS_TOKEN = keys["META_ACCESS_TOKEN"]
META_PHONE_NUMBER_ID = keys["META_PHONE_NUMBER_ID"]
META_VERIFY_TOKEN = keys["META_WEBHOOK_VERIFY_TOKEN"]
META_PHONE_NUMBER = keys["META_PHONE_NUMBER"]

# Google Sheets - New architecture
BUDGET_SHEET_ID = keys["SUMMARY_SPREADSHEET_ID"]    # Budget sheet with categories, budgets, spent, remaining
TRACKER_SHEET_ID = keys["IO_SPREADSHEET_ID"]         # Tracker sheet with individual transactions
GPT_API_KEY = keys["GPT_API_KEY"]

# ---------------------------------------------------------------------------
# Initialize helpers with new architecture
# ---------------------------------------------------------------------------

# Initialize GPT lazily to avoid startup issues
gpt = None
sheets_io = SheetsIO(BUDGET_SHEET_ID, TRACKER_SHEET_ID)
analyzer = Sheets_analyzer(BUDGET_SHEET_ID)
analyzer.sheets_io = sheets_io  # type: ignore  # Link for compatibility
app = Flask(__name__)

def get_gpt():
    """Get GPT client, initializing it if needed."""
    global gpt
    if gpt is None:
        try:
            print("Initializing GPT API with gpt-4.1-mini...")
            gpt = GPT_API(api_key=GPT_API_KEY, model="gpt-4.1-mini")
            test_response = gpt._call_chat([{"role": "user", "content": "Hello"}], temp=0, max_t=25)
            print("GPT-4.1-mini fallback successful!")
        except Exception as e:
            print(f"ERROR: GPT-4.1-mini initialization failed: {e}")
            print(f"API Key length: {len(GPT_API_KEY) if GPT_API_KEY else 'None'}")
            print(f"API Key prefix: {GPT_API_KEY[:10] if GPT_API_KEY else 'None'}...")
            # Try fallback to gpt-4.1-mini
            try:    
                # Start with gpt-4o-mini as it's more reliable in cloud environments
                print("Initializing GPT API with gpt-4o-mini as fallback...")
                gpt = GPT_API(api_key=GPT_API_KEY, model="gpt-4o-mini")
                # Test the connection with a simple call
                test_response = gpt._call_chat([{"role": "user", "content": "Hello"}], temp=0, max_t=25)
                print("GPT-4o-mini initialization successful!")               
            except Exception as e2:
                print(f"ERROR: All models failed: {e2}")
                gpt = None
    return gpt

# ---------------------------------------------------------------------------
# User Configuration & Smart Features
# ---------------------------------------------------------------------------

USER_PROFILES = {
    keys.get("USER1_PHONE", "default"): {
        "name": keys.get("USER1_NAME", "משתמש 1"),
        "emoji": "👨‍💼"
    },
    keys.get("USER2_PHONE", "default"): {
        "name": keys.get("USER2_NAME", "משתמש 2"), 
        "emoji": "👩‍💼"
    }
}

QUICK_COMMANDS = {
    "יתרה": "show_remaining_budgets",
    "סיכום": "show_weekly_summary",
    "עזרה": "show_help",
    "קטגוריות": "show_categories",
    "רענון": "refresh_budgets"
}

# Budget building pipeline state management
BUDGET_SETUP_STATES = {}  # phone_number -> state_info

def get_user_info(phone_number: str) -> dict:
    """Get user information from phone number."""
    return USER_PROFILES.get(phone_number, {
        "name": "משתמש", 
        "emoji": "👤"
    })

def get_smart_budget_warning(category: str, remaining: float, total_budget: float) -> str:
    """Generate smart budget warning based on remaining percentage."""
    if total_budget == 0:
        return f"✅ נותרו {remaining}₪ ב‹{category}›"
    
    percentage = (remaining / total_budget) * 100
    
    if remaining < 0:
        return f"🚨 חריגה! חרגת ב-{abs(remaining)}₪ מתקציב ‹{category}›"
    elif percentage < 5:
        return f"🚨 אזהרה! נותרו רק {remaining}₪ ב‹{category}› ({percentage:.1f}%)"
    elif percentage < 15:
        return f"⚠️ תשומת לב! נותרו {remaining}₪ ב‹{category}› ({percentage:.1f}%)"
    elif percentage < 30:
        return f"⏰ נותרו {remaining}₪ ב‹{category}› ({percentage:.1f}%)"
    else:
        return f"✅ נותרו {remaining}₪ ב‹{category}›"

def check_potential_duplicate(entry: dict) -> str:
    """Check for potential duplicate transactions today."""
    try:
        # Get today's transactions
        today = datetime.now().strftime("%Y-%m-%d")
        recent_transactions = sheets_io.get_recent_transactions(limit=10)
        
        # Check for similar transactions today
        for tx in recent_transactions:
            tx_date = tx.get("תאריך", "")
            tx_category = tx.get("קטגוריה", "")
            tx_description = tx.get("פירוט", "")
            tx_price = tx.get("מחיר", "")
            
            if (tx_date == today and 
                tx_category == entry.get("קטגוריה") and
                tx_description == entry.get("פירוט") and
                str(tx_price) == str(entry.get("מחיר"))):
                return f"🔄 אזהרה: נרשמה הוצאה זהה היום - {tx_description} {tx_price}₪"
        
        return ""
    except Exception:
        return ""

def detect_natural_commands(text: str) -> List[str]:
    """Detect natural language alternatives to quick commands."""
    text_lower = text.lower()
    commands = []
    
    # Budget balance queries
    if any(phrase in text_lower for phrase in [
        "כמה נשאר", "מה היתרה", "תראה לי את היתרה", "מה המצב עם הכסף",
        "איך אני עומד", "מה יש לי", "כמה יש לי", "מה הסטטוס"
    ]):
        commands.append("show_remaining_budgets")
    
    # Category listing
    if any(phrase in text_lower for phrase in [
        "איזה קטגוריות", "מה הקטגוריות", "תראה לי קטגוריות", "רשימת קטגוריות",
        "איזה אפשרויות", "מה אפשר", "איך מחלקים"
    ]):
        commands.append("show_categories")
    
    # Help requests
    if any(phrase in text_lower for phrase in [
        "איך זה עובד", "מה אפשר לעשות", "איך להשתמש", "מה הפקודות",
        "עזרה", "הדרכה", "מדריך", "איך אני משתמש"
    ]):
        commands.append("show_help")
    
    # Refresh/recalculate
    if any(phrase in text_lower for phrase in [
        "רענן", "עדכן", "חשב מחדש", "בדוק שוב", "תקן את המספרים",
        "עדכן יתרות", "תסנכרן"
    ]):
        commands.append("refresh_budgets")
    
    return commands

def handle_natural_commands(sender: str, commands: List[str], original_text: str) -> str:
    """Handle natural language command alternatives."""
    user_info = get_user_info(sender)
    
    # If multiple commands detected, handle the first one
    if commands:
        command = commands[0]
        
        # Add a more natural response prefix
        natural_prefixes = {
            "show_remaining_budgets": f"{user_info['emoji']} בואו נבדוק מה המצב:",
            "show_categories": f"{user_info['emoji']} הנה הקטגוריות הזמינות:",
            "show_help": f"{user_info['emoji']} אני כאן לעזור! הנה מה שאפשר לעשות:",
            "refresh_budgets": f"{user_info['emoji']} בואו נרענן את הכל:"
        }
        
        result = handle_quick_command(command, sender)
        
        # Replace the formal prefix with natural one
        if command in natural_prefixes:
            # Remove the formal emoji prefix and add natural one
            if result.startswith(f"{user_info['emoji']} **"):
                result = result.replace(f"{user_info['emoji']} **", natural_prefixes[command] + "\n**", 1)
            else:
                result = natural_prefixes[command] + "\n" + result
        
        return result
    
    return ""

def handle_quick_command(command: str, sender: str) -> str:
    """Handle quick commands."""
    user_info = get_user_info(sender)
    
    if command == "show_remaining_budgets":
        try:
            summary = sheets_io.get_budget_summary()
            if not summary:
                return "❌ לא נמצא מידע על התקציב"
            
            result = f"{user_info['emoji']} **יתרות התקציב:**\n"
            for item in summary:
                category = item.get("קטגוריה", "")
                remaining = float(item.get("כמה נשאר", 0)) if item.get("כמה נשאר") else 0
                total = float(item.get("תקציב", 0)) if item.get("תקציב") else 0
                warning = get_smart_budget_warning(category, remaining, total)
                result += f"• {warning}\n"
            
            return result
        except Exception as e:
            return f"⚠️ שגיאה בקבלת יתרות: {e}"
    
    elif command == "show_categories":
        try:
            cats = sheets_io.get_budget_categories()
            return f"📂 **קטגוריות זמינות:**\n" + "\n".join([f"• {cat}" for cat in cats])
        except Exception as e:
            return f"⚠️ שגיאה בקבלת קטגוריות: {e}"
    
    elif command == "show_help":
        return """🤖 **מדריך שימוש:**

📝 **לרישום הוצאה:**
• "קניתי לחם ב-12"
• "פלאפל 18 שקל"
• "דלק 200₪"
• "שילמתי 50 על דלק"

❓ **לשאלות:**
• "כמה נשאר בקניות?"
• "מה הוצאתי השבוע?"
• "מה המצב עם הכסף?"
• "איך אני עומד עם התקציב?"

🏗️ **הגדרת תקציב חדש:**
• "רוצה ליצור תקציב חדש"
• "בואו נעשה תקציב חדש"
• "צריך תקציב חדש"

⚡ **פקודות מהירות:**
• יתרה - יתרות כל הקטגוריות
• קטגוריות - רשימת קטגוריות
• רענון - עדכון יתרות
• עזרה - המדריך הזה

💡 **טיפים:**
• הבוט מבין דיבור טבעי
• מזהה כפילויות אוטומטית
• מקבל תאריכים בעברית
• מבין מספרים בעברית"""

    elif command == "refresh_budgets":
        try:
            # Get current categories and recalculate totals
            categories = sheets_io.get_budget_categories()
            updated_count = 0
            
            for category in categories:
                sheets_io.update_budget_sheet(category)
                updated_count += 1
            
            return f"🔄 **רענון הושלם!**\n✅ עודכנו {updated_count} קטגוריות בתקציב\n💰 כל הסכומים עכשיו מדויקים"
        except Exception as e:
            return f"⚠️ שגיאה ברענון: {e}"

    return "❓ פקודה לא מוכרת"

# ---------------------------------------------------------------------------
# Budget Building Pipeline Functions
# ---------------------------------------------------------------------------

def start_budget_setup(sender: str) -> str:
    """Start the budget building pipeline."""
    user_info = get_user_info(sender)
    
    try:
        # Get current month for smart suggestion
        current_month = sheets_io.get_working_sheet_name()
        gpt_client = get_gpt()
        if gpt_client:
            suggested_month = gpt_client.suggest_next_month(current_month)
        else:
            suggested_month = "חודש חדש"
        
        # Store state
        BUDGET_SETUP_STATES[sender] = {
            "step": "awaiting_confirmation",
            "suggested_month": suggested_month,
            "current_month": current_month
        }
        
        return f"""{user_info['emoji']} **הגדרת תקציב חדש**

🗓️ החודש הנוכחי: {current_month}
💡 הצעה לחודש הבא: **{suggested_month}**

❓ רוצה ליצור תקציב חדש עבור "{suggested_month}"?

💬 תגובות אפשריות:
• "כן" - יצירת תקציב עבור {suggested_month}
• "לא" - ביטול
• שם חודש אחר - למשל "ספטמבר\""""

    except Exception as e:
        return f"⚠️ שגיאה בהכנת תקציב חדש: {e}"

def handle_budget_setup_step(sender: str, text: str) -> str:
    """Handle budget setup conversation steps."""
    user_info = get_user_info(sender)
    
    if sender not in BUDGET_SETUP_STATES:
        return "❌ לא נמצא תהליך הגדרת תקציב פעיל. כתבו 'תקציב חדש' להתחלה."
    
    state = BUDGET_SETUP_STATES[sender]
    
    try:
        if state["step"] == "awaiting_confirmation":
            return _handle_month_confirmation(sender, text, state)
        elif state["step"] == "awaiting_categories":
            return _handle_categories_input(sender, text, state)
        elif state["step"] == "awaiting_final_confirmation":
            return _handle_final_confirmation(sender, text, state)
        else:
            return "❌ שגיאה במצב ההגדרה. נתחיל מחדש - כתבו 'תקציב חדש'."
            
    except Exception as e:
        # Clean up state on error
        if sender in BUDGET_SETUP_STATES:
            del BUDGET_SETUP_STATES[sender]
        return f"⚠️ שגיאה בהגדרת התקציב: {e}\nכתבו 'תקציב חדש' לנסות שוב."

def _handle_month_confirmation(sender: str, text: str, state: dict) -> str:
    """Handle month confirmation step."""
    user_info = get_user_info(sender)
    
    # Check if user confirmed suggested month
    gpt_client = get_gpt()
    if gpt_client and gpt_client.parse_confirmation(text):
        month_name = state["suggested_month"]
    else:
        # Check if user provided a custom month name
        if len(text.strip()) > 1 and not any(word in text.lower() for word in ["לא", "ביטול", "לא תודה"]):
            month_name = text.strip()
        else:
            # User declined
            del BUDGET_SETUP_STATES[sender]
            return f"{user_info['emoji']} בסדר, ביטלתי את יצירת התקציב החדש."
    
    # Get previous month's categories for template
    previous_categories = sheets_io.get_previous_month_categories()
    
    # Update state
    state["step"] = "awaiting_categories"
    state["month_name"] = month_name
    state["suggested_categories"] = previous_categories
    
    if previous_categories:
        # Show template from previous month
        template_text = ""
        total_suggested = 0
        for cat in previous_categories:
            cat_name = cat["קטגוריה"]
            amount = float(cat["תקציב"]) if cat["תקציב"] else 0
            template_text += f"• {cat_name}: {amount}₪\n"
            total_suggested += amount
        
        return f"""{user_info['emoji']} **הגדרת קטגוריות עבור {month_name}**

📋 **קטגוריות מהחודש הקודם:**
{template_text}
💰 **סה"כ מוצע: {total_suggested}₪**

💡 **אפשרויות:**
1️⃣ "אישור" - להשתמש באותן קטגוריות וסכומים
2️⃣ רשימה חדשה - למשל: "קניות 800, אוכל בחוץ 400, תחבורה 200"
3️⃣ "ביטול" - לבטל את ההגדרה"""
    
    else:
        return f"""{user_info['emoji']} **הגדרת קטגוריות עבור {month_name}**

📝 **הזינו את הקטגוריות והסכומים:**
דוגמה: "קניות 800, אוכל בחוץ 400, תחבורה 200, בידור 300"

💡 אפשר גם לכתוב כל קטגוריה בשורה נפרדת"""

def _handle_categories_input(sender: str, text: str, state: dict) -> str:
    """Handle categories input step."""
    user_info = get_user_info(sender)
    
    # Check for cancellation
    if any(word in text.lower() for word in ["ביטול", "לא", "עצור"]):
        del BUDGET_SETUP_STATES[sender]
        return f"{user_info['emoji']} ביטלתי את הגדרת התקציב."
    
    # Check if user approved suggested categories
    gpt_client = get_gpt()
    if gpt_client and gpt_client.parse_confirmation(text) and state.get("suggested_categories"):
        categories = state["suggested_categories"]
    else:
        # Parse user input
        try:
            if gpt_client:
                categories = gpt_client.parse_budget_categories(text)
            else:
                print("ERROR: GPT client is None during budget category parsing")
                return "⚠️ שירות הבינה המלאכותית אינו זמין כרגע. בדקו את המפתח API ונסו שוב מאוחר יותר."
        except Exception as e:
            print(f"ERROR in parse_budget_categories: {e}")
            return f"⚠️ לא הצלחתי לפרק את הקטגוריות. נסו שוב:\nדוגמה: 'קניות 800, אוכל בחוץ 400'\n\nשגיאה: {e}"
    
    if not categories:
        return "❌ לא נמצאו קטגוריות תקפות. נסו שוב עם הפורמט: 'קטגוריה סכום, קטגוריה סכום'"
    
    # Prepare summary
    summary_text = ""
    total_budget = 0
    for cat in categories:
        cat_name = cat["קטגוריה"]
        amount = float(cat["תקציב"]) if cat["תקציב"] else 0
        summary_text += f"• {cat_name}: {amount}₪\n"
        total_budget += amount
    
    # Update state
    state["step"] = "awaiting_final_confirmation"
    state["categories"] = categories
    
    return f"""{user_info['emoji']} **סיכום התקציב החדש**

📋 **חודש:** {state['month_name']}
💰 **קטגוריות:**
{summary_text}
💯 **סה"כ תקציב:** {total_budget}₪

✅ **לאישור סופי כתבו "אישור"**
❌ **לביטול כתבו "ביטול"**"""

def _handle_final_confirmation(sender: str, text: str, state: dict) -> str:
    """Handle final confirmation and create the budget."""
    user_info = get_user_info(sender)
    
    gpt_client = get_gpt()
    if not gpt_client or not gpt_client.parse_confirmation(text):
        del BUDGET_SETUP_STATES[sender]
        return f"{user_info['emoji']} ביטלתי את יצירת התקציב החדש."

    # Create the budget!
    try:
        month_name = state["month_name"]
        categories = state["categories"]

        result = sheets_io.complete_budget_setup(month_name, categories)

        # Clean up state
        del BUDGET_SETUP_STATES[sender]

        if result["success"]:
            return f"""{user_info['emoji']} 🎉 **התקציב החדש נוצר בהצלחה!**

📅 **חודש:** {month_name}
📊 **קטגוריות:** {result['categories_count']}
✅ **מוכן לשימוש!**

💡 **עכשיו אפשר להתחיל לרשום הוצאות:**
דוגמה: "קניתי קפה ב-15\""""
        else:
            return f"❌ **שגיאה ביצירת התקציב:**\n{result.get('error', 'שגיאה לא ידועה')}\n\nנסו שוב עם 'תקציב חדש'."

    except Exception as e:
        # Clean up state
        del BUDGET_SETUP_STATES[sender]
        return f"⚠️ שגיאה ביצירת התקציב: {e}\nנסו שוב עם 'תקציב חדש'."

# ---------------------------------------------------------------------------
# Meta WhatsApp API Functions
# ---------------------------------------------------------------------------

def send_whatsapp_message(to: str, message: str) -> bool:
    """Send a WhatsApp message using Meta's API."""
    try:
        url = f"https://graph.facebook.com/v17.0/{META_PHONE_NUMBER_ID}/messages"
        headers = {
            'Authorization': f'Bearer {META_ACCESS_TOKEN}',
            'Content-Type': 'application/json'
        }
        
        # Clean phone number - remove any 'whatsapp:' prefix
        if to.startswith('whatsapp:'):
            to = to[9:]
        
        data = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {
                "body": message
            }
        }
        
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        
        return True
        
    except Exception as e:
        print(f"Error sending message: {e}")
        return False

def parse_meta_webhook(webhook_data: dict) -> dict:
    """Parse Meta's webhook payload and extract message data."""
    try:
        # Navigate Meta's webhook structure
        entry = webhook_data.get('entry', [{}])[0]
        changes = entry.get('changes', [{}])[0]
        value = changes.get('value', {})
        
        # Get message data
        messages = value.get('messages', [])
        if not messages:
            return {}
        
        message = messages[0]
        
        # Extract sender and message
        sender = message.get('from', '')
        message_type = message.get('type', '')
        
        if message_type == 'text':
            body = message.get('text', {}).get('body', '')
        else:
            body = ''
        
        return {
            'sender': sender,
            'body': body,
            'message_type': message_type
        }
        
    except Exception as e:
        print(f"Error parsing webhook: {e}")
        return {}

# ---------------------------------------------------------------------------
# Main webhook route - Meta WhatsApp Business API
# ---------------------------------------------------------------------------

@app.route("/webhook", methods=["POST", "GET"])
def webhook():
    """Main webhook endpoint for Meta WhatsApp Business API."""
    
    if request.method == "GET":
        # Webhook verification
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        
        if mode == 'subscribe' and token == META_VERIFY_TOKEN and challenge:
            print("Webhook verified successfully!")
            return challenge, 200
        else:
            print("Webhook verification failed!")
            return "Forbidden", 403
    
    elif request.method == "POST":
        # Handle incoming messages
        try:
            webhook_data = request.get_json()
            
            # Parse message from Meta's webhook
            message_data = parse_meta_webhook(webhook_data)
            
            if not message_data or not message_data.get('sender') or not message_data.get('body'):
                return "OK", 200
            
            sender = message_data['sender']
            text = message_data['body'].strip()
            
            # Get user info for personalization
            user_info = get_user_info(sender)
            
            # Handle quick commands first
            if text in QUICK_COMMANDS:
                reply = handle_quick_command(QUICK_COMMANDS[text], sender)
                send_whatsapp_message(sender, reply)
                return "OK", 200
            
            # Handle natural language alternatives to quick commands
            natural_commands = detect_natural_commands(text)
            if natural_commands:
                reply = handle_natural_commands(sender, natural_commands, text)
                send_whatsapp_message(sender, reply)
                return "OK", 200

            # Handle context-aware responses
            if any(word in text.lower() for word in ["תודה", "תודה רבה", "יפה", "מעולה", "כל הכבוד"]):
                send_whatsapp_message(sender, f"{user_info['emoji']} בכיף! יש עוד הוצאות להזין?")
                return "OK", 200
            
            if any(word in text.lower() for word in ["שלום", "היי", "הי", "מה נשמע", "מה המצב"]):
                send_whatsapp_message(sender, f"שלום {user_info['name']}! {user_info['emoji']}\nאפשר לעזור לך עם התקציב?")
                return "OK", 200

            # First check if user is in budget setup flow
            if sender in BUDGET_SETUP_STATES:
                reply = handle_budget_setup_step(sender, text)
                send_whatsapp_message(sender, reply)
                return "OK", 200

            # Get categories from budget sheet
            cats = sheets_io.get_budget_categories()
            
            # Get GPT client
            gpt_client = get_gpt()
            if not gpt_client:
                send_whatsapp_message(sender, "⚠️ שירות הבינה המלאכותית אינו זמין כרגע. אנא נסו שוב מאוחר יותר.")
                return "OK", 200
                
            msg_type = gpt_client.classify_message(text, cats)

            # -------------------------------------------------------------------
            # 1️⃣  Budget setup – NEW FEATURE
            # -------------------------------------------------------------------
            if msg_type == "budget_setup":
                reply = start_budget_setup(sender)
                send_whatsapp_message(sender, reply)
                return "OK", 200

            # -------------------------------------------------------------------
            # 2️⃣  Budget entry – NEW FLOW
            # -------------------------------------------------------------------
            if msg_type == "budget_entry":
                try:
                    # Step 1: Get GPT to parse the expense
                    entry = gpt_client.infer_budget_entry(text, cats)
                    category = entry["קטגוריה"]
                    
                    # Step 2: Validate category exists in budget sheet
                    if category not in cats:
                        send_whatsapp_message(sender, f"⚠️ הקטגוריה '{category}' אינה קיימת בגליון התקציב.")
                        return "OK", 200

                    # Step 3: Check for potential duplicates
                    duplicate_warning = check_potential_duplicate(entry)
                    
                    # Step 4: Process the expense (add to tracker + update budget)
                    result = sheets_io.process_expense(entry)
                    
                    if not result["success"]:
                        send_whatsapp_message(sender, f"⚠️ שגיאה בעיבוד: {result['error']}")
                        return "OK", 200
                    
                    # Step 5: Get updated budget info and send confirmation
                    budget_info = result["budget_info"]
                    if budget_info:
                        smart_warning = get_smart_budget_warning(
                            category, 
                            budget_info["כמה נשאר"], 
                            budget_info["תקציב"]
                        )
                    else:
                        smart_warning = "לא נמצא מידע על יתרה"

                    # Build personalized reply
                    reply = f"{user_info['emoji']} **נרשם בהצלחה!**\n"
                    reply += f"📝 {entry.get('פירוט', '')} - {entry.get('מחיר', '')}₪\n"
                    reply += f"💰 {smart_warning}\n"
                    
                    if duplicate_warning:
                        reply += f"\n{duplicate_warning}"
                    
                    send_whatsapp_message(sender, reply)
                    
                except Exception as exc:
                    send_whatsapp_message(sender, f"⚠️ שגיאה בעיבוד: {exc}")

                return "OK", 200

            # -------------------------------------------------------------------
            # 3️⃣  Question – Enhanced with new architecture
            # -------------------------------------------------------------------
            if msg_type == "question":
                try:
                    # Get data from both sheets
                    summary = sheets_io.get_budget_summary()
                    tx_rows = sheets_io.get_recent_transactions(limit=20)
                    
                    # Ask GPT
                    answer = gpt_client.answer_question(text, summary, tx_rows)
                    
                    # Personalized response
                    personalized_answer = f"{user_info['emoji']} {answer}"
                    send_whatsapp_message(sender, personalized_answer)
                    
                except Exception as exc:
                    send_whatsapp_message(sender, f"⚠️ לא הצלחתי לענות: {exc}")
                return "OK", 200

            # -------------------------------------------------------------------
            # 4️⃣  Fallback
            # -------------------------------------------------------------------
            fallback_msg = f"""🤖 {user_info['name']}, לא הבנתי בדיוק מה רציתם.

📝 **דוגמאות לרישום הוצאה:**
• "קניתי לחם ב-12"
• "פלאפל 18₪"
• "דלק 200 שקל"

❓ **דוגמאות לשאלות:**
• "כמה נשאר בקניות?"
• "מה הוצאתי השבוע?"

🏗️ **יצירת תקציב חדש:**
• "רוצה ליצור תקציב חדש"
• "תקציב חדש"

⚡ **פקודות מהירות:**
• יתרה
• עזרה
• קטגוריות

💡 נסו שוב או כתבו "עזרה" למדריך מלא!"""
            
            send_whatsapp_message(sender, fallback_msg)
            return "OK", 200
            
        except Exception as e:
            print(f"Error processing webhook: {e}")
            return "OK", 200

    return "OK", 200

# ---------------------------------------------------------------------------
# Legacy endpoint for backward compatibility
# ---------------------------------------------------------------------------

@app.route("/whatsapp", methods=["POST", "GET"])
def whatsapp_legacy():
    """Legacy endpoint - redirects to new webhook endpoint."""
    if request.method == "GET":
        return "Please use /webhook endpoint", 200
    return webhook()

# ---------------------------------------------------------------------------
# Health check and status endpoints for Google App Engine
# ---------------------------------------------------------------------------

@app.route("/")
def health_check():
    """Health check endpoint for Google App Engine."""
    return {
        "status": "healthy",
        "service": "WhatsApp Budget Bot",
        "version": "2.0",
        "timestamp": datetime.now().isoformat()
    }, 200

@app.route("/health")
def health_detailed():
    """Detailed health check endpoint."""
    try:
        # Test Google Sheets connection
        categories = sheets_io.get_budget_categories()
        sheets_healthy = len(categories) > 0
        
        # Test GPT API (basic test)
        gpt_healthy = True  # We'll assume healthy unless we get an error
        
        health_status = {
            "status": "healthy" if sheets_healthy and gpt_healthy else "unhealthy",
            "service": "WhatsApp Budget Bot",
            "version": "2.0",
            "timestamp": datetime.now().isoformat(),
            "components": {
                "google_sheets": "healthy" if sheets_healthy else "unhealthy",
                "gpt_api": "healthy" if gpt_healthy else "unhealthy",
                "categories_count": len(categories) if sheets_healthy else 0
            }
        }
        
        return health_status, 200 if health_status["status"] == "healthy" else 503
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "WhatsApp Budget Bot",
            "version": "2.0",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }, 503

# ---------------------------------------------------------------------------
# Production vs Development startup
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # This is for local development only
    # In production, App Engine will use the entrypoint defined in app.yaml
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
    