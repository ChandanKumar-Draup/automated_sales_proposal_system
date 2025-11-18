"""Orchestrator Agent - Coordinates all other agents."""
import os
from typing import List, Optional
from datetime import datetime
from models.schemas import (
    WorkflowStatus,
    WorkflowState,
    RFPAnalysis,
    GeneratedResponse,
    Question,
    ProposalRequest,
    ClientContext,
)
from agents.analyzer import AnalyzerAgent
from agents.retriever import RetrieverAgent
from agents.generator import GeneratorAgent
from agents.reviewer import ReviewerAgent
from agents.formatter import FormatterAgent
from services.llm_service import LLMService
from services.vector_store import VectorStore
from models.database import save_document
from config import settings


class OrchestratorAgent:
    """Master orchestrator that coordinates all agents."""

    def __init__(self, llm_service: LLMService, vector_store: VectorStore):
        """Initialize the orchestrator."""
        self.llm = llm_service
        self.vector_store = vector_store

        # Initialize all agents
        self.analyzer = AnalyzerAgent(llm_service)
        self.retriever = RetrieverAgent(vector_store)
        self.generator = GeneratorAgent(llm_service)
        self.reviewer = ReviewerAgent()
        self.formatter = FormatterAgent()

        # Ensure output directories exist
        os.makedirs(settings.output_dir, exist_ok=True)
        os.makedirs(settings.upload_dir, exist_ok=True)

    def process_rfp(
        self,
        rfp_text: str,
        client_name: str,
        industry: Optional[str] = None,
        workflow_id: Optional[str] = None,
    ) -> WorkflowStatus:
        """Process an RFP end-to-end."""

        # Generate workflow ID
        if not workflow_id:
            workflow_id = f"WF-{datetime.now().strftime('%Y%m%d%H%M%S')}"

        print(f"[{workflow_id}] Starting RFP processing for {client_name}")

        # Initialize workflow status
        workflow = WorkflowStatus(
            workflow_id=workflow_id,
            state=WorkflowState.CREATED,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        try:
            # Step 1: Analyze RFP
            print(f"[{workflow_id}] State: ANALYZING")
            workflow.state = WorkflowState.ANALYZING
            workflow.updated_at = datetime.now()

            rfp_analysis = self.analyzer.analyze_rfp(rfp_text, client_name, industry)
            workflow.rfp_analysis = rfp_analysis

            print(
                f"[{workflow_id}] Analysis complete: {rfp_analysis.total_questions} questions identified"
            )

            # Step 2: Generate responses for each question
            print(f"[{workflow_id}] State: GENERATING")
            workflow.state = WorkflowState.GENERATING
            workflow.updated_at = datetime.now()

            generated_responses = []
            for section in rfp_analysis.sections:
                for question in section.questions:
                    print(f"[{workflow_id}] Generating response for {question.q_id}")

                    # Retrieve relevant content
                    retrieval_result = self.retriever.retrieve(
                        query=question.text, client_context=rfp_analysis.client, top_k=3
                    )

                    # Generate response
                    response = self.generator.generate_response(
                        question=question,
                        retrieval_result=retrieval_result,
                        client_context=rfp_analysis.client,
                    )

                    generated_responses.append(response)

            workflow.generated_responses = generated_responses
            print(f"[{workflow_id}] Generated {len(generated_responses)} responses")

            # Step 3: Review
            print(f"[{workflow_id}] State: REVIEWING")
            workflow.state = WorkflowState.REVIEWING
            workflow.updated_at = datetime.now()

            review_result = self.reviewer.review_responses(generated_responses, rfp_analysis)
            workflow.review_result = review_result

            print(
                f"[{workflow_id}] Review complete: {review_result.compliance_status}, "
                f"{review_result.confidence_breakdown['high_confidence']} high confidence, "
                f"{review_result.confidence_breakdown['low_confidence']} low confidence"
            )

            # Step 4: Check if human review needed
            if review_result.overall_readiness == "NEEDS_REVIEW":
                print(f"[{workflow_id}] State: HUMAN_REVIEW (requires manual review)")
                workflow.state = WorkflowState.HUMAN_REVIEW
                workflow.updated_at = datetime.now()
                return workflow

            # Step 5: Format
            print(f"[{workflow_id}] State: FORMATTING")
            workflow.state = WorkflowState.FORMATTING
            workflow.updated_at = datetime.now()

            output_filename = f"proposal_{client_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.docx"
            output_path = os.path.join(settings.output_dir, output_filename)

            formatted_file = self.formatter.format_rfp_response(
                responses=generated_responses,
                rfp_analysis=rfp_analysis,
                output_path=output_path,
                format_type="docx",
            )

            workflow.output_file_path = formatted_file
            print(f"[{workflow_id}] Formatted document: {formatted_file}")

            # Step 6: Ready
            print(f"[{workflow_id}] State: READY")
            workflow.state = WorkflowState.READY
            workflow.updated_at = datetime.now()

            return workflow

        except Exception as e:
            print(f"[{workflow_id}] Error: {str(e)}")
            import traceback

            traceback.print_exc()
            raise

    def create_quick_proposal(self, request: ProposalRequest) -> WorkflowStatus:
        """Create a quick proposal for sales outreach."""

        workflow_id = f"WF-QUICK-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        print(f"[{workflow_id}] Creating quick proposal for {request.client_name}")

        workflow = WorkflowStatus(
            workflow_id=workflow_id,
            state=WorkflowState.CREATED,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        try:
            # Step 1: Analyze client (quick version)
            print(f"[{workflow_id}] State: ANALYZING")
            workflow.state = WorkflowState.ANALYZING

            client_context = self.analyzer.quick_analyze(request.client_name, request.contact_title)
            if request.industry:
                client_context.industry = request.industry
            if request.requirements:
                client_context.additional_context["notes"] = request.requirements
            if request.tone:
                client_context.additional_context["tone"] = request.tone

            # Step 2: Generate proposal
            print(f"[{workflow_id}] State: GENERATING")
            workflow.state = WorkflowState.GENERATING

            proposal_content = self.generator.generate_quick_proposal(
                client_context=client_context, proposal_type=request.proposal_type
            )

            # Save document to database for editing
            save_document(
                workflow_id=workflow_id,
                title=f"Proposal for {request.client_name}",
                content=proposal_content,
                client_name=request.client_name,
                document_type="proposal"
            )
            print(f"[{workflow_id}] Document saved to database")

            # Store proposal content in workflow for UI display
            workflow.proposal_content = proposal_content

            # Step 3: Quick review
            print(f"[{workflow_id}] State: REVIEWING")
            workflow.state = WorkflowState.REVIEWING

            review = self.reviewer.quick_review(proposal_content)
            print(f"[{workflow_id}] Review: confidence={review['confidence']}, ready={review['ready']}")

            # Step 4: Format
            print(f"[{workflow_id}] State: FORMATTING")
            workflow.state = WorkflowState.FORMATTING

            output_filename = (
                f"quick_proposal_{request.client_name.replace(' ', '_')}"
                f"_{datetime.now().strftime('%Y%m%d')}.docx"
            )
            output_path = os.path.join(settings.output_dir, output_filename)

            formatted_file = self.formatter.format_quick_proposal(
                content=proposal_content,
                client_context=client_context,
                output_path=output_path,
                format_type="docx",
            )

            workflow.output_file_path = formatted_file

            # Step 5: Ready
            print(f"[{workflow_id}] State: READY")
            workflow.state = WorkflowState.READY
            workflow.updated_at = datetime.now()

            return workflow

        except Exception as e:
            print(f"[{workflow_id}] Error: {str(e)}")
            import traceback

            traceback.print_exc()
            raise
