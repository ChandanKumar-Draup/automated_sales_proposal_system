# API Reference - Automated Sales Proposal System

Complete API documentation for integrating with the Sales Proposal System backend.

**Base URL**: `http://localhost:8000`
**API Version**: v1
**Content-Type**: `application/json` (unless otherwise specified)

---

## Table of Contents

1. [System Endpoints](#system-endpoints)
2. [Proposal Generation](#proposal-generation)
3. [RFP Processing](#rfp-processing)
4. [Q&A System](#qa-system)
5. [Knowledge Base](#knowledge-base)
6. [Document Management](#document-management)
7. [User Management](#user-management)
8. [Data Models](#data-models)
9. [Error Handling](#error-handling)
10. [Integration Notes](#integration-notes)

---

## System Endpoints

### GET `/`
**Description**: Root endpoint - returns API information and available endpoints.

**Response**:
```json
{
  "message": "Automated Sales Proposal System API",
  "version": "1.0.0",
  "endpoints": {
    "health": "/health",
    "quick_proposal": "/api/v1/proposals/quick",
    ...
  }
}
```

---

### GET `/health`
**Description**: Health check endpoint to verify system status.

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2024-11-18T10:30:00.000000",
  "services": {
    "llm": true,
    "vector_store": true,
    "orchestrator": true
  }
}
```

**Special Instructions**:
- Use this endpoint to check if the backend is running before making other API calls
- `services` values will be `false` until first API call initializes them

---

## Proposal Generation

### POST `/api/v1/proposals/quick`
**Description**: Generate a quick sales proposal without uploading an RFP document.

**Input (JSON Body)**:
```json
{
  "client_name": "Acme Corporation",
  "contact_title": "VP of HR",
  "industry": "Technology",
  "proposal_type": "pitch_deck",
  "requirements": "Need talent sourcing for engineering roles",
  "tone": "professional"
}
```

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `client_name` | string | Yes | - | Name of the target company |
| `contact_title` | string | No | null | Title of the contact person |
| `industry` | string | No | null | Industry sector (e.g., "Technology", "Healthcare") |
| `proposal_type` | string | No | "pitch_deck" | Type: "pitch_deck" or "rfp_response" |
| `requirements` | string | No | null | Specific requirements or focus areas |
| `tone` | string | No | "professional" | Tone: "professional", "friendly", "formal" |

**Output**:
```json
{
  "workflow_id": "WF-QUICK-20241118103000",
  "state": "ready",
  "created_at": "2024-11-18T10:30:00.000000",
  "updated_at": "2024-11-18T10:30:05.000000",
  "rfp_analysis": null,
  "generated_responses": [...],
  "review_result": {...},
  "output_file_path": "/path/to/proposal.docx",
  "proposal_content": "# Proposal for Acme Corporation\n\n..."
}
```

**Special Instructions**:
- This is a synchronous endpoint - it will wait for the proposal to be generated
- Response time: 10-30 seconds depending on LLM provider
- The `proposal_content` field contains raw markdown for editing in UI
- Use the `workflow_id` to download the DOCX file or edit the document

---

### GET `/api/v1/workflows/{workflow_id}`
**Description**: Get the status of a workflow.

**Path Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `workflow_id` | string | The workflow ID returned from proposal creation |

**Output**:
```json
{
  "workflow_id": "WF-QUICK-20241118103000",
  "state": "ready",
  "created_at": "2024-11-18T10:30:00.000000",
  "updated_at": "2024-11-18T10:30:05.000000",
  "output_file_path": "/path/to/proposal.docx",
  "proposal_content": "..."
}
```

**Workflow States**:
- `created` - Workflow initialized
- `analyzing` - Analyzing RFP/requirements
- `routing` - Routing to appropriate agents
- `generating` - Generating proposal content
- `reviewing` - Quality review in progress
- `human_review` - Awaiting human review
- `formatting` - Creating final document
- `ready` - Proposal complete and ready
- `submitted` - Proposal submitted to client
- `closed` - Workflow closed

---

### GET `/api/v1/download/{workflow_id}`
**Description**: Download the generated proposal as a DOCX file.

**Path Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `workflow_id` | string | The workflow ID |

**Output**: Binary file download (application/octet-stream)

**Special Instructions**:
- Only available when workflow state is "ready" or later
- Returns 404 if output file doesn't exist
- File name format: `proposal_{client_name}_{timestamp}.docx`

---

## RFP Processing

### POST `/api/v1/rfp/upload`
**Description**: Upload an RFP document for processing.

**Input (multipart/form-data)**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `file` | File | Yes | RFP document (PDF, DOCX, DOC, TXT) |
| `client_name` | string | Yes | Name of the client |
| `industry` | string | No | Industry sector |

**Output**:
```json
{
  "workflow_id": "WF-RFP-20241118103000",
  "status": "processing",
  "message": "RFP uploaded successfully. Processing in background."
}
```

**Special Instructions**:
- Maximum file size: 10MB (configurable)
- Supported formats: `.pdf`, `.docx`, `.doc`, `.txt`
- Processing happens in background - poll `/api/v1/workflows/{workflow_id}` for status
- Large RFPs may take 1-2 minutes to process

---

## Q&A System

### POST `/api/v1/qa/ask`
**Description**: Ask a question and get an AI-generated answer with sources (RAG-based).

**Input (JSON Body)**:
```json
{
  "question": "What RPO services do we offer?",
  "top_k": 5,
  "include_sources": true,
  "context": "For a healthcare client"
}
```

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `question` | string | Yes | - | The question to answer |
| `top_k` | int | No | 5 | Number of knowledge base chunks to retrieve |
| `include_sources` | bool | No | true | Include source citations in response |
| `context` | string | No | null | Additional context for better answers |

**Output**:
```json
{
  "question": "What RPO services do we offer?",
  "answer": "We offer comprehensive RPO services including...",
  "sources": [
    {
      "text": "Source text chunk...",
      "score": 0.89,
      "metadata": {
        "source": "RFP-2024-001",
        "industry": "Healthcare"
      }
    }
  ],
  "confidence": 0.92,
  "generated_at": "2024-11-18T10:30:00.000000",
  "model_used": "claude-3-5-sonnet-20241022"
}
```

**Special Instructions**:
- Answers are formatted in markdown
- Confidence score: 0.0 to 1.0 (higher is better)
- Sources are sorted by relevance score (descending)
- Use `context` to provide client-specific or situation-specific information

---

### GET `/api/v1/qa/ask`
**Description**: GET version of Q&A endpoint for simple queries.

**Query Parameters**:
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `question` | string | Yes | - | The question to answer |
| `top_k` | int | No | 5 | Number of results |
| `include_sources` | bool | No | true | Include sources |
| `context` | string | No | null | Additional context |

**Example**: `GET /api/v1/qa/ask?question=What%20is%20our%20pricing&top_k=3`

---

### POST `/api/v1/qa/batch`
**Description**: Answer multiple questions at once.

**Input (JSON Body)**:
```json
{
  "questions": [
    "What RPO services do we offer?",
    "What is our implementation timeline?",
    "Do we have healthcare case studies?"
  ],
  "top_k": 5,
  "include_sources": true
}
```

**Output**:
```json
{
  "count": 3,
  "responses": [
    {
      "question": "What RPO services do we offer?",
      "answer": "...",
      "sources": [...],
      "confidence": 0.92,
      "generated_at": "...",
      "model_used": "..."
    },
    ...
  ]
}
```

**Special Instructions**:
- Use for processing FAQ lists or RFP questions
- Maximum recommended: 20 questions per batch
- Processing time scales linearly with question count

---

### GET `/api/v1/qa/suggestions`
**Description**: Get suggested questions based on knowledge base content.

**Query Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `topic` | string | No | Filter suggestions by topic |

**Output**:
```json
{
  "topic": "RPO",
  "suggestions": [
    "What is your approach to high-volume recruiting?",
    "How do you handle compliance requirements?",
    "What technology platforms do you use?"
  ]
}
```

---

## Knowledge Base

### POST `/api/v1/knowledge/add`
**Description**: Add content to the knowledge base (vector store).

**Query Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `text` | string | Yes | Content to add |
| `metadata` | JSON | No | Metadata for the content |

**Example**:
```
POST /api/v1/knowledge/add?text=Our+RPO+solution...&metadata={"industry":"Healthcare","source":"case-study-001"}
```

**Output**:
```json
{
  "status": "success",
  "message": "Content added to knowledge base"
}
```

**Metadata Schema**:
```json
{
  "source": "RFP-2024-001",
  "industry": "Technology",
  "win_outcome": true,
  "client_size": "enterprise",
  "service_type": "RPO",
  "date": "2024-01-15",
  "region": "North America"
}
```

**Special Instructions**:
- Content is automatically chunked and embedded
- Metadata improves search relevance
- Vector store is persisted to disk after addition

---

### GET `/api/v1/knowledge/search`
**Description**: Search the knowledge base using semantic search.

**Query Parameters**:
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `query` | string | Yes | - | Search query |
| `top_k` | int | No | 5 | Number of results |

**Output**:
```json
{
  "query": "talent sourcing best practices",
  "results": [
    {
      "text": "Our talent sourcing approach includes...",
      "score": 0.87,
      "metadata": {
        "source": "RFP-2024-001",
        "industry": "Technology"
      }
    }
  ]
}
```

---

## Document Management

### GET `/api/v1/documents`
**Description**: List all editable documents.

**Query Parameters**:
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `limit` | int | No | 50 | Maximum documents to return |

**Output**:
```json
{
  "count": 10,
  "documents": [
    {
      "id": 1,
      "workflow_id": "WF-QUICK-20241118103000",
      "title": "Proposal for Acme Corp",
      "client_name": "Acme Corp",
      "document_type": "proposal",
      "content": "# Proposal...",
      "created_at": "2024-11-18T10:30:00",
      "updated_at": "2024-11-18T10:35:00",
      "last_edited_by": {
        "id": 1,
        "name": "Sales Rep",
        "email": "sales@company.com"
      }
    }
  ]
}
```

---

### GET `/api/v1/documents/{workflow_id}`
**Description**: Get a specific document by workflow ID.

**Path Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| `workflow_id` | string | The workflow ID |

**Output**: Same as individual document in list

---

### POST `/api/v1/documents`
**Description**: Create a new editable document.

**Query Parameters**:
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `workflow_id` | string | Yes | - | Unique workflow ID |
| `title` | string | Yes | - | Document title |
| `content` | string | Yes | - | Document content (markdown) |
| `client_name` | string | No | null | Client name |
| `document_type` | string | No | "proposal" | Type: "proposal", "rfp_response" |

**Output**:
```json
{
  "status": "success",
  "message": "Document created successfully",
  "document": {...}
}
```

---

### PUT `/api/v1/documents/{workflow_id}`
**Description**: Update/save a document with user tracking.

**Query Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `title` | string | Yes | Updated title |
| `content` | string | Yes | Updated content |
| `user_id` | int | No | User making the edit (uses default if not provided) |

**Output**:
```json
{
  "status": "success",
  "message": "Document saved successfully",
  "document": {...}
}
```

**Special Instructions**:
- Preserves `client_name` and `document_type` from existing document
- Tracks which user made the edit
- Updates `updated_at` timestamp

---

## User Management

### GET `/api/v1/users`
**Description**: List all active users.

**Output**:
```json
{
  "count": 5,
  "users": [
    {
      "id": 1,
      "name": "Sales Rep",
      "email": "sales@company.com",
      "role": "sales_rep",
      "is_active": true
    }
  ]
}
```

---

### GET `/api/v1/users/current`
**Description**: Get the current (default) user.

**Output**:
```json
{
  "id": 1,
  "name": "Sales Rep",
  "email": "sales@company.com",
  "role": "sales_rep",
  "is_active": true
}
```

---

## Data Models

### ProposalRequest
```typescript
interface ProposalRequest {
  client_name: string;           // Required
  contact_title?: string;
  industry?: string;
  proposal_type?: "pitch_deck" | "rfp_response";  // Default: "pitch_deck"
  requirements?: string;
  tone?: "professional" | "friendly" | "formal";  // Default: "professional"
}
```

### WorkflowStatus
```typescript
interface WorkflowStatus {
  workflow_id: string;
  state: WorkflowState;
  created_at: string;           // ISO 8601 datetime
  updated_at: string;
  rfp_analysis?: RFPAnalysis;
  generated_responses: GeneratedResponse[];
  review_result?: ReviewResult;
  output_file_path?: string;
  proposal_content?: string;    // Markdown content for editing
}
```

### QARequest
```typescript
interface QARequest {
  question: string;              // Required
  top_k?: number;                // Default: 5
  include_sources?: boolean;     // Default: true
  context?: string;
}
```

### QAResponse
```typescript
interface QAResponse {
  question: string;
  answer: string;                // Markdown formatted
  sources: QASource[];
  confidence: number;            // 0.0 to 1.0
  generated_at: string;
  model_used: string;
}
```

---

## Error Handling

### Standard Error Response
```json
{
  "detail": "Error message describing what went wrong"
}
```

### HTTP Status Codes
| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Bad Request - Invalid input |
| 404 | Not Found - Resource doesn't exist |
| 422 | Validation Error - Request body validation failed |
| 500 | Internal Server Error |

### Common Errors

**File type not supported (400)**:
```json
{
  "detail": "Unsupported file type. Allowed: ['.pdf', '.docx', '.doc', '.txt']"
}
```

**Workflow not found (404)**:
```json
{
  "detail": "Workflow not found"
}
```

**LLM API error (500)**:
```json
{
  "detail": "Failed to create proposal: API key not configured"
}
```

---

## Integration Notes

### CORS Configuration
The backend allows all origins by default:
```python
allow_origins=["*"]
allow_credentials=True
allow_methods=["*"]
allow_headers=["*"]
```

### React Integration Example

```javascript
// src/services/api.js
const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export const api = {
  // Health check
  checkHealth: async () => {
    const response = await fetch(`${API_BASE}/health`);
    return response.json();
  },

  // Generate quick proposal
  generateProposal: async (data) => {
    const response = await fetch(`${API_BASE}/api/v1/proposals/quick`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!response.ok) throw new Error(await response.text());
    return response.json();
  },

  // Upload RFP
  uploadRFP: async (file, clientName, industry) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('client_name', clientName);
    if (industry) formData.append('industry', industry);

    const response = await fetch(`${API_BASE}/api/v1/rfp/upload`, {
      method: 'POST',
      body: formData
    });
    return response.json();
  },

  // Ask question
  askQuestion: async (question, context = null) => {
    const response = await fetch(`${API_BASE}/api/v1/qa/ask`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question, context })
    });
    return response.json();
  },

  // Get workflow status
  getWorkflowStatus: async (workflowId) => {
    const response = await fetch(`${API_BASE}/api/v1/workflows/${workflowId}`);
    return response.json();
  },

  // Download proposal
  downloadProposal: (workflowId) => {
    window.open(`${API_BASE}/api/v1/download/${workflowId}`, '_blank');
  },

  // List documents
  listDocuments: async (limit = 50) => {
    const response = await fetch(`${API_BASE}/api/v1/documents?limit=${limit}`);
    return response.json();
  },

  // Get document
  getDocument: async (workflowId) => {
    const response = await fetch(`${API_BASE}/api/v1/documents/${workflowId}`);
    return response.json();
  },

  // Save document
  saveDocument: async (workflowId, title, content) => {
    const response = await fetch(
      `${API_BASE}/api/v1/documents/${workflowId}?title=${encodeURIComponent(title)}&content=${encodeURIComponent(content)}`,
      { method: 'PUT' }
    );
    return response.json();
  },

  // Search knowledge base
  searchKnowledge: async (query, topK = 5) => {
    const response = await fetch(
      `${API_BASE}/api/v1/knowledge/search?query=${encodeURIComponent(query)}&top_k=${topK}`
    );
    return response.json();
  }
};
```

### Polling for Background Tasks

```javascript
// Poll for RFP processing completion
async function pollWorkflowStatus(workflowId, interval = 2000) {
  return new Promise((resolve, reject) => {
    const poll = setInterval(async () => {
      try {
        const status = await api.getWorkflowStatus(workflowId);

        if (status.state === 'ready') {
          clearInterval(poll);
          resolve(status);
        } else if (status.state === 'closed' || status.state.includes('error')) {
          clearInterval(poll);
          reject(new Error('Workflow failed'));
        }
      } catch (error) {
        clearInterval(poll);
        reject(error);
      }
    }, interval);
  });
}
```

### Environment Variables

```bash
# .env for React app
REACT_APP_API_URL=http://localhost:8000
```

---

## API Versioning

Current version: **v1**

All API endpoints are prefixed with `/api/v1/`. Future versions will use `/api/v2/`, etc.

---

## Rate Limiting

Currently no rate limiting is implemented. For production, consider adding:
- Request rate limiting per IP
- LLM API call throttling
- File upload size limits

---

**Last Updated**: 2024-11-18
**Version**: 1.0
