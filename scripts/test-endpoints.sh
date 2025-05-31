#!/usr/bin/env bash

# Test all API endpoints with sample requests
# Usage: ./scripts/test-endpoints.sh [base_url]

set -e

# Default to dev URL, but allow override
BASE_URL="${1:-https://jahands--st-api-fastapi-app-dev.modal.run}"

echo "Testing API endpoints at: $BASE_URL"
echo "========================================"
echo

# Function to test an endpoint with error handling
test_endpoint() {
    local name="$1"
    local method="$2"
    local url="$3"
    local data="$4"

    echo "$name:"

    if [ -n "$data" ]; then
        response=$(curl -s -X "$method" "$url" -H "Content-Type: application/json" -d "$data")
    else
        response=$(curl -s -X "$method" "$url")
    fi

    # Check if response contains error message
    if echo "$response" | grep -q "modal-http: app for invoked web endpoint is stopped"; then
        echo "❌ API is not running. Please start it with 'just dev' first."
        return 1
    elif echo "$response" | python3 -c "import sys, json; json.load(sys.stdin)" 2>/dev/null; then
        echo "$response" | python3 -m json.tool
    else
        echo "❌ Invalid JSON response: $response"
        return 1
    fi
    echo
}

echo "1. Testing root endpoint:"
test_endpoint "Root" "GET" "$BASE_URL/" || exit 1

echo "2. Testing health endpoint:"
test_endpoint "Health" "GET" "$BASE_URL/health"

echo "3. Testing square (GET):"
test_endpoint "Square GET" "GET" "$BASE_URL/square/5"

echo "4. Testing square (POST):"
test_endpoint "Square POST" "POST" "$BASE_URL/square" '{"number": 8}'

echo "5. Testing calculator (addition):"
test_endpoint "Calculator Add" "POST" "$BASE_URL/calculate" '{"operation": "add", "a": 15, "b": 25}'

echo "6. Testing calculator (square root):"
test_endpoint "Calculator Sqrt" "POST" "$BASE_URL/calculate" '{"operation": "sqrt", "a": 144}'

echo "7. Testing calculator (power):"
test_endpoint "Calculator Power" "POST" "$BASE_URL/calculate" '{"operation": "power", "a": 2, "b": 8}'

echo "8. Testing calculator (divide):"
test_endpoint "Calculator Divide" "POST" "$BASE_URL/calculate" '{"operation": "divide", "a": 100, "b": 4}'

echo "✅ All tests completed successfully!"
