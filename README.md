# Shop Titans Text Classification API

A production-ready API for extracting and classifying digits/text from Shop Titans game images using a Random Forest machine learning model.

## 🚀 Quick Start

### Install Dependencies

```sh
uv sync
```

### Development

```sh
just dev                    # Start development server
just health-check          # Check API health
just test-endpoints        # Test all endpoints
```

### Production (Modal)

```sh
just deploy                 # Deploy to Modal
just health-check-prod     # Check production health
```

### Railway Deployment

```sh
# Local Docker testing
just docker-build          # Build Docker image
just docker-run            # Run locally with Docker
just test-railway          # Test Railway API locally

# Deploy to Railway.app
just railway-deploy        # Deploy to Railway (requires Railway CLI)
just railway-status        # Check deployment status
```

## 📁 Project Structure

```
├── src/                    # Source code
│   ├── main.py            # Modal FastAPI application
│   ├── railway_main.py    # Railway FastAPI application
│   ├── image_utils.py     # Image processing utilities
│   └── image_manipulate_utils.py  # Core ML image processing
├── model/                  # Machine learning models
│   └── decision_forest.pkl # Trained Random Forest model
├── data/                   # Test data and images
│   ├── image.png          # Sample Shop Titans image
│   └── output.png         # Processed output
├── scripts/               # Utility scripts
│   ├── test-endpoints.sh  # API endpoint testing
│   ├── health-check.sh    # Health check script
│   ├── test_api.py        # API structure tests
│   └── create_test_image.py # Test image generator
├── reference/             # Reference implementations
│   └── eval_forest.py     # Original classification script
├── Dockerfile             # Railway deployment configuration
├── .dockerignore          # Docker build optimization
└── Justfile              # Development commands
```

## 🔧 API Endpoints

| Method | Endpoint    | Description                          |
| ------ | ----------- | ------------------------------------ |
| `POST` | `/classify` | Upload image for text classification |
| `GET`  | `/health`   | Health check with model status       |
| `GET`  | `/docs`     | Interactive API documentation        |
| `GET`  | `/`         | Welcome message                      |

## 📊 Example Usage

### Upload Image for Classification

```bash
curl -X POST "https://your-api-url/classify" \
     -F "file=@data/image.png"
```

### Response

```json
{
  "extracted_text": "3796",
  "confidence": 0.9025,
  "num_characters": 4,
  "processing_time_ms": 39.68,
  "timestamp": "2025-05-31T19:11:33.422273+00:00"
}
```

## 🧪 Testing

### Test Original Implementation

```sh
uv run python reference/eval_forest.py -d data/image.png
```

### Test API Structure

```sh
just test-api
```

### Test All Endpoints

```sh
just test-endpoints
```

## 🛠️ Development

### Modal Deployment

The API uses Modal for serverless deployment with:

- FastAPI for the web framework
- Random Forest model for digit classification
- PIL/numpy for image processing
- uv for dependency management

### Railway Deployment

The API can also be deployed to Railway.app using Docker with:

- Containerized FastAPI application
- Multi-stage Docker build with uv
- Health checks and proper logging
- Environment variable configuration

## 📈 Performance

- **Processing Time**: ~40ms per image
- **Accuracy**: 90%+ confidence on Shop Titans images
- **Model**: Random Forest with 100 estimators
- **Input Format**: PNG, JPG, JPEG images
