"""Retriever Agent - Finds the best existing answer to any question."""
from typing import List, Optional, Dict, Any
from datetime import datetime
from models.schemas import RetrievedContent, RetrievalResult, ClientContext
from services.vector_store import VectorStore


class RetrieverAgent:
    """Agent responsible for retrieving relevant content from past proposals."""

    def __init__(self, vector_store: VectorStore):
        """Initialize the retriever agent."""
        self.vector_store = vector_store

    def retrieve(
        self, query: str, client_context: ClientContext, top_k: int = 5
    ) -> RetrievalResult:
        """Retrieve relevant content for a query."""

        # Build enriched query with context
        enriched_query = self._enrich_query(query, client_context)

        # Search in vector store
        results = self.vector_store.search(enriched_query, top_k=top_k)

        # Convert to RetrievedContent objects
        retrieved_content = []
        for doc, score, meta in results:
            content = RetrievedContent(
                source=meta.get("source", "Unknown"),
                section=meta.get("section", "General"),
                text=doc,
                relevance_score=score,
                reason=self._generate_reason(score, meta, client_context),
                last_used=meta.get("last_used"),
                win_outcome=meta.get("win_outcome"),
            )
            retrieved_content.append(content)

        # Re-rank based on metadata match
        retrieved_content = self._rerank(retrieved_content, client_context)

        return RetrievalResult(
            query=query, client_context=client_context, retrieved_content=retrieved_content[:top_k]
        )

    def _enrich_query(self, query: str, client_context: ClientContext) -> str:
        """Enrich query with client context."""
        context_parts = [query]

        if client_context.industry:
            context_parts.append(f"Industry: {client_context.industry}")

        if client_context.company_size:
            context_parts.append(f"Company size: {client_context.company_size}")

        if client_context.compliance_needs:
            context_parts.append(f"Compliance: {', '.join(client_context.compliance_needs)}")

        return " | ".join(context_parts)

    def _generate_reason(
        self, score: float, metadata: Dict[str, Any], client_context: ClientContext
    ) -> str:
        """Generate explanation for why this content was retrieved."""
        reasons = []

        if score > 0.9:
            reasons.append("Very high semantic similarity")
        elif score > 0.8:
            reasons.append("High semantic similarity")

        if metadata.get("industry") == client_context.industry:
            reasons.append("Same industry")

        if metadata.get("company_size") == client_context.company_size:
            reasons.append("Similar company size")

        if metadata.get("win_outcome"):
            reasons.append("From winning proposal")

        return ", ".join(reasons) if reasons else "Relevant content"

    def _rerank(
        self, content_list: List[RetrievedContent], client_context: ClientContext
    ) -> List[RetrievedContent]:
        """Re-rank results based on metadata match."""

        def calculate_final_score(content: RetrievedContent) -> float:
            score = content.relevance_score * 0.4  # Semantic similarity (40%)

            # Industry match (30%)
            # Note: We'd need to store industry in metadata for this to work
            # For now, we'll use a placeholder
            industry_match = 0.3

            # Recency (20%)
            recency_score = 0.2 if content.last_used else 0.1

            # Win rate (10%)
            win_score = 0.1 if content.win_outcome else 0.0

            return score + industry_match + recency_score + win_score

        # Sort by final score
        content_list.sort(key=calculate_final_score, reverse=True)
        return content_list
