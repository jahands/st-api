set shell := ["bash", "-c"]

[private]
@help:
  just --list

# Run the original local entrypoint
start:
  uv run src/main.py

# Deploy the API to Modal (production)
deploy:
  uv run modal deploy src/main.py

# Run the API in development mode with hot-reload
dev:
  uv run modal serve src/main.py

# Test the API endpoints locally (requires the API to be running)
test-api:
  uv run python test_api.py

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
