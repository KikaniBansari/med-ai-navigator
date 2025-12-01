import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import uvicorn
from media.api.main import app

if __name__ == "__main__":
    print("=" * 60)
    print("Starting MedAI Platform...")
    print("=" * 60)
    print(f"API Documentation: http://localhost:8000/docs")
    print(f"Health Check: http://localhost:8000/health")
    print("=" * 60)
    
    # Use import string for reload to work properly
    uvicorn.run(
        "media.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )