from supabase import create_client
from dotenv import load_dotenv
import os

# Load .env
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Create Supabase client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

try:
    # Query your table
    response = supabase.table("ivf_chunks").select("*").limit(10).execute()  # limit to 10 rows for testing
    print("✅ Supabase connection successful")
    print(response.data)
except Exception as e:
    print("❌ Supabase connection failed")
    print(e)
