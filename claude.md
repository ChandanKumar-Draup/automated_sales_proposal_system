# Automated Sales Proposal System - Complete Documentation

## Table of Contents
1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Directory Structure](#directory-structure)
4. [Core Components](#core-components)
5. [Agents](#agents)
6. [Services](#services)
7. [API Endpoints](#api-endpoints)
8. [Configuration](#configuration)
9. [Data Flow](#data-flow)
10. [Knowledge Base & Embeddings](#knowledge-base--embeddings)
11. [Development Workflow](#development-workflow)
12. [Testing](#testing)
13. [Deployment](#deployment)

---

## Project Overview

The **Automated Sales Proposal System** is an AI-powered platform that generates customized sales proposals by:
- Analyzing RFP (Request for Proposal) documents
- Retrieving relevant content from a knowledge base
- Generating tailored proposal sections
- Reviewing and formatting the final output
- Producing professional DOCX documents

### Key Features
- Multi-agent orchestration using LLMs (OpenAI, Anthropic Claude, Google Gemini)
- Vector-based semantic search with FAISS
- RFP document processing (PDF, DOCX, XLSX)
- Knowledge base management with embeddings
- RESTful API with FastAPI
- Async/await for performance
- Configurable confidence thresholds

---

## Architecture

### System Design

```
┌─────────────────────────────────────────────────────────────┐
│                      FastAPI Server                          │
│                    (api/routes.py)                          │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                 Orchestrator Agent                          │
│              (agents/orchestrator.py)                       │
│  - Coordinates workflow                                     │
│  - Manages agent communication                              │
│  - Tracks workflow state                                    │
└─────────────┬───────────────────────────────────────────────┘
              │
    ┌─────────┼─────────┬────────────┬────────────┬──────────┐
    │         │         │            │            │          │
┌───▼───┐ ┌──▼───┐ ┌───▼────┐ ┌────▼────┐ ┌────▼─────┐ ┌──▼──────┐
│Analyzer│ │Retri-│ │Generator│ │Reviewer │ │Formatter │ │LLM      │
│        │ │ever  │ │         │ │         │ │          │ │Service  │
└────┬───┘ └──┬───┘ └───┬────┘ └────┬────┘ └────┬─────┘ └──┬──────┘
     │        │         │           │           │           │
     └────────┴─────────┴───────────┴───────────┴───────────┘
                               │
                ┌──────────────┼──────────────┐
                │              │              │
         ┌──────▼─────┐ ┌─────▼──────┐ ┌────▼────────┐
         │Vector Store│ │Document    │ │Embedding    │
         │(FAISS)     │ │Processor   │ │Service      │
         └────────────┘ └────────────┘ └─────────────┘
```

### Agent Workflow

1. **Analyzer Agent**: Extracts key requirements from RFP
2. **Retriever Agent**: Searches knowledge base for relevant content
3. **Generator Agent**: Creates proposal sections based on requirements
4. **Reviewer Agent**: Validates quality and completeness
5. **Formatter Agent**: Produces final DOCX document

---

## Directory Structure

```
automated_sales_proposal_system/
│
├── agents/                          # Multi-agent system
│   ├── __init__.py
│   ├── orchestrator.py             # Coordinates all agents
│   ├── analyzer.py                 # RFP analysis agent
│   ├── retriever.py                # Knowledge retrieval agent
│   ├── generator.py                # Content generation agent
│   ├── reviewer.py                 # Quality review agent
│   └── formatter.py                # Document formatting agent
│
├── api/                            # REST API layer
│   ├── __init__.py
│   └── routes.py                   # FastAPI endpoints
│
├── services/                       # Core services
│   ├── __init__.py
│   ├── llm_service.py             # LLM provider abstraction
│   ├── embedding_service.py       # Text embedding generation
│   ├── vector_store.py            # FAISS vector database
│   ├── document_processor.py     # PDF/DOCX/XLSX processing
│   └── metadata_extractor.py     # Document metadata extraction
│
├── models/                         # Data models
│   ├── __init__.py
│   └── schemas.py                  # Pydantic schemas
│
├── scripts/                        # Utility scripts
│   ├── ingest_rfp_knowledge.py    # Batch ingestion of RFP data
│   └── validate_embeddings.py     # Embedding quality validation
│
├── data/                           # Data storage
│   ├── vector_store/              # FAISS indices
│   ├── uploads/                   # User-uploaded files
│   └── outputs/                   # Generated proposals
│
├── resources/                      # Sample data and templates
│   └── RFP_Hackathon/             # RFP examples from various companies
│
├── docs/                           # Documentation
│   ├── RFP_INGESTION_GUIDE.md     # How to populate knowledge base
│   ├── EMBEDDING_STRATEGY.md      # Embedding approach & chunking
│   └── GEMINI_SETUP.md            # Google Gemini configuration
│
├── config.py                       # Configuration settings
├── main.py                         # Application entry point
├── test_system.py                 # Integration tests
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment variable template
├── README.md                      # Project README
├── QUICKSTART.md                  # Quick start guide
└── claude.md                      # This file
```

---

## Core Components

### 1. Entry Point: `main.py`

```python
# Starts the FastAPI server
# Initializes vector store and services
# Configures CORS and middleware
# Runs on 0.0.0.0:8000 by default
```

**Location**: `/home/user/automated_sales_proposal_system/main.py:1`

### 2. Configuration: `config.py`

Manages all system settings using Pydantic Settings:

**Key Configuration Options**:
- LLM providers (OpenAI, Anthropic, Gemini)
- Model selection and parameters
- Vector store paths
- Confidence thresholds
- API settings

**Location**: `/home/user/automated_sales_proposal_system/config.py:1`

### 3. Data Models: `models/schemas.py`

Pydantic schemas for:
- RFP uploads
- Proposal requests
- Workflow tracking
- Knowledge base entries
- API responses

**Location**: `/home/user/automated_sales_proposal_system/models/schemas.py:1`

---

## Agents

### Orchestrator Agent (`agents/orchestrator.py`)

**Responsibility**: Coordinates the entire proposal generation workflow

**Key Methods**:
- `process_rfp()`: Full RFP processing pipeline
- `quick_proposal()`: Generate proposal without RFP upload
- `coordinate_agents()`: Manages agent execution order
- `track_workflow()`: Monitors workflow state

**Location**: `/home/user/automated_sales_proposal_system/agents/orchestrator.py:1`

---

### Analyzer Agent (`agents/analyzer.py`)

**Responsibility**: Extracts structured information from RFP documents

**Capabilities**:
- Identifies key requirements
- Extracts deadlines and deliverables
- Categorizes RFP sections
- Determines proposal scope

**Inputs**: Raw RFP text
**Outputs**: Structured requirements (JSON)

**Location**: `/home/user/automated_sales_proposal_system/agents/analyzer.py:1`

---

### Retriever Agent (`agents/retriever.py`)

**Responsibility**: Searches knowledge base for relevant content

**Capabilities**:
- Semantic search using embeddings
- Filters by metadata (industry, outcome, etc.)
- Ranks results by relevance
- Deduplicates similar content

**Inputs**: Requirements from Analyzer
**Outputs**: Relevant knowledge snippets

**Location**: `/home/user/automated_sales_proposal_system/agents/retriever.py:1`

---

### Generator Agent (`agents/generator.py`)

**Responsibility**: Creates proposal content

**Capabilities**:
- Generates executive summary
- Writes technical sections
- Customizes content for client
- Incorporates retrieved knowledge

**Inputs**: Requirements + Retrieved content
**Outputs**: Draft proposal sections

**Location**: `/home/user/automated_sales_proposal_system/agents/generator.py:1`

---

### Reviewer Agent (`agents/reviewer.py`)

**Responsibility**: Quality assurance and validation

**Capabilities**:
- Checks completeness
- Validates against requirements
- Suggests improvements
- Assigns confidence scores

**Inputs**: Generated proposal
**Outputs**: Review feedback + confidence scores

**Location**: `/home/user/automated_sales_proposal_system/agents/reviewer.py:1`

---

### Formatter Agent (`agents/formatter.py`)

**Responsibility**: Produces final DOCX document

**Capabilities**:
- Applies professional formatting
- Adds headers/footers
- Generates table of contents
- Exports to DOCX format

**Inputs**: Reviewed proposal content
**Outputs**: DOCX file

**Location**: `/home/user/automated_sales_proposal_system/agents/formatter.py:1`

---

## Services

### LLM Service (`services/llm_service.py`)

**Purpose**: Unified interface for multiple LLM providers

**Supported Providers**:
- OpenAI (GPT-4, GPT-3.5)
- Anthropic (Claude 3.5, Claude 3)
- Google (Gemini Pro)

**Key Methods**:
- `generate()`: Generate text completion
- `chat()`: Chat-based interaction
- `stream()`: Streaming responses

**Location**: `/home/user/automated_sales_proposal_system/services/llm_service.py:1`

---

### Embedding Service (`services/embedding_service.py`)

**Purpose**: Generate text embeddings for semantic search

**Supported Models**:
- Sentence Transformers (all-MiniLM-L6-v2)
- OpenAI embeddings
- Google Gemini embeddings

**Key Methods**:
- `embed_text()`: Generate embedding for single text
- `embed_batch()`: Batch embedding generation
- `similarity()`: Calculate cosine similarity

**Location**: `/home/user/automated_sales_proposal_system/services/embedding_service.py:1`

---

### Vector Store (`services/vector_store.py`)

**Purpose**: Manage FAISS-based vector database

**Capabilities**:
- Store and retrieve embeddings
- Semantic search (top-k)
- Metadata filtering
- Index persistence

**Key Methods**:
- `add()`: Add embedding with metadata
- `search()`: Semantic search
- `save()`: Persist to disk
- `load()`: Load from disk

**Location**: `/home/user/automated_sales_proposal_system/services/vector_store.py:1`

---

### Document Processor (`services/document_processor.py`)

**Purpose**: Extract text from various document formats

**Supported Formats**:
- PDF (PyPDF2)
- DOCX (python-docx)
- XLSX (openpyxl)
- TXT (plain text)

**Key Methods**:
- `extract_text()`: Extract raw text
- `extract_with_structure()`: Preserve formatting
- `chunk_text()`: Split into manageable chunks

**Location**: `/home/user/automated_sales_proposal_system/services/document_processor.py:1`

---

### Metadata Extractor (`services/metadata_extractor.py`)

**Purpose**: Extract metadata from documents

**Extracted Fields**:
- Document type
- Creation date
- Author
- Industry/domain
- Key entities

**Location**: `/home/user/automated_sales_proposal_system/services/metadata_extractor.py:1`

---

## API Endpoints

> **Full API Documentation**: See `docs/API_REFERENCE.md` for complete details including input/output schemas, error handling, and integration examples.

### Base URL: `http://localhost:8000`

### Quick Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/docs` | GET | Swagger UI |
| `/api/v1/proposals/quick` | POST | Generate quick proposal |
| `/api/v1/rfp/upload` | POST | Upload RFP document |
| `/api/v1/workflows/{id}` | GET | Get workflow status |
| `/api/v1/download/{id}` | GET | Download proposal DOCX |
| `/api/v1/qa/ask` | POST/GET | Ask a question (RAG) |
| `/api/v1/qa/batch` | POST | Batch Q&A |
| `/api/v1/qa/suggestions` | GET | Get suggested questions |
| `/api/v1/knowledge/add` | POST | Add to knowledge base |
| `/api/v1/knowledge/search` | GET | Search knowledge base |
| `/api/v1/documents` | GET/POST | List/create documents |
| `/api/v1/documents/{id}` | GET/PUT | Get/update document |
| `/api/v1/users` | GET | List users |
| `/api/v1/users/current` | GET | Get current user |

---

### Key Endpoints

#### Quick Proposal
```http
POST /api/v1/proposals/quick
Content-Type: application/json

{
  "client_name": "Acme Corp",
  "contact_title": "CEO",
  "industry": "Healthcare",
  "proposal_type": "pitch_deck",
  "requirements": "talent sourcing needs",
  "tone": "professional"
}
```

**Response**: Returns `WorkflowStatus` with `workflow_id`, `state`, and `proposal_content`

#### Q&A System
```http
POST /api/v1/qa/ask
Content-Type: application/json

{
  "question": "What RPO services do we offer?",
  "top_k": 5,
  "include_sources": true,
  "context": "For healthcare client"
}
```

**Response**: Returns `answer`, `sources`, `confidence` score

#### Document Management
```http
GET /api/v1/documents                    # List all documents
GET /api/v1/documents/{workflow_id}      # Get specific document
PUT /api/v1/documents/{workflow_id}      # Update document
POST /api/v1/documents                   # Create new document
```

**API Routes Location**: `/home/user/automated_sales_proposal_system/api/routes.py:1`

---

## Frontend Integration

### Integration Approaches

The backend has CORS enabled (`allow_origins=["*"]`), supporting multiple integration approaches:

#### 1. Development Mode (Simplest)
Run React and FastAPI separately:
- Backend: `http://localhost:8000`
- Frontend: `http://localhost:3000`

#### 2. Reverse Proxy (Production)
Use Nginx to serve both under same domain:
```nginx
location / {
  # Serve React build
  root /var/www/react-app/build;
}
location /api/ {
  proxy_pass http://localhost:8000;
}
```

#### 3. Docker Compose
Container orchestration for both services.

#### 4. Static Files from FastAPI
Serve React build from FastAPI using `StaticFiles`.

### React API Service Example

```javascript
const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export const api = {
  generateProposal: (data) =>
    fetch(`${API_BASE}/api/v1/proposals/quick`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    }),

  askQuestion: (question, context) =>
    fetch(`${API_BASE}/api/v1/qa/ask`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question, context })
    }),

  uploadRFP: (file, clientName) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('client_name', clientName);
    return fetch(`${API_BASE}/api/v1/rfp/upload`, {
      method: 'POST',
      body: formData
    });
  },

  getDocument: (workflowId) =>
    fetch(`${API_BASE}/api/v1/documents/${workflowId}`),

  saveDocument: (workflowId, title, content) =>
    fetch(`${API_BASE}/api/v1/documents/${workflowId}?title=${encodeURIComponent(title)}&content=${encodeURIComponent(content)}`, {
      method: 'PUT'
    })
};
```

> **See**: `docs/API_REFERENCE.md` for complete integration examples and error handling

---

## Configuration

### Environment Variables (.env)

```bash
# LLM Provider API Keys
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GEMINI_API_KEY=...

# Provider Selection
DEFAULT_LLM_PROVIDER=openai  # or anthropic, gemini
DEFAULT_MODEL=gpt-4-turbo-preview

# Model Parameters
TEMPERATURE=0.7
MAX_TOKENS=2000

# Embedding Settings
EMBEDDING_MODEL=all-MiniLM-L6-v2
VECTOR_STORE_PATH=./data/vector_store
TOP_K_RESULTS=5

# Confidence Thresholds
HIGH_CONFIDENCE_THRESHOLD=0.9
MEDIUM_CONFIDENCE_THRESHOLD=0.7

# Server Settings
API_HOST=0.0.0.0
API_PORT=8000
```

### Switching LLM Providers

**OpenAI**:
```bash
DEFAULT_LLM_PROVIDER=openai
DEFAULT_MODEL=gpt-4-turbo-preview
```

**Anthropic Claude**:
```bash
DEFAULT_LLM_PROVIDER=anthropic
DEFAULT_MODEL=claude-3-5-sonnet-20241022
```

**Google Gemini**:
```bash
DEFAULT_LLM_PROVIDER=gemini
DEFAULT_MODEL=gemini-pro
```

---

## Data Flow

### Full RFP Processing Flow

```
1. Client uploads RFP (PDF/DOCX)
   │
   ▼
2. Document Processor extracts text
   │
   ▼
3. Analyzer Agent extracts requirements
   │   - Identifies key sections
   │   - Extracts deadlines
   │   - Categorizes requirements
   │
   ▼
4. Retriever Agent searches knowledge base
   │   - Generates query embeddings
   │   - Searches FAISS vector store
   │   - Filters by metadata
   │   - Ranks by relevance
   │
   ▼
5. Generator Agent creates proposal
   │   - Executive summary
   │   - Technical sections
   │   - Pricing (if applicable)
   │   - Team structure
   │
   ▼
6. Reviewer Agent validates
   │   - Checks completeness
   │   - Validates against requirements
   │   - Assigns confidence score
   │   - Suggests improvements (if needed)
   │
   ▼
7. Formatter Agent produces DOCX
   │   - Professional formatting
   │   - Headers/footers
   │   - Table of contents
   │
   ▼
8. Client downloads proposal
```

### Quick Proposal Flow (No RFP Upload)

```
1. Client provides basic info
   │
   ▼
2. Retriever searches knowledge base
   │
   ▼
3. Generator creates proposal
   │
   ▼
4. Reviewer validates
   │
   ▼
5. Formatter produces DOCX
   │
   ▼
6. Client downloads proposal
```

---

## Knowledge Base & Embeddings

### Embedding Strategy

The system uses a **multi-level chunking strategy** for optimal retrieval:

1. **Document-level**: Entire document embeddings
2. **Section-level**: Major sections (e.g., "Executive Summary")
3. **Paragraph-level**: Individual paragraphs
4. **Sentence-level**: Key sentences

**See**: `docs/EMBEDDING_STRATEGY.md` for detailed strategy

### Populating the Knowledge Base

#### Method 1: API Endpoint
```bash
curl -X POST "http://localhost:8000/api/v1/knowledge/add" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Our RPO solution includes...",
    "metadata": {
      "source": "RFP-2024-001",
      "industry": "Technology",
      "win_outcome": true
    }
  }'
```

#### Method 2: Batch Script
```bash
python scripts/ingest_rfp_knowledge.py \
  --input_dir resources/RFP_Hackathon \
  --metadata '{"source": "hackathon", "type": "rfp"}'
```

**See**: `docs/RFP_INGESTION_GUIDE.md` for complete guide

### Metadata Schema

```json
{
  "source": "RFP-2024-001",          // Document identifier
  "industry": "Technology",          // Industry sector
  "win_outcome": true,               // Was this proposal successful?
  "client_size": "enterprise",       // Company size
  "service_type": "RPO",             // Service category
  "date": "2024-01-15",             // Creation date
  "region": "North America"          // Geographic region
}
```

---

## Development Workflow

### Setup Development Environment

```bash
# Clone repository
git clone <repo-url>
cd automated_sales_proposal_system

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Initialize data directories
mkdir -p data/vector_store data/uploads data/outputs

# Start development server
python main.py
```

### Code Style

- **Python**: PEP 8 compliant
- **Type hints**: Use throughout
- **Async/await**: For I/O operations
- **Docstrings**: Google style

### Adding a New Agent

1. Create file in `agents/` directory
2. Implement agent class with required methods
3. Register in `agents/__init__.py`
4. Update orchestrator to include agent
5. Add tests in `test_system.py`

### Adding a New LLM Provider

1. Add provider in `services/llm_service.py`
2. Implement provider-specific client
3. Add configuration in `config.py`
4. Update `.env.example`
5. Document in this file

---

## Testing

### Run All Tests

```bash
python test_system.py
```

### Test Coverage

- **Unit tests**: Individual agent testing
- **Integration tests**: Full workflow testing
- **API tests**: Endpoint validation
- **Performance tests**: Response time benchmarks

### Manual Testing

```bash
# Test health endpoint
curl http://localhost:8000/health

# Test quick proposal
curl -X POST "http://localhost:8000/api/v1/proposals/quick" \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "Test Corp",
    "contact_title": "CEO",
    "industry": "Technology"
  }'

# Test knowledge search
curl "http://localhost:8000/api/v1/knowledge/search?query=talent+sourcing&top_k=3"
```

**Test Suite Location**: `/home/user/automated_sales_proposal_system/test_system.py:1`

---

## Deployment

### Local Development
```bash
python main.py
# Access at http://localhost:8000
```

### Production with Uvicorn
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Docker Deployment
```dockerfile
# Dockerfile example
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Considerations

**Development**:
- Single worker
- Debug logging
- Local file storage

**Production**:
- Multiple workers
- Error logging only
- Cloud storage (S3/GCS)
- API key rotation
- Rate limiting
- Authentication

---

## Key Files Reference

| File | Purpose | Location |
|------|---------|----------|
| `main.py` | Application entry point | `/home/user/automated_sales_proposal_system/main.py:1` |
| `config.py` | Configuration management | `/home/user/automated_sales_proposal_system/config.py:6` |
| `api/routes.py` | REST API endpoints | `/home/user/automated_sales_proposal_system/api/routes.py:1` |
| `agents/orchestrator.py` | Workflow coordination | `/home/user/automated_sales_proposal_system/agents/orchestrator.py:1` |
| `services/llm_service.py` | LLM abstraction | `/home/user/automated_sales_proposal_system/services/llm_service.py:1` |
| `services/vector_store.py` | FAISS vector DB | `/home/user/automated_sales_proposal_system/services/vector_store.py:1` |
| `test_system.py` | Integration tests | `/home/user/automated_sales_proposal_system/test_system.py:1` |

---

## Additional Documentation

- **Quick Start**: See `QUICKSTART.md`
- **API Reference**: See `docs/API_REFERENCE.md` - Complete API documentation with inputs, outputs, and integration examples
- **RFP Ingestion**: See `docs/RFP_INGESTION_GUIDE.md`
- **Embedding Strategy**: See `docs/EMBEDDING_STRATEGY.md`
- **Gemini Setup**: See `docs/GEMINI_SETUP.md`

---

## Common Issues & Solutions

### Issue: "Module not found"
**Solution**: Ensure venv is activated and dependencies installed
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Issue: "API key not found"
**Solution**: Check `.env` file has correct API keys
```bash
cat .env | grep API_KEY
```

### Issue: "FAISS index not found"
**Solution**: Initialize vector store or ingest knowledge base
```bash
python scripts/ingest_rfp_knowledge.py --input_dir resources/RFP_Hackathon
```

### Issue: "Port 8000 already in use"
**Solution**: Change port in `.env`
```bash
API_PORT=8001
```

---

## Contributing

When adding new features:
1. Update relevant agent/service files
2. Add tests to `test_system.py`
3. Update configuration if needed
4. Update this documentation
5. Test end-to-end workflow

---

**Last Updated**: 2025-11-18
**Version**: 1.1
**Maintainer**: Development Team
