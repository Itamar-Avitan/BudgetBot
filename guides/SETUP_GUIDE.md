# 🛠️ Setup Guide: Deploy Your WhatsApp Budget Bot

**Get your intelligent Hebrew budget assistant running in 20 minutes** ⏱️

---

## 🎯 **What You'll Accomplish**

By the end of this guide, you'll have:
- ✅ A smart WhatsApp bot that understands Hebrew
- ✅ Real-time expense tracking in Google Sheets
- ✅ GPT-powered natural language processing
- ✅ Professional deployment on Google Cloud
- ✅ Multi-user budget management

**Total time: ~20 minutes** | **Monthly cost: ~$0.50**

---

## 📋 **Prerequisites** (5 minutes)

Before we start, make sure you have:

### **Required Accounts:**
- [ ] **Google Cloud account** with billing enabled ([sign up here](https://cloud.google.com/))
- [ ] **OpenAI account** with API access ([sign up here](https://platform.openai.com/))
- [ ] **Meta Developer account** ([sign up here](https://developers.facebook.com/))

### **Required Tools:**
- [ ] **`gcloud` CLI** installed ([install guide](https://cloud.google.com/sdk/docs/install))
- [ ] **Git** installed
- [ ] **Text editor** (VS Code, nano, etc.)

### **Quick Check:**
```bash
# Verify you have the required tools
gcloud --version
git --version
```

**✅ All set?** Let's get your bot running!

---

## 🔑 **Step 1: Get Your API Keys** (15 minutes)

**This is the only "hard" part, but we've made it super easy with our detailed guide.**

👉 **Follow the [API Setup Guide](API_SETUP.md)** to get:
- 🧠 **OpenAI API key** (for GPT intelligence)
- 📱 **WhatsApp Business API credentials** (for messaging)
- 📊 **Google Sheets API credentials** (for data storage)

**💡 Pro tip:** Open the API guide in a new tab and follow it step-by-step. It takes about 15 minutes total.

---

## 📥 **Step 2: Clone and Configure** (3 minutes)

### **2.1 Get the Code**
```bash
# Clone the repository
git clone https://github.com/YOUR-USERNAME/budget_chat.git
cd budget_chat

# Verify you're in the right place
ls -la
# You should see: whatsapp.py, deploy.sh, credits/, guides/, etc.
```

### **2.2 Copy Templates**
```bash
# Copy the configuration templates
cp credits/templates/keys.json credits/keys.json
cp credits/templates/deploy_config.json deploy_config.json

# Verify files were created
ls -la credits/
ls -la deploy_config.json
```

**✅ Perfect!** Now you have your personal config files that won't be shared publicly.

---

## ⚙️ **Step 3: Fill in Your Credentials** (5 minutes)

### **3.1 Configure API Keys**
Edit `credits/keys.json` with your actual credentials from Step 1:

```bash
# Open the file in your preferred editor
nano credits/keys.json
# or: code credits/keys.json
# or: vim credits/keys.json
```

**Replace ALL placeholders** with your actual values:
```json
{
    "GPT_API_KEY": "sk-proj-YOUR-ACTUAL-OPENAI-KEY-HERE",
    "META_ACCESS_TOKEN": "YOUR-ACTUAL-WHATSAPP-TOKEN",
    "META_PHONE_NUMBER_ID": "YOUR-ACTUAL-PHONE-ID",
    "META_WHATSAPP_ACCOUNT_ID": "YOUR-ACTUAL-ACCOUNT-ID",
    "META_PHONE_NUMBER": "+YOUR-ACTUAL-PHONE-NUMBER",
    "META_APP_ID": "YOUR-ACTUAL-APP-ID",
    "META_WEBHOOK_VERIFY_TOKEN": "YOUR-ACTUAL-VERIFY-TOKEN",
    "IO_SPREADSHEET_ID": "YOUR-TRACKER-SPREADSHEET-ID",
    "SUMMARY_SPREADSHEET_ID": "YOUR-BUDGET-SPREADSHEET-ID",
    "USER1_PHONE": "YOUR-PHONE-WITHOUT-PLUS",
    "USER1_NAME": "Your Name",
    "USER2_PHONE": "PARTNER-PHONE-WITHOUT-PLUS", 
    "USER2_NAME": "Partner Name"
}
```

### **3.2 Configure Deployment**
Edit `deploy_config.json` with your Google Cloud project details:

```bash
# Open the deployment config
nano deploy_config.json
```

```json
{
  "project_id": "your-actual-project-id",
  "region": "europe-west1",
  "app_url": "https://your-actual-project-id.ew.r.appspot.com",
  "service_name": "default",
  "environment": "production"
}
```

**🔍 Where to find your project ID:**
- Go to [Google Cloud Console](https://console.cloud.google.com/)
- Look at the top of the page - your project ID is displayed there

### **3.3 Add Google Credentials**
```bash
# Copy your Google service account file to the credits directory
cp /path/to/your/downloaded/google_creds.json credits/google_creds.json

# Verify it's there
ls -la credits/google_creds.json
```

---

## 🚀 **Step 4: Deploy to Google Cloud** (2 minutes)

### **4.1 Authenticate with Google Cloud**
```bash
# Login to your Google account
gcloud auth login

# Set your project (replace with your actual project ID)
gcloud config set project your-actual-project-id
```

### **4.2 Deploy Your Bot**
```bash
# Make the deployment script executable
chmod +x deploy.sh

# Deploy! 🚀
./deploy.sh
```

**What happens during deployment:**
1. ✅ Checks your configuration files
2. ✅ Sets up Google Cloud project
3. ✅ Uploads your bot to App Engine
4. ✅ Configures auto-scaling and health checks
5. ✅ Returns your bot's URL

**Expected output:**
```
🚀 WhatsApp Budget Bot - Deploy
===============================
✅ Using project: your-project-id
🔧 Setting project: your-project-id
🚀 Deploying to Google Cloud...
...
✅ Deployment successful!
🌐 Your bot is live at: https://your-project-id.ew.r.appspot.com
📱 Webhook URL: https://your-project-id.ew.r.appspot.com/webhook
```

**🎉 Your bot is now live!**

---

## 📱 **Step 5: Connect WhatsApp** (3 minutes)

### **5.1 Update WhatsApp Webhook**
1. Go to [Meta Developers Console](https://developers.facebook.com/)
2. Open your WhatsApp app
3. Go to **WhatsApp → Configuration**
4. Update **Webhook URL** to: `https://your-project-id.ew.r.appspot.com/webhook`
5. Use the **verify token** from your `credits/keys.json` file
6. Click **Verify and Save**

### **5.2 Test Your Bot**
Send a message to your WhatsApp Business number:

```
You: יתרה
Bot: 💰 סה"כ נשאר: 2,340₪
     📊 קניות: 865₪ (87%)
     🍕 אוכל בחוץ: 370₪ (93%)
     ...
```

**🎉 IT WORKS!** Your intelligent Hebrew budget assistant is now live!

---

## ✅ **Success Checklist**

After completing all steps, verify everything works:

- [ ] **Health check**: Visit `https://your-project-id.ew.r.appspot.com/health`
  ```json
  {
    "status": "healthy",
    "components": {
      "google_sheets": "healthy",
      "gpt_api": "healthy",
      "categories_count": 6
    }
  }
  ```

- [ ] **WhatsApp response**: Send `יתרה` and get a response
- [ ] **Expense tracking**: Send `קניתי קפה ב-15` and see it recorded
- [ ] **Google Sheets**: Check your spreadsheets for live updates

**🎯 All green?** Congratulations! Your bot is fully operational!

---

## 🔧 **Quick Commands for Maintenance**

### **Update Your Bot** (after making changes)
```bash
./update.sh
```

### **View Logs** (for debugging)
```bash
./logs.sh
```

### **Health Check** (verify everything's working)
```bash
curl https://your-project-id.ew.r.appspot.com/health
```

---

## 🆘 **Troubleshooting Common Issues**

### **❌ "deploy_config.json not found"**
**Solution:** You forgot to copy the template.
```bash
cp credits/templates/deploy_config.json deploy_config.json
```

### **❌ "Webhook verification failed"**
**Solution:** Check your verify token matches between `credits/keys.json` and WhatsApp settings.

### **❌ "GPT API not available"**
**Solution:** 
1. Check your OpenAI API key in `credits/keys.json`
2. Verify you have billing enabled on OpenAI
3. Test with: `curl -H "Authorization: Bearer YOUR-API-KEY" https://api.openai.com/v1/models`

### **❌ "Google Sheets access denied"**
**Solution:**
1. Make sure you shared your sheets with the service account email
2. Check the Sheet IDs in `credits/keys.json` are correct
3. Verify `credits/google_creds.json` exists

### **❌ Bot responds slowly**
**Solution:** Your App Engine instance might be cold starting. This is normal for the first request after being idle.

---

## 💰 **Cost Breakdown**

### **What You'll Pay:**
- **Google Cloud App Engine**: $0.00 (within free tier)
- **OpenAI API**: ~$0.50/month (GPT-4.1-mini is very cheap)
- **WhatsApp Business API**: $0.00 (free tier: 1,000 messages/month)
- **Google Sheets API**: $0.00 (free tier)

**Total: ~$0.50/month** for unlimited personal budget tracking! 💸

---

## 🎮 **Start Using Your Bot**

### **Basic Commands:**
- `יתרה` - Show budget summary
- `קטגוריות` - List all categories
- `עזרה` - Show help menu

### **Natural Expense Entry:**
- `קניתי קפה ב-15` 
- `פלאפל 18 שקל`
- `דלק 200`
- `קניות בסופר 85 שקל`

### **Smart Questions:**
- `כמה הוצאתי השבוע?`
- `כמה נשאר לי בקניות?`
- `מה הוצאתי החודש על אוכל?`

### **Budget Creation:**
- `רוצה ליצור תקציב חדש`
- `תקציב חדש לחודש הבא`

---

## 🎉 **Congratulations!**

You now have a **professional-grade, AI-powered budget assistant** running in your WhatsApp!

### **What You Built:**
- 🧠 **Intelligent expense recognition** with GPT-4.1-mini
- 📊 **Real-time budget tracking** in Google Sheets
- 🔒 **Private & secure** - runs on your own cloud
- 📱 **WhatsApp native** - no new apps to learn
- 💰 **Costs almost nothing** - ~$0.50/month
- 🚀 **Enterprise-grade** - Google Cloud reliability

### **Next Steps:**
1. **Start tracking expenses** - just chat naturally with your bot
2. **Invite family members** - add their phone numbers to the config
3. **Customize categories** - edit your Google Sheets as needed
4. **Explore advanced features** - try budget creation and analysis

**Happy budgeting! 💰📊🚀**

---

[← Back to README](../README.md) • [API Setup Guide →](API_SETUP.md) • [User Guide →](USER_GUIDE.md) 