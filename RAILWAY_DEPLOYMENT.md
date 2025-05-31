# Railway.app Deployment Guide

This guide explains how to deploy your Shop Titans Text Classification API to Railway.app using Docker.

## 🚀 Quick Start

### Prerequisites

1. **Railway CLI** - Install from [railway.app](https://railway.app)
2. **Docker** - For local testing
3. **Railway Account** - Sign up at [railway.app](https://railway.app)

### Local Development & Testing

```bash
# Build and test locally
just railway-dev

# Test the API
curl http://localhost:8000/health
curl -X POST "http://localhost:8000/classify" -F "file=@data/image.png"

# Stop local container
just docker-stop
```

### Deploy to Railway

1. **Login to Railway**

   ```bash
   railway login
   ```

2. **Create a new project**

   ```bash
   railway new
   ```

3. **Deploy your application**

   ```bash
   just railway-deploy
   ```

4. **Check deployment status**
   ```bash
   just railway-status
   ```

## 📁 Railway Configuration Files

- **`Dockerfile`** - Multi-stage Docker build with uv package manager
- **`railway.json`** - Railway deployment configuration
- **`.dockerignore`** - Optimizes Docker build by excluding unnecessary files
- **`src/railway_main.py`** - Railway-specific FastAPI app with modern lifespan events

## 🔧 Available Commands

| Command                  | Description                       |
| ------------------------ | --------------------------------- |
| `just docker-build`      | Build Docker image locally        |
| `just railway-dev`       | Build and run locally for testing |
| `just docker-stop`       | Stop local development container  |
| `just railway-deploy`    | Deploy to Railway                 |
| `just railway-status`    | Check deployment status           |
| `just railway-logs`      | View deployment logs              |
| `just railway-dashboard` | Open Railway dashboard            |

## 🌐 API Endpoints

Once deployed, your API will be available at your Railway URL:

- `GET /` - Welcome message
- `GET /health` - Health check with model status
- `POST /classify` - Upload image for text classification
- `GET /docs` - Interactive API documentation

## 🔍 Monitoring

- **Health Check**: Railway automatically monitors `/health` endpoint
- **Logs**: Use `just railway-logs` to view application logs
- **Metrics**: Available in Railway dashboard

## 🛠️ Troubleshooting

### Common Issues

1. **Build Failures**

   - Check that all dependencies are in `pyproject.toml`
   - Ensure `model/decision_forest.pkl` exists
   - Verify Docker build works locally: `just docker-build`

2. **Runtime Errors**

   - Check logs: `just railway-logs`
   - Verify health endpoint: `curl https://your-app.railway.app/health`
   - Ensure model file is properly copied in Dockerfile

3. **Port Issues**
   - Railway automatically sets `PORT` environment variable
   - Application listens on `0.0.0.0:8000` by default

### Environment Variables

Railway automatically provides:

- `PORT` - Port to listen on (usually 8000)
- `PYTHONPATH` - Set to `/app` for proper imports

## 📊 Performance

- **Cold Start**: ~2-3 seconds (model loading)
- **Processing Time**: ~40ms per image
- **Memory Usage**: ~200MB (including ML model)
- **Build Time**: ~30-60 seconds

## 🔄 CI/CD

For automatic deployments, connect your GitHub repository to Railway:

1. Go to Railway dashboard
2. Connect GitHub repository
3. Enable automatic deployments on push to main branch

## 📚 Additional Resources

- [Railway Documentation](https://docs.railway.app)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
