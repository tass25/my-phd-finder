import groq
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GROQ_API_KEY")
print(f"API Key found: {bool(api_key)}")

try:
    client = groq.Groq(api_key=api_key)
    print("Client initialized successfully")
except Exception as e:
    print(f"Initialization failed: {e}")
    import traceback
    traceback.print_exc()
