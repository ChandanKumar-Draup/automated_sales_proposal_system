"""Formatter Agent - Converts content into client's required format."""
from typing import List, Optional
from datetime import datetime
from models.schemas import GeneratedResponse, RFPAnalysis, ClientContext
from services.document_processor import DocumentProcessor


class FormatterAgent:
    """Agent responsible for formatting content into various output formats."""

    def __init__(self):
        """Initialize the formatter agent."""
        self.doc_processor = DocumentProcessor()

    def format_rfp_response(
        self,
        responses: List[GeneratedResponse],
        rfp_analysis: RFPAnalysis,
        output_path: str,
        format_type: str = "docx",
    ) -> str:
        """Format RFP responses into a document."""

        # Build the complete proposal document
        content_parts = []

        # Header
        content_parts.append(f"PROPOSAL RESPONSE")
        content_parts.append(f"Client: {rfp_analysis.client.company_name}")
        content_parts.append(f"Date: {datetime.now().strftime('%Y-%m-%d')}")
        content_parts.append(f"RFP ID: {rfp_analysis.rfp_id}")
        content_parts.append("\n" + "=" * 80 + "\n")

        # Group responses by section
        sections = {}
        for response in responses:
            # Find the section for this question
            section_name = "General"
            for section in rfp_analysis.sections:
                for question in section.questions:
                    if question.q_id == response.question_id:
                        section_name = section.title
                        break

            if section_name not in sections:
                sections[section_name] = []

            sections[section_name].append(response)

        # Add each section
        for section_name, section_responses in sections.items():
            content_parts.append(f"\n## {section_name}\n")

            for response in section_responses:
                content_parts.append(f"\n### {response.question_id}: {response.question_text}\n")
                content_parts.append(response.draft_response)
                content_parts.append("\n")

        content = "\n".join(content_parts)

        # Save in requested format
        if format_type == "docx":
            return self.doc_processor.save_as_docx(
                content, output_path, title=f"Proposal for {rfp_analysis.client.company_name}"
            )
        elif format_type == "txt":
            return self.doc_processor.save_as_txt(content, output_path)
        else:
            raise ValueError(f"Unsupported format: {format_type}")

    def format_quick_proposal(
        self, content: str, client_context: ClientContext, output_path: str, format_type: str = "docx"
    ) -> str:
        """Format a quick proposal."""

        # Build document
        doc_content = f"""SALES PROPOSAL

Client: {client_context.company_name}
Industry: {client_context.industry or 'N/A'}
Date: {datetime.now().strftime('%Y-%m-%d')}

{content}

---

Next Steps:
1. Review this proposal
2. Schedule a discovery call
3. Discuss customization options
4. Finalize agreement

Contact us to move forward!
"""

        # Save in requested format
        if format_type == "docx":
            return self.doc_processor.save_as_docx(
                doc_content, output_path, title=f"Proposal for {client_context.company_name}"
            )
        elif format_type == "txt":
            return self.doc_processor.save_as_txt(doc_content, output_path)
        else:
            raise ValueError(f"Unsupported format: {format_type}")

    def format_rfp_response_from_qa(
        self,
        responses: List[dict],
        client_name: str,
        output_path: str,
        format_type: str = "docx"
    ) -> str:
        """Format RFP responses from Q&A format into a document.

        Args:
            responses: List of response dictionaries from QA agent
            client_name: Name of the client
            output_path: Path to save the output file
            format_type: Format type (docx or txt)

        Returns:
            Path to the saved file
        """
        # Build the complete proposal document
        content_parts = []

        # Header
        content_parts.append(f"RFP RESPONSE DOCUMENT")
        content_parts.append(f"Client: {client_name}")
        content_parts.append(f"Date: {datetime.now().strftime('%B %d, %Y')}")
        content_parts.append("\n" + "=" * 80 + "\n")

        # Add each question and answer
        for i, response in enumerate(responses, 1):
            question = response.get("question", "")
            answer = response.get("answer", "")
            confidence = response.get("confidence", 0.0)

            content_parts.append(f"\n### Question {i}")
            content_parts.append(f"\n{question}\n")
            content_parts.append(f"**Answer:**\n")
            content_parts.append(answer)

            # Add confidence indicator for internal use
            if confidence < 0.5:
                content_parts.append(f"\n*(Note: This answer may require additional review)*\n")

            content_parts.append("\n" + "-" * 80 + "\n")

        content = "\n".join(content_parts)

        # Save in requested format
        if format_type == "docx":
            return self.doc_processor.save_as_docx(
                content, output_path, title=f"RFP Response for {client_name}"
            )
        elif format_type == "txt":
            return self.doc_processor.save_as_txt(content, output_path)
        else:
            raise ValueError(f"Unsupported format: {format_type}")
