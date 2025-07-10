# 🤖💰 WhatsApp Budget Bot - Your Personal Finance Assistant

**Turn WhatsApp into your smart budget tracker with AI-powered expense management in Hebrew**

---

## 🎯 **What This Bot Does For You**

Imagine having a **personal finance assistant** that lives in your WhatsApp and understands Hebrew perfectly:

> **🚀 NEW in v2.1-optimized**: Ultra-fast responses with intelligent caching and batch processing!

### **💬 Natural Conversations**
```
You: "קניתי קפה ב-15"
Bot: "✅ נרשם בהצלחה! קפה - 15₪
     💰 נשארו לך 385₪ באוכל בחוץ (רק 4% מהתקציב!)"
```

### **🧠 Smart Understanding**
- **Understands Hebrew naturally** - no rigid commands needed
- **Auto-categorizes expenses** - knows "קפה" goes to "אוכל בחוץ"
- **Detects duplicates** - prevents accidental double entries
- **Learns your patterns** - gets smarter over time

### **📊 Real-Time Budget Tracking**
- **Live budget updates** in Google Sheets
- **Smart alerts** when approaching limits
- **Multiple user support** - perfect for couples
- **Instant balance checks** with `יתרה`

### **🚀 Advanced Features**
- **Budget creation wizard** - "רוצה ליצור תקציב חדש"
- **Expense questions** - "כמה הוצאתי השבוע?"
- **Category management** - automatic budget calculations
- **Multiple sheets** - organize by month
- **⚡ Smart Caching** - Instant responses for repeated questions
- **🚀 Batch Processing** - 50% faster expense processing

---

## ⚡ **"Plug and Play" Setup**

This is **ridiculously easy** to deploy. Seriously.

### **🎯 All You Need:**
1. **3 API keys** (15 minutes to get them all)
2. **Copy templates** (30 seconds)
3. **Deploy** (2 minutes)

**Total setup time: ~20 minutes from zero to working bot** 🚀

### **🔥 Quick Start**
```bash
# 1. Clone this repo
git clone https://github.com/YOUR-USERNAME/budget_chat.git
cd budget_chat

# 2. Copy templates and fill in your API keys  
cp credits/templates/*.json .
# (Edit with your credentials - see guides below)

# 3. Deploy to Google Cloud
./deploy.sh

# 🎉 DONE! Your bot is live!
```

### **💰 Monthly Cost: ~$0.50** (Google Cloud free tier + minimal OpenAI usage)

---

## 🌟 **Why This Bot is Amazing**

### **🧠 GPT-Powered Intelligence**
- Uses **GPT-4.1-mini** for natural language understanding
- **Learns your spending patterns** and categories
- **Contextual responses** - knows when you're overspending

### **🔒 Privacy & Security**
- **Your data stays yours** - runs on your Google Cloud
- **Template-based setup** - no credentials in public repo
- **Open source** - audit everything yourself

### **📱 WhatsApp Native**
- **No new apps to learn** - works in your existing WhatsApp
- **Multi-user support** - great for families/couples
- **Always available** - respond instantly to messages

### **📊 Google Sheets Integration**
- **Live spreadsheet updates** - see changes in real-time
- **Flexible categories** - customize to your needs  
- **Historical data** - track trends over time
- **Export friendly** - your data, your format

### **🚀 Professional Deployment**
- **Google Cloud App Engine** - enterprise-grade reliability
- **Always-on** - no cold starts, instant responses
- **Auto-scaling** - handles traffic spikes
- **Monitoring & logs** - built-in health checks

---

## 🎮 **Demo: What Using This Bot Feels Like**

```
👤 You: "היי, כמה יש לי בתקציב?"
🤖 Bot: "שלום איתמר! 💰 סה"כ נשאר: 2,340₪
      📊 קניות: 865₪ (87%)
      🍕 אוכל בחוץ: 370₪ (93%)  
      ⛽ דלק: 800₪ (100%)
      🎉 יציאות: 400₪ (100%)"

👤 You: "קניתי לחם בסופר ב-8 שקל"
🤖 Bot: "✅ נרשם בהצלחה!
      📝 לחם בסופר - 8₪
      💰 נשארו לך 857₪ בקניות
      👍 אתה עדיין בטווח הבטוח!"

👤 You: "כמה הוצאתי השבוע על אוכל?"
🤖 Bot: "📊 השבוע באוכל בחוץ: 47₪
      • קפה: 15₪ (היום)
      • פלאפל: 18₪ (אתמול)
      • פיצה: 14₪ (יום ב')
      
      🎯 קצב טוב! ממוצע 6.7₪ ליום"
```

---

## 🚀 **Get Started in 3 Steps**

### **1. Get Your API Keys** (15 minutes)
Follow our **[📋 API Setup Guide](guides/API_SETUP.md)** to get:
- 🧠 **OpenAI API key** (for GPT intelligence)
- 📱 **WhatsApp Business API** (for messaging)
- 📊 **Google Sheets API** (for data storage)

### **2. Configure & Deploy** (5 minutes)
Follow our **[🛠️ Setup Guide](guides/SETUP_GUIDE.md)** for:
- Template configuration
- Google Cloud deployment
- WhatsApp webhook setup

### **3. Start Chatting!** (instant)
Send `יתרה` to your bot and watch the magic happen! ✨

---

## 📚 **Complete Documentation**

| Guide | Purpose | Time |
|-------|---------|------|
| **[🔑 API Setup](guides/API_SETUP.md)** | Get all required API keys | 15 min |
| **[🛠️ Setup Guide](guides/SETUP_GUIDE.md)** | Complete installation walkthrough | 10 min |
| **[🚀 Deployment](guides/DEPLOYMENT_GUIDE.md)** | Advanced deployment & troubleshooting | Reference |
| **[👤 User Guide](guides/USER_GUIDE.md)** | How to use your bot effectively | Reference |

---

## 🤝 **Perfect For**

- 👥 **Couples** tracking shared expenses
- 🏠 **Households** managing family budgets  
- 🧑‍💼 **Individuals** wanting effortless expense tracking
- 💻 **Developers** who want to customize their finance tools
- 🇮🇱 **Hebrew speakers** needing native language support

---

## ⭐ **Key Benefits**

✅ **Natural Hebrew conversation** - no learning curve  
✅ **Intelligent categorization** - GPT understands context  
✅ **Real-time budget tracking** - instant Google Sheets updates  
✅ **Smart alerts** - know before you overspend  
✅ **Multi-user support** - perfect for couples/families  
✅ **Private & secure** - your data stays on your servers  
✅ **Open source** - customize everything  
✅ **Cheap to run** - ~$0.50/month total cost  
✅ **Professional deployment** - enterprise-grade reliability  
🆕 **⚡ Lightning-fast responses** - intelligent caching system  
🆕 **🚀 Optimized performance** - 50% faster processing  
🆕 **💾 Smart efficiency** - reduced API costs  

---

## 🎉 **Ready to Transform Your Budget Management?**

**This is the easiest personal finance bot you'll ever deploy.**

👆 **Just follow the [Setup Guide](guides/SETUP_GUIDE.md) and you'll have your intelligent Hebrew budget assistant running in WhatsApp within 20 minutes!**

---

### 💬 **Questions? Issues? Contributions?**
- 📖 Check our comprehensive guides above
- 🐛 Open an issue for bugs or questions  
- 🔧 Submit PRs for improvements
- ⭐ Star this repo if it helps you!

**Happy budgeting! 💰📊🚀** 