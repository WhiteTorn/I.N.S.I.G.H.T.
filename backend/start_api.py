#!/usr/bin/env python3
"""
INSIGHT Backend Startup Script
Starts the FastAPI server with Mark I Foundation Engine integration
"""

import uvicorn
import sys
import os
from dotenv import load_dotenv, find_dotenv

PORT = 8000

# Add the backend directory to the Python path
backend_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_path)

def start_server():
    """Start the INSIGHT API server"""
    # Ensure environment variables from the project root .env are loaded
    try:
        dotenv_path = find_dotenv()
        if dotenv_path:
            load_dotenv(dotenv_path=dotenv_path, override=False)
    except Exception:
        # Non-fatal if .env isn't present; connectors may load their own
        pass
    print("🚀 Starting INSIGHT Intelligence Platform API...")
    print("📡 Frontend URL: http://localhost:5173")
    print("🔧 Backend URL: http://localhost:8000")
    print("📋 API Docs: http://localhost:8000/docs")
    print("-" * 50)
    
    try:
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=PORT,
            reload=True,
            reload_dirs=[backend_path],
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 INSIGHT API server stopped")
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    start_server() 