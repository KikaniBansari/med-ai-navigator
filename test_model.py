"""
Test script to check available Groq models
"""

import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

api_key = os.getenv("GROQ_API_KEY", "")
if not api_key:
    print("ERROR: GROQ_API_KEY not found")
    print("Get your key from: https://console.groq.com/keys")
    exit(1)

# Models to test
models_to_test = [
    "llama-3.3-70b-versatile",  # Default - best performance
    "llama-3.1-70b-versatile",  # Fallback
    "llama-3.1-8b-instant",      # Fast
    "mixtral-8x7b-32768",        # Alternative
]

print("Testing Groq models...")
print("=" * 60)

working_model = None

for model in models_to_test:
    try:
        print(f"\nTesting: {model}")
        llm = ChatGroq(
            model=model,
            groq_api_key=api_key,
            temperature=0.1
        )
        # Try a simple invocation
        result = llm.invoke("Say 'test' if you can hear me")
        print(f"✓ SUCCESS: {model} works!")
        print(f"  Response: {result.content[:50]}")
        working_model = model
        break
    except Exception as e:
        print(f"✗ FAILED: {str(e)[:150]}")

print("\n" + "=" * 60)
if working_model:
    print(f"\n✓ Recommended model: {working_model}")
    print(f"\nAdd to your .env file:")
    print(f"LLM_MODEL={working_model}")
else:
    print("\n✗ No working models found. Please check your API key.")

