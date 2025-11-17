"""
Comprehensive Demo Script for Automated Sales Proposal System

This script demonstrates different functionalities and use cases of the system:

1. Quick Proposal Generation (Fast-track sales outreach)
2. RFP Processing (Complex RFP handling)
3. Knowledge Base Search (Semantic search)
4. Client-Specific Scenarios
5. Workflow Status Tracking

Run this script with different scenarios to demo the system capabilities.
"""

import requests
import json
import time
import os
from typing import Dict, Any, List
from datetime import datetime


class ProposalSystemDemo:
    """Demo harness for the Automated Sales Proposal System."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.results = []

    def print_banner(self, text: str, char: str = "="):
        """Print a formatted banner."""
        print("\n" + char * 100)
        print(f"  {text}")
        print(char * 100 + "\n")

    def print_step(self, step: str):
        """Print a step header."""
        print(f"\n{'➤' * 3} {step}")
        print("-" * 80)

    def check_health(self) -> bool:
        """Check if the system is healthy."""
        try:
            response = self.session.get(f"{self.base_url}/health")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ System Status: {data['status'].upper()}")
                print(f"   Timestamp: {data['timestamp']}")
                print(f"   Services: LLM={data['services']['llm']}, "
                      f"VectorStore={data['services']['vector_store']}, "
                      f"Orchestrator={data['services']['orchestrator']}")
                return True
            else:
                print(f"❌ Health check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Cannot connect to system: {e}")
            return False

    def wait_for_workflow(self, workflow_id: str, timeout: int = 120) -> Dict[str, Any]:
        """Poll workflow status until completion or timeout."""
        start_time = time.time()
        last_state = None

        while time.time() - start_time < timeout:
            response = self.session.get(f"{self.base_url}/api/v1/workflows/{workflow_id}")
            if response.status_code == 200:
                workflow = response.json()
                current_state = workflow["state"]

                if current_state != last_state:
                    print(f"   State: {current_state.upper()}")
                    last_state = current_state

                if current_state in ["ready", "human_review", "closed"]:
                    return workflow

            time.sleep(2)

        print(f"⚠️  Workflow timeout after {timeout}s")
        return None

    def download_proposal(self, workflow_id: str, output_dir: str = "./demo_outputs") -> str:
        """Download generated proposal."""
        try:
            os.makedirs(output_dir, exist_ok=True)
            response = self.session.get(f"{self.base_url}/api/v1/download/{workflow_id}")

            if response.status_code == 200:
                filename = f"{workflow_id}.docx"
                filepath = os.path.join(output_dir, filename)

                with open(filepath, "wb") as f:
                    f.write(response.content)

                print(f"✅ Proposal downloaded: {filepath}")
                return filepath
            else:
                print(f"❌ Download failed: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Error downloading: {e}")
            return None

    # ==================================================================================
    # SCENARIO 1: QUICK PROPOSAL - Technology Company (SaaS)
    # ==================================================================================
    def scenario_quick_proposal_saas(self):
        """Scenario: Sales rep needs a quick proposal for a SaaS company."""
        self.print_banner("SCENARIO 1: Quick Proposal - Technology/SaaS Company")

        print("📋 Use Case:")
        print("   A sales rep is meeting with a VP of Engineering at a fast-growing")
        print("   SaaS company. They need a tailored pitch deck highlighting talent")
        print("   intelligence solutions for scaling their engineering team.\n")

        self.print_step("Step 1: Creating Quick Proposal Request")

        request_data = {
            "company_name": "TechScale Inc",
            "contact_title": "VP of Engineering",
            "industry": "Technology - SaaS",
            "proposal_type": "pitch_deck",
            "additional_context": "Fast-growing SaaS company scaling from 50 to 200 engineers. "
                                  "Interested in talent intelligence and skills taxonomy for tech roles."
        }

        print(f"Request Data:\n{json.dumps(request_data, indent=2)}")

        self.print_step("Step 2: Submitting to API")
        response = self.session.post(f"{self.base_url}/api/v1/proposals/quick", json=request_data)

        if response.status_code == 200:
            workflow = response.json()
            workflow_id = workflow["workflow_id"]
            print(f"✅ Workflow Created: {workflow_id}")

            self.print_step("Step 3: Monitoring Workflow Progress")
            final_workflow = self.wait_for_workflow(workflow_id)

            if final_workflow and final_workflow["state"] == "ready":
                self.print_step("Step 4: Downloading Proposal")
                filepath = self.download_proposal(workflow_id)

                self.results.append({
                    "scenario": "Quick Proposal - SaaS",
                    "workflow_id": workflow_id,
                    "status": "SUCCESS",
                    "output": filepath
                })

                print("\n✅ Scenario 1 Complete!")
                print(f"   Result: Sales rep has a customized pitch deck ready for the meeting")
            else:
                print("❌ Workflow did not complete successfully")
        else:
            print(f"❌ API Error: {response.status_code} - {response.text}")

    # ==================================================================================
    # SCENARIO 2: QUICK PROPOSAL - Healthcare Company (Compliance-Focused)
    # ==================================================================================
    def scenario_quick_proposal_healthcare(self):
        """Scenario: Healthcare company requiring HIPAA-compliant solutions."""
        self.print_banner("SCENARIO 2: Quick Proposal - Healthcare Company")

        print("📋 Use Case:")
        print("   A healthcare provider network needs workforce analytics for their")
        print("   nursing and clinical staff. They require HIPAA compliance and")
        print("   secure data handling.\n")

        self.print_step("Step 1: Creating Proposal Request")

        request_data = {
            "company_name": "HealthFirst Medical Group",
            "contact_title": "Chief Nursing Officer",
            "industry": "Healthcare",
            "proposal_type": "pitch_deck",
            "additional_context": "Healthcare provider network with 500+ nurses and clinical staff. "
                                  "Requires HIPAA-compliant workforce analytics, talent retention analysis, "
                                  "and skills tracking for clinical certifications."
        }

        print(f"Request Data:\n{json.dumps(request_data, indent=2)}")

        self.print_step("Step 2: Submitting to API")
        response = self.session.post(f"{self.base_url}/api/v1/proposals/quick", json=request_data)

        if response.status_code == 200:
            workflow = response.json()
            workflow_id = workflow["workflow_id"]
            print(f"✅ Workflow Created: {workflow_id}")

            self.print_step("Step 3: Monitoring Progress")
            final_workflow = self.wait_for_workflow(workflow_id)

            if final_workflow and final_workflow["state"] == "ready":
                self.print_step("Step 4: Downloading Proposal")
                filepath = self.download_proposal(workflow_id)

                self.results.append({
                    "scenario": "Quick Proposal - Healthcare",
                    "workflow_id": workflow_id,
                    "status": "SUCCESS",
                    "output": filepath
                })

                print("\n✅ Scenario 2 Complete!")
            else:
                print("❌ Workflow did not complete")
        else:
            print(f"❌ API Error: {response.status_code}")

    # ==================================================================================
    # SCENARIO 3: QUICK PROPOSAL - Financial Services (Security-Focused)
    # ==================================================================================
    def scenario_quick_proposal_finance(self):
        """Scenario: Financial services company with strong security requirements."""
        self.print_banner("SCENARIO 3: Quick Proposal - Financial Services")

        print("📋 Use Case:")
        print("   A fintech company needs talent intelligence for their security and")
        print("   compliance teams. Strong emphasis on data security, SOC2, and")
        print("   regulatory compliance.\n")

        request_data = {
            "company_name": "SecureBank Fintech",
            "contact_title": "Head of Security & Compliance",
            "industry": "Financial Services",
            "proposal_type": "pitch_deck",
            "additional_context": "Fintech company hiring for cybersecurity, risk management, and "
                                  "compliance roles. Requires SOC2 Type II compliance, data encryption, "
                                  "and audit trails for all talent analytics."
        }

        print(f"Request Data:\n{json.dumps(request_data, indent=2)}")
        response = self.session.post(f"{self.base_url}/api/v1/proposals/quick", json=request_data)

        if response.status_code == 200:
            workflow = response.json()
            workflow_id = workflow["workflow_id"]
            print(f"✅ Workflow Created: {workflow_id}")

            final_workflow = self.wait_for_workflow(workflow_id)

            if final_workflow and final_workflow["state"] == "ready":
                filepath = self.download_proposal(workflow_id)

                self.results.append({
                    "scenario": "Quick Proposal - Finance",
                    "workflow_id": workflow_id,
                    "status": "SUCCESS",
                    "output": filepath
                })

                print("\n✅ Scenario 3 Complete!")
        else:
            print(f"❌ API Error: {response.status_code}")

    # ==================================================================================
    # SCENARIO 4: RFP PROCESSING - Basic Technical RFP
    # ==================================================================================
    def scenario_rfp_processing_basic(self):
        """Scenario: Processing a basic technical RFP."""
        self.print_banner("SCENARIO 4: RFP Processing - Basic Technical RFP")

        print("📋 Use Case:")
        print("   A mid-size technology company has issued an RFP for talent analytics")
        print("   platform. The RFP contains technical requirements, company info, and")
        print("   pricing questions.\n")

        self.print_step("Step 1: Creating Sample RFP Document")

        rfp_content = """
REQUEST FOR PROPOSAL (RFP)
Company: TechVentures Corp
RFP ID: RFP-2024-TV-001

SECTION 1: COMPANY INFORMATION

Q1. Provide a brief overview of your company, including years in business,
    number of employees, and key leadership team members.

Q2. Describe your experience with talent analytics and workforce intelligence
    solutions. Include relevant case studies.

SECTION 2: TECHNICAL REQUIREMENTS

Q3. Describe your platform architecture and technology stack. Is it cloud-based
    or on-premise?

Q4. What security measures and compliance certifications does your platform have
    (e.g., SOC2, ISO 27001, GDPR compliance)?

Q5. Explain your data integration capabilities. Can you integrate with major
    ATS, HRIS, and HCM systems?

Q6. What is your platform's uptime SLA and disaster recovery plan?

SECTION 3: FUNCTIONAL REQUIREMENTS

Q7. Describe your skills taxonomy and how it maps to different job roles and
    industries.

Q8. What workforce analytics and reporting capabilities do you provide?

Q9. Can your system provide real-time labor market insights and talent
    availability data?

SECTION 4: IMPLEMENTATION & SUPPORT

Q10. What is the typical implementation timeline for an organization of 1,000
     employees?

Q11. What training and onboarding support do you provide?

Q12. Describe your customer support model (hours, channels, response times).

SECTION 5: PRICING

Q13. Provide detailed pricing for an organization with 1,000 employees, including
     any setup fees, annual licensing, and per-user costs.

Q14. What is included in the base price, and what features require additional fees?
"""

        # Create temp file
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(rfp_content)
            temp_file = f.name

        print(f"✅ RFP document created ({len(rfp_content)} characters)")
        print(f"   Questions: 14")
        print(f"   Sections: 5 (Company Info, Technical, Functional, Implementation, Pricing)")

        self.print_step("Step 2: Uploading RFP")

        try:
            with open(temp_file, 'rb') as f:
                files = {'file': ('techventures_rfp.txt', f, 'text/plain')}
                data = {'client_name': 'TechVentures Corp', 'industry': 'Technology'}

                response = self.session.post(
                    f"{self.base_url}/api/v1/rfp/upload",
                    files=files,
                    data=data
                )

            if response.status_code == 200:
                result = response.json()
                workflow_id = result["workflow_id"]
                print(f"✅ RFP Uploaded: {workflow_id}")

                self.print_step("Step 3: Processing RFP")
                print("   This will:")
                print("   • Analyze the RFP and extract questions")
                print("   • Categorize questions by type")
                print("   • Retrieve relevant content from knowledge base")
                print("   • Generate responses for each question")
                print("   • Review responses for completeness and compliance")
                print("   • Format final proposal document")
                print("\n   (This may take 60-120 seconds...)")

                final_workflow = self.wait_for_workflow(workflow_id, timeout=180)

                if final_workflow:
                    self.print_step("Step 4: RFP Analysis Results")

                    if final_workflow.get("rfp_analysis"):
                        analysis = final_workflow["rfp_analysis"]
                        print(f"   Total Questions: {analysis['total_questions']}")
                        print(f"   Estimated Effort: {analysis['estimated_effort_hours']} hours")
                        print(f"   Sections: {len(analysis['sections'])}")

                        if analysis.get('sections'):
                            print("\n   Question Breakdown:")
                            for section in analysis['sections']:
                                print(f"   • {section['title']}: {len(section['questions'])} questions")

                    if final_workflow["state"] == "ready":
                        self.print_step("Step 5: Downloading Response")
                        filepath = self.download_proposal(workflow_id)

                        self.results.append({
                            "scenario": "RFP Processing - Basic",
                            "workflow_id": workflow_id,
                            "status": "SUCCESS",
                            "output": filepath
                        })

                        print("\n✅ Scenario 4 Complete!")
                        print("   Result: Complete RFP response document ready for review")
                    elif final_workflow["state"] == "human_review":
                        print("\n⚠️  Workflow requires human review")
                        print("   Some responses may need manual verification")
                    else:
                        print(f"\n⚠️  Workflow ended in state: {final_workflow['state']}")
                else:
                    print("❌ Workflow did not complete")
            else:
                print(f"❌ Upload failed: {response.status_code} - {response.text}")

        finally:
            # Cleanup
            os.unlink(temp_file)

    # ==================================================================================
    # SCENARIO 5: RFP PROCESSING - Complex Healthcare RFP
    # ==================================================================================
    def scenario_rfp_processing_healthcare(self):
        """Scenario: Processing a complex healthcare RFP with compliance requirements."""
        self.print_banner("SCENARIO 5: RFP Processing - Complex Healthcare RFP")

        print("📋 Use Case:")
        print("   A large healthcare system has issued an RFP for clinical workforce")
        print("   management. Requires HIPAA compliance, clinical certifications tracking,")
        print("   and integration with existing healthcare IT systems.\n")

        rfp_content = """
REQUEST FOR PROPOSAL (RFP)
Company: Metropolitan Healthcare System
RFP ID: RFP-2024-MHS-CLINICAL

SECTION 1: COMPLIANCE & SECURITY

Q1. Describe your HIPAA compliance measures and provide evidence of BAA
    (Business Associate Agreement) capabilities.

Q2. What data encryption standards do you use for data at rest and in transit?

Q3. How do you handle PHI (Protected Health Information) in your system?

Q4. Describe your audit logging and monitoring capabilities for compliance reporting.

SECTION 2: CLINICAL WORKFORCE MANAGEMENT

Q5. Can your system track clinical certifications, licenses, and renewal dates
    (RN, LPN, MD, NP, PA, etc.)?

Q6. How does your system handle shift scheduling for clinical staff across
    multiple departments and locations?

Q7. Describe your competency tracking features for clinical skills and procedures.

Q8. Can you provide workforce forecasting for different clinical specialties
    based on patient volume and acuity?

SECTION 3: TECHNICAL INTEGRATION

Q9. What healthcare IT systems can you integrate with (Epic, Cerner, Meditech,
    Workday, etc.)?

Q10. Do you support HL7 and FHIR standards for healthcare data exchange?

Q11. What is your API architecture for custom integrations?

SECTION 4: ANALYTICS & REPORTING

Q12. What workforce analytics do you provide specific to healthcare (e.g.,
     nurse-to-patient ratios, clinical skill gaps, burnout indicators)?

Q13. Can you benchmark our clinical workforce against industry standards?

Q14. Describe your reporting capabilities for Joint Commission, CMS, and other
     regulatory requirements.

SECTION 5: IMPLEMENTATION

Q15. What is the implementation timeline for a healthcare system with 5 hospitals
     and 3,000 clinical staff?

Q16. Describe your data migration approach for existing workforce data.

Q17. What training do you provide for HR, clinical managers, and end users?

SECTION 6: PRICING

Q18. Provide pricing for 3,000 clinical staff across 5 hospital locations.

Q19. Are there additional costs for HIPAA compliance features or healthcare-specific
     integrations?
"""

        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(rfp_content)
            temp_file = f.name

        print(f"✅ Complex RFP created")
        print(f"   Questions: 19")
        print(f"   Focus: Healthcare compliance, clinical workforce, integrations")

        try:
            with open(temp_file, 'rb') as f:
                files = {'file': ('metropolitan_healthcare_rfp.txt', f, 'text/plain')}
                data = {
                    'client_name': 'Metropolitan Healthcare System',
                    'industry': 'Healthcare'
                }

                response = self.session.post(
                    f"{self.base_url}/api/v1/rfp/upload",
                    files=files,
                    data=data
                )

            if response.status_code == 200:
                result = response.json()
                workflow_id = result["workflow_id"]
                print(f"✅ RFP Uploaded: {workflow_id}")

                print("\n⏳ Processing complex healthcare RFP (may take 2-3 minutes)...")
                final_workflow = self.wait_for_workflow(workflow_id, timeout=240)

                if final_workflow and final_workflow["state"] in ["ready", "human_review"]:
                    if final_workflow.get("output_file_path"):
                        filepath = self.download_proposal(workflow_id)

                        self.results.append({
                            "scenario": "RFP Processing - Healthcare",
                            "workflow_id": workflow_id,
                            "status": "SUCCESS",
                            "output": filepath
                        })

                    print("\n✅ Scenario 5 Complete!")
                else:
                    print("❌ Workflow did not complete")
            else:
                print(f"❌ Upload failed: {response.status_code}")

        finally:
            os.unlink(temp_file)

    # ==================================================================================
    # SCENARIO 6: KNOWLEDGE BASE SEARCH
    # ==================================================================================
    def scenario_knowledge_search(self):
        """Scenario: Searching knowledge base for relevant content."""
        self.print_banner("SCENARIO 6: Knowledge Base Search")

        print("📋 Use Case:")
        print("   Sales rep wants to find relevant past proposals and case studies")
        print("   for different topics and industries.\n")

        search_queries = [
            {
                "query": "semiconductor talent intelligence and workforce analytics",
                "context": "Client in semiconductor manufacturing"
            },
            {
                "query": "skills taxonomy implementation for technology companies",
                "context": "Tech client needs skills framework"
            },
            {
                "query": "labor market analysis and hiring trends",
                "context": "Client wants competitive intelligence"
            },
            {
                "query": "pricing models for workforce analytics platforms",
                "context": "Preparing pricing proposal"
            },
            {
                "query": "HIPAA compliance for healthcare workforce management",
                "context": "Healthcare client compliance needs"
            }
        ]

        for i, search in enumerate(search_queries, 1):
            self.print_step(f"Search {i}: {search['context']}")
            print(f"Query: \"{search['query']}\"")

            response = self.session.get(
                f"{self.base_url}/api/v1/knowledge/search",
                params={"query": search["query"], "top_k": 3}
            )

            if response.status_code == 200:
                results = response.json()
                print(f"✅ Found {len(results['results'])} relevant documents")

                for j, result in enumerate(results['results'][:3], 1):
                    print(f"\n   Result {j}:")
                    print(f"   • Relevance Score: {result['score']:.3f}")
                    text_preview = result['text'][:150].replace('\n', ' ')
                    print(f"   • Preview: {text_preview}...")

                    if result.get('metadata'):
                        metadata = result['metadata']
                        if isinstance(metadata, str):
                            try:
                                metadata = json.loads(metadata)
                            except:
                                pass
                        if isinstance(metadata, dict):
                            if metadata.get('client'):
                                print(f"   • Client: {metadata['client']}")
                            if metadata.get('category'):
                                print(f"   • Category: {metadata['category']}")
            else:
                print(f"❌ Search failed: {response.status_code}")

            time.sleep(1)  # Brief pause between searches

        print("\n✅ Scenario 6 Complete!")

    # ==================================================================================
    # SCENARIO 7: CLIENT-SPECIFIC SEARCH
    # ==================================================================================
    def scenario_client_specific_search(self):
        """Scenario: Find all content related to specific clients."""
        self.print_banner("SCENARIO 7: Client-Specific Content Search")

        print("📋 Use Case:")
        print("   Sales rep wants to review all past work and proposals for")
        print("   specific clients before a meeting.\n")

        clients = [
            "ASM",
            "Atlassian",
            "Denso",
            "GMR Group",
            "ARM"
        ]

        for client in clients:
            self.print_step(f"Searching content for: {client}")

            response = self.session.get(
                f"{self.base_url}/api/v1/knowledge/search",
                params={"query": f"{client} proposal case study", "top_k": 5}
            )

            if response.status_code == 200:
                results = response.json()
                print(f"✅ Found {len(results['results'])} documents related to {client}")

                for result in results['results'][:2]:
                    print(f"   • Score: {result['score']:.3f}")
                    text_preview = result['text'][:100].replace('\n', ' ')
                    print(f"     Preview: {text_preview}...")
            else:
                print(f"❌ Search failed for {client}")

            time.sleep(0.5)

        print("\n✅ Scenario 7 Complete!")

    # ==================================================================================
    # RUN ALL SCENARIOS
    # ==================================================================================
    def run_all_scenarios(self):
        """Run all demo scenarios."""
        self.print_banner("AUTOMATED SALES PROPOSAL SYSTEM - COMPREHENSIVE DEMO", "🚀")

        print("This demo will showcase the following scenarios:\n")
        print("1. Quick Proposal - Technology/SaaS Company")
        print("2. Quick Proposal - Healthcare Company (Compliance-Focused)")
        print("3. Quick Proposal - Financial Services (Security-Focused)")
        print("4. RFP Processing - Basic Technical RFP")
        print("5. RFP Processing - Complex Healthcare RFP")
        print("6. Knowledge Base Search")
        print("7. Client-Specific Content Search")
        print("\nTotal estimated time: 5-10 minutes")

        input("\nPress Enter to start the demo...")

        # Check health
        if not self.check_health():
            print("\n❌ System is not healthy. Please start the server first:")
            print("   python main.py")
            return

        # Run scenarios
        try:
            self.scenario_quick_proposal_saas()
            time.sleep(2)

            self.scenario_quick_proposal_healthcare()
            time.sleep(2)

            self.scenario_quick_proposal_finance()
            time.sleep(2)

            self.scenario_rfp_processing_basic()
            time.sleep(2)

            # Uncomment if you want to run the complex healthcare scenario
            # (it takes longer)
            # self.scenario_rfp_processing_healthcare()
            # time.sleep(2)

            self.scenario_knowledge_search()
            time.sleep(2)

            self.scenario_client_specific_search()

        except KeyboardInterrupt:
            print("\n\n⚠️  Demo interrupted by user")
        except Exception as e:
            print(f"\n\n❌ Error during demo: {e}")
            import traceback
            traceback.print_exc()

        # Print summary
        self.print_summary()

    def print_summary(self):
        """Print summary of all results."""
        self.print_banner("DEMO SUMMARY", "🎯")

        print(f"Total Scenarios Run: {len(self.results)}\n")

        for i, result in enumerate(self.results, 1):
            print(f"{i}. {result['scenario']}")
            print(f"   Workflow ID: {result['workflow_id']}")
            print(f"   Status: {result['status']}")
            if result.get('output'):
                print(f"   Output: {result['output']}")
            print()

        if self.results:
            success_count = sum(1 for r in self.results if r['status'] == 'SUCCESS')
            print(f"✅ Success Rate: {success_count}/{len(self.results)} "
                  f"({100*success_count//len(self.results)}%)")

        print("\n" + "=" * 100)
        print("Demo complete! Check the demo_outputs/ directory for generated proposals.")
        print("=" * 100)


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Demo the Automated Sales Proposal System")
    parser.add_argument(
        "--scenario",
        type=str,
        choices=[
            "all",
            "quick-saas",
            "quick-healthcare",
            "quick-finance",
            "rfp-basic",
            "rfp-healthcare",
            "knowledge-search",
            "client-search"
        ],
        default="all",
        help="Which scenario to run"
    )
    parser.add_argument(
        "--base-url",
        type=str,
        default="http://localhost:8000",
        help="Base URL of the API"
    )

    args = parser.parse_args()

    demo = ProposalSystemDemo(base_url=args.base_url)

    # Run selected scenario
    if args.scenario == "all":
        demo.run_all_scenarios()
    elif args.scenario == "quick-saas":
        demo.check_health()
        demo.scenario_quick_proposal_saas()
        demo.print_summary()
    elif args.scenario == "quick-healthcare":
        demo.check_health()
        demo.scenario_quick_proposal_healthcare()
        demo.print_summary()
    elif args.scenario == "quick-finance":
        demo.check_health()
        demo.scenario_quick_proposal_finance()
        demo.print_summary()
    elif args.scenario == "rfp-basic":
        demo.check_health()
        demo.scenario_rfp_processing_basic()
        demo.print_summary()
    elif args.scenario == "rfp-healthcare":
        demo.check_health()
        demo.scenario_rfp_processing_healthcare()
        demo.print_summary()
    elif args.scenario == "knowledge-search":
        demo.check_health()
        demo.scenario_knowledge_search()
    elif args.scenario == "client-search":
        demo.check_health()
        demo.scenario_client_specific_search()


if __name__ == "__main__":
    main()
