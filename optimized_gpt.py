import os
import json
import time
import hashlib
from datetime import date
from typing import List, Dict, Literal, Union, cast, Optional

from openai import OpenAI

# ---------------------------------------------------------------------------
# Optimized GPT‑API with Caching and Batch Operations
# ---------------------------------------------------------------------------

JsonDict = Dict[str, Union[str, int, float]]
MessageType = Literal["budget_entry", "question", "budget_setup", "error"]

class OptimizedGPT_API:
    """Enhanced GPT API with intelligent caching and batch operations."""

    def __init__(self, api_key: str, model: str = "gpt-4.1-mini"):
        # Initialize OpenAI client (same as original)
        old_proxy_env = {}
        proxy_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy']
        for var in proxy_vars:
            if var in os.environ:
                old_proxy_env[var] = os.environ[var]
                del os.environ[var]
        
        try:
            self.client = OpenAI(
                api_key=api_key,
                timeout=30.0,
                max_retries=2
            )
        finally:
            for var, value in old_proxy_env.items():
                os.environ[var] = value
        
        self.model = model
        
        # Initialize caching systems
        self._question_cache = {}  # {cache_key: (response, timestamp)}
        self._cache_ttl = 300  # 5 minutes
        self._cache_stats = {"hits": 0, "misses": 0}

    # ------------------------------------------------------------------
    # 1) OPTIMIZATION: Smart Question Caching
    # ------------------------------------------------------------------
    
    def answer_question_cached(self, question: str, summary_rows: List[JsonDict], tx_rows: List[JsonDict]) -> Dict[str, Union[str, bool, int]]:
        """Answer question with intelligent caching."""
        
        # Create cache key from question intent + data state
        question_hash = hashlib.md5(question.lower().encode()).hexdigest()[:8]
        data_hash = hashlib.md5(str(summary_rows + tx_rows[:5]).encode()).hexdigest()[:8]
        cache_key = f"{question_hash}_{data_hash}"
        
        current_time = time.time()
        
        # Check cache first
        if cache_key in self._question_cache:
            cached_response, timestamp = self._question_cache[cache_key]
            if current_time - timestamp < self._cache_ttl:
                self._cache_stats["hits"] += 1
                return {
                    "answer": f"⚡ {cached_response}",  # Lightning bolt indicates cached
                    "cached": True,
                    "cache_age": int(current_time - timestamp)
                }
        
        # Cache miss - generate new response
        self._cache_stats["misses"] += 1
        answer = self._answer_question_uncached(question, summary_rows, tx_rows)
        
        # Store in cache
        self._question_cache[cache_key] = (answer, current_time)
        
        # Clean old cache entries (keep cache size manageable)
        self._cleanup_cache()
        
        return {
            "answer": answer,
            "cached": False,
            "cache_age": 0
        }
    
    def _answer_question_uncached(self, question: str, summary_rows: List[JsonDict], tx_rows: List[JsonDict]) -> str:
        """Original question answering logic (uncached)."""
        system = (
            "אתה עוזר תקציב חכם שעונה בעברית על שאלות בצורה טבעית וחברותית.\n"
            "יש לך גישה לנתוני התקציב:\n\n"
            "**סיכום תקציב (summary_rows):**\n" + json.dumps(summary_rows[:3], ensure_ascii=False, indent=2) + "\n...\n\n"
            "**הוצאות אחרונות (tx_rows):**\n" + json.dumps(tx_rows[:3], ensure_ascii=False, indent=2) + "\n...\n\n"
            "**אתה יכול לענות על:**\n"
            "• שאלות על יתרות ('כמה נשאר?', 'מה המצב?')\n"
            "• הוצאות לפי קטגוריה ('מה הוצאתי על קניות?')\n"
            "• הוצאות לפי זמן ('מה הוצאתי השבוע?')\n"
            "• ניתוחים והשוואות ('איפה הוצאתי הכי הרבה?')\n"
            "• עצות ותובנות ('איך אני עומד עם התקציב?')\n\n"
            "**סגנון תשובה:**\n"
            "• טבעי וחברותי\n"
            "• עם מספרים ספציפיים\n"
            "• עם תובנות מועילות\n"
            "• אם אין מידע - הסבר בנועם\n\n"
            "**דוגמאות לתשובות טובות:**\n"
            "• 'נשארו לך 450₪ בקניות מתוך 800₪ - מצב טוב!'\n"
            "• 'השבוע הוצאת 230₪, רובם על אוכל בחוץ (180₪)'\n"
            "• 'הכי הוצאת על תחבורה - 340₪ מתוך 400₪'\n"
            "• 'התקציב שלך במצב יציב, אין חריגות'\n"
            "• 'לא מצאתי מידע על זה, אבל אני כאן לעזור עם שאלות אחרות'"
        )
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": question}
        ]
        return self._call_chat(messages, temp=0.3)
    
    def _cleanup_cache(self):
        """Remove old cache entries to prevent memory bloat."""
        current_time = time.time()
        expired_keys = [
            k for k, (_, timestamp) in self._question_cache.items() 
            if current_time - timestamp > self._cache_ttl
        ]
        for key in expired_keys:
            del self._question_cache[key]

    # ------------------------------------------------------------------
    # 2) OPTIMIZATION: Batch GPT Operations for Expense Processing  
    # ------------------------------------------------------------------
    
    def process_message_batch(self, text: str, categories: List[str]) -> Dict:
        """
        Combined classification + parsing in a single GPT call.
        Returns comprehensive analysis of the message.
        """
        
        batch_prompt = f"""
אתה עוזר תקציב חכם שמנתח הודעות בעברית. 
הודעה לניתוח: "{text}"
קטגוריות זמינות: {', '.join(categories)}

בצע ניתוח מלא והחזר JSON עם המבנה הבא:

{{
    "message_type": "budget_entry|question|budget_setup|other",
    "confidence": 0.0-1.0,
    "expense_data": {{
        "קטגוריה": "...",
        "פירוט": "...", 
        "מחיר": מספר,
        "תאריך": "YYYY-MM-DD"
    }},
    "quick_answer": "תשובה מהירה אם זו שאלה פשוטה",
    "suggested_action": "פעולה מומלצת",
    "reasoning": "הסבר קצר למה בחרת את הסיווג הזה"
}}

**כללי סיווג:**
- budget_entry: הוצאה או רכישה (קניתי, שילמתי, הוצאה)
- question: שאלה על תקציב (כמה נשאר, מה הוצאתי)  
- budget_setup: יצירת תקציב חדש
- other: שלום, תודה, מזג אוויר

**כללי פירוט הוצאות:**
- השתמש בקטגוריה הכי מתאימה מהרשימה
- פירוט צריך להיות טבעי קצר
- תאריך - היום אם לא צוין אחרת
- מחיר - רק המספר

החזר רק JSON תקני, ללא הסברים נוספים.
"""

        try:
            result = self._call_chat([{"role": "user", "content": batch_prompt}], temp=0.1)
            parsed = json.loads(result)
            
            # Add processing metadata
            parsed["processing_time"] = time.time()
            parsed["batch_processed"] = True
            
            return parsed
        
        except json.JSONDecodeError as e:
            # Fallback if JSON parsing fails
            return {
                "message_type": "error",
                "confidence": 0.0,
                "error": f"Failed to parse GPT response: {e}",
                "batch_processed": False
            }
    
    # ------------------------------------------------------------------
    # 3) Cache Statistics and Management
    # ------------------------------------------------------------------
    
    def get_cache_stats(self) -> Dict[str, Union[int, float]]:
        """Get cache performance statistics."""
        total_requests = self._cache_stats["hits"] + self._cache_stats["misses"]
        hit_rate = self._cache_stats["hits"] / total_requests if total_requests > 0 else 0.0
        
        return {
            "cache_hits": self._cache_stats["hits"],
            "cache_misses": self._cache_stats["misses"], 
            "hit_rate": hit_rate,
            "cache_size": len(self._question_cache)
        }
    
    def clear_cache(self):
        """Clear all cached responses."""
        self._question_cache.clear()
        self._cache_stats = {"hits": 0, "misses": 0}

    # ------------------------------------------------------------------
    # 4) Backward Compatibility Methods (for existing code)
    # ------------------------------------------------------------------
    
    def classify_message(self, text: str, categories: List[str]) -> MessageType:
        """Backward compatible classification (uses batch processing internally)."""
        result = self.process_message_batch(text, categories)
        msg_type = result.get("message_type", "error")
        return cast(MessageType, msg_type) if msg_type in {"budget_entry", "question", "budget_setup", "error"} else "error"
    
    def infer_budget_entry(self, text: str, categories: List[str]) -> JsonDict:
        """Backward compatible expense parsing (uses batch processing internally)."""
        result = self.process_message_batch(text, categories)
        return result.get("expense_data", {})
    
    def answer_question(self, question: str, summary_rows: List[JsonDict], tx_rows: List[JsonDict]) -> str:
        """Backward compatible question answering (uses caching internally)."""
        result = self.answer_question_cached(question, summary_rows, tx_rows)
        return str(result["answer"])

    # ------------------------------------------------------------------
    # 5) Original methods (unchanged for compatibility)
    # ------------------------------------------------------------------
    
    def parse_budget_categories(self, text: str) -> List[Dict[str, Union[str, float]]]:
        """Parse natural language budget category input (unchanged)."""
        system = (
            "אתה עוזר חכם שמבין דיבור טבעי בעברית ומחלץ תקציב לקטגוריות.\n\n"
            "**מה אתה צריך לחלץ:**\n"
            "מטקסט חופשי, זהה קטגוריות וסכומים ובנה JSON.\n\n"
            "**דוגמאות לדיבור טבעי:**\n"
            "• 'קניות 800, אוכל בחוץ 400' → מפוצל וברור\n"
            "• 'אני רוצה 500 לקניות ו-300 לבידור' → טקסט חופשי\n"
            "• 'תחבורה 200 שקל, בריאות גם בערך 400' → עם מילות רישול\n"
            "• 'בואו נשים 1000 על קניות, 600 על מסעדות ובערך 300 על תחבורה' → משפט ארוך\n"
            "• 'צריך תקציב של 400 לבידור, 800 לקניות' → סדר הפוך\n\n"
            "**כללים:**\n"
            "• הבן את הכוונה, לא רק את הפורמט\n"
            "• התעלם ממילות רישול ('בערך', 'גם', 'בואו נשים')\n"
            "• זהה מספרים וקטגוריות גם אם הם מפוזרים\n"
            "• עבור קטגוריות דומות, בחר את השם הכי פשוט\n\n"
            "**פורמט תשובה:**\n"
            "JSON array עם אובייקטים: [{\"קטגוריה\": \"שם\", \"תקציב\": מספר}, ...]\n"
            "החזר רק JSON, ללא הסברים."
        )
        
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": text}
        ]
        raw = self._call_chat(messages)
        return json.loads(raw)

    def suggest_next_month(self, current_month: str) -> str:
        """Suggest next month name based on current month (unchanged)."""
        system = (
            "אתה עוזר שמציע שם לחודש הבא בעברית.\n"
            "קבל שם חודש נוכחי והחזר שם החודש הבא.\n"
            "דוגמאות:\n"
            "נוכחי: 'July' → הבא: 'August'\n"
            "נוכחי: 'ינואר' → הבא: 'פברואר'\n"
            "נוכחי: 'דצמבר' → הבא: 'ינואר'\n"
            "החזר רק את שם החודש, ללא הסברים."
        )
        
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": f"החודש הנוכחי: {current_month}"}
        ]
        return self._call_chat(messages, temp=0).strip()

    def parse_confirmation(self, text: str) -> bool:
        """Parse user confirmation from natural Hebrew speech (unchanged)."""
        system = (
            "אתה עוזר שמזהה אישור או דחייה בדיבור טבעי בעברית.\n\n"
            "**מה אתה צריך לזהות:**\n"
            "האם המשתמש מסכים או מסרב, גם אם הוא מתבטא בצורה לא ישירה.\n\n"
            "**דוגמאות לאישור (yes):**\n"
            "• כן, לא, אישור, בטח\n"
            "• בואו נעשה את זה, אני מסכים\n"
            "• נשמע טוב, אוקיי, מעולה\n"
            "• כן בטח, בהחלט, למה לא\n"
            "• אני רוצה, בואו נתקדם\n"
            "• הזדמנות, בסדר, עובד עליי\n\n"
            "**דוגמאות לדחייה (no):**\n"
            "• לא, ביטול, לא תודה\n"
            "• אני לא רוצה, זה לא מתאים\n"
            "• בואו נדחה, אולי אחר כך\n"
            "• לא עכשיו, לא זמן מתאים\n"
            "• אני מתחרט, לא נעשה\n"
            "• תירגע, עצור, לא צריך\n\n"
            "**כללים:**\n"
            "• הבן את הכוונה העיקרית\n"
            "• התעלם מנימוסים ('תודה', 'בבקשה')\n"
            "• שים לב לטון חיובי או שלילי\n"
            "• במקרה של ספק - נטה לדחייה (no)\n\n"
            "החזר רק 'yes' או 'no'."
        )
        
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": text}
        ]
        result = self._call_chat(messages, temp=0).strip().lower()
        return result == "yes"

    # ------------------------------------------------------------------
    # Internal helper to call the API once
    # ------------------------------------------------------------------
    def _call_chat(self, messages: List[Dict[str, str]], temp: float = 0.0, max_t: int = 512) -> str:
        """Internal helper to call OpenAI API."""
        formatted_messages = []
        for msg in messages:
            formatted_msg = {
                "role": msg["role"],
                "content": msg["content"]
            }
            formatted_messages.append(formatted_msg)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=formatted_messages,
            temperature=temp,
            max_tokens=max_t
        )
        content = response.choices[0].message.content
        if content is None:
            return ""
        return content.strip() 