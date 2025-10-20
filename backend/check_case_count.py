"""
Quick script to check current case count in database
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pymongo import MongoClient
from app.core.config import settings

def check_cases():
    """Check current case count in MongoDB"""
    try:
        # Use settings from your config - or fallback to hardcoded MongoDB URI
        mongo_uri = settings.MONGODB_URL if settings.MONGODB_URL else "mongodb+srv://vignesharivumani37:Vignesharivumani1230@cluster0.w7x5vdv.mongodb.net/dcm_system?retryWrites=true&w=majority&tls=true&tlsAllowInvalidCertificates=true"
        db_name = settings.MONGODB_DATABASE if settings.MONGODB_DATABASE else "dcm_system"
        
        print("\n" + "=" * 60)
        print("📊 DATABASE CASE COUNT CHECK")
        print("=" * 60)
        print(f"\n🔌 Connecting to: {db_name}")
        
        client = MongoClient(mongo_uri)
        db = client[db_name]
        
        # Get case count
        total_cases = db.cases.count_documents({})
        
        print(f"\n✅ Connection successful!")
        print(f"\n📈 **Total Cases in Database: {total_cases}**\n")
        
        if total_cases > 0:
            # Get breakdown by case type
            print("🔹 Breakdown by Case Type:")
            for case_type in ["CRIMINAL", "CIVIL", "FAMILY", "COMMERCIAL", "CONSTITUTIONAL"]:
                count = db.cases.count_documents({"case_type": case_type})
                if count > 0:
                    print(f"   • {case_type}: {count}")
            
            # Get breakdown by priority
            print("\n🔹 Breakdown by Priority:")
            for priority in ["URGENT", "HIGH", "MEDIUM", "LOW"]:
                count = db.cases.count_documents({"priority": priority})
                if count > 0:
                    print(f"   • {priority}: {count}")
            
            # Get breakdown by status
            print("\n🔹 Breakdown by Status:")
            for status in ["FILED", "UNDER_REVIEW", "SCHEDULED", "HEARING", "DISPOSED"]:
                count = db.cases.count_documents({"status": status})
                if count > 0:
                    print(f"   • {status}: {count}")
        else:
            print("⚠️  No cases found in database!")
            print("\n💡 Run 'python create_large_dataset.py' to generate 100+ cases")
        
        print("\n" + "=" * 60)
        
        client.close()
        return total_cases
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return -1

if __name__ == "__main__":
    count = check_cases()
    print("\n")
