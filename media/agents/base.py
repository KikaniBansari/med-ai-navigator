import os
from typing import Optional
from dotenv import load_dotenv
from langchain_groq import ChatGroq

# Ensure environment is loaded
load_dotenv()


class BaseAgent:
    """Base class for all MedAI agents"""
    
    def __init__(self, llm: Optional[ChatGroq] = None):
        """
        Initialize base agent with LLM
        
        Args:
            llm: Optional pre-configured LLM, otherwise creates new one
        """
        if llm is None:
            api_key = os.getenv("GROQ_API_KEY", "")
            if not api_key:
                raise ValueError(
                    "GROQ_API_KEY environment variable is required. "
                    "Please set it in your .env file or environment variables."
                )
            
            # Use model from config or environment variable
            from media.config import Config
            model_name = os.getenv("LLM_MODEL", Config.MODEL_NAME)
            
            # List of valid Groq models to try (in order of preference)
            valid_models = [
                model_name,  # Try config model first
                "llama-3.3-70b-versatile",  # Best performance
                # "llama-3.1-8b-instant",  # Fallback
                "llama-3.1-8b-instant",      # Fast
                "mixtral-8x7b-32768",        # Alternative
            ]
            
            # Try to initialize with the specified model
            self.llm = None
            last_error = None
            
            # Remove duplicates while preserving order
            models_to_try = []
            seen = set()
            for model in valid_models:
                if model not in seen:
                    models_to_try.append(model)
                    seen.add(model)
            
            for model in models_to_try:
                try:
                    self.llm = ChatGroq(
                        model=model,
                        groq_api_key=api_key,
                        temperature=0.1  # Low temp for medical accuracy
                    )
                    print(f"✓ Successfully initialized Groq model: {model}")
                    break
                except Exception as e:
                    last_error = e
                    # Only print error for first few attempts to avoid spam
                    if models_to_try.index(model) < 2:
                        print(f"✗ Model {model} failed: {str(e)[:100]}")
                    continue
            
            if self.llm is None:
                raise ValueError(
                    f"Could not initialize any Groq model. Last error: {str(last_error)[:200]}. "
                    f"Please check your GROQ_API_KEY and available models."
                )
        else:
            self.llm = llm