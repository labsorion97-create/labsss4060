"""
ORIONIS Backend Server
Main entry point that imports from the app module
"""
from app.main import app

# Re-export app for uvicorn
__all__ = ["app"]
