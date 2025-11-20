#!/usr/bin/env python3
"""
Integration Test Script for RFP Upload Flow

This script tests the complete end-to-end RFP processing workflow:
1. Upload RFP document
2. Poll workflow status
3. Monitor state transitions
4. Download generated document

Usage:
    python tests/integration_test_rfp.py
    python tests/integration_test_rfp.py --rfp-file path/to/rfp.pdf --client "Acme Corp"
"""
import requests
import time
import sys
import os
import argparse
from pathlib import Path
from datetime import datetime
import json

# Configuration
API_BASE_URL = os.getenv("API_URL", "http://localhost:8000")
POLL_INTERVAL = 2  # seconds
MAX_WAIT_TIME = 300  # 5 minutes


class Colors:
    """ANSI color codes for terminal output."""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'


def print_header(text):
    """Print colored header."""
    print(f"\n{Colors.BOLD}{Colors.HEADER}{'='*80}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.HEADER}{text.center(80)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.HEADER}{'='*80}{Colors.END}\n")


def print_step(step_num, text):
    """Print step indicator."""
    print(f"{Colors.BOLD}{Colors.CYAN}[Step {step_num}]{Colors.END} {text}")


def print_success(text):
    """Print success message."""
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")


def print_error(text):
    """Print error message."""
    print(f"{Colors.RED}✗ {text}{Colors.END}")


def print_info(text):
    """Print info message."""
    print(f"{Colors.BLUE}ℹ {text}{Colors.END}")


def create_sample_rfp_file():
    """Create a sample RFP text file for testing."""
    sample_rfp = """
REQUEST FOR PROPOSAL (RFP)
Enterprise Software Development Services

Client: TechCorp Industries
Industry: Technology / Software
Date: November 20, 2024
Deadline: December 15, 2024

================================================================================
SECTION 1: COMPANY BACKGROUND
================================================================================

1. Please provide a brief history of your company, including years in business,
   number of employees, and primary service offerings.

2. Describe your experience developing enterprise software for Fortune 500 companies.

3. What industries have you served in the past 5 years?

================================================================================
SECTION 2: TECHNICAL REQUIREMENTS
================================================================================

4. What is your approach to cloud-native architecture and microservices development?

5. Describe your experience with the following technologies:
   - Kubernetes and container orchestration
   - React/Vue.js frontend frameworks
   - Node.js/Python backend development
   - PostgreSQL/MongoDB databases

6. How do you ensure application security and data protection?

7. What is your approach to API design and development?

================================================================================
SECTION 3: DEVELOPMENT METHODOLOGY
================================================================================

8. Describe your software development lifecycle (SDLC) process.

9. What project management methodologies do you use (Agile, Scrum, etc.)?

10. How do you handle code quality assurance and testing?

11. What is your approach to CI/CD and DevOps practices?

================================================================================
SECTION 4: IMPLEMENTATION & SUPPORT
================================================================================

12. What is your typical timeline for implementing a full-stack web application?

13. Describe your post-implementation support and maintenance services.

14. What are your SLA commitments for production support?

15. How do you handle emergency issues and critical bugs?

================================================================================
SECTION 5: PRICING & TERMS
================================================================================

16. Provide your hourly rates for different skill levels (junior, mid, senior developers).

17. What are your payment terms and billing cycle?

18. Do you offer fixed-price project options?

19. What are your cancellation and change order policies?

================================================================================
SECTION 6: REFERENCES
================================================================================

20. Provide three client references from similar enterprise software projects.

Thank you for your submission. We look forward to reviewing your proposal.
"""

    # Create sample file
    sample_file = Path("./data/uploads/sample_rfp.txt")
    sample_file.parent.mkdir(parents=True, exist_ok=True)

    with open(sample_file, "w") as f:
        f.write(sample_rfp)

    return str(sample_file)


def upload_rfp(file_path: str, client_name: str, industry: str = None):
    """
    Step 1: Upload RFP document.

    Returns:
        tuple: (workflow_id, success)
    """
    print_step(1, "Uploading RFP document...")

    try:
        with open(file_path, 'rb') as f:
            files = {'file': (Path(file_path).name, f)}
            data = {
                'client_name': client_name,
            }
            if industry:
                data['industry'] = industry

            response = requests.post(
                f"{API_BASE_URL}/api/v1/rfp/upload",
                files=files,
                data=data,
                timeout=30
            )

        if response.status_code == 200:
            result = response.json()
            workflow_id = result.get("workflow_id")
            print_success(f"RFP uploaded successfully!")
            print_info(f"Workflow ID: {workflow_id}")
            print_info(f"Status: {result.get('status')}")
            return workflow_id, True
        else:
            print_error(f"Upload failed: {response.status_code}")
            print_error(f"Response: {response.text}")
            return None, False

    except Exception as e:
        print_error(f"Upload error: {str(e)}")
        return None, False


def poll_workflow_status(workflow_id: str):
    """
    Step 2: Poll workflow status and monitor state transitions.

    Returns:
        tuple: (final_workflow, success)
    """
    print_step(2, "Monitoring workflow progress...")

    start_time = time.time()
    last_state = None
    state_history = []

    while True:
        elapsed = time.time() - start_time

        if elapsed > MAX_WAIT_TIME:
            print_error(f"Timeout: Workflow did not complete within {MAX_WAIT_TIME} seconds")
            return None, False

        try:
            response = requests.get(
                f"{API_BASE_URL}/api/v1/workflows/{workflow_id}",
                timeout=10
            )

            if response.status_code == 200:
                workflow = response.json()
                current_state = workflow.get("state")

                # Print state transition
                if current_state != last_state:
                    state_history.append((current_state, time.time() - start_time))

                    if current_state == "analyzing":
                        print_info(f"State: {current_state} - Extracting questions from RFP...")
                    elif current_state == "routing":
                        print_info(f"State: {current_state} - Routing questions to agents...")
                    elif current_state == "generating":
                        print_info(f"State: {current_state} - Generating answers...")
                        # Show progress if responses are available
                        responses = workflow.get("generated_responses", [])
                        if responses:
                            total = workflow.get("rfp_analysis", {}).get("total_questions", 0)
                            print_info(f"  Progress: {len(responses)}/{total} answers generated")
                    elif current_state == "reviewing":
                        print_info(f"State: {current_state} - Performing quality review...")
                    elif current_state == "formatting":
                        print_info(f"State: {current_state} - Formatting final document...")
                    elif current_state == "ready":
                        print_success(f"State: {current_state} - RFP processing complete! ✓")
                    else:
                        print_info(f"State: {current_state}")

                    last_state = current_state

                # Check if complete
                if current_state == "ready":
                    print_success(f"Workflow completed in {elapsed:.1f} seconds")
                    print_state_summary(state_history)
                    return workflow, True

                elif current_state == "error":
                    print_error("Workflow encountered an error")
                    return workflow, False

                # Progressive update during generating
                if current_state == "generating":
                    responses = workflow.get("generated_responses", [])
                    if responses:
                        # Show latest answer briefly
                        latest = responses[-1]
                        question = latest.get("question", "")[:60] + "..."
                        print(f"  ├─ Latest: {question}", end='\r')

            else:
                print_error(f"Failed to get workflow status: {response.status_code}")
                return None, False

        except Exception as e:
            print_error(f"Polling error: {str(e)}")
            return None, False

        time.sleep(POLL_INTERVAL)


def print_state_summary(state_history):
    """Print summary of state transitions."""
    print(f"\n{Colors.BOLD}State Transition Summary:{Colors.END}")
    for i, (state, elapsed) in enumerate(state_history):
        duration = 0
        if i < len(state_history) - 1:
            duration = state_history[i+1][1] - elapsed
        print(f"  {i+1}. {state.ljust(15)} @ {elapsed:6.1f}s (duration: {duration:.1f}s)")


def print_workflow_results(workflow):
    """
    Step 3: Display workflow results.
    """
    print_step(3, "Workflow Results Summary...")

    # RFP Analysis
    if workflow.get("rfp_analysis"):
        analysis = workflow["rfp_analysis"]
        print(f"\n{Colors.BOLD}RFP Analysis:{Colors.END}")
        print(f"  Total Questions: {analysis.get('total_questions', 0)}")
        print(f"  Sections Detected: {len(analysis.get('sections', []))}")

        # Show first few questions
        questions = analysis.get("questions", [])
        if questions:
            print(f"\n  Sample Questions:")
            for i, q in enumerate(questions[:3], 1):
                print(f"    {i}. {q[:70]}...")

    # Generated Responses
    if workflow.get("generated_responses"):
        responses = workflow["generated_responses"]
        print(f"\n{Colors.BOLD}Generated Responses:{Colors.END}")
        print(f"  Total Responses: {len(responses)}")

        # Calculate average confidence
        avg_confidence = sum(r.get("confidence", 0) for r in responses) / len(responses)
        print(f"  Average Confidence: {avg_confidence:.2%}")

        # Show confidence distribution
        high = sum(1 for r in responses if r.get("confidence", 0) >= 0.8)
        medium = sum(1 for r in responses if 0.5 <= r.get("confidence", 0) < 0.8)
        low = sum(1 for r in responses if r.get("confidence", 0) < 0.5)

        print(f"  Confidence Distribution:")
        print(f"    High (≥80%):   {high}")
        print(f"    Medium (50-80%): {medium}")
        print(f"    Low (<50%):    {low}")

    # Review Result
    if workflow.get("review_result"):
        review = workflow["review_result"]
        print(f"\n{Colors.BOLD}Quality Review:{Colors.END}")
        print(f"  Overall Quality: {review.get('overall_quality', 'N/A').upper()}")
        print(f"  Completeness Score: {review.get('completeness_score', 0):.1%}")

        issues = review.get("issues_found", [])
        if issues:
            print(f"  Issues Found: {len(issues)}")
            for issue in issues[:3]:
                print(f"    - {issue.get('issue', 'Unknown issue')}")

    # Output File
    if workflow.get("output_file_path"):
        print(f"\n{Colors.BOLD}Output File:{Colors.END}")
        print(f"  Path: {workflow['output_file_path']}")
        print_success("Document generated successfully!")


def download_document(workflow_id: str):
    """
    Step 4: Download generated document.
    """
    print_step(4, "Downloading generated document...")

    try:
        response = requests.get(
            f"{API_BASE_URL}/api/v1/download/{workflow_id}",
            timeout=30
        )

        if response.status_code == 200:
            # Save file
            filename = f"rfp_response_{workflow_id}.docx"
            output_path = Path("./data/outputs") / filename
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, 'wb') as f:
                f.write(response.content)

            print_success(f"Document downloaded successfully!")
            print_info(f"Saved to: {output_path}")
            return str(output_path), True

        else:
            print_error(f"Download failed: {response.status_code}")
            return None, False

    except Exception as e:
        print_error(f"Download error: {str(e)}")
        return None, False


def test_health_check():
    """Test API health check."""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print_success("API is healthy and running")
            return True
        else:
            print_error(f"API health check failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Cannot connect to API: {str(e)}")
        print_info(f"Make sure the API is running at {API_BASE_URL}")
        return False


def main():
    """Main test execution."""
    parser = argparse.ArgumentParser(description="Integration test for RFP upload workflow")
    parser.add_argument("--rfp-file", help="Path to RFP file (PDF, DOCX, or TXT)")
    parser.add_argument("--client", default="TechCorp Industries", help="Client name")
    parser.add_argument("--industry", default="Technology", help="Industry")
    parser.add_argument("--api-url", default=API_BASE_URL, help="API base URL")

    args = parser.parse_args()

    global API_BASE_URL
    API_BASE_URL = args.api_url

    print_header("RFP UPLOAD WORKFLOW - INTEGRATION TEST")

    # Pre-flight check
    print_step(0, "Pre-flight checks...")
    if not test_health_check():
        print_error("\nTest aborted: API is not accessible")
        sys.exit(1)

    print_success("All pre-flight checks passed\n")

    # Get RFP file
    if args.rfp_file and os.path.exists(args.rfp_file):
        rfp_file = args.rfp_file
        print_info(f"Using provided RFP file: {rfp_file}")
    else:
        print_info("Creating sample RFP file...")
        rfp_file = create_sample_rfp_file()
        print_success(f"Sample RFP created: {rfp_file}")

    # Execute test steps
    start_time = time.time()

    # Step 1: Upload
    workflow_id, success = upload_rfp(rfp_file, args.client, args.industry)
    if not success or not workflow_id:
        print_error("\nTest failed at Step 1: Upload")
        sys.exit(1)

    # Step 2: Poll and monitor
    workflow, success = poll_workflow_status(workflow_id)
    if not success or not workflow:
        print_error("\nTest failed at Step 2: Polling")
        sys.exit(1)

    # Step 3: Display results
    print_workflow_results(workflow)

    # Step 4: Download
    output_path, success = download_document(workflow_id)
    if not success:
        print_error("\nTest failed at Step 4: Download")
        sys.exit(1)

    # Final summary
    total_time = time.time() - start_time

    print_header("TEST SUMMARY")
    print_success(f"All tests passed! ✓")
    print_info(f"Total execution time: {total_time:.1f} seconds")
    print_info(f"Workflow ID: {workflow_id}")
    print_info(f"Output document: {output_path}")

    print(f"\n{Colors.BOLD}Next steps:{Colors.END}")
    print(f"  1. Review the generated document at: {output_path}")
    print(f"  2. Check the workflow in database: SELECT * FROM workflows WHERE workflow_id='{workflow_id}'")
    print(f"  3. Test the document editing API: PUT /api/v1/documents/{workflow_id}")

    sys.exit(0)


if __name__ == "__main__":
    main()
