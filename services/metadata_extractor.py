"""Metadata extraction for RFP documents using LLM."""
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import re
from pathlib import Path
from services.llm_service import LLMService


class MetadataExtractor:
    """Extract rich metadata from RFP documents."""

    def __init__(self, llm_service: LLMService):
        """Initialize metadata extractor."""
        self.llm = llm_service

    def extract_from_path(self, file_path: str) -> Dict[str, Any]:
        """Extract metadata from file path."""
        path = Path(file_path)
        parts = path.parts

        metadata = {"file_path": file_path, "file_name": path.name, "file_extension": path.suffix}

        # Extract client name (folder name in RFP_Hackathon)
        try:
            rfp_idx = parts.index("RFP_Hackathon")
            if rfp_idx + 1 < len(parts):
                metadata["client_name"] = parts[rfp_idx + 1]
        except ValueError:
            metadata["client_name"] = "Unknown"

        # Determine document type from path
        if "Received" in file_path:
            metadata["doc_type"] = "rfp_received"
        elif "Final" in file_path or "Sent" in file_path:
            metadata["doc_type"] = "rfp_response"
        elif "Attachment" in file_path:
            metadata["doc_type"] = "attachment"
        else:
            metadata["doc_type"] = "unknown"

        return metadata

    def extract_from_content(self, text: str, max_chars: int = 3000) -> Dict[str, Any]:
        """Extract metadata from document content using LLM."""

        # If LLM is not available, use fallback immediately
        if self.llm is None:
            return self._fallback_extraction(text)

        # Truncate to avoid token limits
        excerpt = text[:max_chars]

        system_prompt = """You are an expert at analyzing RFP (Request for Proposal) documents.
Extract structured metadata from the provided document excerpt."""

        prompt = f"""Analyze this RFP document excerpt and extract the following information:

{excerpt}

Extract and return as JSON:
{{
    "industry": "The client's industry (e.g., Semiconductor, Technology, Healthcare, Finance)",
    "categories": ["List of RFP categories like technical, legal, pricing, case_study, skills_taxonomy, talent_intelligence"],
    "key_requirements": ["List of 3-5 main requirements or needs mentioned"],
    "geographic_focus": ["Countries or regions mentioned"],
    "timeline_mentions": ["Any dates, deadlines, or timeline references"],
    "company_context": "Brief 1-sentence description of the client company if mentioned"
}}

Return ONLY valid JSON, no additional text."""

        try:
            result = self.llm.generate_structured(
                prompt=prompt, system_prompt=system_prompt, schema=None  # Let LLM generate structure
            )

            return result
        except Exception as e:
            print(f"LLM metadata extraction failed: {e}")
            return self._fallback_extraction(text)

    def _fallback_extraction(self, text: str) -> Dict[str, Any]:
        """Fallback heuristic-based metadata extraction."""
        metadata = {}

        # Industry keywords
        industry_keywords = {
            "semiconductor": "Semiconductor",
            "healthcare": "Healthcare",
            "finance": "Finance",
            "technology": "Technology",
            "manufacturing": "Manufacturing",
            "retail": "Retail",
        }

        text_lower = text.lower()
        for keyword, industry in industry_keywords.items():
            if keyword in text_lower:
                metadata["industry"] = industry
                break

        # Extract dates (YYYY-MM-DD or Month DD, YYYY)
        date_patterns = [
            r"\d{4}-\d{2}-\d{2}",  # 2025-05-20
            r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}",  # May 20, 2025
        ]

        dates = []
        for pattern in date_patterns:
            matches = re.findall(pattern, text)
            dates.extend(matches)

        if dates:
            metadata["timeline_mentions"] = dates[:5]  # First 5 dates

        # Category detection
        categories = []
        if "talent" in text_lower or "hiring" in text_lower:
            categories.append("talent_intelligence")
        if "skill" in text_lower or "taxonomy" in text_lower:
            categories.append("skills_taxonomy")
        if "price" in text_lower or "pricing" in text_lower or "cost" in text_lower:
            categories.append("pricing")
        if "technical" in text_lower or "architecture" in text_lower:
            categories.append("technical")
        if "legal" in text_lower or "compliance" in text_lower:
            categories.append("legal")

        metadata["categories"] = categories if categories else ["general"]

        return metadata

    def extract_qa_pairs(self, text: str) -> List[Dict[str, Any]]:
        """Extract question-answer pairs from RFP."""
        qa_pairs = []

        # Pattern: Numbered questions (Q1, Q2, or 1., 2.)
        # Looking for questions
        question_patterns = [
            r"(?:Q\d+|Question \d+|^\d+\.)\s*:?\s*(.+?)(?=(?:Q\d+|Question \d+|^\d+\.)|$)",
            r"^(\d+\.\s+.+?)(?=^\d+\.|\Z)",  # Numbered list
        ]

        for pattern in question_patterns:
            matches = re.finditer(pattern, text, re.MULTILINE | re.DOTALL)
            for i, match in enumerate(matches, 1):
                question_text = match.group(1).strip()
                if len(question_text) > 20:  # Meaningful question
                    qa_pairs.append(
                        {"question_id": f"Q{i}", "question": question_text, "answer": None  # To be linked later
                        }
                    )

        return qa_pairs

    def extract_complete_metadata(self, file_path: str, text: str) -> Dict[str, Any]:
        """
        Extract complete metadata combining path, content, and LLM analysis.
        """
        # Step 1: Extract from path
        metadata = self.extract_from_path(file_path)

        # Step 2: Extract from content
        content_metadata = self.extract_from_content(text)
        metadata.update(content_metadata)

        # Step 3: Extract Q&A pairs
        qa_pairs = self.extract_qa_pairs(text)
        if qa_pairs:
            metadata["qa_pairs"] = qa_pairs
            metadata["total_questions"] = len(qa_pairs)

        # Step 4: Add timestamps
        metadata["ingestion_date"] = datetime.now().isoformat()

        # Step 5: Initialize tracking fields
        metadata.update(
            {
                "win_status": None,  # To be updated manually
                "times_retrieved": 0,
                "last_used": None,
                "quality_score": 0.7,  # Default score
            }
        )

        return metadata


class ClientMatcher:
    """Match and link related RFP documents."""

    @staticmethod
    def link_rfp_to_response(rfp_metadata: Dict, response_metadata: Dict) -> bool:
        """
        Determine if an RFP and response are related.
        """
        # Same client?
        if rfp_metadata.get("client_name") != response_metadata.get("client_name"):
            return False

        # Complementary doc types?
        if rfp_metadata.get("doc_type") == "rfp_received" and response_metadata.get("doc_type") == "rfp_response":
            return True

        return False

    @staticmethod
    def find_similar_clients(
        target_metadata: Dict, all_metadata: List[Dict], top_k: int = 3
    ) -> List[Tuple[str, float]]:
        """
        Find similar clients based on metadata.
        """
        target_industry = target_metadata.get("industry", "")
        target_categories = set(target_metadata.get("categories", []))

        similar = []
        for meta in all_metadata:
            if meta.get("client_name") == target_metadata.get("client_name"):
                continue  # Skip self

            similarity = 0.0

            # Industry match (40% weight)
            if meta.get("industry") == target_industry:
                similarity += 0.4

            # Category overlap (40% weight)
            other_categories = set(meta.get("categories", []))
            if target_categories and other_categories:
                overlap = len(target_categories & other_categories) / len(target_categories | other_categories)
                similarity += 0.4 * overlap

            # Geographic overlap (20% weight)
            target_geo = set(target_metadata.get("geographic_focus", []))
            other_geo = set(meta.get("geographic_focus", []))
            if target_geo and other_geo:
                geo_overlap = len(target_geo & other_geo) / len(target_geo | other_geo)
                similarity += 0.2 * geo_overlap

            if similarity > 0.3:  # Threshold
                similar.append((meta.get("client_name", "Unknown"), similarity))

        # Sort by similarity
        similar.sort(key=lambda x: x[1], reverse=True)
        return similar[:top_k]
