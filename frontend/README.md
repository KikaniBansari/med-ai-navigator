# MedAI Frontend

Beautiful, modern web interface for the MedAI Healthcare AI Platform.

## Features

- 🎨 Modern, responsive design
- 🚀 Real-time patient assessment
- 📊 Comprehensive results display
- 📝 Patient history tracking
- 📈 System metrics dashboard
- ⚡ Fast and intuitive user experience

## Setup

### Option 1: Simple File Server

1. Make sure the MedAI API is running on `http://localhost:8000`
2. Open `index.html` in a web browser
3. Or use a simple HTTP server:

```bash
# Python 3
cd frontend
python -m http.server 8080

# Then open http://localhost:8080 in your browser
```

### Option 2: Serve with FastAPI (Recommended)

Add this to your `media/api/main.py`:

```python
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Add before app definition
app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/")
async def serve_frontend():
    return FileResponse("frontend/index.html")
```

Then access at `http://localhost:8000`

## Usage

1. **Enter Patient Information:**
   - Patient ID (e.g., P12345)
   - Symptoms description
   - Optional medical record text

2. **Click "Analyze Patient"** to process

3. **View Results:**
   - Symptoms analysis
   - Medical history extraction
   - Risk assessment with visual score
   - Triage recommendation

4. **Additional Features:**
   - View patient history
   - Check system metrics

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)

## Customization

Edit `styles.css` to customize colors, fonts, and layout.

The design uses CSS variables for easy theming:

```css
:root {
    --primary-color: #2563eb;
    --secondary-color: #10b981;
    /* ... */
}
```

