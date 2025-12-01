"""
Quick script to check if environment is properly configured
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

print("=" * 60)
print("MedAI Environment Check")
print("=" * 60)

# Check GROQ_API_KEY
api_key = os.getenv("GROQ_API_KEY", "")
if api_key:
    print("✓ GROQ_API_KEY: Found")
    print(f"  Key preview: {api_key[:10]}...{api_key[-4:]}")
else:
    print("✗ GROQ_API_KEY: NOT FOUND")
    print("  Please create a .env file with:")
    print("  GROQ_API_KEY=your_api_key_here")
    print("  Get your key from: https://console.groq.com/keys")

# Check other optional variables
print("\nOptional Configuration:")
print(f"  LLM_MODEL: {os.getenv('LLM_MODEL', 'llama-3.3-70b-versatile')} (default)")
print(f"  ENABLE_TRACING: {os.getenv('ENABLE_TRACING', 'true')}")

print("\n" + "=" * 60)
if api_key:
    print("✓ Environment is ready!")
else:
    print("✗ Please configure GROQ_API_KEY before running the application")
print("=" * 60)
