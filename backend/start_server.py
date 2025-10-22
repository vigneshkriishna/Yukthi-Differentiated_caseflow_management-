#!/usr/bin/env python3
"""
Startup script for the DCM System Backend
"""
import os
import subprocess
import sys

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def main():
    print("🏛️ Starting Smart DCM System Backend...")
    print(f"📂 Working Directory: {current_dir}")
    print(f"🐍 Python Version: {sys.version}")

    # Set environment variables
    os.environ['PYTHONPATH'] = current_dir

    try:
        # Import and run the application
        print("📦 Importing application modules...")
        from app.core.database import create_db_and_tables

        # Create database tables
        print("🗄️ Creating database tables...")
        create_db_and_tables()

        # Start the server
        print("🚀 Starting FastAPI server...")
        print("📋 API Documentation: http://localhost:8000/docs")
        print("🏥 Health Check: http://localhost:8000/health")
        print("👤 Login with demo accounts (password: demo123):")
        print("   • admin / admin")
        print("   • chief_judge / chief_judge")
        print("   • senior_clerk / senior_clerk")

        import uvicorn
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )

    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("📦 Installing missing packages...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("✅ Packages installed. Please run the script again.")

    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
