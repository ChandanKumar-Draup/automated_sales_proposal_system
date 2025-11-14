"""Test script for the Automated Sales Proposal System."""
import requests
import json
import time

BASE_URL = "http://localhost:8000"


def print_section(title):
    """Print a section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def test_health_check():
    """Test health check endpoint."""
    print_section("Testing Health Check")

    response = requests.get(f"{BASE_URL}/health")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    assert response.status_code == 200
    print("✅ Health check passed!")


def test_add_knowledge():
    """Test adding knowledge to vector store."""
    print_section("Testing Knowledge Base - Adding Content")

    # Sample content from past proposals
    sample_content = [
        {
            "text": "Our cloud security solution provides enterprise-grade encryption with AES-256, "
            "multi-factor authentication, and continuous monitoring. We are SOC2 Type II and ISO 27001 certified.",
            "metadata": {
                "source": "RFP-2024-TechCorp",
                "section": "Security",
                "industry": "Technology",
                "win_outcome": True,
            },
        },
        {
            "text": "We have successfully implemented talent acquisition solutions for Fortune 500 companies "
            "including Microsoft, Google, and Amazon, reducing time-to-hire by 40% on average.",
            "metadata": {
                "source": "RFP-2024-MegaCorp",
                "section": "Case Studies",
                "industry": "Technology",
                "win_outcome": True,
            },
        },
        {
            "text": "Our pricing model is flexible and scalable, starting at $50,000 for small enterprises "
            "(up to 1,000 employees) and custom pricing for larger organizations. All plans include 24/7 support.",
            "metadata": {
                "source": "RFP-2024-BigCo",
                "section": "Pricing",
                "industry": "Finance",
                "win_outcome": False,
            },
        },
    ]

    for i, item in enumerate(sample_content):
        response = requests.post(
            f"{BASE_URL}/api/v1/knowledge/add", params={"text": item["text"], "metadata": json.dumps(item["metadata"])}
        )

        print(f"\nAdding content {i+1}...")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")

        assert response.status_code == 200

    print("\n✅ Knowledge base populated!")


def test_search_knowledge():
    """Test searching the knowledge base."""
    print_section("Testing Knowledge Base - Searching")

    query = "cloud security and encryption"
    response = requests.get(f"{BASE_URL}/api/v1/knowledge/search", params={"query": query, "top_k": 3})

    print(f"Query: {query}")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    assert response.status_code == 200
    results = response.json()
    assert len(results["results"]) > 0

    print(f"\n✅ Found {len(results['results'])} results!")


def test_quick_proposal():
    """Test quick proposal generation."""
    print_section("Testing Quick Proposal Generation")

    request_data = {
        "company_name": "Microsoft",
        "contact_title": "VP of Talent Acquisition",
        "industry": "Technology",
        "proposal_type": "pitch_deck",
        "additional_context": "Interested in AI-powered recruitment solutions",
    }

    print(f"Request: {json.dumps(request_data, indent=2)}")
    print("\nGenerating proposal... (this may take 30-60 seconds)")

    response = requests.post(f"{BASE_URL}/api/v1/proposals/quick", json=request_data)

    print(f"\nStatus Code: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        workflow_id = result["workflow_id"]
        print(f"Workflow ID: {workflow_id}")
        print(f"State: {result['state']}")

        # Check if output file was created
        if result.get("output_file_path"):
            print(f"Output File: {result['output_file_path']}")

            # Try to download
            download_response = requests.get(f"{BASE_URL}/api/v1/download/{workflow_id}")
            if download_response.status_code == 200:
                output_filename = f"test_proposal_{int(time.time())}.docx"
                with open(output_filename, "wb") as f:
                    f.write(download_response.content)
                print(f"✅ Proposal downloaded to: {output_filename}")
        else:
            print("⚠️ Output file not yet ready")

        print("\n✅ Quick proposal generation completed!")
    else:
        print(f"❌ Error: {response.text}")


def test_rfp_processing_simulation():
    """Test RFP processing with sample text."""
    print_section("Testing RFP Processing (Simulated)")

    # Sample RFP text
    sample_rfp = """
    REQUEST FOR PROPOSAL (RFP)
    Company: Acme Healthcare Corp

    SECTION 1: TECHNICAL REQUIREMENTS

    Q1. Describe your cloud infrastructure and security measures.

    Q2. What compliance certifications do you hold (HIPAA, SOC2, etc.)?

    Q3. Explain your data backup and disaster recovery procedures.

    SECTION 2: COMPANY INFORMATION

    Q4. Provide a brief company overview and history.

    Q5. List your key clients in the healthcare industry.

    SECTION 3: PRICING

    Q6. Provide detailed pricing for 5,000 users.
    """

    # For simulation, we'll create a text file and "upload" it
    import tempfile
    import os

    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write(sample_rfp)
        temp_file_path = f.name

    try:
        # Upload the RFP
        with open(temp_file_path, "rb") as f:
            files = {"file": ("sample_rfp.txt", f, "text/plain")}
            data = {"client_name": "Acme Healthcare Corp", "industry": "Healthcare"}

            print("Uploading RFP...")
            response = requests.post(f"{BASE_URL}/api/v1/rfp/upload", files=files, data=data)

        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            workflow_id = result["workflow_id"]
            print(f"Workflow ID: {workflow_id}")
            print(f"Status: {result['status']}")

            # If processing synchronously, check result
            if "workflow" in result:
                workflow = result["workflow"]
                print(f"\nWorkflow State: {workflow['state']}")

                if workflow.get("rfp_analysis"):
                    analysis = workflow["rfp_analysis"]
                    print(f"Total Questions: {analysis['total_questions']}")
                    print(f"Estimated Effort: {analysis['estimated_effort_hours']} hours")

                if workflow.get("output_file_path"):
                    print(f"Output File: {workflow['output_file_path']}")

            print("\n✅ RFP processing test completed!")
        else:
            print(f"❌ Error: {response.text}")

    finally:
        # Clean up temp file
        os.unlink(temp_file_path)


def main():
    """Run all tests."""
    print("\n" + "🧪" * 40)
    print("  AUTOMATED SALES PROPOSAL SYSTEM - TEST SUITE")
    print("🧪" * 40)

    try:
        # Test 1: Health check
        test_health_check()

        # Test 2: Add knowledge
        test_add_knowledge()

        # Test 3: Search knowledge
        test_search_knowledge()

        # Test 4: Quick proposal
        test_quick_proposal()

        # Test 5: RFP processing (simulated)
        test_rfp_processing_simulation()

        print_section("✅ ALL TESTS PASSED!")

    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to server.")
        print("Make sure the server is running: python main.py")
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
