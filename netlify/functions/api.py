import sys
from pathlib import Path

# Add backend directory to path so internal imports work
backend_path = Path(__file__).resolve().parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from main import app
from mangum import Mangum

# Wrap the FastAPI application for Netlify Functions (AWS Lambda)
handler = Mangum(app, lifespan="on")
