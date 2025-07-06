#!/bin/bash
# update.sh - Quick update and deploy script
# Usage: ./update.sh [commit_message]

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

COMMIT_MSG="${1:-Quick update}"

echo -e "${BLUE}🚀 WhatsApp Budget Bot - Quick Update & Deploy${NC}"
echo "=============================================="

# Check if there are any changes
if git diff --quiet && git diff --cached --quiet; then
    echo -e "${GREEN}✅ No changes detected${NC}"
else
    # Add all changes
    echo -e "${BLUE}📝 Staging changes...${NC}"
    git add .
    
    # Commit changes
    echo -e "${BLUE}💾 Committing: $COMMIT_MSG${NC}"
    git commit -m "$COMMIT_MSG"
    
    # Push to origin
    echo -e "${BLUE}⬆️ Pushing to origin...${NC}"
    git push origin main
fi

# Deploy to Google Cloud
echo -e "${BLUE}🚀 Deploying to Google Cloud...${NC}"
./deploy_gcp.sh

echo -e "${GREEN}✅ Update complete!${NC}"
echo ""
echo -e "${GREEN}🎉 Your WhatsApp Budget Bot is updated and live!${NC}" 