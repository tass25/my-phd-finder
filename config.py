import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("agent_system.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("PhDFinder")

# API Keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    logger.warning("GROQ_API_KEY not found in .env file. AI features will be limited.")

# Database
DB_PATH = "database/phd_finder.db"

# User Data
DATA_DIR = "data"
CV_PATH = os.path.join(DATA_DIR, "cv.pdf")
TRANSCRIPT_PATH = os.path.join(DATA_DIR, "transcript.pdf")

# Ensure data dir exists
os.makedirs(DATA_DIR, exist_ok=True)

# Email Config
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS", "")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")

# LLM Settings
MODEL_NAME = "llama-3.3-70b-versatile"  # Updated to latest Llama 3.3

# Scraping Settings
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}
TIMEOUT = 15
max_retries = 3