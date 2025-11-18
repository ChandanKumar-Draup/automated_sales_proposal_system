"""Pydantic schemas for data validation."""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class QuestionCategory(str, Enum):
    """Question categories."""
    TECHNICAL = "technical"
    LEGAL = "legal"
    PRICING = "pricing"
    CASE_STUDY = "case_study"
    COMPANY_INFO = "company_info"


class Priority(str, Enum):
    """Priority levels."""
    MUST_HAVE = "must_have"
    SHOULD_HAVE = "should_have"
    NICE_TO_HAVE = "nice_to_have"


class WorkflowState(str, Enum):
    """Workflow states."""
    CREATED = "created"
    ANALYZING = "analyzing"
    ROUTING = "routing"
    GENERATING = "generating"
    REVIEWING = "reviewing"
    HUMAN_REVIEW = "human_review"
    FORMATTING = "formatting"
    READY = "ready"
    SUBMITTED = "submitted"
    CLOSED = "closed"


class Question(BaseModel):
    """Individual question from RFP."""
    q_id: str
    text: str
    category: QuestionCategory
    priority: Priority
    complexity: str = "medium"  # low, medium, high
    assigned_to: Optional[str] = None
    similar_past_questions: List[str] = Field(default_factory=list)


class RFPSection(BaseModel):
    """Section of an RFP."""
    section_id: str
    title: str
    category: QuestionCategory
    questions: List[Question] = Field(default_factory=list)


class ClientContext(BaseModel):
    """Client context information."""
    company_name: str
    industry: Optional[str] = None
    company_size: Optional[str] = None
    compliance_needs: List[str] = Field(default_factory=list)
    additional_context: Dict[str, Any] = Field(default_factory=dict)


class RFPAnalysis(BaseModel):
    """Analysis result from Analyzer Agent."""
    rfp_id: str
    client: ClientContext
    deadline: Optional[datetime] = None
    sections: List[RFPSection] = Field(default_factory=list)
    total_questions: int = 0
    estimated_effort_hours: float = 0
    risk_factors: List[str] = Field(default_factory=list)
    confidence: float = 0.0


class RetrievedContent(BaseModel):
    """Content retrieved by Retriever Agent."""
    source: str
    section: str
    text: str
    relevance_score: float
    reason: str
    last_used: Optional[datetime] = None
    win_outcome: Optional[bool] = None


class RetrievalResult(BaseModel):
    """Result from retrieval."""
    query: str
    client_context: ClientContext
    retrieved_content: List[RetrievedContent] = Field(default_factory=list)


class GeneratedResponse(BaseModel):
    """Generated response for a question."""
    question_id: str
    question_text: str
    draft_response: str
    personalization_elements: Dict[str, str] = Field(default_factory=dict)
    sources_used: List[str] = Field(default_factory=list)
    confidence: float = 0.0
    flags: List[str] = Field(default_factory=list)


class ReviewIssue(BaseModel):
    """Issue found during review."""
    severity: str  # warning, error
    location: str
    issue: str
    suggestion: Optional[str] = None


class ReviewResult(BaseModel):
    """Result from Reviewer Agent."""
    compliance_status: str  # PASS, FAIL, WARNING
    checks_performed: Dict[str, bool] = Field(default_factory=dict)
    issues_found: List[ReviewIssue] = Field(default_factory=list)
    confidence_breakdown: Dict[str, int] = Field(default_factory=dict)
    overall_readiness: str


class ProposalRequest(BaseModel):
    """Request to create a proposal."""
    company_name: str
    contact_title: Optional[str] = None
    industry: Optional[str] = None
    proposal_type: str = "pitch_deck"  # pitch_deck, rfp_response
    additional_context: Optional[str] = None


class RFPUploadRequest(BaseModel):
    """Request to upload and process RFP."""
    client_name: str
    deadline: Optional[datetime] = None
    industry: Optional[str] = None
    company_size: Optional[str] = None


class WorkflowStatus(BaseModel):
    """Status of a workflow."""
    workflow_id: str
    state: WorkflowState
    created_at: datetime
    updated_at: datetime
    rfp_analysis: Optional[RFPAnalysis] = None
    generated_responses: List[GeneratedResponse] = Field(default_factory=list)
    review_result: Optional[ReviewResult] = None
    output_file_path: Optional[str] = None


class QASource(BaseModel):
    """Source chunk used in Q&A response."""
    text: str
    score: float
    metadata: Dict[str, Any] = Field(default_factory=dict)


class QARequest(BaseModel):
    """Request for Q&A endpoint."""
    question: str
    top_k: int = 5
    include_sources: bool = True
    context: Optional[str] = None  # Optional additional context


class QAResponse(BaseModel):
    """Response from Q&A endpoint."""
    question: str
    answer: str
    sources: List[QASource] = Field(default_factory=list)
    confidence: float
    generated_at: datetime
    model_used: str = ""
