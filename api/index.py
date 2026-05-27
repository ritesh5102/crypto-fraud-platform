"""
Vercel serverless entrypoint - imports from backend
"""
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

# Import the FastAPI app from backend/main.py
from main import app

# Export for Vercel
__all__ = ["app"]
