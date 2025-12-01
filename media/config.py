import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY not found in .env file")
    
    # Groq models: llama-3.3-70b-versatile, mixtral-8x7b-32768, llama-3.1-8b-instant
    # Using llama-3.3-70b-versatile for best performance
    MODEL_NAME = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")
    
    ENABLE_TRACING = True
    MAX_HISTORY_LENGTH = 10