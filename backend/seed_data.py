#!/usr/bin/env python3
"""
Demo data seeding script for DCM System
"""
import sys
import os

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def main():
    print("🌱 Starting Demo Data Seeding...")
    
    try:
        # Import seeding module
        from scripts.seed_demo import main as seed_main
        
        # Run the seeding
        seed_main()
        
        print("✅ Demo data seeding completed!")
        print("🚀 You can now start the server with: python start_server.py")
        
    except Exception as e:
        print(f"❌ Error seeding data: {e}")
        print("📦 Make sure all packages are installed: pip install -r requirements.txt")
        sys.exit(1)

if __name__ == "__main__":
    main()
