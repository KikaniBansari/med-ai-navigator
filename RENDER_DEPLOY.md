# Render Deployment Guide

## MedAI Platform ని Render లో Deploy చేయడం

### Prerequisites
- GitHub repository లో code push చేయబడి ఉండాలి
- Render account (free tier available)
- Groq API key మరియు Serper API key

### Step 1: Render Account Setup

1. [Render.com](https://render.com) లో sign up చేయండి
2. GitHub account ని connect చేయండి

### Step 2: New Web Service Create చేయడం

1. Render dashboard లో **"New +"** button click చేయండి
2. **"Web Service"** select చేయండి
3. GitHub repository ని connect చేయండి:
   - Repository: `KikaniBansari/med-ai-navigator`
   - Branch: `main`

### Step 3: Service Configuration

#### Basic Settings:
- **Name**: `medai-platform` (or your preferred name)
- **Region**: Choose closest region (e.g., `Oregon (US West)`)
- **Branch**: `main`
- **Root Directory**: (leave empty - root directory)
- **Runtime**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python run_api.py`

#### Environment Variables:
Render dashboard లో **"Environment"** section లో add చేయండి:

```
GROQ_API_KEY=your_groq_api_key_here
SERPER_API_KEY=your_serper_api_key_here
LLM_MODEL=llama-3.3-70b-versatile
ENV=production
```

**Important**: 
- `GROQ_API_KEY` - [Groq Console](https://console.groq.com) నుండి get చేయండి
- `SERPER_API_KEY` - [Serper.dev](https://serper.dev) నుండి get చేయండి (web search కోసం)

### Step 4: Deploy

1. **"Create Web Service"** button click చేయండి
2. Build process start అవుతుంది (5-10 minutes పడవచ్చు)
3. Deployment complete అయిన తర్వాత, URL మీకు లభిస్తుంది

### Step 5: Verify Deployment

1. Health check: `https://your-app-name.onrender.com/health`
2. API docs: `https://your-app-name.onrender.com/docs`
3. Frontend: `https://your-app-name.onrender.com/`

**Frontend-Backend Connection**: 
- Frontend automatically connects to backend (same origin)
- No additional configuration needed
- See `FRONTEND_BACKEND_SETUP.md` for detailed information

### Alternative: Using render.yaml (Automated)

Repository లో `render.yaml` file ఉంది. Render dashboard లో:

1. **"New +"** → **"Blueprint"** select చేయండి
2. Repository connect చేయండి
3. Render automatically `render.yaml` read చేసి services create చేస్తుంది
4. Environment variables manually add చేయండి

### Troubleshooting

#### Build Fails:
- Check build logs లో errors
- Ensure all dependencies `requirements.txt` లో ఉన్నాయి
- Python version compatibility check చేయండి

#### Application Crashes:
- Check logs section లో runtime errors
- Verify environment variables correctly set చేయబడ్డాయి
- Health check endpoint working ఉందా verify చేయండి

#### Slow Response Times:
- Free tier లో cold starts ఉంటాయి (15-30 seconds)
- Paid plans లో better performance
- Health checks enable చేయండి to keep service warm

### Free Tier Limitations

- **Sleeps after 15 minutes** of inactivity
- **Cold starts** take 30-60 seconds
- **512 MB RAM** limit
- **100 GB bandwidth** per month

### Upgrading to Paid Plan

Better performance కోసం:
1. Dashboard లో service select చేయండి
2. **"Settings"** → **"Plan"** section
3. Paid plan select చేయండి

### Custom Domain (Optional)

1. Settings → **"Custom Domains"**
2. Your domain add చేయండి
3. DNS records configure చేయండి (Render instructions follow చేయండి)

### Monitoring

- **Logs**: Real-time logs dashboard లో available
- **Metrics**: CPU, Memory usage monitor చేయవచ్చు
- **Alerts**: Email alerts setup చేయవచ్చు

### Support

Issues ఉంటే:
- Render documentation: https://render.com/docs
- Render community: https://community.render.com

---

**Deployment URL**: After successful deployment, మీ app URL:
`https://medai-platform.onrender.com` (or your custom name)

**Note**: First deployment తర్వాత 2-3 minutes wait చేయండి for service to fully start.

