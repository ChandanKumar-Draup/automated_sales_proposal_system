# 🚀 Quick Start Guide

Get the Automated Sales Proposal System running in 5 minutes!

## Step 1: Install Dependencies (2 minutes)

```bash
cd automated_sales_proposal_system

# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Step 2: Configure API Key (1 minute)

```bash
# Copy example env file
cp .env.example .env

# Edit .env and add your API key
# For OpenAI:
echo "OPENAI_API_KEY=your_key_here" >> .env

# OR for Anthropic:
echo "ANTHROPIC_API_KEY=your_key_here" >> .env
echo "DEFAULT_LLM_PROVIDER=anthropic" >> .env
```

## Step 3: Start the Server (30 seconds)

```bash
python main.py
```

You should see:
```
🚀 Automated Sales Proposal System
Starting server on 0.0.0.0:8000
```

## Step 4: Test It! (1 minute)

Open another terminal and run:

```bash
# Activate venv in new terminal
source venv/bin/activate

# Run tests
python test_system.py
```

Or test manually:

```bash
# Quick proposal generation
curl -X POST "http://localhost:8000/api/v1/proposals/quick" \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "Microsoft",
    "contact_title": "VP of Talent Acquisition",
    "industry": "Technology"
  }'
```

## Step 5: View API Docs

Open in browser: http://localhost:8000/docs

You'll see interactive API documentation where you can test all endpoints!

## Common Use Cases

### Use Case 1: Generate Quick Proposal

```python
import requests

response = requests.post("http://localhost:8000/api/v1/proposals/quick", json={
    "company_name": "Acme Corp",
    "contact_title": "CEO",
    "industry": "Healthcare"
})

workflow_id = response.json()["workflow_id"]
print(f"Proposal generated! Workflow ID: {workflow_id}")

# Download the proposal
download = requests.get(f"http://localhost:8000/api/v1/download/{workflow_id}")
with open("proposal.docx", "wb") as f:
    f.write(download.content)
```

### Use Case 2: Process RFP Document

```python
import requests

with open("rfp.pdf", "rb") as f:
    response = requests.post(
        "http://localhost:8000/api/v1/rfp/upload",
        files={"file": f},
        data={"client_name": "Acme Corp", "industry": "Healthcare"}
    )

workflow_id = response.json()["workflow_id"]
print(f"RFP processing started! Workflow ID: {workflow_id}")

# Check status
status = requests.get(f"http://localhost:8000/api/v1/workflows/{workflow_id}")
print(status.json())
```

### Use Case 3: Add Knowledge to Vector Store

```python
import requests

# Add past proposal content
requests.post("http://localhost:8000/api/v1/knowledge/add", params={
    "text": "Our security solution includes AES-256 encryption, MFA, and 24/7 monitoring.",
    "metadata": '{"source": "RFP-2024-001", "industry": "Technology", "win_outcome": true}'
})

# Search the knowledge base
results = requests.get("http://localhost:8000/api/v1/knowledge/search", params={
    "query": "cloud security",
    "top_k": 5
})
print(results.json())
```

## Troubleshooting

### "Connection refused"
- Make sure the server is running: `python main.py`
- Check it's on port 8000: http://localhost:8000/health

### "API key not found"
- Make sure `.env` file exists
- Add your API key: `OPENAI_API_KEY=sk-...`

### "Module not found"
- Make sure venv is activated: `source venv/bin/activate`
- Reinstall dependencies: `pip install -r requirements.txt`

## Next Steps

1. **Populate Knowledge Base**: Add your past proposals
2. **Customize Prompts**: Edit agent prompts in `agents/` files
3. **Adjust Thresholds**: Modify `config.py` for confidence levels
4. **Build UI**: Create a web frontend (React/Vue)
5. **Deploy**: Use Docker + K8s for production

## Architecture Overview

```
┌─────────────────────────────────────────────┐
│           Orchestrator Agent                │
│  (Coordinates all other agents)             │
└─────────────┬───────────────────────────────┘
              │
    ┌─────────┼─────────┬────────────┬────────┐
    │         │         │            │        │
┌───▼───┐ ┌──▼───┐ ┌───▼────┐ ┌────▼───┐ ┌──▼────┐
│Analyzer│ │Retri-│ │Generator│ │Reviewer│ │Format-│
│        │ │ever  │ │         │ │        │ │ter    │
└────────┘ └──────┘ └─────────┘ └────────┘ └───────┘
```

## Key Files

- `main.py` - Entry point
- `api/routes.py` - REST API endpoints
- `agents/orchestrator.py` - Main workflow coordinator
- `agents/*.py` - Individual agent implementations
- `config.py` - Configuration settings
- `test_system.py` - Test suite

## Support

- **API Docs**: http://localhost:8000/docs
- **README**: See README.md for detailed documentation
- **Issues**: Check the code comments for implementation details

Happy building! 🎉
