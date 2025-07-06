import os
import sys
import uvicorn
from pathlib import Path

def main():
    #starts the backend server

    print("🚀 Starting AI Finance Agent Backend...")
    print("=" * 50)
    
    # Add backend directory to path
    backend_dir = Path(__file__).parent / "backend"
    sys.path.insert(0, str(backend_dir))
    
     # Start the server
    print("🌐 Starting FastAPI server...")
    print("📖 API documentation will be available at: http://localhost:8000/docs")
    print("🔍 Health check: http://localhost:8000/health")
    print()
    
    try:
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            reload_dirs=[str(backend_dir)],
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Failed to start server: {e}")

if __name__ == "__main__":
    main() 