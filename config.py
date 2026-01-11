import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# Database
DB_PATH = "database/phd_finder.db"

# User Data
CV_PATH = "data/cv.pdf"
TRANSCRIPT_PATH = "data/transcript.pdf"

# Email Config (we'll set this up later)
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS", "")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")

# LLM Settings
MODEL_NAME = "llama-3.1-70b-versatile"  # Groq's fast model

# Scraping Settings
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}