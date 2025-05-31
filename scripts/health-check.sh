#!/usr/bin/env bash

# Quick health check for the API
# Usage: ./scripts/health-check.sh [base_url]

# Default to dev URL, but allow override
BASE_URL="${1:-https://jahands--st-api-fastapi-app-dev.modal.run}"

echo "Checking API health at: $BASE_URL"
echo "=================================="

response=$(curl -s "$BASE_URL/health")

# Check if response contains error message
if echo "$response" | grep -q "modal-http: app for invoked web endpoint is stopped"; then
    echo "❌ API is not running. Please start it with 'just dev' first."
    exit 1
elif echo "$response" | python3 -c "import sys, json; json.load(sys.stdin)" 2>/dev/null; then
    echo "✅ API is healthy!"
    echo "$response" | python3 -m json.tool
else
    echo "❌ Invalid response: $response"
    exit 1
fi
