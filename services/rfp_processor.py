"""RFP Processing Service - Handles stepwise RFP processing with database persistence.

This service follows SOLID principles:
- Single Responsibility: Only handles RFP workflow orchestration
- Open/Closed: Extensible for new processing steps
- Dependency Inversion: Depends on abstractions (services, not implementations)

State Machine:
    created → analyzing → routing → generating → reviewing → formatting → ready
"""
import asyncio
from typing import Optional, List, Dict, Any
from datetime import datetime

from services.llm_service import LLMService
from services.vector_store import VectorStore
from services.question_extractor import QuestionExtractorService
from agents.qa_agent import QAAgent
from agents.formatter import FormatterAgent
from models.database import (
    update_workflow_state,
    update_workflow_analysis,
    update_workflow_responses,
    update_workflow_review,
    update_workflow_final,
    get_workflow
)
from config import settings
import os


class RFPProcessorService:
    """Service for processing RFP documents through all workflow steps.

    This service implements a state machine that processes RFPs through
    4 distinct steps, updating the database at each step for frontend polling.
    """

    def __init__(self, llm_service: LLMService, vector_store: VectorStore):
        """Initialize the RFP processor.

        Args:
            llm_service: LLM service for AI operations
            vector_store: Vector store for knowledge retrieval
        """
        self.llm = llm_service
        self.vector_store = vector_store
        self.question_extractor = QuestionExtractorService(llm_service)
        self.qa_agent = QAAgent(llm_service, vector_store)
        self.formatter = FormatterAgent()

        # Ensure output directory exists
        os.makedirs(settings.output_dir, exist_ok=True)

    async def process_rfp_async(
        self,
        workflow_id: str,
        rfp_text: str,
        client_name: str,
        industry: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process RFP asynchronously through all steps.

        This is the main entry point for RFP processing. It orchestrates
        all steps and updates the workflow state progressively.

        Args:
            workflow_id: Unique workflow identifier
            rfp_text: Full text of the RFP document
            client_name: Name of the client
            industry: Optional industry classification

        Returns:
            Final workflow state dictionary
        """
        try:
            print(f"[{workflow_id}] Starting RFP processing for {client_name}")

            # === STEP 1: EXTRACT QUESTIONS ===
            await self._step_1_extract_questions(workflow_id, rfp_text)

            # === STEP 2: GENERATE ANSWERS ===
            await self._step_2_generate_answers(workflow_id, client_name, industry)

            # === STEP 3: QUALITY REVIEW ===
            await self._step_3_quality_review(workflow_id)

            # === STEP 4: FORMAT DOCUMENT ===
            await self._step_4_format_document(workflow_id, client_name)

            print(f"[{workflow_id}] RFP processing complete!")
            return get_workflow(workflow_id)

        except Exception as e:
            print(f"[{workflow_id}] Error during processing: {e}")
            import traceback
            traceback.print_exc()

            # Update workflow to error state
            try:
                update_workflow_state(workflow_id, "error")
            except:
                pass

            raise

    async def _step_1_extract_questions(self, workflow_id: str, rfp_text: str):
        """Step 1: Extract questions from RFP document.

        State: created → analyzing

        Args:
            workflow_id: Workflow identifier
            rfp_text: Full text of RFP document
        """
        print(f"[{workflow_id}] === STEP 1: EXTRACT QUESTIONS ===")

        # Update state to 'analyzing'
        update_workflow_state(workflow_id, "analyzing")

        # Extract questions using LLM
        rfp_analysis = self.question_extractor.extract_questions(rfp_text)

        print(f"[{workflow_id}] Extracted {rfp_analysis['total_questions']} questions")
        print(f"[{workflow_id}] Detected {len(rfp_analysis['sections'])} sections")

        # Save analysis to workflow
        update_workflow_analysis(workflow_id, rfp_analysis)

        # Small delay to make the state visible to frontend
        await asyncio.sleep(0.5)

    async def _step_2_generate_answers(
        self,
        workflow_id: str,
        client_name: str,
        industry: Optional[str]
    ):
        """Step 2: Generate answers for each question.

        State: analyzing → routing → generating

        Args:
            workflow_id: Workflow identifier
            client_name: Name of the client
            industry: Optional industry
        """
        print(f"[{workflow_id}] === STEP 2: GENERATE ANSWERS ===")

        # Get workflow to retrieve questions
        workflow = get_workflow(workflow_id)
        questions = workflow.get("rfp_analysis", {}).get("questions", [])

        if not questions:
            raise ValueError("No questions found in workflow analysis")

        # Update state to 'routing'
        update_workflow_state(workflow_id, "routing")
        await asyncio.sleep(0.5)

        # Update state to 'generating'
        update_workflow_state(workflow_id, "generating")

        # Generate answers progressively
        generated_responses = []

        for i, question in enumerate(questions):
            print(f"[{workflow_id}] Generating answer {i+1}/{len(questions)}: {question[:60]}...")

            try:
                # Generate answer using QA agent
                answer_result = self.qa_agent.ask(
                    question=question,
                    top_k=5,
                    include_sources=True,
                    context=f"Client: {client_name}, Industry: {industry or 'Not specified'}"
                )

                # Format response for storage
                response = {
                    "question": question,
                    "answer": answer_result.answer,
                    "sources": [
                        {
                            "text": source.text,
                            "score": source.score,
                            "metadata": source.metadata
                        }
                        for source in answer_result.sources
                    ],
                    "confidence": answer_result.confidence
                }

                generated_responses.append(response)

                # Progressive update - save after each answer
                update_workflow_responses(workflow_id, generated_responses)

                # Small delay between questions
                await asyncio.sleep(0.2)

            except Exception as e:
                print(f"[{workflow_id}] Error generating answer for question {i+1}: {e}")
                # Add error response
                response = {
                    "question": question,
                    "answer": "Unable to generate answer at this time. Please review manually.",
                    "sources": [],
                    "confidence": 0.0
                }
                generated_responses.append(response)
                update_workflow_responses(workflow_id, generated_responses)

        print(f"[{workflow_id}] Generated {len(generated_responses)} answers")

    async def _step_3_quality_review(self, workflow_id: str):
        """Step 3: Quality review of generated responses.

        State: generating → reviewing

        Args:
            workflow_id: Workflow identifier
        """
        print(f"[{workflow_id}] === STEP 3: QUALITY REVIEW ===")

        # Update state to 'reviewing'
        update_workflow_state(workflow_id, "reviewing")

        # Get workflow to retrieve responses
        workflow = get_workflow(workflow_id)
        responses = workflow.get("generated_responses", [])

        if not responses:
            raise ValueError("No responses found in workflow")

        # Perform quality review
        high_confidence = sum(1 for r in responses if r.get("confidence", 0) >= 0.8)
        medium_confidence = sum(1 for r in responses if 0.5 <= r.get("confidence", 0) < 0.8)
        low_confidence = sum(1 for r in responses if r.get("confidence", 0) < 0.5)

        # Calculate completeness
        completeness_score = (high_confidence * 1.0 + medium_confidence * 0.7 + low_confidence * 0.3) / len(responses)

        # Determine overall quality
        if completeness_score >= 0.8:
            overall_quality = "high"
        elif completeness_score >= 0.6:
            overall_quality = "medium"
        else:
            overall_quality = "low"

        review_result = {
            "overall_quality": overall_quality,
            "completeness_score": completeness_score,
            "high_confidence_count": high_confidence,
            "medium_confidence_count": medium_confidence,
            "low_confidence_count": low_confidence,
            "issues_found": [],
            "reviewed_at": datetime.utcnow().isoformat()
        }

        # Flag low confidence responses
        for i, response in enumerate(responses):
            if response.get("confidence", 0) < 0.5:
                review_result["issues_found"].append({
                    "question_index": i,
                    "question": response["question"],
                    "issue": "Low confidence answer - may need manual review",
                    "severity": "warning"
                })

        print(f"[{workflow_id}] Review complete: {overall_quality} quality, {completeness_score:.2f} completeness")

        # Save review result
        update_workflow_review(workflow_id, review_result)

        await asyncio.sleep(0.5)

    async def _step_4_format_document(self, workflow_id: str, client_name: str):
        """Step 4: Format final document.

        State: reviewing → formatting → ready

        Args:
            workflow_id: Workflow identifier
            client_name: Name of the client
        """
        print(f"[{workflow_id}] === STEP 4: FORMAT DOCUMENT ===")

        # Update state to 'formatting'
        update_workflow_state(workflow_id, "formatting")

        # Get workflow to retrieve all data
        workflow = get_workflow(workflow_id)
        questions = workflow.get("rfp_analysis", {}).get("questions", [])
        responses = workflow.get("generated_responses", [])

        # Generate output filename
        timestamp = datetime.now().strftime("%Y%m%d")
        client_slug = client_name.replace(" ", "_").replace("/", "_")
        output_filename = f"RFP_Response_{client_slug}_{timestamp}.docx"
        output_path = os.path.join(settings.output_dir, output_filename)

        # Format document
        try:
            formatted_file = self.formatter.format_rfp_response_from_qa(
                responses=responses,
                client_name=client_name,
                output_path=output_path
            )

            print(f"[{workflow_id}] Document formatted: {formatted_file}")

            # Update workflow to ready state with output file
            update_workflow_final(
                workflow_id=workflow_id,
                output_file_path=formatted_file,
                state="ready"
            )

        except Exception as e:
            print(f"[{workflow_id}] Error formatting document: {e}")
            # Still mark as ready but without file
            update_workflow_final(
                workflow_id=workflow_id,
                state="ready"
            )
            raise

        await asyncio.sleep(0.5)

    def process_rfp_sync(
        self,
        workflow_id: str,
        rfp_text: str,
        client_name: str,
        industry: Optional[str] = None
    ) -> Dict[str, Any]:
        """Synchronous wrapper for process_rfp_async.

        Args:
            workflow_id: Unique workflow identifier
            rfp_text: Full text of the RFP document
            client_name: Name of the client
            industry: Optional industry classification

        Returns:
            Final workflow state dictionary
        """
        # Run the async function in a new event loop
        return asyncio.run(
            self.process_rfp_async(workflow_id, rfp_text, client_name, industry)
        )
