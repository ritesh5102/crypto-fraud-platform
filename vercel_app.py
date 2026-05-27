"""
Vercel serverless entrypoint
"""
import sys
from pathlib import Path

# Add backend directory to Python path
backend_path = Path(__file__).parent / "backend"
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

try:
    # Import the FastAPI app
    from main import app
except Exception as e:
    from fastapi import FastAPI
    app = FastAPI()
    
    @app.get("/")
    async def error_endpoint():
        return {"error": str(e), "type": type(e).__name__}

# Vercel expects the app variable
__all__ = ["app"]
