# Groq API Setup Guide

## Getting Your Groq API Key

1. Visit [Groq Console](https://console.groq.com/keys)
2. Sign in or create an account
3. Click "Create API Key"
4. Copy the generated API key

## Configuration

Add your API key to the `.env` file:

```env
GROQ_API_KEY=your_api_key_here
```

## Available Models

The platform uses `llama-3.3-70b-versatile` by default. You can change this in `config.py`:

```python
MODEL_NAME = "llama-3.3-70b-versatile"  # Best performance
# or
MODEL_NAME = "llama-3.1-70b-versatile"  # Fallback
# or
MODEL_NAME = "llama-3.1-8b-instant"      # Faster
# or
MODEL_NAME = "mixtral-8x7b-32768"       # Alternative
```

## Model Options

- **llama-3.3-70b-versatile**: Best performance, most capable (default)
- **llama-3.1-70b-versatile**: Fallback option
- **llama-3.1-8b-instant**: Fast responses, good for quick queries
- **mixtral-8x7b-32768**: Alternative model with large context

## Usage

Once configured, the platform will automatically use Groq for all LLM operations:

- SymptomAgent: NLP parsing
- DocAgent: Document analysis
- RiskAgent: Risk assessment
- TriageAgent: Triage recommendations
- DiagnosisAgent: Diagnosis suggestions

## Rate Limits

Groq API has generous rate limits:
- Free tier: Very high limits
- Fast inference speeds

## Troubleshooting

### "GROQ_API_KEY environment variable is required"
- Ensure `.env` file exists in project root
- Verify `GROQ_API_KEY` is set correctly
- Restart your application after adding the key

### API Key Invalid
- Verify the key is copied correctly (no extra spaces)
- Check if the key is active in Groq Console
- Ensure you're using the correct API key format

### Model Not Found
- Verify the model name is correct
- Check Groq's available models: https://console.groq.com/docs/models
- Try using `llama-3.3-70b-versatile` as it's the default, or `llama-3.1-70b-versatile` as fallback

