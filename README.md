# 🤖 WhatsApp Budget Bot v2.0

**Personal budget tracking bot for WhatsApp in Hebrew - Deploy your own instance**

## 🚀 Getting Started

### **Step 1: Clone or Fork the Repository**
```bash
# Option 1: Clone the repository
git clone https://github.com/YOUR-USERNAME/budget_chat.git
cd budget_chat

# Option 2: Fork on GitHub first, then clone your fork
git clone https://github.com/YOUR-USERNAME/budget_chat.git
cd budget_chat
```

### **Step 2: Get Your API Keys**
📋 **Get all required API keys**: Follow the [API Setup Guide](guides/API_SETUP.md) to obtain:
- OpenAI API key
- Meta WhatsApp Business API credentials  
- Google Sheets API credentials

### **Step 3: Configure Your Bot**
1. **Copy the credentials template**:
   ```bash
   cp credits/templates/keys.json credits/keys.json
   ```
2. **Fill in your credentials** in `credits/keys.json` with your actual API keys
3. **Add Google credentials** file as `credits/google_creds.json`

### **Step 4: Configure Deployment**
1. **Copy the deployment template**:
   ```bash
   cp credits/templates/deploy_config.json deploy_config.json
   ```
2. **Edit `deploy_config.json`** with your project details:
   ```json
   {
     "project_id": "your-actual-project-id",
     "region": "europe-west1",
     "app_url": "https://your-actual-project-id.ew.r.appspot.com",
     "service_name": "default",
     "environment": "production"
   }
   ```

### **Step 5: Deploy**
```bash
# First time deployment
./deploy.sh
```

### **Prerequisites**
- Google Cloud account with billing enabled
- `gcloud` CLI installed and authenticated
- All API keys configured (see guides)

📖 **New to this?** See the complete [Setup Guide](guides/SETUP_GUIDE.md) for detailed step-by-step instructions.

## 📋 **Required Configuration Files**

### `credits/keys.json` (Configuration Steps)
1. **Copy the template**: `cp credits/templates/keys.json credits/keys.json`
2. **Replace all placeholders** with your actual credentials:
```json
{
  "GPT_API_KEY": "sk-proj-your-actual-openai-key-here",
  "META_ACCESS_TOKEN": "your-actual-whatsapp-token",
  "META_PHONE_NUMBER_ID": "your-actual-phone-id",
  "META_WHATSAPP_ACCOUNT_ID": "your-actual-whatsapp-account-id",
  "META_PHONE_NUMBER": "+your-actual-phone-number",
  "META_APP_ID": "your-actual-app-id",
  "META_WEBHOOK_VERIFY_TOKEN": "your-actual-webhook-verify-token",
  "IO_SPREADSHEET_ID": "your-actual-tracker-spreadsheet-id",
  "SUMMARY_SPREADSHEET_ID": "your-actual-budget-spreadsheet-id",
  "USER1_PHONE": "your-actual-user1-phone",
  "USER1_NAME": "Your Name",
  "USER2_PHONE": "your-actual-user2-phone", 
  "USER2_NAME": "Partner Name"
}
```

📋 **See [credentials template](credits/templates/keys.json) for detailed explanations of each field.**

### `deploy_config.json` (Deployment Configuration)
1. **Copy the template**: `cp credits/templates/deploy_config.json deploy_config.json`
2. **Replace with your project details**:
```json
{
  "project_id": "your-actual-project-id",
  "region": "europe-west1",
  "app_url": "https://your-actual-project-id.ew.r.appspot.com",
  "service_name": "default",
  "environment": "production"
}
```

### `credits/google_creds.json`
Google service account credentials for Sheets API access.

## 🔄 **Updates & Maintenance**

### **Your Git Workflow** (You control this)
```bash
# 1. Make your code changes
# 2. Test locally
# 3. Commit when ready
git add .
git commit -m "Your commit message"
git push origin main
```

### **Deployment Only** (Scripts handle this)
```bash
# Quick redeploy after changes
./update.sh

# Full deployment (first time or troubleshooting)
./deploy.sh

# View logs
./logs.sh
```

**Note:** The scripts only handle deployment to Google Cloud - they don't touch your git repository. You maintain full control over when and what gets committed to your public repo.

### **Monitor Health**
```bash
curl https://YOUR-PROJECT-ID.ew.r.appspot.com/health
```

## 🧠 **Smart Features**

- **Natural Language Processing**: "קניתי קפה ב-15"
- **Smart Budget Warnings**: Progressive alerts based on remaining %
- **Duplicate Detection**: Automatic detection of identical transactions
- **Multi-User Support**: Personalized experience per user
- **Quick Commands**: `יתרה`, `קטגוריות`, `עזרה`
- **Budget Creation**: Natural language budget setup

## 🔗 **Your URLs After Deployment**

- **App**: `https://YOUR-PROJECT-ID.ew.r.appspot.com`
- **Webhook**: `https://YOUR-PROJECT-ID.ew.r.appspot.com/webhook`
- **Health**: `https://YOUR-PROJECT-ID.ew.r.appspot.com/health`

Replace `YOUR-PROJECT-ID` with your actual Google Cloud project ID.

## 📱 **WhatsApp Setup**

1. Update webhook URL to: `https://YOUR-PROJECT-ID.ew.r.appspot.com/webhook`
2. Use verify token from your `keys.json` file
3. Test with message: `יתרה`

Replace `YOUR-PROJECT-ID` with your actual Google Cloud project ID.

## 💰 **Cost**

- **Google Cloud**: ~$0.50/month (always-on with minimal instances)
- **OpenAI**: ~$0.50/month (optimized usage)

## 📚 **Documentation Structure**

This project has **two main guides**:

1. **🔑 [API Setup Guide](guides/API_SETUP.md)** - Get all required API keys and credentials
   - OpenAI API key
   - Meta WhatsApp Business API credentials
   - Google Sheets API credentials

2. **🛠️ [Setup Guide](guides/SETUP_GUIDE.md)** - Clone, configure, and deploy your bot
   - Clone the repository
   - Configure your credentials
   - Deploy to Google Cloud

📋 **Follow both guides in order** to get your bot running!

---

**Ready to use! Just run `./update.sh "your changes"` for any updates! 🚀** 