#!/bin/bash
# deploy.sh - Deploy WhatsApp Budget Bot (no git operations)
set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}🚀 WhatsApp Budget Bot - Deploy${NC}"
echo "==============================="

# Check if config file exists
if [ ! -f "deploy_config.json" ]; then
    echo -e "${RED}❌ Error: deploy_config.json not found${NC}"
    echo ""
    echo -e "${YELLOW}📋 First time setup:${NC}"
    echo "1. Copy template: cp credits/templates/deploy_config.json deploy_config.json"
    echo "2. Edit deploy_config.json with your project details"
    echo "3. Run this script again"
    echo ""
    echo -e "${BLUE}💡 See README.md for detailed setup instructions${NC}"
    exit 1
fi

# Check if jq is available for JSON parsing
if ! command -v jq &> /dev/null; then
    echo -e "${YELLOW}⚠️ jq not found, using basic parsing${NC}"
    # Fallback: extract project_id manually
    PROJECT_ID=$(grep -o '"project_id"[^,]*' deploy_config.json | cut -d'"' -f4)
    APP_URL=$(grep -o '"app_url"[^,]*' deploy_config.json | cut -d'"' -f4)
else
    # Use jq for proper JSON parsing
    PROJECT_ID=$(jq -r '.project_id' deploy_config.json)
    APP_URL=$(jq -r '.app_url' deploy_config.json)
fi

echo -e "${GREEN}✅ Using project: $PROJECT_ID${NC}"

# Check required files
if [ ! -f "credits/keys.json" ]; then
    echo -e "${RED}❌ Error: credits/keys.json not found${NC}"
    echo "Please follow the setup guide to configure your credentials"
    exit 1
fi

if [ ! -f "credits/google_creds.json" ]; then
    echo -e "${RED}❌ Error: credits/google_creds.json not found${NC}"
    echo "Please follow the setup guide to configure your Google credentials"
    exit 1
fi

# Set project
echo -e "${BLUE}🔧 Setting project: $PROJECT_ID${NC}"
gcloud config set project "$PROJECT_ID"

# Deploy
echo -e "${BLUE}🚀 Deploying to Google Cloud...${NC}"
gcloud app deploy --quiet

echo ""
echo -e "${GREEN}✅ Deployment successful!${NC}"
echo -e "${GREEN}🌐 Your bot is live at: $APP_URL${NC}"
echo -e "${GREEN}📱 Webhook URL: $APP_URL/webhook${NC}"
echo ""
echo -e "${BLUE}📊 Useful commands:${NC}"
echo "• Check logs: ./logs.sh"
echo "• Health check: curl $APP_URL/health"
echo "• Quick redeploy: ./update.sh" 