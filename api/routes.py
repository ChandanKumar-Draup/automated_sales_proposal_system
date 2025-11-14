"""FastAPI routes for the sales proposal system."""
import os
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from datetime import datetime

from models.schemas import ProposalRequest, RFPUploadRequest, WorkflowStatus
from services.llm_service import LLMService
from services.vector_store import VectorStore
from services.document_processor import DocumentProcessor
from agents.orchestrator import OrchestratorAgent
from config import settings

# Initialize FastAPI app
app = FastAPI(
    title="Automated Sales Proposal System",
    description="AI-powered system for generating sales proposals and RFP responses",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services (singleton pattern)
llm_service = None
vector_store = None
orchestrator = None
doc_processor = DocumentProcessor()


def get_orchestrator() -> OrchestratorAgent:
    """Get or create orchestrator instance."""
    global llm_service, vector_store, orchestrator

    if orchestrator is None:
        # Initialize services
        llm_service = LLMService()
        vector_store = VectorStore()
        orchestrator = OrchestratorAgent(llm_service, vector_store)

    return orchestrator


# In-memory workflow storage (in production, use a database)
workflows = {}


@app.get("/")
def root():
    """Root endpoint."""
    return {
        "message": "Automated Sales Proposal System API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "quick_proposal": "/api/v1/proposals/quick",
            "upload_rfp": "/api/v1/rfp/upload",
            "workflow_status": "/api/v1/workflows/{workflow_id}",
            "download": "/api/v1/download/{workflow_id}",
        },
    }


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "llm": llm_service is not None,
            "vector_store": vector_store is not None,
            "orchestrator": orchestrator is not None,
        },
    }


@app.post("/api/v1/proposals/quick", response_model=WorkflowStatus)
async def create_quick_proposal(request: ProposalRequest):
    """
    Create a quick proposal for sales outreach.

    This is the fast-track pipeline for sales reps who need a proposal quickly.
    """
    try:
        orch = get_orchestrator()
        workflow = orch.create_quick_proposal(request)

        # Store workflow
        workflows[workflow.workflow_id] = workflow

        return workflow

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create proposal: {str(e)}")


@app.post("/api/v1/rfp/upload")
async def upload_rfp(
    file: UploadFile = File(...),
    client_name: str = "",
    industry: Optional[str] = None,
    background_tasks: BackgroundTasks = None,
):
    """
    Upload an RFP document for processing.

    Supports PDF, DOCX, and TXT formats.
    """
    try:
        # Validate file type
        allowed_extensions = [".pdf", ".docx", ".doc", ".txt"]
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400, detail=f"Unsupported file type. Allowed: {allowed_extensions}"
            )

        # Save uploaded file
        upload_path = os.path.join(
            settings.upload_dir, f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}"
        )
        with open(upload_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # Extract text from document
        rfp_text = doc_processor.extract_text(upload_path)

        # Create initial workflow
        workflow_id = f"WF-RFP-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        workflow = WorkflowStatus(
            workflow_id=workflow_id,
            state="created",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        workflows[workflow_id] = workflow

        # Process RFP in background
        if background_tasks:
            background_tasks.add_task(process_rfp_background, workflow_id, rfp_text, client_name, industry)
            return {
                "workflow_id": workflow_id,
                "status": "processing",
                "message": "RFP uploaded successfully. Processing in background.",
            }
        else:
            # Process synchronously (for testing)
            orch = get_orchestrator()
            workflow = orch.process_rfp(rfp_text, client_name, industry, workflow_id)
            workflows[workflow_id] = workflow
            return {"workflow_id": workflow_id, "status": workflow.state, "workflow": workflow}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process RFP: {str(e)}")


def process_rfp_background(workflow_id: str, rfp_text: str, client_name: str, industry: Optional[str]):
    """Background task to process RFP."""
    try:
        orch = get_orchestrator()
        workflow = orch.process_rfp(rfp_text, client_name, industry, workflow_id)
        workflows[workflow_id] = workflow
    except Exception as e:
        print(f"Error processing RFP in background: {e}")
        import traceback

        traceback.print_exc()


@app.get("/api/v1/workflows/{workflow_id}", response_model=WorkflowStatus)
def get_workflow_status(workflow_id: str):
    """Get the status of a workflow."""
    if workflow_id not in workflows:
        raise HTTPException(status_code=404, detail="Workflow not found")

    return workflows[workflow_id]


@app.get("/api/v1/download/{workflow_id}")
def download_proposal(workflow_id: str):
    """Download the generated proposal document."""
    if workflow_id not in workflows:
        raise HTTPException(status_code=404, detail="Workflow not found")

    workflow = workflows[workflow_id]

    if not workflow.output_file_path or not os.path.exists(workflow.output_file_path):
        raise HTTPException(status_code=404, detail="Output file not found")

    filename = os.path.basename(workflow.output_file_path)
    return FileResponse(
        workflow.output_file_path, media_type="application/octet-stream", filename=filename
    )


@app.post("/api/v1/knowledge/add")
async def add_knowledge(text: str, metadata: Optional[dict] = None):
    """
    Add content to the knowledge base (vector store).

    Use this to populate the system with past proposals, case studies, etc.
    """
    try:
        vs = get_orchestrator().vector_store
        vs.add_documents([text], [metadata] if metadata else None)
        vs.save()

        return {"status": "success", "message": "Content added to knowledge base"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add knowledge: {str(e)}")


@app.get("/api/v1/knowledge/search")
def search_knowledge(query: str, top_k: int = 5):
    """Search the knowledge base."""
    try:
        vs = get_orchestrator().vector_store
        results = vs.search(query, top_k=top_k)

        return {
            "query": query,
            "results": [{"text": doc, "score": score, "metadata": meta} for doc, score, meta in results],
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=settings.api_host, port=settings.api_port)
