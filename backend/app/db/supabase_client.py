import os
from supabase import create_client
from dotenv import load_dotenv

# 🔥 FORCE LOAD CORRECT .env PATH
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ENV_PATH = os.path.join(BASE_DIR, ".env")

load_dotenv(dotenv_path=ENV_PATH)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")



if not SUPABASE_URL or not SUPABASE_KEY:
    raise Exception("❌ Supabase env variables not loaded properly")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)