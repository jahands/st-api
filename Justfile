set shell := ["bash", "-c"]

[private]
@help:
  just --list

# Deploy the API to Modal (production)
deploy:
  uv run modal deploy src/main.py

# Run the API in development mode with hot-reload
dev:
  uv run modal serve src/main.py

# Test the API endpoints locally (requires the API to be running)
test-api:
  cd scripts && uv run python test_api.py

# Run a quick health check on the deployed API
health-check:
  ./scripts/health-check.sh

# Check health of production API
health-check-prod:
  ./scripts/health-check.sh "https://jahands--st-api-fastapi-app.modal.run"

# Test all API endpoints with sample requests
test-endpoints:
  ./scripts/test-endpoints.sh

# Test endpoints against production URL
test-endpoints-prod:
  ./scripts/test-endpoints.sh "https://jahands--st-api-fastapi-app.modal.run"

# Open the API documentation in browser
docs:
  open "https://jahands--st-api-fastapi-app-dev.modal.run/docs"

# View Modal app logs
logs:
  uv run modal app logs st-api

# Stop the running Modal app
stop:
  uv run modal app stop st-api

# === Railway Deployment Commands ===

# Build Docker image for Railway deployment
docker-build:
  docker build -t st-api-railway .

# Run Railway API locally using Docker
docker-run:
  docker run -p 8000:8000 --rm st-api-railway

# Run Railway API locally in background
docker-run-bg:
  docker run -d -p 8000:8000 --name st-api-railway-dev st-api-railway

# Stop background Railway API container
docker-stop:
  docker stop st-api-railway-dev && docker rm st-api-railway-dev

# Test Railway API locally (requires docker-run to be running)
test-railway:
  curl -f http://localhost:8000/health && echo "\n✅ Railway API health check passed"

# Test Railway API endpoints locally
test-railway-endpoints:
  ./scripts/test-endpoints.sh "http://localhost:8000"

# Build and run Railway API locally in background, then test
railway-dev: docker-build docker-run-bg
  sleep 3
  just test-railway
  echo "🚀 Railway API running at http://localhost:8000"
  echo "📖 API docs at http://localhost:8000/docs"
  echo "🛑 Stop with: just docker-stop"

# Deploy to Railway (requires Railway CLI)
railway-deploy:
  railway up

# Check Railway deployment status
railway-status:
  railway status

# View Railway logs
railway-logs:
  railway logs

# Open Railway dashboard
railway-dashboard:
  railway open

# === Load Testing Commands ===

# Run load test against production API (1000 requests, 10 concurrency)
loadtest:
  uv run python scripts/loadtest.py --url "https://st-api.geostyx.com/classify"

# Run quick load test (100 requests, 5 concurrency)
loadtest-quick:
  uv run python scripts/loadtest.py --url "https://st-api.geostyx.com/classify" --requests 100 --concurrency 5

# Run intensive load test (5000 requests, 20 concurrency)
loadtest-intensive:
  uv run python scripts/loadtest.py --url "https://st-api.geostyx.com/classify" --requests 5000 --concurrency 20

# Load test local Railway API (requires docker-run-bg)
loadtest-local:
  uv run python scripts/loadtest.py --url "http://localhost:8000/classify" --requests 100 --concurrency 5

# Load test with custom parameters
loadtest-custom url requests="1000" concurrency="10":
  uv run python scripts/loadtest.py --url "{{url}}" --requests {{requests}} --concurrency {{concurrency}}

# Load test and save results with timestamp
loadtest-save:
  uv run python scripts/loadtest.py --url "https://st-api.geostyx.com/classify" --output "loadtest_$(date +%Y%m%d_%H%M%S).json"
