"""FastAPI routes for the sales proposal system."""
import os
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from datetime import datetime

from models.schemas import ProposalRequest, RFPUploadRequest, WorkflowStatus, QARequest, QAResponse
from models.database import (
    init_database, save_document, get_document, get_all_documents,
    get_default_user, get_all_users, get_user_by_id,
    create_workflow, get_workflow, get_all_workflows, update_workflow_state
)
from services.llm_service import LLMService
from services.vector_store import VectorStore
from services.document_processor import DocumentProcessor
from services.rfp_processor import RFPProcessorService
from agents.orchestrator import OrchestratorAgent
from agents.qa_agent import QAAgent
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
qa_agent = None
rfp_processor = None
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


def get_qa_agent() -> QAAgent:
    """Get or create QA agent instance."""
    global llm_service, vector_store, qa_agent

    if qa_agent is None:
        # Initialize services if not already done
        if llm_service is None:
            get_orchestrator()  # This will initialize llm_service and vector_store
        qa_agent = QAAgent(llm_service, vector_store)

    return qa_agent


def get_rfp_processor() -> RFPProcessorService:
    """Get or create RFP processor instance."""
    global llm_service, vector_store, rfp_processor

    if rfp_processor is None:
        # Initialize services if not already done
        if llm_service is None:
            get_orchestrator()  # This will initialize llm_service and vector_store
        rfp_processor = RFPProcessorService(llm_service, vector_store)

    return rfp_processor


# Startup event to initialize database
@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    init_database()
    print("Database initialized successfully")


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
            "qa_ask": "/api/v1/qa/ask",
            "qa_batch": "/api/v1/qa/batch",
            "qa_suggestions": "/api/v1/qa/suggestions",
            "knowledge_search": "/api/v1/knowledge/search",
            "knowledge_add": "/api/v1/knowledge/add",
            "documents_list": "/api/v1/documents",
            "document_get": "/api/v1/documents/{workflow_id}",
            "document_update": "/api/v1/documents/{workflow_id}",
            "users_list": "/api/v1/users",
            "user_current": "/api/v1/users/current",
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
        # Generate workflow ID
        workflow_id = f"WF-QUICK-{datetime.now().strftime('%Y%m%d%H%M%S')}"

        # Create workflow in database
        create_workflow(
            workflow_id=workflow_id,
            client_name=request.client_name,
            workflow_type="quick_proposal",
            industry=request.industry
        )

        # Process using orchestrator (synchronous for quick proposals)
        orch = get_orchestrator()
        workflow = orch.create_quick_proposal(request)

        # Update workflow in database with results
        from models.database import update_workflow_final
        update_workflow_final(
            workflow_id=workflow_id,
            output_file_path=workflow.output_file_path,
            proposal_content=workflow.proposal_content,
            state=workflow.state
        )

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
    Processes the RFP through 4 steps with state updates:
      1. analyzing - Extract questions
      2. generating - Generate answers
      3. reviewing - Quality review
      4. ready - Format document
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

        # Create workflow in database
        workflow_id = f"WF-RFP-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        create_workflow(
            workflow_id=workflow_id,
            client_name=client_name,
            workflow_type="rfp_response",
            industry=industry,
            file_path=upload_path
        )

        # Process RFP in background
        if background_tasks:
            background_tasks.add_task(
                process_rfp_background,
                workflow_id,
                rfp_text,
                client_name,
                industry
            )
            return {
                "workflow_id": workflow_id,
                "status": "processing",
                "message": "RFP uploaded successfully. Processing in background.",
            }
        else:
            # Process synchronously (for testing)
            processor = get_rfp_processor()
            result = processor.process_rfp_sync(workflow_id, rfp_text, client_name, industry)
            return {
                "workflow_id": workflow_id,
                "status": result.get("state", "ready"),
                "workflow": result
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process RFP: {str(e)}")


def process_rfp_background(workflow_id: str, rfp_text: str, client_name: str, industry: Optional[str]):
    """Background task to process RFP using new stepwise processor."""
    try:
        processor = get_rfp_processor()
        processor.process_rfp_sync(workflow_id, rfp_text, client_name, industry)
    except Exception as e:
        print(f"Error processing RFP in background: {e}")
        import traceback
        traceback.print_exc()
        # Update workflow to error state
        try:
            update_workflow_state(workflow_id, "error")
        except:
            pass


@app.get("/api/v1/workflows/{workflow_id}")
def get_workflow_status(workflow_id: str):
    """Get the status of a workflow from database.

    Returns workflow with progressive updates:
    - State transitions through: created → analyzing → routing → generating → reviewing → formatting → ready
    - rfp_analysis available after 'analyzing' state
    - generated_responses progressively populated during 'generating' state
    - review_result available after 'reviewing' state
    - output_file_path available when state is 'ready'
    """
    workflow = get_workflow(workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    return workflow


@app.get("/api/v1/workflows")
def list_workflows(limit: int = 50):
    """List all workflows, most recent first."""
    try:
        workflows = get_all_workflows(limit=limit)
        return {
            "count": len(workflows),
            "workflows": workflows
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list workflows: {str(e)}")


@app.get("/api/v1/download/{workflow_id}")
def download_proposal(workflow_id: str):
    """Download the generated proposal document."""
    workflow = get_workflow(workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    output_file_path = workflow.get("output_file_path")
    if not output_file_path or not os.path.exists(output_file_path):
        raise HTTPException(status_code=404, detail="Output file not found")

    # Generate appropriate filename
    client_name = workflow.get("client_name", "Client").replace(" ", "_")
    timestamp = datetime.now().strftime("%Y%m%d")
    workflow_type = workflow.get("workflow_type", "document")

    if workflow_type == "rfp_response":
        filename = f"RFP_Response_{client_name}_{timestamp}.docx"
    else:
        filename = f"Proposal_{client_name}_{timestamp}.docx"

    return FileResponse(
        output_file_path,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=filename
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


# ==================== Q&A Endpoints ====================

@app.post("/api/v1/qa/ask", response_model=QAResponse)
async def ask_question(request: QARequest):
    """
    Ask a question and get an AI-generated answer with sources.

    This endpoint uses RAG (Retrieval Augmented Generation) to:
    1. Search the knowledge base for relevant content
    2. Generate a comprehensive answer using the LLM
    3. Return the answer with source citations and confidence score

    Use this for any questions the sales team or anyone needs answered.
    """
    try:
        agent = get_qa_agent()
        response = agent.ask(
            question=request.question,
            top_k=request.top_k,
            include_sources=request.include_sources,
            context=request.context
        )
        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to answer question: {str(e)}")


@app.get("/api/v1/qa/ask")
async def ask_question_get(
    question: str,
    top_k: int = 5,
    include_sources: bool = True,
    context: Optional[str] = None
):
    """
    GET version of the Q&A endpoint for simple queries.

    Same as POST /api/v1/qa/ask but accepts query parameters.
    """
    try:
        agent = get_qa_agent()
        response = agent.ask(
            question=question,
            top_k=top_k,
            include_sources=include_sources,
            context=context
        )
        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to answer question: {str(e)}")


@app.post("/api/v1/qa/batch")
async def batch_ask_questions(questions: list[str], top_k: int = 5, include_sources: bool = True):
    """
    Answer multiple questions at once.

    Useful for processing a list of FAQ questions or RFP questions.
    """
    try:
        agent = get_qa_agent()
        responses = agent.batch_ask(
            questions=questions,
            top_k=top_k,
            include_sources=include_sources
        )
        return {
            "count": len(responses),
            "responses": responses
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process batch questions: {str(e)}")


@app.get("/api/v1/qa/suggestions")
async def get_suggested_questions(topic: Optional[str] = None):
    """
    Get suggested questions based on the knowledge base.

    Optionally provide a topic to get topic-specific suggestions.
    """
    try:
        agent = get_qa_agent()
        suggestions = agent.get_suggested_questions(topic)
        return {
            "topic": topic,
            "suggestions": suggestions
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get suggestions: {str(e)}")


# ==================== Document Editing Endpoints ====================

@app.get("/api/v1/documents")
async def list_documents(limit: int = 50):
    """
    List all editable documents.

    Returns documents sorted by most recently updated.
    """
    try:
        documents = get_all_documents(limit=limit)
        return {
            "count": len(documents),
            "documents": documents
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list documents: {str(e)}")


@app.get("/api/v1/documents/{workflow_id}")
async def get_document_content(workflow_id: str):
    """
    Get a specific document by workflow ID.
    """
    try:
        document = get_document(workflow_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        return document
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get document: {str(e)}")


@app.put("/api/v1/documents/{workflow_id}")
async def update_document(workflow_id: str, title: str, content: str, user_id: Optional[int] = None):
    """
    Update/save a document with user tracking.

    If user_id is not provided, uses the default user.
    """
    try:
        # Use default user if not specified
        if user_id is None:
            default_user = get_default_user()
            if default_user:
                user_id = default_user.id

        # Get existing document to preserve client_name
        existing = get_document(workflow_id)
        client_name = existing.get("client_name") if existing else None
        document_type = existing.get("document_type", "proposal") if existing else "proposal"

        document = save_document(
            workflow_id=workflow_id,
            title=title,
            content=content,
            client_name=client_name,
            document_type=document_type,
            user_id=user_id
        )

        return {
            "status": "success",
            "message": "Document saved successfully",
            "document": document
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save document: {str(e)}")


@app.post("/api/v1/documents")
async def create_document(
    workflow_id: str,
    title: str,
    content: str,
    client_name: Optional[str] = None,
    document_type: str = "proposal"
):
    """
    Create a new editable document.
    """
    try:
        # Check if document already exists
        existing = get_document(workflow_id)
        if existing:
            raise HTTPException(status_code=400, detail="Document with this workflow_id already exists")

        document = save_document(
            workflow_id=workflow_id,
            title=title,
            content=content,
            client_name=client_name,
            document_type=document_type
        )

        return {
            "status": "success",
            "message": "Document created successfully",
            "document": document
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create document: {str(e)}")


@app.get("/api/v1/users")
async def list_users():
    """
    List all active users.
    """
    try:
        users = get_all_users()
        return {
            "count": len(users),
            "users": users
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list users: {str(e)}")


@app.get("/api/v1/users/current")
async def get_current_user():
    """
    Get the current (default) user.
    """
    try:
        user = get_default_user()
        if not user:
            raise HTTPException(status_code=404, detail="No default user found")
        return user.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get current user: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=settings.api_host, port=settings.api_port)
