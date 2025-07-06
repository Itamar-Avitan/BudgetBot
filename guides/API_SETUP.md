# 🔑 API Keys Setup Guide - Smart Hebrew Budget Bot

<div align="center">

**How to obtain all required API keys and credentials**

[OpenAI Setup](#-openai-api-setup) • [Meta WhatsApp](#-meta-whatsapp-business-api-setup) • [Google Sheets](#-google-sheets-api-setup)

</div>

> **📋 Note**: This guide focuses on **getting API keys**. For project setup and deployment, see the [Setup Guide](SETUP_GUIDE.md).

---

---

## 🤖 **OpenAI API Setup**

### **Step 1: Create OpenAI Account**
1. Visit [OpenAI Platform](https://platform.openai.com/)
2. **Sign up** or **log in** to your account
3. **Verify your phone number** (required for API access)

### **Step 2: Add Payment Method**
1. Go to **Settings** → **Billing**
2. **Add payment method** (credit card required)
3. **Set usage limits** to control costs:
   - Recommended: $10-20/month for personal use
   - Our bot costs ~$0.25/month with GPT-4o-mini

### **Step 3: Generate API Key**
1. Navigate to **API Keys** section
2. Click **"Create new secret key"**
3. **Name it**: "Budget Bot Key"
4. **Copy the key** - it starts with `sk-proj-`
5. **⚠️ IMPORTANT**: Save it immediately - you won't see it again!

```
Example: sk-proj-abc123...xyz789
```

### **Step 4: Verify Model Access**
1. Check available models at **Playground**
2. Verify **GPT-4.1-mini** is available
3. If not available, contact OpenAI support

### **💡 Cost Optimization Tips**
- **GPT-4.1-mini**: $0.40 per 1M input tokens (recommended)
- **GPT-4.1**: $2.00 per 1M input tokens (more expensive)
- **Set usage alerts** in billing settings
- **Monitor usage** monthly

---

## 📱 **Meta WhatsApp Business API Setup**

### **Step 1: Create Meta Developer Account**
1. Go to [developers.facebook.com](https://developers.facebook.com)
2. Click **"Get Started"** → **"Create Account"**
3. Verify your email and phone number

### **Step 2: Create WhatsApp Business App**
1. In Meta Developers dashboard, click **"Create App"**
2. Choose **"Business"** as app type
3. Fill in app details:
   - **App Name**: "Budget Bot" (or any name)
   - **Business Account**: Create new or use existing
4. Click **"Create App"**

### **Step 3: Add WhatsApp Product**
1. In your app dashboard, find **"WhatsApp"**
2. Click **"Set up"**
3. You'll see the WhatsApp Business API setup page

### **Step 4: Get Your Credentials**
Copy these values (you'll need them for configuration):

#### **Access Token**
- **Temporary Token**: Available immediately (24 hours)
- **Permanent Token**: Requires app review for production

#### **Phone Number ID**
- Found in the "From" section of the API setup page
- Example: `123456789012345`

#### **WhatsApp Account ID**
- Found in the WhatsApp Business Account section
- Example: `123456789012345`

#### **App ID**
- Found in App Settings → Basic
- Example: `123456789012345`

#### **Phone Number**
- Your test phone number provided by Meta
- Example: `+15551234567`

### **Step 5: Create Webhook Verify Token**
1. **Create a secure random string** for webhook verification
2. **Save it** - you'll need it for both Meta and your app configuration
3. **Example**: `CoolCharizard123` (use your own secure token)

### **📋 What You'll Have**
After completing this section, you'll have:
- `META_ACCESS_TOKEN`: Your WhatsApp API access token
- `META_PHONE_NUMBER_ID`: Your phone number ID
- `META_WHATSAPP_ACCOUNT_ID`: Your WhatsApp account ID
- `META_APP_ID`: Your Meta app ID
- `META_PHONE_NUMBER`: Your test phone number
- `META_WEBHOOK_VERIFY_TOKEN`: Your custom verification token

---

## 📊 **Google Sheets API Setup**

### **Step 1: Create Google Cloud Project**
1. Visit [Google Cloud Console](https://console.cloud.google.com/)
2. **Create new project** or select existing one
3. **Name it**: "Budget Bot Project"

### **Step 2: Enable Google Sheets API**
1. Go to **APIs & Services** → **Library**
2. Search for **"Google Sheets API"**
3. **Enable** the API
4. Also enable **Google Drive API** (for file permissions)

### **Step 3: Create Service Account**
1. Go to **APIs & Services** → **Credentials**
2. Click **"Create Credentials"** → **Service Account**
3. **Name**: "budget-bot-service"
4. **Description**: "Service account for budget bot"
5. **Create and continue**

### **Step 4: Generate Service Account Key**
1. Click on the created service account
2. Go to **Keys** tab
3. **Add Key** → **Create new key**
4. **Key type**: JSON
5. **Download** the JSON file
6. **Rename** it to `google_creds.json`
7. **Move** it to `credits/google_creds.json`

### **Step 5: Share Spreadsheets with Service Account**
1. **Open your Google Sheets**
2. **Share** each spreadsheet
3. **Add the service account email** (from JSON file):
   ```
   budget-bot-service@your-project.iam.gserviceaccount.com
   ```
4. **Give "Editor" permissions**

### **Step 6: Create Required Spreadsheets**

#### **Budget Spreadsheet (SUMMARY_SPREADSHEET_ID)**
1. **Create new spreadsheet**
2. **Name**: "Budget Summary"
3. **Create sheets** for each month (e.g., "July", "August")
4. **Add headers** in A1:D1:
   ```
   קטגוריה | תקציב | כמה יצא | כמה נשאר
   ```
5. **Create __configs sheet**:
   - Sheet name: `__configs`
   - A1: `working_sheet`
   - B1: `July` (or current month)

#### **Tracker Spreadsheet (IO_SPREADSHEET_ID)**
1. **Create new spreadsheet**
2. **Name**: "Expense Tracker"
3. **Create sheets** for each month (e.g., "July", "August")
4. **Add headers** in A1:D1:
   ```
   קטגוריה | פירוט | מחיר | תאריך
   ```

### **Step 7: Get Spreadsheet IDs**
From the URL of each spreadsheet:
```
https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit#gid=0
                                    ^^^^^^^^^^^^^^^^
```

### **🔐 Security Best Practices**
- **Never commit** `google_creds.json` to version control
- **Add to .gitignore**:
  ```
  credits/google_creds.json
  ```
- **Regenerate keys** if compromised
- **Use minimal permissions** (Editor only, not Owner)

---

## 📋 **Summary - What You'll Have**

After completing this guide, you'll have collected all the necessary API keys and credentials:

### **OpenAI API**
- `GPT_API_KEY`: Your OpenAI API key (starts with `sk-proj-`)

### **Meta WhatsApp Business API**
- `META_ACCESS_TOKEN`: Your WhatsApp Business API access token
- `META_PHONE_NUMBER_ID`: Your phone number ID
- `META_WHATSAPP_ACCOUNT_ID`: Your WhatsApp account ID
- `META_APP_ID`: Your Meta app ID
- `META_PHONE_NUMBER`: Your test phone number
- `META_WEBHOOK_VERIFY_TOKEN`: Your custom verification token

### **Google Sheets API**
- `IO_SPREADSHEET_ID`: Your tracker spreadsheet ID
- `SUMMARY_SPREADSHEET_ID`: Your budget spreadsheet ID
- `google_creds.json`: Service account credentials file

### **User Configuration**
- `USER1_PHONE`: First user's phone number
- `USER1_NAME`: First user's name
- `USER2_PHONE`: Second user's phone number
- `USER2_NAME`: Second user's name

---

## 🎯 **Next Steps**

✅ **Got all your API keys?** Now proceed to the [Setup Guide](SETUP_GUIDE.md) to:
1. Clone the repository
2. Configure your credentials
3. Deploy your bot

---

## 🔧 **API Testing Tools**
- **OpenAI**: [Playground](https://platform.openai.com/playground)
- **Meta WhatsApp**: [API Explorer](https://developers.facebook.com/docs/whatsapp/business-management-api)
- **Google Sheets**: [API Explorer](https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets.values/get)

---

## 📞 **Support Resources**

### **API Documentation**
- [OpenAI API Docs](https://platform.openai.com/docs)
- [Meta WhatsApp API](https://developers.facebook.com/docs/whatsapp)
- [Google Sheets API](https://developers.google.com/sheets/api)

### **Community Support**
- [OpenAI Community](https://community.openai.com/)
- [Meta Developer Community](https://developers.facebook.com/community/)
- [Google Cloud Support](https://cloud.google.com/support)

---

<div align="center">

**🎉 APIs Successfully Configured!**

Your Smart Hebrew Budget Bot is ready to use.

[← Back to README](../README.md) • [User Guide →](USER_GUIDE.md)

</div> 