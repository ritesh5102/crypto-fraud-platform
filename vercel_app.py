"""
Vercel serverless entrypoint
"""
import sys
from pathlib import Path
from fastapi import FastAPI

# Add backend directory to Python path
backend_path = Path(__file__).parent / "backend"
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

# Import the FastAPI app
try:
    from main import app
except Exception as e:
    # Fallback app if import fails
    app = FastAPI()
    
    @app.get("/")
    async def error_endpoint():
        return {"error": str(e), "type": type(e).__name__, "message": "Backend import failed"}

# Vercel expects the app variable
__all__ = ["app"]
