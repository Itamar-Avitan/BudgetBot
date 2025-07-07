# 🛠️ Complete Setup Guide: WhatsApp Budget Bot

**Step-by-step guide to get your own WhatsApp budget bot running**

> **📋 Prerequisites**: You need API keys first! See the [API Setup Guide](API_SETUP.md) to get all required credentials.

---

## 🚀 **What You'll Do**

This guide will help you:
1. **Clone/Fork the repository**
2. **Configure your credentials**
3. **Set up Google Sheets**
4. **Deploy to Google Cloud**
5. **Test your bot**

**Total estimated setup time**: 30-45 minutes  
**Monthly cost**: ~$1.00 (mostly OpenAI usage)

---

## 📦 **Step 1: Get the Code**

### **Option A: Clone the Repository**
```bash
git clone https://github.com/YOUR-USERNAME/budget_chat.git
cd budget_chat
```

### **Option B: Fork and Clone (Recommended)**
1. **Fork the repository** on GitHub
2. **Clone your fork**:
   ```bash
   git clone https://github.com/YOUR-USERNAME/budget_chat.git
   cd budget_chat
   ```

### **Verify Project Structure**
```bash
ls -la
```
You should see:
```
budget_chat/
├── whatsapp.py
├── GPT_API.py
├── sheets_IO.py
├── requirements.txt
├── guides/
└── credits/
    └── keys_layout.json
```

---

## 📁 **Step 2: Configure Your Bot**

### **2.1 Create Configuration Files**
1. **Copy the templates**:
   ```bash
   cp credits/templates/keys.json credits/keys.json
   cp credits/templates/deploy_config.json deploy_config.json
   ```

2. **Fill in `credits/keys.json`** with your actual credentials from the [API Setup Guide](API_SETUP.md):
```json
{
  "GPT_API_KEY": "your_openai_key_from_api_setup",
  "META_ACCESS_TOKEN": "your_whatsapp_token_from_api_setup",
  "META_PHONE_NUMBER_ID": "your_phone_id_from_api_setup",
  "META_WHATSAPP_ACCOUNT_ID": "your_whatsapp_account_id_from_api_setup",
  "META_PHONE_NUMBER": "your_test_phone_from_api_setup",
  "META_APP_ID": "your_app_id_from_api_setup",
  "META_WEBHOOK_VERIFY_TOKEN": "your_verify_token_from_api_setup",
  "IO_SPREADSHEET_ID": "your_tracker_sheet_id_from_api_setup",
  "SUMMARY_SPREADSHEET_ID": "your_budget_sheet_id_from_api_setup",
  "USER1_PHONE": "1234567890",
  "USER1_NAME": "Your Name",
  "USER2_PHONE": "0987654321",
  "USER2_NAME": "Partner Name"
}
```

3. **Fill in `deploy_config.json`** with your project details:
```json
{
  "project_id": "your-actual-project-id",
  "region": "europe-west1",
  "app_url": "https://your-actual-project-id.ew.r.appspot.com",
  "service_name": "default",
  "environment": "production"
}
```

📋 **Note**: The templates in `credits/templates/` contain detailed explanations for each field.

### **2.2 Add Google Credentials**
Place your downloaded `google_creds.json` file in the `credits/` folder.

### **2.3 Set Up Google Sheets**
1. **Create 2 new Google Sheets**:
   - **Budget Sheet**: For categories and totals
   - **Tracker Sheet**: For individual transactions

2. **Budget Sheet Setup**:
   - Sheet name: "July" (current month)
   - Headers in row 1: `קטגוריה`, `תקציב`, `כמה יצא`, `כמה נשאר`
   - Add a sheet called "__configs" with:
     - A1: "working_sheet", B1: "July"

3. **Tracker Sheet Setup**:
   - Sheet name: "July" (matching budget sheet)
   - Headers in row 1: `קטגוריה`, `פירוט`, `מחיר`, `תאריך`

4. **Share both sheets** with your service account email (found in `google_creds.json`)
   - Give "Editor" permissions

5. **Copy the Sheet IDs** from the URLs and update them in `keys.json`:
   - URL format: `https://docs.google.com/spreadsheets/d/SHEET_ID/edit`

---

## ☁️ **Step 3: Google Cloud Platform Setup**

### **3.1 Install Google Cloud CLI**
```bash
# On Ubuntu/Debian:
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# Authenticate:
gcloud auth login
gcloud config set project YOUR-PROJECT-ID
```

### **3.2 Enable App Engine**
1. In your Google Cloud Console
2. Go to **"App Engine"**
3. Click **"Create Application"**
4. Choose region (e.g., "europe-west1")
5. Click **"Create App"**

### **3.3 Enable Billing**
1. Go to **"Billing"**
2. Link a billing account
3. **Don't worry**: With minimal usage, costs are ~$0.50/month

---

## 🚀 **Step 4: Deploy Your Bot**

### **4.1 Deploy to Google Cloud**
```bash
# First-time deployment
./deploy.sh
```

### **4.2 Complete WhatsApp Setup**
1. Go back to Meta Developers
2. In WhatsApp → Configuration
3. Set Webhook URL to: `https://YOUR-PROJECT-ID.ew.r.appspot.com/webhook`
4. Use your verify token from `keys.json`
5. Test the webhook

### **4.3 Test Your Bot**
1. Send a WhatsApp message to your test number: `יתרה`
2. You should get a response with budget information
3. Try adding an expense: `קניתי קפה ב-15`

---

## 🔧 **Troubleshooting**

### **Common Issues**

#### **"Webhook verification failed"**
- Check your verify token in `keys.json` matches Meta settings
- Ensure your bot is deployed and accessible
- Verify you copied the template: `cp credits/templates/keys.json credits/keys.json`

#### **"שירות הבינה המלאכותית אינו זמין"**
- Check your OpenAI API key is correct
- Verify you have billing enabled on OpenAI
- Check the model name is supported (`gpt-4.1-mini`)

#### **"Google Sheets access denied"**
- Verify you shared the sheets with your service account email
- Check the Sheet IDs are correct in `keys.json`
- Ensure you copied the template: `cp credits/templates/keys.json credits/keys.json`

#### **"Budget categories not found"**
- Ensure your budget sheet has the correct headers
- Add some sample data to test

### **Health Check**
Visit: `https://YOUR-PROJECT-ID.ew.r.appspot.com/health`

Should return:
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

### **View Logs**
```bash
gcloud app logs tail -s default
```

---

## 💰 **Cost Breakdown**

### **Monthly Expenses**
- **Google Cloud App Engine**: ~$0.50
- **OpenAI API**: ~$0.50  
- **WhatsApp Business API**: Free (up to 1,000 messages)
- **Google Sheets API**: Free

**Total**: ~$1.00/month

### **Cost Optimization Tips**
- Use `gpt-4.1-mini` (cheapest model)
- Set OpenAI usage limits
- Monitor Google Cloud billing

---

## 🎉 **You're Done!**

Your WhatsApp budget bot is now running! 

### **What You Can Do:**
- **Track expenses**: "קניתי קפה ב-15"
- **Check balances**: "יתרה"
- **Ask questions**: "כמה הוצאתי השבוע?"
- **Create new budgets**: "רוצה ליצור תקציב חדש"

### **Updates**
```bash
# After making code changes
./update.sh
```

**Need help?** Check the troubleshooting section or review the logs.

---

[← Back to README](../README.md) • [API Setup Guide →](API_SETUP.md) • [User Guide →](USER_GUIDE.md)

**Happy budgeting! 💰📊** 