"""
Minimal FastAPI application for testing purposes.
This version uses minimal dependencies and doesn't require database connection.
"""

import sys
from datetime import datetime

# Simple FastAPI test without full dependencies
try:
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware

    app = FastAPI(
        title="AI Research Competitive Intelligence Platform",
        description="Testing Mode",
        version="0.1.0",
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/")
    async def root():
        """Root endpoint."""
        return {
            "message": "AI Research Competitive Intelligence Platform API",
            "version": "0.1.0",
            "status": "running",
            "timestamp": datetime.utcnow().isoformat(),
        }

    @app.get("/health")
    async def health():
        """Health check endpoint."""
        return {
            "status": "healthy",
            "version": "0.1.0",
            "environment": "development",
            "timestamp": datetime.utcnow().isoformat(),
        }

    @app.get("/test")
    async def test():
        """Test endpoint."""
        return {
            "message": "Test endpoint working",
            "components": {"fastapi": True, "cors": True, "routing": True},
        }

    if __name__ == "__main__":
        import uvicorn

        print("Starting minimal test server...")
        print("Access at: http://localhost:8000")
        print("Health check: http://localhost:8000/health")
        print("Press Ctrl+C to stop")

        uvicorn.run(app, host="0.0.0.0", port=8000)

except ImportError as e:
    print(f"Missing dependency: {e}")
    print("Please install: pip install fastapi uvicorn")
    sys.exit(1)
except Exception as e:
    print(f"Error starting server: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)
