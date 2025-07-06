#!/bin/bash
# deploy_gcp.sh - Deploy WhatsApp Budget Bot to Google Cloud Platform
# Usage: ./deploy_gcp.sh [PROJECT_ID]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 WhatsApp Budget Bot - Google Cloud Deployment${NC}"
echo "=================================================="

# Check if PROJECT_ID is provided
PROJECT_ID="${1}"

if [ -z "$PROJECT_ID" ]; then
    echo "Usage: $0 <PROJECT_ID>"
    echo "Example: $0 my-budget-bot-project"
    exit 1
fi

echo -e "${GREEN}✅ Using project: $PROJECT_ID${NC}"

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ Error: gcloud CLI is not installed${NC}"
    echo "Please install Google Cloud SDK: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Check if user is logged in
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo -e "${YELLOW}⚠️ Not logged in to Google Cloud${NC}"
    echo "Please run: gcloud auth login"
    exit 1
fi

# Set project
echo -e "${BLUE}🔧 Setting up project: $PROJECT_ID${NC}"
gcloud config set project "$PROJECT_ID"

# Enable required APIs (only if not already enabled)
echo -e "${BLUE}🔧 Ensuring required APIs are enabled...${NC}"
gcloud services enable appengine.googleapis.com sheets.googleapis.com logging.googleapis.com monitoring.googleapis.com cloudbuild.googleapis.com --quiet

# Check if App Engine app exists
if ! gcloud app describe &>/dev/null; then
    echo -e "${YELLOW}⚠️ App Engine app not found. Creating...${NC}"
    
    # Default to europe-west1 (can be changed if needed)
    REGION="europe-west1"
    echo -e "${BLUE}🌍 Creating App Engine app in region: $REGION${NC}"
    
    gcloud app create --region="$REGION"
    echo -e "${GREEN}✅ App Engine app created in $REGION${NC}"
fi

# Verify required files exist
if [ ! -f "app.yaml" ]; then
    echo -e "${RED}❌ Error: app.yaml not found${NC}"
    exit 1
fi

if [ ! -f "credits/keys.json" ]; then
    echo -e "${RED}❌ Error: credits/keys.json not found${NC}"
    echo "Please make sure you have the configuration file with your API keys"
    exit 1
fi

if [ ! -f "credits/google_creds.json" ]; then
    echo -e "${RED}❌ Error: credits/google_creds.json not found${NC}"
    echo "Please make sure you have the Google service account credentials file"
    exit 1
fi

# Deploy the application
echo -e "${BLUE}🚀 Deploying WhatsApp Budget Bot...${NC}"
echo "Using existing configuration from credits/keys.json"

gcloud app deploy --quiet

# Get the deployed URL
APP_URL=$(gcloud app browse --no-launch-browser)
echo ""
echo -e "${GREEN}✅ Deployment successful!${NC}"
echo ""
echo -e "${GREEN}🎉 Your WhatsApp Budget Bot is live at:${NC}"
echo -e "${BLUE}$APP_URL${NC}"
echo ""
echo -e "${GREEN}📱 Webhook URL for WhatsApp:${NC}"
echo -e "${BLUE}${APP_URL}/webhook${NC}"
echo ""
echo -e "${YELLOW}📋 Next steps:${NC}"
echo "1. Update your WhatsApp Business API webhook URL to: ${APP_URL}/webhook"
echo "2. Test the webhook with a message"
echo "3. Monitor logs with: gcloud app logs tail -s default"
echo ""
echo -e "${GREEN}🔧 Useful commands:${NC}"
echo "• View logs: gcloud app logs tail -s default"
echo "• Check health: curl ${APP_URL}/health"
echo "• Update deployment: ./deploy_gcp.sh"
echo "• View all versions: gcloud app versions list"
echo ""
echo -e "${GREEN}📊 Monitoring:${NC}"
echo "• Health check: ${APP_URL}/health"
echo "• Google Cloud Console: https://console.cloud.google.com/appengine?project=$PROJECT_ID"
echo ""
echo -e "${BLUE}💡 Pro tip:${NC} Your bot has minimum 1 instance always running - no cold starts!"
echo -e "${GREEN}💰 Estimated monthly cost: ~$0.50 for always-on service!${NC}"
echo ""
echo -e "${GREEN}✅ Deployment complete! Your intelligent WhatsApp Bot is ready! 🤖💬${NC}" 