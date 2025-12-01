# Frontend-Backend Connection Guide for Render

## Current Setup

మీ MedAI platform లో **frontend మరియు backend రెండూ same service లో run అవుతాయి**. FastAPI backend frontend files (HTML, CSS, JS) serve చేస్తుంది.

## How It Works

### Architecture:
```
┌─────────────────────────────────────┐
│     Render Web Service              │
│  ┌───────────────────────────────┐  │
│  │   FastAPI Backend             │  │
│  │   (Python)                    │  │
│  │                                │  │
│  │   - Serves / (index.html)     │  │
│  │   - Serves /styles.css        │  │
│  │   - Serves /app.js            │  │
│  │   - API: /process             │  │
│  │   - API: /health              │  │
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘
         │
         │ Same Origin
         ▼
    Frontend (app.js)
    Auto-detects API URL
```

## Automatic API URL Detection

Frontend (`frontend/app.js`) automatically detects environment:

```javascript
// Development: Uses localhost:8000
// Production (Render): Uses same origin (your-render-url.onrender.com)
const API_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:8000'
    : window.location.origin;
```

**This means**: 
- Local development: Frontend connects to `http://localhost:8000`
- Render deployment: Frontend automatically uses your Render URL (e.g., `https://medai-platform.onrender.com`)

## Deployment Steps

### Option 1: Single Service (Recommended - Current Setup)

మీ current setup లో frontend మరియు backend రెండూ same Render service లో run అవుతాయి.

#### Steps:

1. **Render లో Web Service Deploy చేయండి** (మీరు already చేసారు)
   - Repository: `KikaniBansari/med-ai-navigator`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python run_api.py`

2. **Environment Variables Set చేయండి**:
   ```
   GROQ_API_KEY=your_key
   SERPER_API_KEY=your_key
   LLM_MODEL=llama-3.3-70b-versatile
   ENV=production
   ```

3. **Deploy Complete అయిన తర్వాత**:
   - Frontend: `https://your-app.onrender.com/`
   - API: `https://your-app.onrender.com/process`
   - Health: `https://your-app.onrender.com/health`

4. **Frontend automatically connects** to backend (same origin)

### Option 2: Separate Frontend Service (Advanced)

Frontend ని separate static site గా deploy చేయాలనుకుంటే:

#### Frontend Service (Static Site):

1. **New Static Site** create చేయండి:
   - Repository: Same repo
   - Root Directory: `frontend`
   - Build Command: (empty - no build needed)
   - Publish Directory: `frontend`

2. **Frontend app.js Update**:
   ```javascript
   // Use environment variable or hardcode backend URL
   const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://your-backend.onrender.com';
   ```

3. **CORS Settings**:
   - Backend లో CORS already configured (`allow_origins=["*"]`)
   - Frontend service URL ని allow list లో add చేయండి (optional)

**Note**: Option 1 recommended - simpler మరియు cost-effective.

## Testing the Connection

### 1. Health Check:
```bash
curl https://your-app.onrender.com/health
```

Expected response:
```json
{"status": "healthy", "service": "MedAI"}
```

### 2. Frontend Test:
1. Browser లో open చేయండి: `https://your-app.onrender.com/`
2. Browser console open చేయండి (F12)
3. Check for errors
4. Form submit చేయండి
5. Network tab లో API calls verify చేయండి

### 3. API Direct Test:
```bash
curl -X POST https://your-app.onrender.com/process \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "TEST123",
    "symptoms": "headache and fever",
    "medical_record_text": ""
  }'
```

## Troubleshooting

### Issue: Frontend shows "Cannot connect to API"

**Solution**:
1. Check backend service running ఉందా
2. Health endpoint test చేయండి: `/health`
3. Browser console లో errors check చేయండి
4. Network tab లో failed requests check చేయండి

### Issue: CORS Errors

**Solution**:
- Backend లో CORS already configured
- If using separate frontend service, backend `main.py` లో:
  ```python
  allow_origins=["https://your-frontend.onrender.com"]
  ```

### Issue: 404 for CSS/JS files

**Solution**:
- Check `media/api/main.py` లో static file serving configured ఉందా
- Verify `frontend/` directory structure correct

### Issue: API returns 500 errors

**Solution**:
1. Render logs check చేయండి
2. Environment variables verify చేయండి
3. `GROQ_API_KEY` మరియు `SERPER_API_KEY` set చేయబడ్డాయి verify చేయండి

## Current File Structure

```
MedAI/
├── frontend/
│   ├── index.html      # Main HTML (served at /)
│   ├── styles.css      # Styles (served at /styles.css)
│   └── app.js          # Frontend JS (served at /app.js)
│                       # Auto-detects API URL
├── media/
│   └── api/
│       └── main.py     # FastAPI app
│                       # Serves frontend + API endpoints
└── run_api.py          # Entry point
```

## Quick Verification Checklist

After deployment, verify:

- [ ] Backend health check works: `/health`
- [ ] Frontend loads: `/`
- [ ] CSS loads: `/styles.css`
- [ ] JS loads: `/app.js`
- [ ] Browser console shows no errors
- [ ] Form submission works
- [ ] API returns responses
- [ ] Network tab shows successful API calls

## Example Render URLs

After deployment, మీ URLs:
- **Frontend**: `https://medai-platform.onrender.com/`
- **API Docs**: `https://medai-platform.onrender.com/docs`
- **Health**: `https://medai-platform.onrender.com/health`
- **API Endpoint**: `https://medai-platform.onrender.com/process`

All same origin, so no CORS issues!

## Summary

✅ **Current Setup**: Frontend మరియు backend same service లో run అవుతాయి  
✅ **Auto-detection**: Frontend automatically uses correct API URL  
✅ **No Configuration Needed**: Render deploy చేసిన తర్వాత automatically works  
✅ **Single Service**: Cost-effective మరియు simple  

మీ backend deploy చేసిన తర్వాత, frontend automatically connect అవుతుంది - no additional setup needed!

