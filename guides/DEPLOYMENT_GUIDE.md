# 🚀 Modern Deployment Guide: WhatsApp Budget Bot

**Complete guide for the new template-based deployment system**

---

## 🎯 **Overview**

This bot uses a **template-based configuration system** that keeps your personal settings private while making it easy for others to use your open-source project.

### **📁 File Organization**
```
budget_chat/
├── deploy_config.json           # Your private deployment settings
├── credits/
│   ├── keys.json               # Your private API credentials
│   ├── google_creds.json       # Your private Google credentials
│   └── templates/              # Public templates (safe to commit)
│       ├── keys.json           # Template for API credentials
│       └── deploy_config.json  # Template for deployment settings
├── deploy.sh                   # Smart deployment script
├── update.sh                   # Quick redeploy script
└── logs.sh                     # Easy log viewing
```

---

## 🔧 **Initial Setup**

### **Step 1: Clone and Configure**
```bash
# Clone the repository
git clone https://github.com/YOUR-USERNAME/budget_chat.git
cd budget_chat

# Copy templates to create your personal configs
cp credits/templates/keys.json credits/keys.json
cp credits/templates/deploy_config.json deploy_config.json
```

### **Step 2: Fill in Your Credentials**

**Edit `credits/keys.json`** with your actual API keys:
```json
{
    "GPT_API_KEY": "sk-proj-YOUR-ACTUAL-OPENAI-KEY",
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

**Edit `deploy_config.json`** with your project details:
```json
{
  "project_id": "your-actual-project-id",
  "region": "europe-west1",
  "app_url": "https://your-actual-project-id.ew.r.appspot.com",
  "service_name": "default",
  "environment": "production"
}
```

### **Step 3: Add Google Credentials**
Place your `google_creds.json` service account file in the `credits/` directory.

---

## 🚀 **Deployment**

### **First-Time Deployment**
```bash
# The script will check your config and guide you
./deploy.sh
```

### **Quick Updates**
```bash
# After making code changes
./update.sh
```

### **View Logs**
```bash
./logs.sh
```

---

## 🔐 **Security & Privacy**

### **What Stays Private (Hidden from Git)**
- ✅ `credits/keys.json` - Your actual API credentials
- ✅ `credits/google_creds.json` - Your Google service account
- ✅ `deploy_config.json` - Your project settings

### **What's Public (Safe to Commit)**
- ✅ `credits/templates/` - Templates for others to use
- ✅ `deploy.sh`, `update.sh`, `logs.sh` - Deployment scripts
- ✅ Documentation and guides
- ✅ Source code

### **Git Workflow**
```bash
# 1. Make your changes
# 2. Test locally
# 3. When ready, commit and push
git add .
git commit -m "Your changes"
git push origin main

# 4. Deploy your changes
./update.sh
```

**Note**: The deployment scripts **never touch git** - you maintain full control over your repository.

---

## ⚙️ **App Engine Configuration**

### **Current Settings (app.yaml)**
```yaml
runtime: python311                    # Latest Python for better performance

# Optimized free tier usage
automatic_scaling:
  min_instances: 1                    # No cold starts
  max_instances: 3                    # Scale efficiently
  target_cpu_utilization: 0.5        # Scale early for responsiveness

# Maximized free tier resources
resources:
  cpu: 1                              # Full CPU
  memory_gb: 1                        # Full memory
  disk_size_gb: 10                    # Plenty of disk space
```

### **Performance Optimizations**
- ✅ **Python 3.11** - 10-60% faster than older versions
- ✅ **Efficient scaling** - Creates instances at 50% CPU usage
- ✅ **Always-on** - 1 instance always running (no cold starts)
- ✅ **Free tier optimized** - Uses ~26/28 hours daily (still free!)

---

## 📊 **Monitoring & Maintenance**

### **Health Checks**
```bash
# Check if your bot is healthy
curl https://your-project-id.ew.r.appspot.com/health

# Expected response:
{
  "status": "healthy",
  "components": {
    "google_sheets": "healthy",
    "gpt_api": "healthy",
    "categories_count": 6
  }
}
```

### **Log Monitoring**
```bash
# Real-time logs
./logs.sh

# Or manually:
gcloud app logs tail -s default
```

### **Cost Monitoring**
- **Monthly cost**: $0 (within Google Cloud free tier)
- **OpenAI usage**: ~$0.50/month for GPT calls
- **Total**: ~$0.50/month

---

## 🆘 **Troubleshooting**

### **Common Issues**

#### **"deploy_config.json not found"**
```bash
# Solution: Copy the template
cp credits/templates/deploy_config.json deploy_config.json
# Then edit with your project details
```

#### **"credits/keys.json not found"**
```bash
# Solution: Copy the template
cp credits/templates/keys.json credits/keys.json
# Then edit with your actual API keys
```

#### **"Webhook verification failed"**
- Check your verify token in `credits/keys.json` matches WhatsApp settings
- Ensure your bot is deployed and accessible

#### **"GPT API not available"**
- Verify your OpenAI API key in `credits/keys.json`
- Check you have billing enabled on OpenAI

### **Debug Commands**
```bash
# Check deployment status
gcloud app versions list

# View error logs
gcloud app logs read --severity=ERROR

# Health check
curl https://your-project-id.ew.r.appspot.com/health
```

---

## 🔄 **For Contributors**

### **Contributing to the Project**
1. **Fork the repository**
2. **Follow the setup steps** above
3. **Make your changes**
4. **Test thoroughly**
5. **Submit a pull request**

### **File Guidelines**
- ✅ **Always use templates** - Never commit actual credentials
- ✅ **Update documentation** - Keep guides current
- ✅ **Test deployment** - Ensure scripts work
- ✅ **Follow conventions** - Match existing code style

---

## 🎉 **Success Checklist**

After successful deployment, you should have:

- ✅ **Bot responding** to WhatsApp messages
- ✅ **Health check** returning "healthy"
- ✅ **Logs showing** successful operations
- ✅ **No errors** in Google Cloud Console
- ✅ **Webhook verified** in Meta Developer Console

### **Test Your Bot**
1. Send: `יתרה` → Should show budget summary
2. Send: `קניתי קפה ב-15` → Should record expense
3. Send: `עזרה` → Should show help menu

---

## 📱 **WhatsApp Configuration**

After deployment, update your WhatsApp Business API settings:

1. **Webhook URL**: `https://your-project-id.ew.r.appspot.com/webhook`
2. **Verify Token**: Use the value from your `credits/keys.json`
3. **Test the webhook** in Meta Developer Console

---

## 💡 **Pro Tips**

### **Development Workflow**
```bash
# 1. Make changes locally
# 2. Test with local server (optional)
python whatsapp.py

# 3. Deploy when ready
./update.sh

# 4. Monitor logs
./logs.sh
```

### **Quick Commands**
```bash
# Full deployment (first time or troubleshooting)
./deploy.sh

# Quick redeploy (after code changes)
./update.sh

# View logs
./logs.sh

# Health check
curl $(jq -r '.app_url' deploy_config.json)/health
```

---

**Your WhatsApp Budget Bot is now professionally deployed with modern DevOps practices!** 🚀

[← Back to README](../README.md) • [API Setup →](API_SETUP.md) • [User Guide →](USER_GUIDE.md) 