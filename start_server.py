#!/usr/bin/env python3
"""
Startup script for the Antonio Silván Chatbot API
"""

import uvicorn
import os
from app import app

if __name__ == "__main__":
    # Get port from Railway environment variable or default to 8000
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    # Disable reload in production
    reload = os.getenv("ENVIRONMENT", "production") != "production"
    
    print("Starting Antonio Silván Chatbot API...")
    print(f"Server will be available at: http://{host}:{port}")
    print(f"API Documentation: http://{host}:{port}/docs")
    print(f"Health Check: http://{host}:{port}/health")
    print(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
    print("\nPress Ctrl+C to stop the server")
    
    # Run the server
    uvicorn.run(
        app, 
        host=host, 
        port=port,
        reload=reload,
        log_level="info",
        access_log=True
    )
