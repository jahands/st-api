import modal
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Union, Dict, Any
import math
from datetime import datetime, timezone

# Create Modal app with uv-managed dependencies
image = (
    modal.Image.debian_slim()
    .pip_install("uv")
    .workdir("/work")
    .add_local_file("pyproject.toml", "/work/pyproject.toml", copy=True)
    .add_local_file("uv.lock", "/work/uv.lock", copy=True)
    .env({"UV_PROJECT_ENVIRONMENT": "/usr/local"})
    .run_commands([
        "uv sync --frozen --compile-bytecode",
        "uv build",
    ])
)
app = modal.App("st-api", image=image)

# Pydantic models for request/response validation
class SquareRequest(BaseModel):
    number: float = Field(..., description="The number to square")

class SquareResponse(BaseModel):
    input: float
    result: float
    timestamp: str

class CalculationRequest(BaseModel):
    operation: str = Field(..., description="Operation: add, subtract, multiply, divide, power, sqrt")
    a: float = Field(..., description="First number")
    b: Union[float, None] = Field(None, description="Second number (not needed for sqrt)")

class CalculationResponse(BaseModel):
    operation: str
    inputs: Dict[str, Any]
    result: float
    timestamp: str

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str = "1.0.0"

# Create FastAPI app instance
web_app = FastAPI(
    title="ST API",
    description="A comprehensive API built with Modal and FastAPI",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

@web_app.get("/", response_model=Dict[str, str])
async def root():
    """Welcome endpoint"""
    return {
        "message": "Welcome to ST API!",
        "docs": "/docs",
        "health": "/health",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@web_app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(timezone.utc).isoformat()
    )

@web_app.post("/square", response_model=SquareResponse)
async def square_post(request: SquareRequest):
    """Square a number using POST request with JSON body"""
    print(f"Squaring {request.number} on remote worker!")
    result = request.number ** 2
    return SquareResponse(
        input=request.number,
        result=result,
        timestamp=datetime.now(timezone.utc).isoformat()
    )

@web_app.get("/square/{number}", response_model=SquareResponse)
async def square_get(number: float):
    """Square a number using GET request with path parameter"""
    print(f"Squaring {number} on remote worker!")
    result = number ** 2
    return SquareResponse(
        input=number,
        result=result,
        timestamp=datetime.now(timezone.utc).isoformat()
    )

@web_app.post("/calculate", response_model=CalculationResponse)
async def calculate(request: CalculationRequest):
    """Perform various mathematical calculations"""
    print(f"Performing {request.operation} on remote worker!")

    try:
        if request.operation == "add":
            if request.b is None:
                raise HTTPException(status_code=400, detail="Operation 'add' requires both 'a' and 'b'")
            result = request.a + request.b
            inputs = {"a": request.a, "b": request.b}

        elif request.operation == "subtract":
            if request.b is None:
                raise HTTPException(status_code=400, detail="Operation 'subtract' requires both 'a' and 'b'")
            result = request.a - request.b
            inputs = {"a": request.a, "b": request.b}

        elif request.operation == "multiply":
            if request.b is None:
                raise HTTPException(status_code=400, detail="Operation 'multiply' requires both 'a' and 'b'")
            result = request.a * request.b
            inputs = {"a": request.a, "b": request.b}

        elif request.operation == "divide":
            if request.b is None:
                raise HTTPException(status_code=400, detail="Operation 'divide' requires both 'a' and 'b'")
            if request.b == 0:
                raise HTTPException(status_code=400, detail="Cannot divide by zero")
            result = request.a / request.b
            inputs = {"a": request.a, "b": request.b}

        elif request.operation == "power":
            if request.b is None:
                raise HTTPException(status_code=400, detail="Operation 'power' requires both 'a' and 'b'")
            result = request.a ** request.b
            inputs = {"a": request.a, "b": request.b}

        elif request.operation == "sqrt":
            if request.a < 0:
                raise HTTPException(status_code=400, detail="Cannot take square root of negative number")
            result = math.sqrt(request.a)
            inputs = {"a": request.a}

        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported operation: {request.operation}. Supported: add, subtract, multiply, divide, power, sqrt"
            )

        return CalculationResponse(
            operation=request.operation,
            inputs=inputs,
            result=result,
            timestamp=datetime.now(timezone.utc).isoformat()
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Calculation error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Deploy the FastAPI app using Modal's ASGI app decorator
@app.function()
@modal.asgi_app()
def fastapi_app():
    return web_app

# Keep the original function for backward compatibility and local testing
@app.function()
def square(x):
    print("This code is running on a remote worker!")
    return x**2

@app.local_entrypoint()
def main():
    print("the square is", square.remote(42))
