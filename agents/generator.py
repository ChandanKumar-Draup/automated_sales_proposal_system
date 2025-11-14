"""Generator Agent - Creates customized content that sounds human-written."""
from typing import List, Optional
from models.schemas import (
    GeneratedResponse,
    RetrievalResult,
    Question,
    ClientContext,
)
from services.llm_service import LLMService


class GeneratorAgent:
    """Agent responsible for generating customized proposal content."""

    def __init__(self, llm_service: LLMService):
        """Initialize the generator agent."""
        self.llm = llm_service

    def generate_response(
        self, question: Question, retrieval_result: RetrievalResult, client_context: ClientContext
    ) -> GeneratedResponse:
        """Generate a response for a specific question."""

        system_prompt = """You are an expert proposal writer. Your job is to:
1. Create personalized, compelling responses to RFP questions
2. Use provided reference content but adapt it for the specific client
3. Maintain a professional, confident tone
4. Include specific details relevant to the client's industry and needs
5. Avoid generic language"""

        # Build context from retrieved content
        reference_content = "\n\n".join(
            [
                f"Reference {i+1} (relevance: {c.relevance_score:.2f}):\n{c.text}"
                for i, c in enumerate(retrieval_result.retrieved_content[:3])
            ]
        )

        prompt = f"""Question: {question.text}

Client: {client_context.company_name}
Industry: {client_context.industry or 'Not specified'}
Category: {question.category.value}
Priority: {question.priority.value}

Reference content from past proposals:
{reference_content}

Generate a compelling, personalized response for {client_context.company_name}.
- Make it specific to their industry
- Adapt the reference content, don't copy it verbatim
- Keep it concise but comprehensive
- Sound human-written, not templated

Response:"""

        try:
            response_text = self.llm.generate(prompt=prompt, system_prompt=system_prompt, temperature=0.7)

            # Calculate confidence based on retrieval quality
            confidence = self._calculate_confidence(retrieval_result)

            # Extract personalization elements
            personalization = {
                "client_name": client_context.company_name,
                "industry": client_context.industry or "",
            }

            # Flag potential issues
            flags = self._check_flags(response_text, client_context)

            return GeneratedResponse(
                question_id=question.q_id,
                question_text=question.text,
                draft_response=response_text,
                personalization_elements=personalization,
                sources_used=[c.source for c in retrieval_result.retrieved_content],
                confidence=confidence,
                flags=flags,
            )

        except Exception as e:
            print(f"Error generating response: {e}")
            return GeneratedResponse(
                question_id=question.q_id,
                question_text=question.text,
                draft_response="[Error generating response]",
                confidence=0.0,
                flags=["generation_failed"],
            )

    def generate_quick_proposal(self, client_context: ClientContext, proposal_type: str = "pitch_deck") -> str:
        """Generate a quick proposal for sales outreach."""

        system_prompt = """You are an expert sales proposal writer. Create compelling, personalized pitch content."""

        prompt = f"""Create a {proposal_type} for {client_context.company_name}.

Industry: {client_context.industry or 'Technology'}
Contact: {client_context.additional_context.get('contact_title', 'Executive')}

Generate a brief proposal (3-5 paragraphs) covering:
1. Understanding of their business and challenges
2. How our solution addresses their needs
3. Key benefits and value proposition
4. Relevant case studies or examples
5. Clear next steps

Make it personalized, compelling, and focused on their specific industry needs.

Proposal:"""

        try:
            proposal = self.llm.generate(prompt=prompt, system_prompt=system_prompt, temperature=0.7)
            return proposal
        except Exception as e:
            print(f"Error generating quick proposal: {e}")
            return f"Error generating proposal for {client_context.company_name}"

    def _calculate_confidence(self, retrieval_result: RetrievalResult) -> float:
        """Calculate confidence score based on retrieval quality."""
        if not retrieval_result.retrieved_content:
            return 0.5  # Low confidence without references

        # Average relevance score of top 3 results
        top_scores = [c.relevance_score for c in retrieval_result.retrieved_content[:3]]
        avg_score = sum(top_scores) / len(top_scores) if top_scores else 0.5

        # Boost if we have winning proposals
        has_win = any(c.win_outcome for c in retrieval_result.retrieved_content if c.win_outcome)
        if has_win:
            avg_score = min(avg_score + 0.1, 1.0)

        return avg_score

    def _check_flags(self, response: str, client_context: ClientContext) -> List[str]:
        """Check for potential issues in the response."""
        flags = []

        # Check length
        if len(response) < 100:
            flags.append("too_short")
        elif len(response) > 2000:
            flags.append("too_long")

        # Check for client name personalization
        if client_context.company_name.lower() not in response.lower():
            flags.append("missing_client_name")

        # Check for generic language
        generic_phrases = ["our company", "we offer", "leading provider"]
        if any(phrase in response.lower() for phrase in generic_phrases):
            flags.append("generic_language")

        return flags
