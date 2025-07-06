import os
import json
from datetime import date
from typing import List, Dict, Literal, Union, cast

from openai import OpenAI

# ---------------------------------------------------------------------------
# GPT‑API helper  – v3 (2025‑07‑03)
# ---------------------------------------------------------------------------
# Tweaks requested by the user:
# ‑ “פירוט/מוצר” may contain up to **five Hebrew words** if that is what the
#   user wrote (e.g. "חיתולים לתינוק סופר פלוס"). One word is fine when the
#   item is simple ("לחם").
# ‑ Added richer few‑shot examples so takeaway food is mapped to **אוכל בחוץ**,
#   public‑transport tickets to **תחבורה** etc.
# ---------------------------------------------------------------------------

JsonDict = Dict[str, Union[str, int, float]]
MessageType = Literal["budget_entry", "question", "budget_setup", "error"]


class GPT_API:
    """Light wrapper around the OpenAI Chat API."""

    def __init__(self, api_key: str, model: str = "gpt-4.1-mini"):
        # Explicitly control OpenAI client initialization to avoid proxy issues in App Engine
        # Clear any environment variables that might interfere
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
            # Restore environment variables
            for var, value in old_proxy_env.items():
                os.environ[var] = value
        
        self.model = model

    # ------------------------------------------------------------------
    # 1) Message classification
    # ------------------------------------------------------------------
    def classify_message(self, text: str, categories: List[str]) -> MessageType:
        prompt = (
            "אתה מסווג הודעות בעברית לפי הכוונה של המשתמש. "
            "סווג את ההודעה לאחת מ-4 קטגוריות:\n\n"
            "**budget_entry** - הוצאה או רכישה:\n"
            "• קניתי קפה ב-12\n"
            "• שילמתי 50 שקל על דלק\n"
            "• הוצאה של 200 על קניות\n"
            "• בילוי אתמול עלה לי 150\n"
            "• פיצה 45 שקל\n\n"
            "**question** - שאלה על תקציב:\n"
            "• כמה נשאר בקניות?\n"
            "• מה הוצאתי השבוע?\n"
            "• תראה לי את היתרה\n"
            "• איך אני עומד עם התקציב?\n"
            "• מה המצב עם הכסף?\n\n"
            "**budget_setup** - יצירת תקציב חדש:\n"
            "• רוצה ליצור תקציב חדש\n"
            "• בואו נעשה תקציב חדש\n"
            "• חודש חדש\n"
            "• צריך תקציב חדש\n"
            "• איך יוצרים תקציב?\n\n"
            "**error** - כל דבר אחר:\n"
            "• שלום מה נשמע?\n"
            "• תודה\n"
            "• מזג האוויר\n\n"
            "החזר רק את הלייבל: budget_entry, question, budget_setup, או error\n"
            "הודעה לסיווג: " + text
        )
        r = self._call_chat([{"role": "user", "content": prompt}], temp=0.1)
        label = r.strip().lower()
        return cast(MessageType, label) if label in {"budget_entry", "question", "budget_setup", "error"} else "error"

    # ------------------------------------------------------------------
    # 2) Parse a budget entry
    # ------------------------------------------------------------------
    def infer_budget_entry(self, text: str, categories: List[str]) -> JsonDict:
        system = (
            "אתה עוזר חכם שמבין דיבור טבעי בעברית ומחלץ מידע על הוצאות.\n"
            "הקטגוריות הזמינות: " + ", ".join(categories) + ".\n\n"
            "מהטקסט החופשי, חלץ:\n"
            "• **קטגוריה** - הכי מתאימה מהרשימה\n"
            "• **פירוט** - תיאור טבעי וקצר של הרכישה\n"
            "• **מחיר** - הסכום (רק מספר)\n"
            "• **תאריך** - YYYY-MM-DD (היום אם לא צוין)\n\n"
            "**דוגמאות לדיבור טבעי:**\n"
            "• 'קניתי קפה ב-15' → פירוט: 'קפה'\n"
            "• 'שילמתי 200 שקל על דלק' → פירוט: 'דלק'\n"
            "• 'בילוי אתמול עלה לי 150' → פירוט: 'בילוי'\n"
            "• 'הוצאה של 45 על פיצה' → פירוט: 'פיצה'\n"
            "• 'קניות השבוע 800 שקל' → פירוט: 'קניות השבוע'\n\n"
            "**כללים:**\n"
            "• פירוט צריך להיות טבעי ומובן\n"
            "• אם יש תאריך יחסי (אתמול, אמש) - חשב את התאריך האמיתי\n"
            "• אם לא ברור איזו קטגוריה - בחר הכי הגיונית\n\n"
            "החזר JSON בלבד עם המפתחות: 'קטגוריה', 'פירוט', 'מחיר', 'תאריך'"
        )

        few_shots = [
            # Take‑away food → אוכל בחוץ
            ("קניתי פלאפל ב‑18", {"קטגוריה": "אוכל בחוץ", "פירוט": "פלאפל", "מחיר": 18, "תאריך": date.today().isoformat()}),
            ("הזמנתי פיצה משפחתית ב‑55 שקל", {"קטגוריה": "אוכל בחוץ", "פירוט": "פיצה משפחתית", "מחיר": 55, "תאריך": date.today().isoformat()}),
            # Groceries → קניות
            ("קניתי חלב וחלה ב‑20", {"קטגוריה": "קניות", "פירוט": "חלב וחלה", "מחיר": 20, "תאריך": date.today().isoformat()}),
            # Transport
            ("רכבת לתל אביב 28 ₪", {"קטגוריה": "תחבורה", "פירוט": "כרטיס רכבת", "מחיר": 28, "תאריך": date.today().isoformat()}),
            # Entertainment
            ("מנוי נטפליקס 39.9", {"קטגוריה": "בידור", "פירוט": "מנוי נטפליקס", "מחיר": 39.9, "תאריך": date.today().isoformat()}),
        ]

        messages = [
            {"role": "system", "content": system}
        ]
        # Add few‑shot examples
        for user_txt, answer_dict in few_shots:
            messages.append({"role": "user", "content": user_txt})
            messages.append({"role": "assistant", "content": json.dumps(answer_dict, ensure_ascii=False)})

        messages.append({"role": "user", "content": text})
        raw = self._call_chat(messages)
        return json.loads(raw)

    # ------------------------------------------------------------------
    # 3) Answer a question using current budget data
    # ------------------------------------------------------------------
    def answer_question(self, question: str, summary_rows: List[JsonDict], tx_rows: List[JsonDict]) -> str:
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

    # ------------------------------------------------------------------
    # 4) Parse bulk category budget input
    # ------------------------------------------------------------------
    def parse_budget_categories(self, text: str) -> List[Dict[str, Union[str, float]]]:
        """Parse natural language budget category input"""
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

    # ------------------------------------------------------------------
    # 5) Smart month name suggestion
    # ------------------------------------------------------------------
    def suggest_next_month(self, current_month: str) -> str:
        """Suggest next month name based on current month"""
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

    # ------------------------------------------------------------------
    # 6) Validate budget setup confirmation
    # ------------------------------------------------------------------
    def parse_confirmation(self, text: str) -> bool:
        """Parse user confirmation from natural Hebrew speech"""
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
        # Ensure messages are in the correct format for OpenAI API
        from openai.types.chat import ChatCompletionMessageParam

        # Convert messages to ChatCompletionMessageParam if needed
        formatted_messages = []
        for msg in messages:
            # Only keep allowed keys and types
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
        # Defensive: handle possible None content
        content = response.choices[0].message.content
        if content is None:
            return ""
        return content.strip()

