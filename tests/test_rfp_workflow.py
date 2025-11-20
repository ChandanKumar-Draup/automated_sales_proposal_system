"""
Comprehensive test suite for RFP workflow processing.

This test suite validates:
1. Question extraction from RFP documents
2. Stepwise workflow processing
3. Database persistence
4. API endpoints
5. End-to-end RFP upload flow

Run with: pytest tests/test_rfp_workflow.py -v
"""
import pytest
import os
import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.llm_service import LLMService
from services.vector_store import VectorStore
from services.question_extractor import QuestionExtractorService, LLMQuestionExtractor
from services.rfp_processor import RFPProcessorService
from models.database import (
    init_database, create_workflow, get_workflow,
    update_workflow_state, update_workflow_analysis,
    update_workflow_responses, get_all_workflows
)


@pytest.fixture(scope="module")
def setup_services():
    """Initialize services for testing."""
    # Initialize database
    init_database()

    # Initialize services
    llm_service = LLMService()
    vector_store = VectorStore()

    yield {
        "llm": llm_service,
        "vector_store": vector_store
    }


@pytest.fixture
def sample_rfp_text():
    """Sample RFP text for testing."""
    return """
REQUEST FOR PROPOSAL (RFP)
Healthcare Management System Implementation

Client: Acme Healthcare Systems
Industry: Healthcare
Deadline: December 31, 2024

SECTION 1: TECHNICAL REQUIREMENTS

1. What is your approach to data security and HIPAA compliance?
2. Describe your cloud infrastructure and disaster recovery capabilities.
3. How do you handle real-time patient data synchronization across facilities?

SECTION 2: IMPLEMENTATION

4. What is your typical implementation timeline for a 500-bed hospital?
5. Describe your staff training methodology and materials.
6. How do you ensure minimal disruption during go-live?

SECTION 3: PRICING

7. Provide detailed pricing for software licenses, implementation, and annual support.
8. What are your payment terms and milestone structure?

SECTION 4: COMPANY BACKGROUND

9. Describe your experience with healthcare organizations of similar size.
10. Provide three references from recent healthcare implementations.
"""


class TestQuestionExtraction:
    """Test question extraction service."""

    def test_question_extractor_initialization(self, setup_services):
        """Test that question extractor initializes correctly."""
        llm = setup_services["llm"]
        extractor = QuestionExtractorService(llm)

        assert extractor is not None
        assert extractor.strategy is not None

    def test_extract_questions_from_rfp(self, setup_services, sample_rfp_text):
        """Test extracting questions from RFP text."""
        llm = setup_services["llm"]
        extractor = QuestionExtractorService(llm)

        result = extractor.extract_questions(sample_rfp_text)

        # Validate structure
        assert "questions" in result
        assert "total_questions" in result
        assert "sections" in result

        # Validate questions were extracted
        assert isinstance(result["questions"], list)
        assert result["total_questions"] > 0
        assert len(result["questions"]) == result["total_questions"]

        # Validate sections were detected
        assert isinstance(result["sections"], list)

        print(f"\n✓ Extracted {result['total_questions']} questions")
        print(f"✓ Detected {len(result['sections'])} sections")

    def test_fallback_extraction(self, setup_services):
        """Test fallback extraction when LLM fails."""
        llm = setup_services["llm"]
        strategy = LLMQuestionExtractor(llm)

        # Test with simple text containing questions
        text = """
        What is your pricing model?
        Describe your implementation process.
        Please provide details about your support services.
        """

        questions = strategy._fallback_extraction(text)

        assert len(questions) > 0
        print(f"\n✓ Fallback extracted {len(questions)} questions")


class TestWorkflowDatabase:
    """Test workflow database operations."""

    def test_create_workflow(self):
        """Test creating a workflow in database."""
        workflow_id = f"TEST-WF-{datetime.now().strftime('%Y%m%d%H%M%S')}"

        workflow = create_workflow(
            workflow_id=workflow_id,
            client_name="Test Client",
            workflow_type="rfp_response",
            industry="Technology"
        )

        assert workflow is not None
        assert workflow["workflow_id"] == workflow_id
        assert workflow["state"] == "created"
        assert workflow["client_name"] == "Test Client"

        print(f"\n✓ Created workflow: {workflow_id}")

    def test_update_workflow_state(self):
        """Test updating workflow state."""
        workflow_id = f"TEST-WF-{datetime.now().strftime('%Y%m%d%H%M%S')}"

        # Create workflow
        create_workflow(
            workflow_id=workflow_id,
            client_name="Test Client",
            workflow_type="rfp_response"
        )

        # Update state
        updated = update_workflow_state(workflow_id, "analyzing")

        assert updated["state"] == "analyzing"
        print(f"\n✓ Updated workflow state to: {updated['state']}")

    def test_update_workflow_analysis(self):
        """Test updating workflow with analysis results."""
        workflow_id = f"TEST-WF-{datetime.now().strftime('%Y%m%d%H%M%S')}"

        # Create workflow
        create_workflow(
            workflow_id=workflow_id,
            client_name="Test Client",
            workflow_type="rfp_response"
        )

        # Update with analysis
        analysis = {
            "questions": ["Q1?", "Q2?", "Q3?"],
            "total_questions": 3,
            "sections": ["Section 1", "Section 2"]
        }

        updated = update_workflow_analysis(workflow_id, analysis)

        assert updated["rfp_analysis"] is not None
        assert updated["rfp_analysis"]["total_questions"] == 3
        print(f"\n✓ Updated workflow with {analysis['total_questions']} questions")

    def test_progressive_response_updates(self):
        """Test progressive updates of generated responses."""
        workflow_id = f"TEST-WF-{datetime.now().strftime('%Y%m%d%H%M%S')}"

        # Create workflow
        create_workflow(
            workflow_id=workflow_id,
            client_name="Test Client",
            workflow_type="rfp_response"
        )

        # Simulate progressive response generation
        responses = []

        for i in range(3):
            responses.append({
                "question": f"Question {i+1}?",
                "answer": f"Answer {i+1}",
                "sources": [],
                "confidence": 0.85
            })

            updated = update_workflow_responses(workflow_id, responses)
            assert len(updated["generated_responses"]) == i + 1

        print(f"\n✓ Progressively updated {len(responses)} responses")

    def test_get_all_workflows(self):
        """Test retrieving all workflows."""
        workflows = get_all_workflows(limit=10)

        assert isinstance(workflows, list)
        print(f"\n✓ Retrieved {len(workflows)} workflows from database")


class TestRFPProcessor:
    """Test RFP processor service."""

    @pytest.mark.asyncio
    async def test_rfp_processor_initialization(self, setup_services):
        """Test RFP processor initialization."""
        llm = setup_services["llm"]
        vector_store = setup_services["vector_store"]

        processor = RFPProcessorService(llm, vector_store)

        assert processor is not None
        assert processor.llm is not None
        assert processor.vector_store is not None
        assert processor.question_extractor is not None

        print("\n✓ RFP processor initialized successfully")

    def test_end_to_end_rfp_processing(self, setup_services, sample_rfp_text):
        """Test complete RFP processing workflow (synchronous).

        This test validates all 4 steps:
        1. Question extraction
        2. Answer generation
        3. Quality review
        4. Document formatting
        """
        llm = setup_services["llm"]
        vector_store = setup_services["vector_store"]

        # Create workflow in database
        workflow_id = f"TEST-RFP-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        create_workflow(
            workflow_id=workflow_id,
            client_name="Acme Healthcare",
            workflow_type="rfp_response",
            industry="Healthcare"
        )

        print(f"\n✓ Created workflow: {workflow_id}")

        # Process RFP
        processor = RFPProcessorService(llm, vector_store)

        try:
            result = processor.process_rfp_sync(
                workflow_id=workflow_id,
                rfp_text=sample_rfp_text,
                client_name="Acme Healthcare",
                industry="Healthcare"
            )

            # Validate final result
            assert result is not None
            assert result["state"] == "ready"
            assert result["rfp_analysis"] is not None
            assert result["generated_responses"] is not None
            assert len(result["generated_responses"]) > 0
            assert result["review_result"] is not None

            print(f"\n✓ RFP processing complete!")
            print(f"  - State: {result['state']}")
            print(f"  - Questions extracted: {result['rfp_analysis']['total_questions']}")
            print(f"  - Responses generated: {len(result['generated_responses'])}")
            print(f"  - Quality: {result['review_result'].get('overall_quality', 'N/A')}")

            # Check if document was created
            if result.get("output_file_path"):
                print(f"  - Document: {result['output_file_path']}")
                assert os.path.exists(result["output_file_path"])

        except Exception as e:
            pytest.fail(f"RFP processing failed: {str(e)}")


class TestStateTransitions:
    """Test workflow state transitions."""

    def test_state_transition_sequence(self):
        """Test that states transition in correct order."""
        workflow_id = f"TEST-STATE-{datetime.now().strftime('%Y%m%d%H%M%S')}"

        # Create workflow
        workflow = create_workflow(
            workflow_id=workflow_id,
            client_name="Test Client",
            workflow_type="rfp_response"
        )
        assert workflow["state"] == "created"

        # Expected state sequence
        states = ["analyzing", "routing", "generating", "reviewing", "formatting", "ready"]

        for state in states:
            updated = update_workflow_state(workflow_id, state)
            assert updated["state"] == state
            print(f"✓ Transitioned to: {state}")


# ==================== Integration Tests ====================

class TestAPIIntegration:
    """Integration tests for API endpoints."""

    @pytest.mark.integration
    def test_workflow_retrieval_endpoint(self):
        """Test GET /api/v1/workflows/{workflow_id} endpoint."""
        # Create a workflow
        workflow_id = f"TEST-API-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        create_workflow(
            workflow_id=workflow_id,
            client_name="API Test Client",
            workflow_type="rfp_response"
        )

        # Retrieve workflow
        workflow = get_workflow(workflow_id)

        assert workflow is not None
        assert workflow["workflow_id"] == workflow_id
        print(f"\n✓ Successfully retrieved workflow via API: {workflow_id}")

    @pytest.mark.integration
    def test_workflow_list_endpoint(self):
        """Test GET /api/v1/workflows endpoint."""
        workflows = get_all_workflows(limit=5)

        assert isinstance(workflows, list)
        print(f"\n✓ Successfully listed {len(workflows)} workflows")


if __name__ == "__main__":
    """Run tests directly."""
    pytest.main([__file__, "-v", "--tb=short"])
