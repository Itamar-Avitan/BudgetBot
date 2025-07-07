#!/bin/bash
# update.sh - Quick redeploy (no git operations)
set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}⚡ Quick Redeploy${NC}"
echo "================"

# Check if config file exists
if [ ! -f "deploy_config.json" ]; then
    echo -e "${RED}❌ Error: deploy_config.json not found${NC}"
    echo "Please run ./deploy.sh first for initial setup"
    exit 1
fi

# Simple parsing without jq dependency
PROJECT_ID=$(grep -o '"project_id"[^,]*' deploy_config.json | cut -d'"' -f4)
APP_URL=$(grep -o '"app_url"[^,]*' deploy_config.json | cut -d'"' -f4)

echo -e "${GREEN}📦 Redeploying to: $PROJECT_ID${NC}"

# Set project and deploy
gcloud config set project "$PROJECT_ID"
gcloud app deploy --quiet

echo ""
echo -e "${GREEN}✅ Redeploy complete!${NC}"
echo -e "${GREEN}🎉 Your bot is updated at: $APP_URL${NC}" 