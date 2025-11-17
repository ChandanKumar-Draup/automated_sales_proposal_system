# Demo Scenarios - Automated Sales Proposal System

This document describes the comprehensive demo scenarios for the Automated Sales Proposal System. These scenarios showcase the different functionalities and real-world use cases of the system.

## Prerequisites

1. **Start the API Server:**
   ```bash
   python main.py
   ```
   The server should be running on `http://localhost:8000`

2. **Verify Embeddings:**
   ```bash
   python scripts/validate_embeddings.py
   ```
   Ensure you have 587+ documents indexed

3. **Install Dependencies:**
   ```bash
   pip install requests
   ```

## Running the Demo

### Run All Scenarios
```bash
python scripts/demo_workflows.py --scenario all
```

### Run Individual Scenarios
```bash
# Quick proposal for SaaS company
python scripts/demo_workflows.py --scenario quick-saas

# Quick proposal for healthcare
python scripts/demo_workflows.py --scenario quick-healthcare

# Quick proposal for finance
python scripts/demo_workflows.py --scenario quick-finance

# Basic RFP processing
python scripts/demo_workflows.py --scenario rfp-basic

# Complex healthcare RFP
python scripts/demo_workflows.py --scenario rfp-healthcare

# Knowledge base search
python scripts/demo_workflows.py --scenario knowledge-search

# Client-specific search
python scripts/demo_workflows.py --scenario client-search
```

## Scenario Descriptions

### 🚀 Scenario 1: Quick Proposal - Technology/SaaS Company

**Use Case:** A sales rep is meeting with a VP of Engineering at a fast-growing SaaS company. They need a tailored pitch deck highlighting talent intelligence solutions for scaling their engineering team.

**What It Demonstrates:**
- Quick proposal generation (fast-track pipeline)
- Industry-specific customization (Technology/SaaS)
- Role-based targeting (VP of Engineering)
- Integration with knowledge base for relevant content

**Input:**
- Company: TechScale Inc
- Contact: VP of Engineering
- Industry: Technology - SaaS
- Context: Scaling from 50 to 200 engineers, interested in talent intelligence and skills taxonomy

**Expected Output:**
- Customized pitch deck document (.docx)
- 3-5 slides covering company overview, solution highlights, case studies, and next steps
- Workflow completed in ~30-60 seconds

**API Endpoint:** `POST /api/v1/proposals/quick`

---

### 🏥 Scenario 2: Quick Proposal - Healthcare Company

**Use Case:** A healthcare provider network needs workforce analytics for nursing and clinical staff, with HIPAA compliance requirements.

**What It Demonstrates:**
- Compliance-focused proposals
- Healthcare industry expertise
- Regulatory requirement handling (HIPAA)
- Clinical workforce specialization

**Input:**
- Company: HealthFirst Medical Group
- Contact: Chief Nursing Officer
- Industry: Healthcare
- Context: 500+ nurses, requires HIPAA-compliant workforce analytics

**Expected Output:**
- Healthcare-specific proposal with compliance sections
- Emphasis on data security and regulatory adherence
- Clinical certifications and skills tracking

**Key Features Highlighted:**
- HIPAA compliance
- Secure data handling
- Clinical skills taxonomy
- Workforce retention analysis

---

### 💰 Scenario 3: Quick Proposal - Financial Services

**Use Case:** A fintech company needs talent intelligence for security and compliance teams, with strong emphasis on data security.

**What It Demonstrates:**
- Security-focused proposals
- Regulatory compliance (SOC2, financial regulations)
- Risk management considerations
- Audit trail capabilities

**Input:**
- Company: SecureBank Fintech
- Contact: Head of Security & Compliance
- Industry: Financial Services
- Context: Hiring for cybersecurity, risk, and compliance roles

**Expected Output:**
- Security-centric proposal
- SOC2 Type II compliance details
- Data encryption and audit capabilities
- Financial services case studies

---

### 📄 Scenario 4: RFP Processing - Basic Technical RFP

**Use Case:** A mid-size technology company has issued a 14-question RFP covering technical requirements, company information, and pricing.

**What It Demonstrates:**
- **End-to-end RFP workflow:**
  1. Document upload and text extraction
  2. Question identification and categorization
  3. Content retrieval from knowledge base
  4. Response generation per question
  5. Quality review and compliance check
  6. Document formatting and generation

**RFP Structure:**
- **Section 1:** Company Information (2 questions)
- **Section 2:** Technical Requirements (4 questions)
- **Section 3:** Functional Requirements (3 questions)
- **Section 4:** Implementation & Support (3 questions)
- **Section 5:** Pricing (2 questions)

**What the System Does:**
1. **Analyzer Agent:** Parses RFP, extracts questions, categorizes by type
2. **Retriever Agent:** Searches knowledge base for relevant past responses
3. **Generator Agent:** Creates customized responses using retrieved content
4. **Reviewer Agent:** Checks completeness, compliance, and confidence levels
5. **Formatter Agent:** Creates professional Word document

**Expected Output:**
- Complete RFP response document
- 14 detailed answers
- Processing time: ~60-120 seconds
- Workflow state tracking at each step

**Sample Questions Addressed:**
- Company overview and experience
- Platform architecture and security
- Integration capabilities
- Skills taxonomy functionality
- Implementation timeline
- Pricing structure

---

### 🏥 Scenario 5: RFP Processing - Complex Healthcare RFP

**Use Case:** A large healthcare system with 5 hospitals needs clinical workforce management with HIPAA compliance, clinical certifications tracking, and healthcare IT integration.

**What It Demonstrates:**
- Complex, multi-section RFP handling
- Domain-specific expertise (healthcare)
- Technical integration requirements (Epic, Cerner, HL7, FHIR)
- Compliance and regulatory considerations

**RFP Structure:**
- **Section 1:** Compliance & Security (4 questions)
- **Section 2:** Clinical Workforce Management (4 questions)
- **Section 3:** Technical Integration (3 questions)
- **Section 4:** Analytics & Reporting (3 questions)
- **Section 5:** Implementation (3 questions)
- **Section 6:** Pricing (2 questions)

**Complex Requirements:**
- HIPAA/BAA compliance
- Clinical certifications tracking (RN, LPN, MD, NP, PA)
- Shift scheduling across multiple locations
- Integration with Epic, Cerner, Meditech
- HL7 and FHIR standards support
- Regulatory reporting (Joint Commission, CMS)

**Expected Output:**
- Comprehensive RFP response
- 19 detailed answers
- Healthcare-specific technical details
- Processing time: ~2-3 minutes

**What Makes This Complex:**
- Higher question count (19 vs 14)
- Industry-specific terminology
- Multiple compliance frameworks
- Technical integration requirements
- Multi-location deployment considerations

---

### 🔍 Scenario 6: Knowledge Base Search

**Use Case:** Sales rep wants to find relevant past proposals and case studies for different topics before client meetings.

**What It Demonstrates:**
- Semantic search capabilities
- Vector similarity search with FAISS
- Relevance scoring
- Multi-domain knowledge retrieval

**Search Topics:**
1. **Semiconductor talent intelligence** - Manufacturing industry use case
2. **Skills taxonomy implementation** - Technology companies
3. **Labor market analysis** - Competitive intelligence
4. **Pricing models** - Financial proposals
5. **HIPAA compliance** - Healthcare requirements

**Expected Output:**
- Top 3 most relevant documents per query
- Relevance scores (0-1 scale)
- Text previews
- Metadata (client, category, source)

**How It Works:**
- Query text is embedded using the same model as documents
- FAISS performs vector similarity search
- Results are ranked by cosine similarity
- Metadata helps identify source context

**Example Result:**
```
Query: "semiconductor talent intelligence"
✅ Found 3 relevant documents

Result 1:
• Relevance Score: 0.543
• Preview: "Majority of hardware semiconductor talent is concentrated..."
• Client: ARM
• Category: talent_intelligence
```

---

### 👥 Scenario 7: Client-Specific Content Search

**Use Case:** Sales rep is preparing for a meeting with an existing client and wants to review all past work and proposals for that client.

**What It Demonstrates:**
- Client-centric knowledge retrieval
- Historical proposal review
- Relationship context building
- Client-specific customization

**Clients Searched:**
- ASM
- Atlassian
- Denso
- GMR Group
- ARM

**Expected Output:**
- All documents related to each client
- Past proposals and case studies
- Client-specific insights
- Success stories and outcomes

**Use Cases:**
- Preparing for renewal discussions
- Identifying upsell opportunities
- Understanding past engagement history
- Maintaining consistency across interactions

---

## System Architecture Demonstrated

### Agent Orchestration
The demo showcases how the `OrchestratorAgent` coordinates multiple specialized agents:

```
OrchestratorAgent
├── AnalyzerAgent (RFP analysis, question extraction)
├── RetrieverAgent (Knowledge base search)
├── GeneratorAgent (Response generation)
├── ReviewerAgent (Quality assurance)
└── FormatterAgent (Document creation)
```

### Workflow States
Each workflow progresses through these states:

1. **CREATED** - Workflow initialized
2. **ANALYZING** - Parsing input and extracting requirements
3. **GENERATING** - Creating responses
4. **REVIEWING** - Quality and compliance checks
5. **HUMAN_REVIEW** - Requires manual review (if needed)
6. **FORMATTING** - Creating final document
7. **READY** - Complete and available for download

### API Endpoints Tested

| Endpoint | Method | Purpose | Scenario |
|----------|--------|---------|----------|
| `/health` | GET | System health check | All |
| `/api/v1/proposals/quick` | POST | Quick proposal generation | 1, 2, 3 |
| `/api/v1/rfp/upload` | POST | Upload and process RFP | 4, 5 |
| `/api/v1/workflows/{id}` | GET | Check workflow status | All |
| `/api/v1/download/{id}` | GET | Download proposal | 1-5 |
| `/api/v1/knowledge/search` | GET | Search knowledge base | 6, 7 |

---

## Performance Benchmarks

Based on the demo scenarios:

| Operation | Average Time | Notes |
|-----------|--------------|-------|
| Quick Proposal | 30-60 seconds | Depends on LLM latency |
| Basic RFP (14Q) | 60-120 seconds | ~5-10s per question |
| Complex RFP (19Q) | 120-180 seconds | More questions + complexity |
| Knowledge Search | 5-10ms | FAISS is very fast |
| Document Generation | 5-10 seconds | DOCX formatting |

**Total Demo Time:** 5-10 minutes for all scenarios

---

## Output Files

All generated proposals are saved to:
```
./demo_outputs/
├── WF-QUICK-20240116120000.docx
├── WF-QUICK-20240116120100.docx
├── WF-RFP-20240116120200.docx
└── ...
```

Each file is named with the workflow ID for traceability.

---

## Interpreting Results

### Success Indicators
✅ Workflow state reaches `READY`
✅ Output file is generated
✅ No critical errors in review
✅ Confidence scores are reasonable (>0.6)

### Warning Signs
⚠️ Workflow state is `HUMAN_REVIEW` - Some responses need manual verification
⚠️ Low confidence scores (<0.5) - Content may need refinement
⚠️ Missing required content - Knowledge base gaps identified

### Error Conditions
❌ Workflow fails - System error or configuration issue
❌ No relevant content found - Knowledge base needs updating
❌ API connection error - Server not running

---

## Extending the Demo

### Add Your Own Scenarios

1. **Create a new scenario method:**
   ```python
   def scenario_your_custom_case(self):
       self.print_banner("SCENARIO X: Your Custom Case")
       # Your test logic
   ```

2. **Add to the scenario list:**
   ```python
   parser.add_argument("--scenario", choices=[..., "custom"])
   ```

3. **Run it:**
   ```bash
   python scripts/demo_workflows.py --scenario custom
   ```

### Modify Existing Scenarios

Edit the RFP content, client information, or search queries in `demo_workflows.py` to test different variations.

---

## Troubleshooting

### Server Not Running
```
❌ ERROR: Could not connect to server
```
**Solution:** Start the server: `python main.py`

### Timeout Issues
```
⚠️ Workflow timeout after 120s
```
**Solution:**
- Check LLM API credentials
- Increase timeout parameter
- Check network connectivity

### No Results Found
```
❌ Search failed or returned 0 results
```
**Solution:**
- Run `python scripts/validate_embeddings.py`
- Check vector store path in config
- Verify documents are embedded

### Authentication Errors
```
❌ API Error: 401 Unauthorized
```
**Solution:**
- Check `.env` file has correct API keys
- Verify `ANTHROPIC_API_KEY` is set
- Ensure API key has sufficient credits

---

## Next Steps

After running the demo:

1. **Review Generated Proposals** - Check `demo_outputs/` directory
2. **Analyze Workflow Results** - Review confidence scores and review flags
3. **Test with Real RFPs** - Upload actual RFP documents
4. **Expand Knowledge Base** - Add more past proposals using `/api/v1/knowledge/add`
5. **Customize for Your Use Case** - Modify prompts and templates

---

## Additional Resources

- **API Documentation:** http://localhost:8000/docs
- **System Architecture:** See `claude.md`
- **Quick Start Guide:** See `QUICKSTART.md`
- **Embedding Validation:** `scripts/validate_embeddings.py`

---

## Questions or Issues?

If you encounter any issues or have questions:

1. Check the server logs for error messages
2. Verify all dependencies are installed
3. Ensure embeddings are properly loaded (587 documents)
4. Check API key configuration in `.env`

Happy demoing! 🚀
