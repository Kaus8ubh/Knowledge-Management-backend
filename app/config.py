import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    MONGO_URI = os.getenv("MONGO_URI")
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
    SECRET_KEY = os.getenv("SECRET_KEY")
    OPEN_API_KEY = os.getenv("OPEN_API_KEY")
    OPEN_API_BASE = os.getenv("OPEN_API_BASE")
    HF_MODEL_ID = os.getenv("HF_MODEL_ID")
    HF_TOKEN = os.getenv("HF_TOKEN")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")