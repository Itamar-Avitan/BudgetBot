#!/bin/bash
# logs.sh - View application logs
set -e

echo "📊 Viewing logs..."

if [ ! -f "deploy_config.json" ]; then
    echo "❌ Error: deploy_config.json not found"
    echo "Please run ./deploy.sh first"
    exit 1
fi

PROJECT_ID=$(grep -o '"project_id"[^,]*' deploy_config.json | cut -d'"' -f4)
gcloud config set project "$PROJECT_ID"
gcloud app logs tail -s default 