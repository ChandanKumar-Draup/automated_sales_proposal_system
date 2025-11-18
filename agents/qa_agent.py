"""QA Agent - Standalone question answering using RAG."""
from typing import List, Tuple, Dict, Any, Optional
from datetime import datetime

from models.schemas import QAResponse, QASource
from services.llm_service import LLMService
from services.vector_store import VectorStore


class QAAgent:
    """Agent responsible for answering questions using RAG (Retrieval Augmented Generation)."""

    def __init__(self, llm_service: LLMService, vector_store: VectorStore):
        """Initialize the QA agent."""
        self.llm = llm_service
        self.vector_store = vector_store

    def ask(
        self,
        question: str,
        top_k: int = 5,
        include_sources: bool = True,
        context: Optional[str] = None
    ) -> QAResponse:
        """
        Answer a question using RAG.

        Args:
            question: The question to answer
            top_k: Number of chunks to retrieve
            include_sources: Whether to include source chunks in response
            context: Optional additional context for the question

        Returns:
            QAResponse with answer, sources, and confidence
        """
        # Step 1: Retrieve relevant chunks
        search_results = self.vector_store.search(question, top_k=top_k)

        # Step 2: Generate answer using LLM
        answer, confidence = self._generate_answer(question, search_results, context)

        # Step 3: Build sources list
        sources = []
        if include_sources:
            sources = [
                QASource(
                    text=text,
                    score=score,
                    metadata=metadata
                )
                for text, score, metadata in search_results
            ]

        return QAResponse(
            question=question,
            answer=answer,
            sources=sources,
            confidence=confidence,
            generated_at=datetime.now(),
            model_used=self.llm.model
        )

    def _generate_answer(
        self,
        question: str,
        search_results: List[Tuple[str, float, Dict[str, Any]]],
        context: Optional[str] = None
    ) -> Tuple[str, float]:
        """
        Generate an answer using LLM based on retrieved chunks.

        Returns:
            Tuple of (answer_text, confidence_score)
        """
        # Handle case with no results
        if not search_results:
            return (
                "I don't have enough information in the knowledge base to answer this question. "
                "Please try rephrasing your question or add relevant content to the knowledge base.",
                0.0
            )

        # Build context from retrieved chunks
        context_text = self._build_context(search_results)

        # System prompt for Q&A
        system_prompt = """You are a helpful sales assistant with access to a knowledge base of proposals, case studies, and company information. Your job is to:

1. Answer questions accurately based ONLY on the provided context
2. Be clear and concise in your responses
3. If the context doesn't contain enough information to fully answer the question, say so clearly
4. Cite which sources you used by referencing their numbers (e.g., [Source 1], [Source 2])
5. If you need to make assumptions, state them clearly
6. Maintain a professional, helpful tone

IMPORTANT: Only use information from the provided context. Do not make up information."""

        # Build the prompt
        prompt = f"""Context from knowledge base:
{context_text}

"""
        if context:
            prompt += f"""Additional context provided:
{context}

"""

        prompt += f"""Question: {question}

Please provide a comprehensive answer based on the context above. Include source citations where relevant."""

        try:
            answer = self.llm.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.3,  # Lower temperature for more focused answers
                max_tokens=1500
            )

            # Calculate confidence based on search results quality
            confidence = self._calculate_confidence(search_results)

            return answer, confidence

        except Exception as e:
            print(f"Error generating answer: {e}")
            return (
                f"Sorry, I encountered an error while generating the answer: {str(e)}",
                0.0
            )

    def _build_context(self, search_results: List[Tuple[str, float, Dict[str, Any]]]) -> str:
        """Build context string from search results."""
        context_parts = []

        for i, (text, score, metadata) in enumerate(search_results, 1):
            # Build metadata info
            meta_info = []
            if metadata.get("source"):
                meta_info.append(f"Source: {metadata['source']}")
            if metadata.get("category"):
                meta_info.append(f"Category: {metadata['category']}")
            if metadata.get("industry"):
                meta_info.append(f"Industry: {metadata['industry']}")
            if metadata.get("date"):
                meta_info.append(f"Date: {metadata['date']}")

            meta_str = " | ".join(meta_info) if meta_info else "No metadata"

            context_parts.append(
                f"[Source {i}] (Relevance: {score:.2f})\n"
                f"Metadata: {meta_str}\n"
                f"Content:\n{text}\n"
            )

        return "\n---\n".join(context_parts)

    def _calculate_confidence(self, search_results: List[Tuple[str, float, Dict[str, Any]]]) -> float:
        """
        Calculate confidence score based on search results quality.

        Factors:
        - Number of results
        - Average relevance score
        - Highest relevance score
        """
        if not search_results:
            return 0.0

        scores = [score for _, score, _ in search_results]

        # Calculate metrics
        num_results = len(scores)
        avg_score = sum(scores) / num_results
        max_score = max(scores)

        # Weighted confidence calculation
        # - 40% weight on average score
        # - 40% weight on top score
        # - 20% weight on having multiple results
        result_coverage = min(num_results / 5, 1.0)  # Normalized to 5 results

        confidence = (
            0.4 * avg_score +
            0.4 * max_score +
            0.2 * result_coverage
        )

        return min(confidence, 1.0)  # Cap at 1.0

    def get_suggested_questions(self, topic: Optional[str] = None) -> List[str]:
        """
        Get suggested questions based on the knowledge base.

        Args:
            topic: Optional topic to focus suggestions on

        Returns:
            List of suggested questions
        """
        # Default suggested questions for common sales scenarios
        default_questions = [
            "What case studies do we have in the healthcare industry?",
            "What are our key differentiators compared to competitors?",
            "What security certifications and compliance standards do we meet?",
            "What is our typical implementation timeline?",
            "What pricing models do we offer?",
            "What ROI have our customers achieved?",
            "What integration capabilities do we have?",
            "What support and SLA options are available?",
        ]

        if topic:
            # If a topic is provided, search for related content and generate suggestions
            try:
                results = self.vector_store.search(topic, top_k=3)
                if results:
                    # Generate topic-specific suggestions
                    system_prompt = "Generate 5 relevant questions that a sales team might ask about the following topic and context."
                    context = "\n".join([text for text, _, _ in results])
                    prompt = f"Topic: {topic}\n\nContext:\n{context}\n\nGenerate 5 relevant questions:"

                    response = self.llm.generate(prompt, system_prompt, temperature=0.7)

                    # Parse questions from response
                    questions = []
                    for line in response.split("\n"):
                        line = line.strip()
                        if line and (line[0].isdigit() or line.startswith("-")):
                            # Remove numbering and bullets
                            question = line.lstrip("0123456789.-) ").strip()
                            if question and question.endswith("?"):
                                questions.append(question)

                    if questions:
                        return questions[:5]
            except Exception as e:
                print(f"Error generating suggested questions: {e}")

        return default_questions

    def batch_ask(
        self,
        questions: List[str],
        top_k: int = 5,
        include_sources: bool = True
    ) -> List[QAResponse]:
        """
        Answer multiple questions.

        Args:
            questions: List of questions to answer
            top_k: Number of chunks to retrieve per question
            include_sources: Whether to include source chunks in responses

        Returns:
            List of QAResponse objects
        """
        responses = []
        for question in questions:
            response = self.ask(question, top_k, include_sources)
            responses.append(response)
        return responses
