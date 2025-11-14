"""Analyzer Agent - Understands what the client actually wants."""
from typing import List, Dict, Any
from models.schemas import (
    RFPAnalysis,
    ClientContext,
    RFPSection,
    Question,
    QuestionCategory,
    Priority,
)
from services.llm_service import LLMService


class AnalyzerAgent:
    """Agent responsible for analyzing RFPs and extracting requirements."""

    def __init__(self, llm_service: LLMService):
        """Initialize the analyzer agent."""
        self.llm = llm_service

    def analyze_rfp(self, rfp_text: str, client_name: str, industry: str = None) -> RFPAnalysis:
        """Analyze an RFP document and extract structured requirements."""

        system_prompt = """You are an expert RFP analyzer. Your job is to:
1. Extract all questions and requirements from the RFP
2. Categorize each question (technical, legal, pricing, case_study, company_info)
3. Determine priority (must_have, should_have, nice_to_have)
4. Assess complexity (low, medium, high)
5. Estimate total effort in hours"""

        prompt = f"""Analyze this RFP document from {client_name}:

{rfp_text[:4000]}  # Limit for token efficiency

Extract all questions and requirements. For each question, provide:
- Unique ID (Q1, Q2, etc.)
- Question text
- Category (technical/legal/pricing/case_study/company_info)
- Priority (must_have/should_have/nice_to_have)
- Complexity (low/medium/high)

Also provide:
- Total number of questions
- Estimated effort hours
- Any risk factors you identify

Respond in JSON format."""

        try:
            result = self.llm.generate_structured(
                prompt=prompt,
                system_prompt=system_prompt,
                schema={
                    "questions": [
                        {
                            "q_id": "string",
                            "text": "string",
                            "category": "string",
                            "priority": "string",
                            "complexity": "string",
                        }
                    ],
                    "total_questions": "integer",
                    "estimated_effort_hours": "number",
                    "risk_factors": ["string"],
                },
            )

            # Convert to structured format
            sections = self._group_questions_by_category(result.get("questions", []))

            return RFPAnalysis(
                rfp_id=f"RFP-{client_name}-{hash(rfp_text[:100]) % 10000}",
                client=ClientContext(company_name=client_name, industry=industry),
                sections=sections,
                total_questions=result.get("total_questions", len(result.get("questions", []))),
                estimated_effort_hours=result.get("estimated_effort_hours", 0),
                risk_factors=result.get("risk_factors", []),
                confidence=0.85,  # Base confidence
            )

        except Exception as e:
            print(f"Error analyzing RFP: {e}")
            # Return minimal analysis
            return RFPAnalysis(
                rfp_id=f"RFP-{client_name}-ERROR",
                client=ClientContext(company_name=client_name, industry=industry),
                sections=[],
                total_questions=0,
                estimated_effort_hours=0,
                risk_factors=["analysis_failed"],
                confidence=0.0,
            )

    def _group_questions_by_category(self, questions: List[Dict[str, Any]]) -> List[RFPSection]:
        """Group questions by category into sections."""
        sections_dict = {}

        for q in questions:
            category = q.get("category", "company_info")
            try:
                cat_enum = QuestionCategory(category)
            except ValueError:
                cat_enum = QuestionCategory.COMPANY_INFO

            if category not in sections_dict:
                sections_dict[category] = RFPSection(
                    section_id=f"S-{category}",
                    title=category.replace("_", " ").title(),
                    category=cat_enum,
                    questions=[],
                )

            # Create Question object
            try:
                priority = Priority(q.get("priority", "should_have"))
            except ValueError:
                priority = Priority.SHOULD_HAVE

            question = Question(
                q_id=q.get("q_id", f"Q{len(sections_dict[category].questions) + 1}"),
                text=q.get("text", ""),
                category=cat_enum,
                priority=priority,
                complexity=q.get("complexity", "medium"),
            )

            sections_dict[category].questions.append(question)

        return list(sections_dict.values())

    def quick_analyze(self, company_name: str, contact_title: str = None) -> ClientContext:
        """Quick analysis for simple proposal requests."""
        # For quick proposals, we just need basic context
        # In a real system, this would query Draup APIs for company intelligence

        system_prompt = "You are a company research expert. Provide brief industry classification."

        prompt = f"""What industry is {company_name} in? Respond with just the industry name (e.g., 'Technology', 'Healthcare', 'Finance')."""

        try:
            industry = self.llm.generate(prompt=prompt, system_prompt=system_prompt, temperature=0.3).strip()
        except:
            industry = "Unknown"

        return ClientContext(
            company_name=company_name,
            industry=industry,
            additional_context={"contact_title": contact_title} if contact_title else {},
        )
