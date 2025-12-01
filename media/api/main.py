import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import Optional
from media.orchestrator import MedAIOrchestrator
from media.observability import metrics_service
from media.memory import memory_bank

app = FastAPI(
    title="MedAI Platform",
    version="1.0.0",
    description="End-to-End Healthcare AI Platform for Medical Triage"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Lazy initialization of orchestrator
_orchestrator = None

def get_orchestrator() -> MedAIOrchestrator:
    """Get or create orchestrator instance (lazy initialization)"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = MedAIOrchestrator()
    return _orchestrator


class QueryRequest(BaseModel):
    """Patient query request model"""
    patient_id: str = Field(..., description="Unique patient identifier")
    symptoms: str = Field(..., description="Patient symptom description")
    medical_record_text: str = Field(
        default="", 
        description="Optional medical document/EHR text content"
    )


class QueryResponse(BaseModel):
    """Response model for patient query"""
    success: bool
    session_id: str
    processing_time: float
    analysis: Optional[dict] = None
    error: Optional[str] = None


@app.get("/")
async def root():
    """Serve frontend or return API info"""
    frontend_path = Path(__file__).parent.parent.parent / "frontend" / "index.html"
    if frontend_path.exists():
        return FileResponse(str(frontend_path))
    return {
        "status": "MedAI System Operational",
        "version": "1.0.0",
        "endpoints": {
            "process": "/process",
            "history": "/history/{patient_id}",
            "observability": "/observability",
            "health": "/health"
        }
    }

# Serve static files (CSS, JS) - serve from frontend directory
frontend_dir = Path(__file__).parent.parent.parent / "frontend"
if frontend_dir.exists():
    # Serve CSS and JS files
    @app.get("/styles.css")
    async def serve_css():
        css_file = frontend_dir / "styles.css"
        if css_file.exists():
            return FileResponse(str(css_file), media_type="text/css")
        raise HTTPException(status_code=404)
    
    @app.get("/app.js")
    async def serve_js():
        js_file = frontend_dir / "app.js"
        if js_file.exists():
            return FileResponse(str(js_file), media_type="application/javascript")
        raise HTTPException(status_code=404)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "MedAI"}


@app.post("/process", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """
    Process patient query through multi-agent pipeline
    
    Args:
        request: QueryRequest with patient_id, symptoms, and optional medical_record_text
        
    Returns:
        QueryResponse with analysis results
    """
    try:
        if not request.symptoms or not request.symptoms.strip():
            raise HTTPException(
                status_code=400, 
                detail="Symptoms text is required"
            )
        
        orchestrator = get_orchestrator()
        result = await orchestrator.process_patient_query(
            request.patient_id,
            request.symptoms,
            request.medical_record_text
        )
        
        if not result.get("success", True):
            raise HTTPException(
                status_code=500,
                detail=result.get("error", "Processing failed")
            )
        
        return QueryResponse(
            success=True,
            session_id=result.get("session_id", ""),
            processing_time=result.get("processing_time", 0.0),
            analysis=result.get("analysis")
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/history/{patient_id}")
async def get_history(patient_id: str):
    """
    Get patient history from memory bank
    
    Args:
        patient_id: Patient identifier
        
    Returns:
        Patient facts stored in memory
    """
    try:
        facts = memory_bank.get_patient_facts(patient_id)
        return {
            "patient_id": patient_id,
            "stored_facts": facts,
            "fact_count": len(facts)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/observability")
async def get_metrics():
    """
    Get observability metrics and reports
    
    Returns:
        Metrics service report
    """
    try:
        return metrics_service.get_report()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))