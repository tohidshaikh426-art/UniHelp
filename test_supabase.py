# test_supabase.py
# Quick test to verify Supabase connection

from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

# Get credentials
url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_KEY')

print("🔍 Testing Supabase Connection...")
print(f"URL: {url}")
print(f"Key: {key[:20]}...")

try:
    # Create client
    supabase = create_client(url, key)
    
    # Test query - get all users
    response = supabase.table('user').select('*').limit(5).execute()
    
    print("\n✅ SUCCESS! Connected to Supabase!")
    print(f"\n📊 Found {len(response.data)} users:")
    
    for user in response.data:
        print(f"  - {user['name']} ({user['email']}) - {user['role']}")
    
    print("\n🎉 Supabase is working perfectly!")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    print("\n💡 Troubleshooting:")
    print("  1. Check SUPABASE_URL and SUPABASE_KEY in .env")
    print("  2. Make sure you ran the migration SQL")
    print("  3. Verify tables exist in Supabase Table Editor")
