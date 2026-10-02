"""
DATA VERSE Launcher Script
Starts the FastAPI application and Virtual Quantum Computer platform.
"""
import sys
import os
import uvicorn

# Ensure repository root is on sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from backend.core.config import settings

def main():
    print(f"============================================================")
    print(f"  {settings.PROJECT_NAME} - Research Prototype (SIH26141)")
    print(f"  Quantum-Information Digital Signature Security & Threat Detection")
    print(f"============================================================")
    print(f"  API Docs : http://{settings.HOST}:{settings.PORT}/docs")
    print(f"  Web UI   : http://{settings.HOST}:{settings.PORT}/")
    print(f"============================================================")
    uvicorn.run("backend.api.app:app", host=settings.HOST, port=settings.PORT, reload=False)

if __name__ == "__main__":
    main()
