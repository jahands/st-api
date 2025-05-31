import modal
from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel, Field
from typing import List
import numpy as np
from PIL import Image
import io
from datetime import datetime, timezone

# Create Modal app with uv-managed dependencies and model files
image = (
    modal.Image.debian_slim()
    .pip_install("uv")
    .workdir("/work")
    .add_local_file("pyproject.toml", "/work/pyproject.toml", copy=True)
    .add_local_file("uv.lock", "/work/uv.lock", copy=True)
    .add_local_file("model/decision_forest.pkl", "/work/decision_forest.pkl", copy=True)
    .add_local_file("src/image_manipulate_utils.py", "/work/image_manipulate_utils.py", copy=True)
    .env({"UV_PROJECT_ENVIRONMENT": "/usr/local"})
    .run_commands([
        "uv sync --frozen --compile-bytecode",
        "uv build",
    ])
)
app = modal.App("st-api", image=image)

# Pydantic models for request/response validation
class ClassificationResponse(BaseModel):
    """Response model for image classification"""
    extracted_text: str = Field(..., description="The extracted and classified text from the image")
    confidence: float = Field(..., description="Average confidence score for the classification")
    num_characters: int = Field(..., description="Number of characters detected")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")
    timestamp: str = Field(..., description="ISO timestamp of when the classification was performed")

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str = "1.0.0"
    model_loaded: bool = Field(..., description="Whether the ML model is loaded and ready")

class ErrorResponse(BaseModel):
    error: str
    detail: str
    timestamp: str

# Create FastAPI app instance
web_app = FastAPI(
    title="Shop Titans Text Classification API",
    description="API for extracting and classifying digits/text from images using Random Forest ML model",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Global variable to store the ML model (will be loaded on container startup)
model = None

@web_app.get("/")
async def root():
    """Welcome endpoint"""
    return {
        "message": "Welcome to Shop Titans Text Classification API!",
        "description": "Upload images to extract and classify digits/text",
        "endpoints": {
            "classify": "POST /classify - Upload image for text classification",
            "health": "GET /health - Health check",
            "docs": "GET /docs - API documentation"
        },
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@web_app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    global model
    return HealthResponse(
        status="healthy",
        model_loaded=model is not None,
        timestamp=datetime.now(timezone.utc).isoformat()
    )

@web_app.post("/classify", response_model=ClassificationResponse)
async def classify_image(file: UploadFile = File(...)):
    """
    Classify text/digits in an uploaded image.

    Accepts image files (PNG, JPG, JPEG) and returns extracted text.
    """
    import time
    start_time = time.time()

    try:
        # Validate file type
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=400,
                detail="File must be an image (PNG, JPG, JPEG)"
            )

        # Read and process the image
        image_data = await file.read()
        image = Image.open(io.BytesIO(image_data))

        # Extract text using the classification logic
        extracted_text, confidence, num_chars = await classify_text_in_image(image)

        processing_time = (time.time() - start_time) * 1000  # Convert to milliseconds

        return ClassificationResponse(
            extracted_text=extracted_text,
            confidence=confidence,
            num_characters=num_chars,
            processing_time_ms=processing_time,
            timestamp=datetime.now(timezone.utc).isoformat()
        )

    except Exception as e:
        processing_time = (time.time() - start_time) * 1000
        print(f"Error processing image: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing image: {str(e)}"
        )

async def classify_text_in_image(image: Image.Image) -> tuple[str, float, int]:
    """
    Extract and classify text from an image using the Random Forest model.

    This implementation follows the exact logic from eval_forest.py

    Args:
        image: PIL Image to process

    Returns:
        Tuple of (extracted_text, confidence, num_characters)
    """
    global model

    # Load model if not already loaded
    if model is None:
        try:
            from pickle import load
            with open('/work/decision_forest.pkl', 'rb') as f:
                model = load(f)
            print("✅ Random Forest model loaded successfully")
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            return "ERROR", 0.0, 0

    try:
        # Import the actual image processing utilities
        import sys
        sys.path.append('/work')
        from image_manipulate_utils import filter_rgb_color_range, find_connected_disjoint_structures

        # Convert image to numpy array and preprocess (following eval_forest.py exactly)
        image_array = np.array(image.convert('RGB'))

        # Apply the same color filtering as in eval_forest.py
        filtered_image = filter_rgb_color_range(image_array, (160, 154, 157), (255, 255, 255))
        binary_image = np.all(filtered_image != 0, -1)

        # Find connected structures
        structures = find_connected_disjoint_structures(binary_image)

        if not structures:
            return "", 0.0, 0

        number_xpos_pairs: List[tuple[str, int]] = []
        confidences: List[float] = []

        for symbol in structures:
            box, symbol_image = symbol

            # Pad the symbol to match training data dimensions (17x10) - exactly as in eval_forest.py
            X = np.pad(symbol_image, ((0, 17 - symbol_image.shape[0]), (0, 10 - symbol_image.shape[1])))
            X_reshaped = X.reshape(1, -1)

            # Get prediction and confidence
            prediction = model.predict(X_reshaped)[0]
            probabilities = model.predict_proba(X_reshaped)[0]
            confidence = probabilities.max()

            # Skip commas (class 10) - exactly as in eval_forest.py
            if prediction == 10:
                continue

            # Store digit and its x-position for sorting (using box.top as in eval_forest.py)
            number_xpos_pairs.append((str(prediction), box.top))
            confidences.append(confidence)

        # Sort by x-position (left to right) - exactly as in eval_forest.py
        number_xpos_pairs.sort(key=lambda p: p[1])

        # Combine digits into final text - exactly as in eval_forest.py
        extracted_text = ''.join([p[0] for p in number_xpos_pairs])

        # Calculate average confidence
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

        print(f"✅ Successfully classified: '{extracted_text}' with {len(number_xpos_pairs)} characters")

        return extracted_text, avg_confidence, len(number_xpos_pairs)

    except Exception as e:
        print(f"❌ Error in classification: {str(e)}")
        import traceback
        traceback.print_exc()
        # Return error indicator
        return "ERROR", 0.0, 0

# Deploy the FastAPI app using Modal's ASGI app decorator
@app.function()
@modal.asgi_app()
def fastapi_app():
    return web_app

# Function to load the ML model (called on container startup)
@app.function()
def load_model():
    """Load the Random Forest model for digit classification."""
    global model
    try:
        from pickle import load
        with open('/work/decision_forest.pkl', 'rb') as f:
            model = load(f)
        print("✅ Random Forest model loaded successfully in load_model function")
        return f"Model loaded successfully: {type(model).__name__} with {model.n_estimators} estimators"
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        return f"Error loading model: {e}"

@app.local_entrypoint()
def main():
    """Test the model loading function."""
    result = load_model.remote()
    print(f"Model loading result: {result}")
