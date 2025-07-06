# 📚 Smart Hebrew Budget Bot - User Guide

<div align="center">

**Complete guide for using the Smart Hebrew Budget WhatsApp Bot**

[Getting Started](#-getting-started) • [Recording Expenses](#-recording-expenses) • [Budget Questions](#-asking-questions) • [Budget Setup](#️-budget-setup) • [Advanced Features](#-advanced-features)

</div>

---

## 🚀 **Getting Started**

### **First Contact**
1. **Add the bot** to your WhatsApp contacts
2. **Send a message** - "שלום" or "עזרה"
3. **Get personalized welcome** with your name and emoji

```
👨‍💼 שלום יוסי! 👨‍💼
אפשר לעזור לך עם התקציב?
```

### **Quick Orientation**
Send `עזרה` to see all available features:

```
🤖 מדריך שימוש:

📝 לרישום הוצאה:
• "קניתי לחם ב-12"
• "שילמתי 50 על דלק"

❓ לשאלות:
• "מה המצב עם הכסף?"
• "איך אני עומד עם התקציב?"

🏗️ הגדרת תקציב חדש:
• "רוצה ליצור תקציב חדש"
• "בואו נעשה תקציב חדש"

⚡ פקודות מהירות:
• יתרה - יתרות כל הקטגוריות
• קטגוריות - רשימת קטגוריות
• רענון - עדכון יתרות
• עזרה - המדריך הזה

💡 טיפים:
• הבוט מבין דיבור טבעי
• מזהה כפילויות אוטומטית
• מקבל תאריכים בעברית
• מבין מספרים בעברית
```

---

## 💸 **Recording Expenses**

### **Natural Language Examples**

The bot understands **natural Hebrew speech**. Here are various ways to record expenses:

#### **💰 Basic Purchases**
```
✨ You Say:
"קניתי קפה ב-15"

🤖 Bot Response:
"👨‍💼 נרשם בהצלחה!
📝 קפה - 15₪
💰 ✅ נותרו 485₪ באוכל בחוץ"
```

#### **🚗 Transportation**
```
✨ You Say:
"שילמתי 200 שקל על דלק"

🤖 Bot Response:
"👨‍💼 נרשם בהצלחה!
📝 דלק - 200₪
💰 ⚠️ תשומת לב! נותרו 100₪ בתחבורה (20.0%)"
```

#### **🎉 Entertainment**
```
✨ You Say:
"בילוי אתמול עלה לי 150"

🤖 Bot Response:
"👨‍💼 נרשם בהצלחה!
📝 בילוי - 150₪
💰 ✅ נותרו 250₪ בבידור

🔄 אזהרה: נרשמה הוצאה זהה היום - בילוי 150₪"
```

### **Advanced Natural Language**

#### **🛒 Complex Purchases**
```
✨ Flexible Expressions:
• "הוצאה של 45 על פיצה משפחתית"
• "קניות השבוע 800 שקל"
• "שילמתי על הבנזין 180"
• "ארוחה במסעדה עלתה 250"
```

#### **📅 Date Recognition**
```
✨ Date Examples:
• "קניתי לחם אתמול ב-12" → Previous day
• "בילוי אמש עלה 180" → Last night
• "הוצאה של שלשום 50" → Day before yesterday
• "דלק ב-200 ביום ראשון" → Specific day
```

#### **💱 Currency Formats**
```
✨ Currency Recognition:
• "קפה ב-15" → 15₪
• "200 שקל" → 200₪
• "45₪" → 45₪
• "מחיר: 80" → 80₪
```

### **Smart Category Mapping**

The bot automatically maps expenses to the right categories:

| **What You Say** | **Category** | **Logic** |
|------------------|--------------|-----------|
| "קפה", "פלאפל", "מסעדה" | אוכל בחוץ | Food outside home |
| "דלק", "רכבת", "אוטובוס" | תחבורה | Transportation |
| "סרט", "בילוי", "נטפליקס" | בידור | Entertainment |
| "סופר", "חלב", "לחם" | קניות | Groceries/Shopping |

### **Smart Budget Warnings**

The bot provides intelligent warnings based on remaining budget:

#### **🚨 Critical (< 5%)**
```
"🚨 אזהרה! נותרו רק 50₪ בבידור (4.2%)"
```

#### **⚠️ Warning (< 15%)**
```
"⚠️ תשומת לב! נותרו 120₪ בתחבורה (12.4%)"
```

#### **⏰ Caution (< 30%)**
```
"⏰ נותרו 200₪ בקניות (25.5%)"
```

#### **✅ Safe (> 30%)**
```
"✅ נותרו 450₪ בקניות"
```

#### **🚨 Over Budget**
```
"🚨 חריגה! חרגת ב-150₪ מתקציב בידור"
```

---

## ❓ **Asking Questions**

### **Natural Questions**

Ask the bot questions in **natural Hebrew** about your budget:

#### **💰 Budget Balance Queries**
```
✨ Natural Ways to Ask:
• "כמה נשאר בקניות?"
• "מה המצב עם הכסף?"
• "איך אני עומד עם התקציב?"
• "מה יש לי?"
• "תראה לי את היתרה"

🤖 Smart Response:
"👨‍💼 נשארו לך 450₪ בקניות מתוך 800₪ - מצב טוב!"
```

#### **📊 Spending Analysis**
```
✨ Analysis Questions:
• "מה הוצאתי השבוע?"
• "איפה הוצאתי הכי הרבה?"
• "כמה הוצאתי על אוכל?"
• "מה ההוצאות שלי?"

🤖 Detailed Response:
"👨‍💼 השבוע הוצאת 320₪:
• אוכל בחוץ: 180₪ (56%)
• תחבורה: 90₪ (28%)
• בידור: 50₪ (16%)

💡 הכי הוצאת על אוכל בחוץ"
```

#### **🔍 Specific Category Questions**
```
✨ Category-Specific:
• "כמה הוצאתי על בידור?"
• "מה המצב עם התחבורה?"
• "איך עומד התקציב לקניות?"

🤖 Category Response:
"👨‍💼 בבידור:
• הוצאת: 350₪ מתוך 400₪
• נותרו: 50₪ (12.5%)
• ⚠️ תשומת לב - כמעט גמר!"
```

### **Quick Commands**

For faster access, use these **one-word commands**:

#### **⚡ Instant Commands**
```
יתרה → Full budget overview
קטגוריות → List all categories
עזרה → Complete help guide
רענון → Refresh all calculations
```

#### **🔄 Natural Alternatives**
Instead of quick commands, you can also say:
```
✨ Natural Alternatives:
• "מה המצב עם הכסף?" → יתרה
• "איזה קטגוריות יש?" → קטגוריות
• "איך זה עובד?" → עזרה
• "רענן את המספרים" → רענון
```

---

## 🏗️ **Budget Setup**

### **Starting a New Budget**

Creating a new monthly budget is a **guided conversation**:

#### **🎬 Step 1: Initiate**
```
✨ Natural Ways to Start:
• "רוצה ליצור תקציב חדש"
• "בואו נעשה תקציב חדש"
• "צריך תקציב חדש"
• "איך יוצרים תקציב?"

🤖 Bot Response:
"👨‍💼 הגדרת תקציב חדש

🗓️ החודש הנוכחי: July
💡 הצעה לחודש הבא: August

❓ רוצה ליצור תקציב חדש עבור "August"?

💬 תגובות אפשריות:
• "כן" - יצירת תקציב עבור August
• "לא" - ביטול
• שם חודש אחר - למשל "ספטמבר""
```

#### **🗓️ Step 2: Month Confirmation**
```
✨ Your Options:
• "כן" → Use suggested month
• "לא" → Cancel setup
• "ספטמבר" → Custom month name

🤖 Bot Response (if confirmed):
"👨‍💼 הגדרת קטגוריות עבור August

📋 קטגוריות מהחודש הקודם:
• קניות: 800₪
• אוכל בחוץ: 400₪
• תחבורה: 200₪
• בידור: 300₪
💰 סה"כ מוצע: 1700₪

💡 אפשרויות:
1️⃣ "אישור" - להשתמש באותן קטגוריות וסכומים
2️⃣ רשימה חדשה - למשל: "קניות 800, אוכל בחוץ 400"
3️⃣ "ביטול" - לבטל את ההגדרה"
```

#### **📊 Step 3: Category Setup**

##### **Option A: Approve Previous Month**
```
✨ You Say: "אישור"

🤖 → Uses previous month's categories
```

##### **Option B: Create New Categories**
```
✨ Natural Category Input:
• "קניות 800, אוכל בחוץ 400, תחבורה 200"
• "אני רוצה 500 לקניות ו-300 לבידור"
• "בואו נשים 1000 על קניות, 600 על מסעדות"
• "צריך תקציב של 400 לבידור, 800 לקניות"

🤖 Bot Response:
"👨‍💼 סיכום התקציב החדש

📋 חודש: August
💰 קטגוריות:
• קניות: 800₪
• אוכל בחוץ: 400₪
• תחבורה: 200₪
💯 סה"כ תקציב: 1400₪

✅ לאישור סופי כתבו "אישור"
❌ לביטול כתבו "ביטול""
```

#### **✅ Step 4: Final Confirmation**
```
✨ You Say: "אישור"

🤖 Bot Response:
"👨‍💼 🎉 התקציב החדש נוצר בהצלחה!

📅 חודש: August
📊 קטגוריות: 3
✅ מוכן לשימוש!

💡 עכשיו אפשר להתחיל לרשום הוצאות:
דוגמה: "קניתי קפה ב-15""
```

### **Advanced Category Input**

The bot understands **flexible category formats**:

#### **🎯 Format Examples**
```
✨ Different Ways to Input:
• Comma-separated: "קניות 800, בידור 300"
• Natural speech: "אני רוצה 500 לקניות ו-200 לבידור"
• Mixed format: "תחבורה 200 שקל, בריאות גם בערך 400"
• Long sentences: "בואו נשים 1000 על קניות ו-300 על תחבורה"
```

#### **🔄 Error Recovery**
If the bot doesn't understand:
```
🤖 Error Response:
"⚠️ לא הצלחתי לפרק את הקטגוריות. נסו שוב:
דוגמה: 'קניות 800, אוכל בחוץ 400'

✨ או: 'אני רוצה 500 לקניות ו-300 לבידור'"
```

---

## 🎯 **Advanced Features**

### **🔄 Duplicate Detection**

The bot automatically detects **identical transactions**:

```
✨ Example:
First: "קפה 15₪" → Recorded successfully
Second: "קפה 15₪" (same day) → Warning issued

🤖 Response:
"👨‍💼 נרשם בהצלחה!
📝 קפה - 15₪
💰 ✅ נותרו 470₪ באוכל בחוץ

🔄 אזהרה: נרשמה הוצאה זהה היום - קפה 15₪"
```

### **👥 Multi-User Support**

Each user gets **personalized experience**:

#### **User 1 (יוסי)**
```
🤖 Response: "👨‍💼 שלום יוסי!"
```

#### **User 2 (רחל)**  
```
🤖 Response: "👩‍💼 שלום רחל!"
```

#### **Unknown User**
```
🤖 Response: "👤 שלום משתמש!"
```

### **🧠 Context Awareness**

The bot remembers **conversation context**:

#### **🙏 Gratitude Response**
```
✨ You Say: "תודה" / "מעולה" / "כל הכבוד"
🤖 Response: "👨‍💼 בכיף! יש עוד הוצאות להזין?"
```

#### **👋 Greetings**
```
✨ You Say: "שלום" / "מה נשמע" / "מה המצב"
🤖 Response: "שלום יוסי! 👨‍💼\nאפשר לעזור לך עם התקציב?"
```

### **🔧 Budget Refresh**

**Recalculate all totals** when needed:

```
✨ Natural Ways:
• "רענון"
• "רענן את המספרים"
• "עדכן יתרות"
• "בדוק שוב"

🤖 Response:
"🔄 רענון הושלם!
✅ עודכנו 5 קטגוריות בתקציב
💰 כל הסכומים עכשיו מדויקים"
```

---

## 💡 **Best Practices**

### **🎯 Effective Usage**

#### **✅ Do's**
- **Use natural language** - "שילמתי 50 על דלק"
- **Be specific with descriptions** - "פיצה משפחתית" not just "אוכל"
- **Check balances regularly** - "מה המצב עם הכסף?"
- **Set up new budgets monthly** - "צריך תקציב חדש"

#### **❌ Don'ts**
- Don't use overly complex sentences
- Don't mix multiple expenses in one message
- Don't worry about exact format - bot understands variations

### **🔍 Troubleshooting**

#### **Common Issues & Solutions**

**❓ Bot doesn't understand expense**
```
Problem: "לא הבנתי מה רציתם"
Solution: Try simpler format: "קפה 15"
```

**❓ Wrong category assignment**
```
Problem: Coffee assigned to "קניות" instead of "אוכל בחוץ"
Solution: Be more specific: "קפה במסעדה 15"
```

**❓ Missing balance information**
```
Problem: "לא נמצא מידע על התקציב"
Solution: Send "רענון" to refresh calculations
```

### **📊 Monthly Workflow**

#### **🗓️ Monthly Setup Process**
1. **End of month**: Send "מה הוצאתי החודש?"
2. **Start new month**: "צריך תקציב חדש"
3. **Follow guided setup** with previous month's template
4. **Adjust categories** based on last month's analysis
5. **Start tracking** new month's expenses

#### **📈 Ongoing Management**
- **Daily**: Record expenses as they happen
- **Weekly**: Check balances with "יתרה"
- **Mid-month**: Ask "איך אני עומד?" for analysis
- **Monthly**: Review spending patterns before new budget

---

## 🆘 **Getting Help**

### **📞 Built-in Help**
- Send `עזרה` for complete usage guide
- Ask "איך זה עובד?" for natural help
- Use `קטגוריות` to see available categories

### **🔧 Advanced Support**
- Check `README.md` for technical setup
- See `API_SETUP.md` for configuration issues
- Review `CHANGELOG.md` for recent updates

---

<div align="center">

**🎉 You're now ready to master the Smart Hebrew Budget Bot!**

Start with a simple expense: "קניתי קפה ב-15"

</div> 