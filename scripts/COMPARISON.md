# Comparison: test_system.py vs demo_workflows.py

## Overview

This document compares the original `test_system.py` with the new comprehensive `demo_workflows.py` script.

---

## Feature Comparison

| Feature | test_system.py | demo_workflows.py |
|---------|---------------|-------------------|
| **Purpose** | Basic API testing | Comprehensive scenario demos |
| **Scenarios** | 5 basic tests | 7 detailed use-case scenarios |
| **Documentation** | Inline comments | Full scenario narratives |
| **Industry Focus** | Generic | Industry-specific (SaaS, Healthcare, Finance) |
| **RFP Complexity** | Simple sample | Basic + Complex RFPs |
| **Workflow Tracking** | Basic | Real-time state monitoring |
| **Output Organization** | Current directory | Dedicated `demo_outputs/` folder |
| **Client Context** | Minimal | Detailed business context |
| **Search Demos** | Basic search | Semantic + Client-specific search |
| **CLI Options** | None | Multiple scenario selection |
| **Progress Display** | Basic print | Formatted banners and steps |
| **Result Summary** | None | Comprehensive summary report |
| **Reusability** | One-off test | Repeatable demo scenarios |

---

## Detailed Comparison

### 1. Health Check

#### test_system.py
```python
def test_health_check():
    """Test health check endpoint."""
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 200
    print("✅ Health check passed!")
```

#### demo_workflows.py
```python
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
    except Exception as e:
        print(f"❌ Cannot connect to system: {e}")
        return False
```

**Improvements:**
- Returns boolean for conditional execution
- More detailed service status
- Exception handling with user-friendly messages
- Used as pre-flight check for all scenarios

---

### 2. Quick Proposal Generation

#### test_system.py
```python
def test_quick_proposal():
    """Test quick proposal generation."""
    request_data = {
        "company_name": "Microsoft",
        "contact_title": "VP of Talent Acquisition",
        "industry": "Technology",
        "proposal_type": "pitch_deck",
        "additional_context": "Interested in AI-powered recruitment solutions",
    }
    # ... basic API call
```

#### demo_workflows.py
```python
def scenario_quick_proposal_saas(self):
    """Scenario: Sales rep needs a quick proposal for a SaaS company."""
    self.print_banner("SCENARIO 1: Quick Proposal - Technology/SaaS Company")

    print("📋 Use Case:")
    print("   A sales rep is meeting with a VP of Engineering at a fast-growing")
    print("   SaaS company. They need a tailored pitch deck highlighting talent")
    print("   intelligence solutions for scaling their engineering team.\n")

    # Detailed business context
    request_data = {
        "company_name": "TechScale Inc",
        "contact_title": "VP of Engineering",
        "industry": "Technology - SaaS",
        "proposal_type": "pitch_deck",
        "additional_context": "Fast-growing SaaS company scaling from 50 to 200 engineers. "
                              "Interested in talent intelligence and skills taxonomy for tech roles."
    }
    # ... workflow monitoring, download, result tracking
```

**Improvements:**
- Real business use case narrative
- Detailed context and motivations
- Step-by-step progress display
- Workflow state monitoring
- Automatic download and file organization
- Result tracking for summary report
- Multiple industry variants (SaaS, Healthcare, Finance)

---

### 3. RFP Processing

#### test_system.py
- Simple 6-question RFP
- Generic questions
- No industry focus
- Basic processing

#### demo_workflows.py
- **Basic RFP**: 14 questions across 5 sections
- **Complex RFP**: 19 questions with healthcare specifics
- Industry-specific terminology and requirements
- Multi-section organization:
  - Company Information
  - Technical Requirements
  - Functional Requirements
  - Implementation & Support
  - Pricing
- Compliance considerations (HIPAA, SOC2)
- Technical integrations (Epic, Cerner, HL7, FHIR)
- Detailed analysis reporting

**Example - Complex Healthcare RFP:**
```python
rfp_content = """
REQUEST FOR PROPOSAL (RFP)
Company: Metropolitan Healthcare System
RFP ID: RFP-2024-MHS-CLINICAL

SECTION 1: COMPLIANCE & SECURITY
Q1. Describe your HIPAA compliance measures...
Q2. What data encryption standards do you use...
...

SECTION 2: CLINICAL WORKFORCE MANAGEMENT
Q5. Can your system track clinical certifications...
...
"""
```

This reflects real-world RFP complexity.

---

### 4. Knowledge Base Search

#### test_system.py
```python
def test_search_knowledge():
    query = "cloud security and encryption"
    response = requests.get(f"{BASE_URL}/api/v1/knowledge/search",
                           params={"query": query, "top_k": 3})
    # Basic result display
```

#### demo_workflows.py
```python
def scenario_knowledge_search(self):
    """Demonstrate semantic search across multiple topics."""
    search_queries = [
        {
            "query": "semiconductor talent intelligence and workforce analytics",
            "context": "Client in semiconductor manufacturing"
        },
        {
            "query": "skills taxonomy implementation for technology companies",
            "context": "Tech client needs skills framework"
        },
        # ... 5 different search scenarios
    ]

    for search in search_queries:
        # Contextual search with business motivation
        # Detailed result display with metadata
        # Relevance score interpretation
```

**Improvements:**
- Multiple search topics
- Business context for each search
- Relevance score display
- Metadata extraction (client, category, source)
- Use-case driven (pre-meeting research)

---

### 5. Workflow Monitoring

#### test_system.py
- No workflow monitoring
- Synchronous processing only
- No state visibility

#### demo_workflows.py
```python
def wait_for_workflow(self, workflow_id: str, timeout: int = 120) -> Dict:
    """Poll workflow status until completion or timeout."""
    start_time = time.time()
    last_state = None

    while time.time() - start_time < timeout:
        response = self.session.get(f"{self.base_url}/api/v1/workflows/{workflow_id}")
        if response.status_code == 200:
            workflow = response.json()
            current_state = workflow["state"]

            # Show state transitions in real-time
            if current_state != last_state:
                print(f"   State: {current_state.upper()}")
                last_state = current_state
```

**Features:**
- Real-time state monitoring
- Timeout handling
- State transition display
- Background processing support
- Detailed workflow result inspection

---

### 6. Client-Specific Search

#### test_system.py
- Not available

#### demo_workflows.py
```python
def scenario_client_specific_search(self):
    """Find all content related to specific clients."""
    clients = ["ASM", "Atlassian", "Denso", "GMR Group", "ARM"]

    for client in clients:
        # Search all historical content for this client
        # Display past proposals and case studies
        # Show client relationship history
```

**Use Case:**
- Preparing for client renewal meetings
- Understanding engagement history
- Identifying upsell opportunities
- Maintaining consistency across touchpoints

---

### 7. Output Management

#### test_system.py
```python
# Saves to current directory with timestamp
output_filename = f"test_proposal_{int(time.time())}.docx"
with open(output_filename, "wb") as f:
    f.write(download_response.content)
```

#### demo_workflows.py
```python
def download_proposal(self, workflow_id: str, output_dir: str = "./demo_outputs"):
    """Download generated proposal with organized file management."""
    os.makedirs(output_dir, exist_ok=True)
    filename = f"{workflow_id}.docx"
    filepath = os.path.join(output_dir, filename)
    # ... download and save
    return filepath
```

**Improvements:**
- Dedicated output directory
- Workflow ID-based naming (traceable)
- Directory auto-creation
- Organized file structure
- Easy to find and review

---

### 8. Result Reporting

#### test_system.py
- No summary
- No result tracking
- No success metrics

#### demo_workflows.py
```python
def print_summary(self):
    """Print comprehensive summary of all results."""
    print(f"Total Scenarios Run: {len(self.results)}\n")

    for i, result in enumerate(self.results, 1):
        print(f"{i}. {result['scenario']}")
        print(f"   Workflow ID: {result['workflow_id']}")
        print(f"   Status: {result['status']}")
        print(f"   Output: {result['output']}")

    success_count = sum(1 for r in self.results if r['status'] == 'SUCCESS')
    print(f"✅ Success Rate: {success_count}/{len(self.results)} "
          f"({100*success_count//len(self.results)}%)")
```

**Output:**
```
🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯
  DEMO SUMMARY
🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯🎯

Total Scenarios Run: 5

1. Quick Proposal - SaaS
   Workflow ID: WF-QUICK-20240116120000
   Status: SUCCESS
   Output: demo_outputs/WF-QUICK-20240116120000.docx

2. Quick Proposal - Healthcare
   Workflow ID: WF-QUICK-20240116120100
   Status: SUCCESS
   Output: demo_outputs/WF-QUICK-20240116120100.docx

...

✅ Success Rate: 5/5 (100%)
```

---

### 9. CLI Interface

#### test_system.py
```python
# No CLI arguments
# Always runs all tests
if __name__ == "__main__":
    main()
```

#### demo_workflows.py
```python
parser = argparse.ArgumentParser(description="Demo the Automated Sales Proposal System")
parser.add_argument(
    "--scenario",
    type=str,
    choices=["all", "quick-saas", "quick-healthcare", "quick-finance",
             "rfp-basic", "rfp-healthcare", "knowledge-search", "client-search"],
    default="all",
    help="Which scenario to run"
)
parser.add_argument("--base-url", type=str, default="http://localhost:8000")
```

**Usage:**
```bash
# Run specific scenario
python scripts/demo_workflows.py --scenario quick-saas

# Run against different server
python scripts/demo_workflows.py --base-url http://staging.example.com

# Run all with custom server
python scripts/demo_workflows.py --scenario all --base-url http://prod.example.com
```

---

### 10. User Experience

#### test_system.py
```
Testing Health Check
Status Code: 200
Response: {...}
✅ Health check passed!
```

#### demo_workflows.py
```
====================================================================================================
  SCENARIO 1: Quick Proposal - Technology/SaaS Company
====================================================================================================

📋 Use Case:
   A sales rep is meeting with a VP of Engineering at a fast-growing
   SaaS company. They need a tailored pitch deck highlighting talent
   intelligence solutions for scaling their engineering team.

➤➤➤ Step 1: Creating Quick Proposal Request
--------------------------------------------------------------------------------
Request Data:
{
  "company_name": "TechScale Inc",
  ...
}

➤➤➤ Step 2: Submitting to API
--------------------------------------------------------------------------------
✅ Workflow Created: WF-QUICK-20240116120000

➤➤➤ Step 3: Monitoring Workflow Progress
--------------------------------------------------------------------------------
   State: ANALYZING
   State: GENERATING
   State: REVIEWING
   State: FORMATTING
   State: READY

➤➤➤ Step 4: Downloading Proposal
--------------------------------------------------------------------------------
✅ Proposal downloaded: demo_outputs/WF-QUICK-20240116120000.docx

✅ Scenario 1 Complete!
   Result: Sales rep has a customized pitch deck ready for the meeting
```

**UX Improvements:**
- Visual banners and separators
- Step-by-step progress
- Clear business context
- Real-time state updates
- Success/error indicators
- Outcome explanation

---

## When to Use Each

### Use `test_system.py` when:
- Quick API validation needed
- Testing basic functionality
- Debugging individual endpoints
- Development testing

### Use `demo_workflows.py` when:
- Demonstrating to stakeholders
- Showcasing different use cases
- Testing end-to-end workflows
- Generating sample outputs for review
- Training new users
- Validating business scenarios

---

## Migration Guide

To transition from test_system.py patterns to demo_workflows.py:

1. **Add Business Context**
   ```python
   # Before
   request_data = {"company_name": "Test Corp"}

   # After
   print("📋 Use Case: Sales rep meeting with...")
   request_data = {
       "company_name": "TechScale Inc",
       "additional_context": "Fast-growing SaaS company..."
   }
   ```

2. **Add Progress Tracking**
   ```python
   # Before
   response = requests.post(...)
   print(response.json())

   # After
   self.print_step("Step 1: Creating Request")
   response = requests.post(...)
   workflow = self.wait_for_workflow(workflow_id)
   ```

3. **Organize Outputs**
   ```python
   # Before
   with open("output.docx", "wb") as f:
       f.write(content)

   # After
   filepath = self.download_proposal(workflow_id, output_dir="./demo_outputs")
   self.results.append({"scenario": "...", "output": filepath})
   ```

4. **Add Summary Reporting**
   ```python
   # After all scenarios
   self.print_summary()
   ```

---

## Conclusion

The `demo_workflows.py` script builds upon `test_system.py` by:

✅ Adding business context and narratives
✅ Providing industry-specific scenarios
✅ Implementing real-time workflow monitoring
✅ Organizing outputs systematically
✅ Supporting CLI-based scenario selection
✅ Generating comprehensive summary reports
✅ Improving user experience with clear progress display
✅ Enabling repeatable, presentable demos

**Bottom Line:** `test_system.py` is for testing, `demo_workflows.py` is for demonstrating.
