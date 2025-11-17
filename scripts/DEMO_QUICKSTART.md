# Demo Quick Start Guide

## TL;DR - Run the Demo in 3 Steps

```bash
# 1. Start the API server (in one terminal)
python main.py

# 2. Run the demo (in another terminal)
./scripts/run_demo.sh

# 3. Check the outputs
ls demo_outputs/
```

---

## Quick Commands

### Interactive Menu
```bash
./scripts/run_demo.sh
```

### Run Specific Scenario
```bash
# Quick proposals
python scripts/demo_workflows.py --scenario quick-saas
python scripts/demo_workflows.py --scenario quick-healthcare
python scripts/demo_workflows.py --scenario quick-finance

# RFP processing
python scripts/demo_workflows.py --scenario rfp-basic
python scripts/demo_workflows.py --scenario rfp-healthcare

# Knowledge base
python scripts/demo_workflows.py --scenario knowledge-search
python scripts/demo_workflows.py --scenario client-search

# Run everything
python scripts/demo_workflows.py --scenario all
```

### Using the Shell Script
```bash
# Run with menu
./scripts/run_demo.sh

# Run specific scenario directly
./scripts/run_demo.sh 1    # SaaS
./scripts/run_demo.sh 4    # Basic RFP
./scripts/run_demo.sh 8    # All scenarios
```

---

## What Each Scenario Does

| Scenario | Time | What It Shows |
|----------|------|---------------|
| **quick-saas** | ~30s | Fast proposal for tech company |
| **quick-healthcare** | ~30s | HIPAA-compliant healthcare proposal |
| **quick-finance** | ~30s | Security-focused finance proposal |
| **rfp-basic** | ~90s | Process 14-question technical RFP |
| **rfp-healthcare** | ~2m | Process 19-question complex healthcare RFP |
| **knowledge-search** | ~10s | Search knowledge base by topic |
| **client-search** | ~5s | Find all content for specific clients |
| **all** | ~5-10m | Run all scenarios sequentially |

---

## Expected Output

### Terminal Output
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
  "contact_title": "VP of Engineering",
  "industry": "Technology - SaaS",
  "proposal_type": "pitch_deck",
  "additional_context": "Fast-growing SaaS company..."
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

### File Outputs
```
demo_outputs/
├── WF-QUICK-20240116120000.docx    # SaaS proposal
├── WF-QUICK-20240116120100.docx    # Healthcare proposal
├── WF-QUICK-20240116120200.docx    # Finance proposal
├── WF-RFP-20240116120300.docx      # Basic RFP response
└── WF-RFP-20240116120400.docx      # Healthcare RFP response
```

Each file is a complete Word document ready to review and send to clients.

---

## Monitoring Workflow Progress

The demo shows real-time workflow state transitions:

```
CREATED → ANALYZING → GENERATING → REVIEWING → FORMATTING → READY
   ↓                                              ↓
   └─────────────────────────────────────────────┴→ HUMAN_REVIEW (if needed)
```

- **ANALYZING**: Parsing RFP, extracting questions
- **GENERATING**: Creating responses using AI and knowledge base
- **REVIEWING**: Quality checks and compliance validation
- **FORMATTING**: Creating Word document
- **READY**: Complete and available for download
- **HUMAN_REVIEW**: Requires manual verification (low confidence responses)

---

## Interpreting Results

### ✅ Success
```
✅ Workflow Created: WF-QUICK-20240116120000
✅ Proposal downloaded: demo_outputs/WF-QUICK-20240116120000.docx
✅ Scenario Complete!
```

### ⚠️ Warning
```
⚠️ Workflow requires human review
   Some responses may need manual verification
```
This is normal for complex RFPs. The system flagged low-confidence responses for review.

### ❌ Error
```
❌ API Error: 500 - Failed to create proposal
❌ Cannot connect to server
```
Check:
- Is the server running? (`python main.py`)
- Are embeddings loaded? (`python scripts/validate_embeddings.py`)
- Do you have API keys configured? (check `.env`)

---

## Common Issues

### Problem: Server not running
```
❌ Cannot connect to system: Connection refused
```
**Solution:**
```bash
# Terminal 1 - Start server
python main.py

# Terminal 2 - Run demo
./scripts/run_demo.sh
```

### Problem: Embeddings not found
```
❌ Vector store not found
```
**Solution:**
```bash
python scripts/create_embeddings.py
python scripts/validate_embeddings.py
```

### Problem: API timeout
```
⚠️ Workflow timeout after 120s
```
**Solution:**
- Check your API key credits
- Try running a simpler scenario first (quick-saas)
- Check network connectivity
- Look at server logs for errors

---

## Demo Tips

### 🎯 For Quick Demos (5 minutes)
Run just the quick proposal scenarios:
```bash
python scripts/demo_workflows.py --scenario quick-saas
python scripts/demo_workflows.py --scenario knowledge-search
```

### 🎯 For Comprehensive Demos (10 minutes)
Run all scenarios:
```bash
python scripts/demo_workflows.py --scenario all
```

### 🎯 For Technical Audiences
Focus on RFP processing to show the full workflow:
```bash
python scripts/demo_workflows.py --scenario rfp-basic
```

### 🎯 For Business Audiences
Focus on quick proposals to show ease of use:
```bash
./scripts/run_demo.sh 1
./scripts/run_demo.sh 2
./scripts/run_demo.sh 3
```

---

## Next Steps After Demo

1. **Review Generated Proposals**
   ```bash
   open demo_outputs/  # macOS
   # or
   xdg-open demo_outputs/  # Linux
   # or
   explorer demo_outputs  # Windows
   ```

2. **Try with Your Own RFP**
   - Save your RFP as a .txt, .pdf, or .docx file
   - Use the upload endpoint:
     ```bash
     curl -X POST "http://localhost:8000/api/v1/rfp/upload" \
       -F "file=@your_rfp.pdf" \
       -F "client_name=Your Client" \
       -F "industry=Your Industry"
     ```

3. **Explore the API**
   - Open http://localhost:8000/docs in your browser
   - Try different endpoints interactively
   - View request/response schemas

4. **Add Your Own Knowledge**
   ```bash
   curl -X POST "http://localhost:8000/api/v1/knowledge/add" \
     -H "Content-Type: application/json" \
     -d '{"text": "Your past proposal content...", "metadata": {...}}'
   ```

---

## Customizing the Demo

### Change the Client Names
Edit `scripts/demo_workflows.py`:
```python
request_data = {
    "company_name": "Your Company Name",  # Change this
    "contact_title": "Your Contact",      # Change this
    "industry": "Your Industry",          # Change this
    ...
}
```

### Modify RFP Content
The RFP content is defined in the scenario methods. Search for `rfp_content = """` and customize the questions.

### Add New Scenarios
Copy an existing scenario method and modify:
```python
def scenario_your_custom_case(self):
    self.print_banner("SCENARIO X: Your Custom Case")
    # Your custom logic here
```

---

## Performance Notes

- **Quick Proposals**: 30-60 seconds (depends on LLM API latency)
- **Basic RFP (14 questions)**: 60-120 seconds (~5-10s per question)
- **Complex RFP (19 questions)**: 120-180 seconds
- **Knowledge Search**: 5-10ms (FAISS is very fast)

**Bottleneck**: LLM API calls (generation step). This could be optimized with:
- Parallel question processing
- Caching common responses
- Faster model selection (e.g., Claude Haiku)

---

## Demo Checklist

Before starting the demo:

- [ ] Server is running (`python main.py`)
- [ ] Embeddings are loaded (587 documents)
- [ ] API keys are configured (`.env` file)
- [ ] Output directory exists (`mkdir -p demo_outputs`)
- [ ] You have ~5-10 minutes for full demo
- [ ] You can access http://localhost:8000/health

After the demo:

- [ ] Check `demo_outputs/` for generated files
- [ ] Review workflow results and confidence scores
- [ ] Note any "HUMAN_REVIEW" flags
- [ ] Share generated proposals with stakeholders

---

## Questions?

- **API Documentation**: http://localhost:8000/docs
- **Full Scenario Details**: See `DEMO_SCENARIOS.md`
- **System Architecture**: See `claude.md`
- **Troubleshooting**: Check server logs in terminal

Happy demoing! 🚀
