"""Question extraction service for RFP documents.

This service follows SOLID principles:
- Single Responsibility: Only handles question extraction from RFP text
- Dependency Inversion: Depends on LLMService abstraction
- Open/Closed: Extensible for different extraction strategies
"""
import re
from typing import List, Dict, Any, Optional
from services.llm_service import LLMService
from services.question_cache import QuestionCache


class QuestionExtractionStrategy:
    """Base strategy for question extraction (Strategy Pattern)."""

    def extract(self, document_text: str) -> List[str]:
        """Extract questions from document text."""
        raise NotImplementedError


class LLMQuestionExtractor(QuestionExtractionStrategy):
    """Extract questions using LLM analysis with file-based caching."""

    def __init__(self, llm_service: LLMService, cache: Optional[QuestionCache] = None):
        """Initialize with LLM service and optional cache.

        Args:
            llm_service: LLM service for question extraction
            cache: Optional cache instance (defaults to new QuestionCache)
        """
        self.llm = llm_service
        self.cache = cache or QuestionCache()

    def extract(self, document_text: str) -> List[str]:
        """Extract questions from RFP using LLM with caching.

        Args:
            document_text: Full text of the RFP document

        Returns:
            List of questions extracted from the RFP
        """
        # Check cache first
        cached_questions = self.cache.get(document_text)
        if cached_questions is not None:
            return cached_questions

        # Truncate if too long (keep first 8000 chars)
        truncated_text = document_text[:8000] if len(document_text) > 8000 else document_text

        prompt = f"""You are an RFP analysis expert. Extract ALL questions and requirements from this RFP document.

Rules:
1. Extract explicit questions (sentences ending with ?)
2. Extract implicit requirements (e.g., "Vendor must provide...", "Describe your approach to...")
3. Rephrase implicit requirements as questions
4. Keep questions clear and specific
5. Preserve technical terminology
6. Group related sub-questions together if needed
7. Number each question

RFP Document:
{truncated_text}

Return ONLY a numbered list of questions, one per line. Format:
1. First question here?
2. Second question here?
...

Questions:"""

        try:
            # Generate questions using LLM
            response = self.llm.generate(
                prompt=prompt,
                max_tokens=2000,
                temperature=0.3,  # Lower temperature for more consistent extraction
            )

            # Parse the response
            questions = self._parse_questions(response)

            # If no questions found, try fallback
            if not questions:
                questions = self._fallback_extraction(document_text)

            # Cache the extracted questions
            if questions:
                self.cache.set(document_text, questions)

            return questions

        except Exception as e:
            print(f"Error extracting questions with LLM: {e}")
            # Fallback to simple extraction
            fallback_questions = self._fallback_extraction(document_text)

            # Cache fallback questions too
            if fallback_questions:
                self.cache.set(document_text, fallback_questions)

            return fallback_questions

    def _parse_questions(self, llm_response: str) -> List[str]:
        """Parse questions from LLM response.

        Args:
            llm_response: Raw response from LLM

        Returns:
            List of cleaned questions
        """
        questions = []
        lines = llm_response.split('\n')

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Remove numbering (1. 2. etc.) and clean up
            cleaned = re.sub(r'^\d+[\.\)]\s*', '', line)
            cleaned = cleaned.strip()

            # Only add if it looks like a question
            if cleaned and len(cleaned) > 10:
                # Ensure it ends with a question mark if it's actually a question
                if not cleaned.endswith('?') and not cleaned.endswith('.'):
                    cleaned += '?'
                questions.append(cleaned)

        return questions

    def _fallback_extraction(self, document_text: str) -> List[str]:
        """Fallback method using pattern matching.

        Args:
            document_text: Full text of the RFP document

        Returns:
            List of questions found using pattern matching
        """
        questions = []

        # Split into sentences
        sentences = re.split(r'[.!?]+', document_text)

        for sentence in sentences:
            sentence = sentence.strip()

            # Look for explicit questions
            if '?' in sentence or sentence.endswith('?'):
                questions.append(sentence if sentence.endswith('?') else sentence + '?')

            # Look for requirement patterns
            elif any(pattern in sentence.lower() for pattern in [
                'please describe',
                'please provide',
                'must provide',
                'should provide',
                'vendor must',
                'vendor should',
                'explain your',
                'describe your',
                'what is your',
                'how do you',
                'provide details'
            ]):
                # Convert to question format
                if not sentence.endswith('?'):
                    sentence += '?'
                questions.append(sentence)

        # Deduplicate and limit
        unique_questions = list(dict.fromkeys(questions))  # Preserves order
        return unique_questions[:50]  # Limit to 50 questions


class QuestionExtractorService:
    """Service for extracting questions from RFP documents.

    This is the main interface for question extraction, following
    the Facade pattern to simplify usage.
    """

    def __init__(self, llm_service: LLMService, strategy: QuestionExtractionStrategy = None):
        """Initialize the question extractor service.

        Args:
            llm_service: LLM service for AI-powered extraction
            strategy: Optional custom extraction strategy
        """
        self.strategy = strategy or LLMQuestionExtractor(llm_service)

    def extract_questions(self, document_text: str) -> Dict[str, Any]:
        """Extract questions and metadata from RFP document.

        Args:
            document_text: Full text of the RFP document

        Returns:
            Dictionary containing:
                - questions: List of extracted questions
                - total_questions: Count of questions
                - sections: Detected section names (if any)
        """
        questions = self.strategy.extract(document_text)

        # Extract section names (simple heuristic)
        sections = self._extract_sections(document_text)

        return {
            "questions": questions,
            "total_questions": len(questions),
            "sections": sections
        }

    def _extract_sections(self, document_text: str) -> List[str]:
        """Extract section headers from document.

        Args:
            document_text: Full text of the RFP document

        Returns:
            List of section names
        """
        sections = []
        lines = document_text.split('\n')

        # Look for common section patterns
        section_patterns = [
            r'^[A-Z][A-Z\s]+$',  # ALL CAPS
            r'^\d+\.\s+[A-Z]',  # 1. Section Name
            r'^Section \d+',  # Section 1
        ]

        for line in lines:
            line = line.strip()
            if not line or len(line) > 100:  # Skip empty or very long lines
                continue

            for pattern in section_patterns:
                if re.match(pattern, line):
                    sections.append(line)
                    break

        # Return unique sections, limited to top 20
        return list(dict.fromkeys(sections))[:20]
