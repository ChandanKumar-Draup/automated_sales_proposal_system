"""Reviewer Agent - Catches errors before they reach the client."""
from typing import List, Dict
from models.schemas import (
    GeneratedResponse,
    ReviewResult,
    ReviewIssue,
    RFPAnalysis,
)
from config import settings


class ReviewerAgent:
    """Agent responsible for reviewing and validating generated content."""

    def __init__(self):
        """Initialize the reviewer agent."""
        self.high_threshold = settings.high_confidence_threshold
        self.medium_threshold = settings.medium_confidence_threshold

    def review_responses(
        self, responses: List[GeneratedResponse], rfp_analysis: RFPAnalysis = None
    ) -> ReviewResult:
        """Review all generated responses for quality and compliance."""

        issues = []
        checks = {
            "all_questions_answered": True,
            "no_placeholder_text": True,
            "confidence_acceptable": True,
            "no_generic_responses": True,
        }

        # Categorize by confidence
        high_confidence = []
        medium_confidence = []
        low_confidence = []

        for response in responses:
            # Check confidence level
            if response.confidence >= self.high_threshold:
                high_confidence.append(response)
            elif response.confidence >= self.medium_threshold:
                medium_confidence.append(response)
            else:
                low_confidence.append(response)

            # Check for placeholders or errors
            if "[Error" in response.draft_response or "[TODO]" in response.draft_response:
                checks["no_placeholder_text"] = False
                issues.append(
                    ReviewIssue(
                        severity="error",
                        location=f"Question {response.question_id}",
                        issue="Contains placeholder or error text",
                        suggestion="Review and regenerate this response",
                    )
                )

            # Check for generic language
            if "generic_language" in response.flags:
                issues.append(
                    ReviewIssue(
                        severity="warning",
                        location=f"Question {response.question_id}",
                        issue="Response contains generic language",
                        suggestion="Add more client-specific details",
                    )
                )

            # Check for missing client personalization
            if "missing_client_name" in response.flags:
                issues.append(
                    ReviewIssue(
                        severity="warning",
                        location=f"Question {response.question_id}",
                        issue="Client name not mentioned in response",
                        suggestion="Personalize the response for the client",
                    )
                )

            # Check length
            if "too_short" in response.flags:
                issues.append(
                    ReviewIssue(
                        severity="warning",
                        location=f"Question {response.question_id}",
                        issue="Response is too brief",
                        suggestion="Expand with more details",
                    )
                )

        # Check if all questions answered (if we have RFP analysis)
        if rfp_analysis:
            total_expected = rfp_analysis.total_questions
            total_answered = len(responses)
            if total_answered < total_expected:
                checks["all_questions_answered"] = False
                issues.append(
                    ReviewIssue(
                        severity="error",
                        location="Overall",
                        issue=f"Only {total_answered} of {total_expected} questions answered",
                        suggestion="Generate responses for remaining questions",
                    )
                )

        # Overall confidence check
        if low_confidence:
            checks["confidence_acceptable"] = False

        # Determine compliance status
        has_errors = any(issue.severity == "error" for issue in issues)
        has_warnings = any(issue.severity == "warning" for issue in issues)

        if has_errors:
            compliance_status = "FAIL"
            overall_readiness = "NOT_READY"
        elif has_warnings:
            compliance_status = "WARNING"
            overall_readiness = "READY_WITH_REVIEW"
        else:
            compliance_status = "PASS"
            overall_readiness = "READY"

        # Override if too many low confidence responses
        if len(low_confidence) > len(responses) * 0.3:  # More than 30% low confidence
            overall_readiness = "NEEDS_REVIEW"

        return ReviewResult(
            compliance_status=compliance_status,
            checks_performed=checks,
            issues_found=issues,
            confidence_breakdown={
                "high_confidence": len(high_confidence),
                "medium_confidence": len(medium_confidence),
                "low_confidence": len(low_confidence),
            },
            overall_readiness=overall_readiness,
        )

    def quick_review(self, content: str) -> Dict[str, any]:
        """Quick review for simple proposals."""
        issues = []

        # Basic checks
        if len(content) < 200:
            issues.append("Content is too brief")

        if "[Error" in content or "[TODO]" in content:
            issues.append("Contains placeholder text")

        # Generic phrase check
        generic_count = sum(
            1 for phrase in ["our company", "we offer", "leading provider"] if phrase in content.lower()
        )

        confidence = 0.9
        if issues:
            confidence = 0.7
        if generic_count > 2:
            confidence -= 0.1
            issues.append("Contains generic language")

        return {"confidence": max(confidence, 0.5), "issues": issues, "ready": len(issues) == 0}
