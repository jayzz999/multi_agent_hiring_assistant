"""FastAPI application for the Multi-Agent Hiring Assistant."""

# Load environment variables FIRST, before any other imports
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException, BackgroundTasks, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import asyncio
import json
import uuid
from datetime import datetime
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.orchestration.router import HiringOrchestrator
from src.orchestration.state import create_initial_state, validate_state
from src.rag.document_loader import DocumentLoader
from src.rag.vector_store import VectorStore
from src.tools.jd_parser import JDParserTool
from src.tools.resume_parser import ResumeParserTool
from src.evaluation.metrics import MetricsCollector
from src.evaluation.robustness import RobustnessTests
from src.evaluation.reporter import ReportGenerator

# Create FastAPI app
app = FastAPI(
    title="Multi-Agent Hiring Assistant API",
    description="AI-powered hiring workflow automation using multiple specialized agents",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for workflow jobs
workflow_jobs: Dict[str, Dict[str, Any]] = {}

# Lazy initialization of shared components
_orchestrator = None
_vector_store = None
_document_loader = None
_metrics_collector = None
_report_generator = None


def get_orchestrator():
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = HiringOrchestrator()
    return _orchestrator


def get_vector_store():
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStore()
    return _vector_store


def get_document_loader():
    global _document_loader
    if _document_loader is None:
        _document_loader = DocumentLoader()
    return _document_loader


def get_metrics_collector():
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    return _metrics_collector


def get_report_generator():
    global _report_generator
    if _report_generator is None:
        _report_generator = ReportGenerator()
    return _report_generator


# Request/Response Models
class HiringRequest(BaseModel):
    """Request model for starting a hiring workflow."""
    job_description: str = Field(..., min_length=50, description="The job description")
    num_candidates: int = Field(default=10, ge=1, le=100)
    num_to_interview: int = Field(default=3, ge=1, le=20)
    special_requirements: Optional[str] = None


class JobDescriptionParseRequest(BaseModel):
    """Request for parsing a job description."""
    job_description: str = Field(..., min_length=50)


class ResumeSearchRequest(BaseModel):
    """Request for searching resumes."""
    query: str = Field(..., min_length=3)
    doc_type: Optional[str] = "resume"
    top_k: int = Field(default=5, ge=1, le=20)


class WorkflowResponse(BaseModel):
    """Response model for workflow results."""
    job_id: str
    status: str
    message: str
    result: Optional[Dict[str, Any]] = None


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    timestamp: str
    components: Dict[str, str]


# API Endpoints
@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Multi-Agent Hiring Assistant API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Check API health and component status."""
    components = {
        "api": "healthy",
        "vector_store": "not initialized",
        "orchestrator": "not initialized"
    }

    try:
        # Check vector store (only if already initialized)
        if _vector_store is not None:
            count = _vector_store.get_document_count()
            components["vector_store"] = f"healthy ({count} documents)"
        else:
            components["vector_store"] = "ready (lazy load)"
    except Exception as e:
        components["vector_store"] = f"error: {str(e)[:50]}"

    try:
        # Check orchestrator
        if _orchestrator is not None:
            components["orchestrator"] = "healthy"
        else:
            components["orchestrator"] = "ready (lazy load)"
    except Exception as e:
        components["orchestrator"] = f"error: {str(e)[:50]}"

    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        components=components
    )


@app.post("/api/v1/workflow/start", response_model=WorkflowResponse)
async def start_workflow(
    request: HiringRequest,
    background_tasks: BackgroundTasks
):
    """
    Start a new hiring workflow.

    This initiates the multi-agent hiring process including:
    - Planning
    - Resume screening
    - Skill matching
    - Candidate ranking
    - Quality critique
    """
    # Generate job ID
    job_id = str(uuid.uuid4())[:8]

    # Validate request
    state = create_initial_state(
        job_description=request.job_description,
        num_candidates=request.num_candidates,
        num_to_interview=request.num_to_interview,
        special_requirements=request.special_requirements
    )

    errors = validate_state(state)
    if errors:
        raise HTTPException(status_code=400, detail="; ".join(errors))

    # Initialize job tracking
    workflow_jobs[job_id] = {
        "status": "running",
        "started_at": datetime.now().isoformat(),
        "request": request.model_dump(),
        "result": None,
        "error": None
    }

    # Run workflow in background
    background_tasks.add_task(
        run_workflow_background,
        job_id,
        request.job_description,
        request.num_candidates,
        request.num_to_interview,
        request.special_requirements
    )

    return WorkflowResponse(
        job_id=job_id,
        status="running",
        message="Workflow started. Use /api/v1/workflow/status/{job_id} to check progress."
    )


async def run_workflow_background(
    job_id: str,
    job_description: str,
    num_candidates: int,
    num_to_interview: int,
    special_requirements: Optional[str]
):
    """Run the workflow in the background."""
    try:
        result = get_orchestrator().run(
            job_description=job_description,
            num_candidates=num_candidates,
            num_to_interview=num_to_interview,
            special_requirements=special_requirements
        )

        workflow_jobs[job_id]["status"] = "completed" if result.get("success") else "failed"
        workflow_jobs[job_id]["result"] = result
        workflow_jobs[job_id]["completed_at"] = datetime.now().isoformat()

    except Exception as e:
        workflow_jobs[job_id]["status"] = "error"
        workflow_jobs[job_id]["error"] = str(e)
        workflow_jobs[job_id]["completed_at"] = datetime.now().isoformat()


@app.get("/api/v1/workflow/status/{job_id}", response_model=WorkflowResponse)
async def get_workflow_status(job_id: str):
    """Get the status of a workflow job."""
    if job_id not in workflow_jobs:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    job = workflow_jobs[job_id]

    return WorkflowResponse(
        job_id=job_id,
        status=job["status"],
        message=f"Workflow {job['status']}",
        result=job.get("result")
    )


@app.post("/api/v1/workflow/run-sync")
async def run_workflow_sync(request: HiringRequest):
    """
    Run a hiring workflow synchronously.

    Warning: This may take several minutes. Use /workflow/start for async execution.
    """
    try:
        result = get_orchestrator().run(
            job_description=request.job_description,
            num_candidates=request.num_candidates,
            num_to_interview=request.num_to_interview,
            special_requirements=request.special_requirements
        )

        return {
            "success": result.get("success", False),
            "result": result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/workflow/stream/{job_id}")
async def stream_workflow(job_id: str):
    """Stream workflow updates using Server-Sent Events."""

    async def event_generator():
        while True:
            if job_id not in workflow_jobs:
                yield f"data: {json.dumps({'error': 'Job not found'})}\n\n"
                break

            job = workflow_jobs[job_id]
            yield f"data: {json.dumps({'status': job['status']})}\n\n"

            if job["status"] in ["completed", "failed", "error"]:
                yield f"data: {json.dumps(job)}\n\n"
                break

            await asyncio.sleep(2)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )


@app.post("/api/v1/parse/job-description")
async def parse_job_description(request: JobDescriptionParseRequest):
    """Parse a job description to extract structured requirements."""
    parser = JDParserTool()

    try:
        result = parser._run(request.job_description)
        return json.loads(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    doc_type: str = Form(default="resume")
):
    """Upload a resume or job description document."""
    # Save uploaded file temporarily
    temp_dir = "./data/uploads"
    os.makedirs(temp_dir, exist_ok=True)

    file_path = os.path.join(temp_dir, file.filename)

    try:
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # Load and add to vector store
        documents = get_document_loader().load_document(
            file_path,
            metadata={"type": doc_type}
        )

        count = get_vector_store().add_documents(documents)

        return {
            "success": True,
            "filename": file.filename,
            "chunks_added": count,
            "doc_type": doc_type
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        # Clean up temp file
        if os.path.exists(file_path):
            os.remove(file_path)


@app.post("/api/v1/documents/search")
async def search_documents(request: ResumeSearchRequest):
    """Search for documents in the vector store."""
    try:
        filter_dict = {"type": request.doc_type} if request.doc_type else None

        results = get_vector_store().similarity_search_with_scores(
            query=request.query,
            k=request.top_k,
            filter_dict=filter_dict
        )

        return {
            "query": request.query,
            "count": len(results),
            "results": [
                {
                    "content": doc.page_content[:500],
                    "metadata": doc.metadata,
                    "score": score
                }
                for doc, score in results
            ]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/documents/stats")
async def get_document_stats():
    """Get vector store statistics."""
    try:
        vs = get_vector_store()
        count = vs.get_document_count()
        return {
            "total_documents": count,
            "collection_name": vs.collection_name
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/v1/documents/reset")
async def reset_documents():
    """Reset the vector store (delete all documents)."""
    try:
        get_vector_store().reset()
        return {"success": True, "message": "Vector store reset successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/tests/robustness")
async def run_robustness_tests():
    """Run robustness tests (without API calls)."""
    tests = RobustnessTests()
    results = tests.run_all_tests(skip_api_tests=True)
    summary = tests.get_summary()

    return {
        "summary": summary,
        "results": [r.to_dict() for r in results]
    }


@app.get("/api/v1/reports/generate/{job_id}")
async def generate_report(job_id: str):
    """Generate a detailed report for a completed workflow."""
    if job_id not in workflow_jobs:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    job = workflow_jobs[job_id]

    if job["status"] != "completed":
        raise HTTPException(status_code=400, detail="Workflow not completed")

    report = get_report_generator().generate_workflow_report(
        job.get("result", {}),
        include_details=True
    )

    return {
        "job_id": job_id,
        "report": report
    }


@app.get("/api/v1/jobs")
async def list_jobs():
    """List all workflow jobs."""
    return {
        "total": len(workflow_jobs),
        "jobs": [
            {
                "job_id": job_id,
                "status": job["status"],
                "started_at": job.get("started_at"),
                "completed_at": job.get("completed_at")
            }
            for job_id, job in workflow_jobs.items()
        ]
    }


@app.delete("/api/v1/jobs/{job_id}")
async def delete_job(job_id: str):
    """Delete a job from history."""
    if job_id not in workflow_jobs:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    del workflow_jobs[job_id]
    return {"success": True, "message": f"Job {job_id} deleted"}


# Run with: uvicorn api.main:app --reload --port 8000
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
