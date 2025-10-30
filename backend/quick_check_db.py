"""Quick database check without starting server"""
from pymongo import MongoClient

mongo_uri = "mongodb+srv://vignesharivumani37:Vignesharivumani1230@cluster0.w7x5vdv.mongodb.net/dcm_system?retryWrites=true&w=majority&tls=true&tlsAllowInvalidCertificates=true"

print("\n" + "=" * 60)
print("📊 QUICK DATABASE CHECK")
print("=" * 60)

try:
    client = MongoClient(mongo_uri)
    db = client["dcm_system"]
    
    # Check cases
    total_cases = db.cases.count_documents({})
    print(f"\n✅ Total Cases: {total_cases}")
    
    if total_cases > 0:
        # Show some sample case data
        sample = db.cases.find_one()
        print(f"\n📋 Sample Case Fields:")
        if sample:
            for key in sample.keys():
                print(f"   • {key}: {type(sample[key]).__name__}")
    
    # Check users
    total_users = db.users.count_documents({})
    print(f"\n👥 Total Users: {total_users}")
    
    if total_users > 0:
        print("\n🔐 User Accounts:")
        users = db.users.find({}, {"username": 1, "role": 1, "_id": 0})
        for user in users:
            print(f"   • {user.get('username')} - {user.get('role')}")
    
    client.close()
    print("\n" + "=" * 60 + "\n")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
