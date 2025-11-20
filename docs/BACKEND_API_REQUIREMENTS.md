# Backend API Implementation Guide

This document describes all the backend APIs that need to be implemented to support the frontend features. Each section includes detailed specifications, request/response formats, and implementation notes.

---

## Table of Contents

1. [Stepwise RFP Processing APIs](#stepwise-rfp-processing-apis)
2. [Enhanced Workflow Status API](#enhanced-workflow-status-api)
3. [Document Edit and Save APIs](#document-edit-and-save-apis)
4. [Missing API Endpoints](#missing-api-endpoints)
5. [Database Schema Requirements](#database-schema-requirements)
6. [Implementation Priority](#implementation-priority)

---

## Stepwise RFP Processing APIs

### Overview

The frontend expects RFP processing to happen in **4 distinct steps** with real-time progress updates. The backend needs to update the workflow state and provide intermediate results at each step.

### Required Workflow States

The workflow must transition through these states in order:

```
created → analyzing → routing → generating → reviewing → formatting → ready
```

**State Definitions:**

| State | Step | Description | Frontend Display |
|-------|------|-------------|------------------|
| `created` | 0 | Workflow initialized | "Uploading..." |
| `analyzing` | 1 | Extracting questions from RFP | "Extracting questions..." |
| `routing` | 2 | Routing to agents | "Preparing to generate..." |
| `generating` | 2 | Creating AI responses | "Generating answers..." |
| `reviewing` | 3 | Quality review | "Reviewing responses..." |
| `formatting` | 3 | Creating final document | "Formatting document..." |
| `ready` | 4 | Complete | "Complete" ✓ |

---

### 1. Enhanced RFP Upload Endpoint

**Endpoint:** `POST /api/v1/rfp/upload`

**Current Status:** ✅ Exists (but may need enhancement)

**What Needs to Be Added:**

The endpoint should:
1. Accept the file and metadata
2. Create a workflow with state `created`
3. **Immediately start background processing**
4. Return workflow ID to frontend
5. Process should update workflow state as it progresses

**Request:**
```
Content-Type: multipart/form-data

Fields:
- file: File (PDF, DOCX, DOC, TXT)
- client_name: string (required)
- industry: string (optional)
```

**Response:**
```json
{
  "workflow_id": "WF-RFP-20241120123456",
  "status": "processing",
  "message": "RFP uploaded successfully. Processing in background."
}
```

**Implementation Notes:**

```python
@app.post("/api/v1/rfp/upload")
async def upload_rfp(
    file: UploadFile,
    client_name: str = Form(...),
    industry: Optional[str] = Form(None)
):
    # 1. Save file
    file_path = save_uploaded_file(file)

    # 2. Create workflow
    workflow_id = generate_workflow_id()
    workflow = create_workflow(
        workflow_id=workflow_id,
        state="created",
        client_name=client_name,
        industry=industry,
        file_path=file_path
    )

    # 3. Start background processing (async)
    background_tasks.add_task(process_rfp, workflow_id, file_path)

    # 4. Return immediately
    return {
        "workflow_id": workflow_id,
        "status": "processing",
        "message": "RFP uploaded successfully. Processing in background."
    }
```

---

### 2. Background RFP Processing Function

**Function:** `process_rfp(workflow_id, file_path)`

**Status:** 🔴 Needs Implementation

**Purpose:** Process the RFP through all steps and update workflow state at each step

**Implementation Pseudocode:**

```python
async def process_rfp(workflow_id: str, file_path: str):
    """
    Process RFP through all 4 steps, updating workflow state at each step.
    Frontend polls GET /api/v1/workflows/{workflow_id} every 2 seconds.
    """

    try:
        # === STEP 1: EXTRACT QUESTIONS ===
        # Update state to 'analyzing'
        update_workflow_state(workflow_id, "analyzing")

        # Extract text from document
        document_text = extract_text_from_file(file_path)

        # Use LLM to extract questions
        questions = await extract_questions_from_rfp(document_text)
        # Returns: ["What is your approach?", "Describe timeline", ...]

        # Save questions to workflow
        update_workflow_analysis(workflow_id, {
            "questions": questions,
            "total_questions": len(questions),
            "document_text": document_text
        })


        # === STEP 2: GENERATE ANSWERS ===
        # Update state to 'routing'
        update_workflow_state(workflow_id, "routing")

        # Route questions to appropriate agents/handlers
        question_routing = route_questions(questions)

        # Update state to 'generating'
        update_workflow_state(workflow_id, "generating")

        # Generate answers for each question
        generated_responses = []
        for i, question in enumerate(questions):
            # Generate answer using RAG/LLM
            answer_data = await generate_answer_for_question(
                question=question,
                context=document_text,
                knowledge_base=get_knowledge_base()
            )

            response = {
                "question": question,
                "answer": answer_data["answer"],  # Markdown formatted
                "sources": answer_data["sources"],
                "confidence": answer_data.get("confidence", 0.8)
            }

            generated_responses.append(response)

            # Update workflow with progressive results
            # Frontend will see answers appear one by one
            update_workflow_responses(workflow_id, generated_responses)


        # === STEP 3: QUALITY REVIEW ===
        # Update state to 'reviewing'
        update_workflow_state(workflow_id, "reviewing")

        # Review all responses for quality/consistency
        review_result = await review_responses(generated_responses)

        update_workflow_review(workflow_id, review_result)

        # Update state to 'formatting'
        update_workflow_state(workflow_id, "formatting")

        # Create final document (DOCX)
        output_file_path = create_rfp_response_document(
            workflow_id=workflow_id,
            questions=questions,
            responses=generated_responses,
            client_name=get_workflow_client_name(workflow_id)
        )


        # === STEP 4: COMPLETE ===
        # Update state to 'ready'
        update_workflow_final(workflow_id, {
            "state": "ready",
            "output_file_path": output_file_path,
            "completed_at": datetime.now()
        })

    except Exception as e:
        # Handle errors
        update_workflow_state(workflow_id, "error")
        log_error(workflow_id, str(e))
```

---

### 3. Enhanced Workflow Status Endpoint

**Endpoint:** `GET /api/v1/workflows/{workflow_id}`

**Current Status:** ⚠️ Exists but needs enhancement

**What Needs to Be Enhanced:**

The response must include:
1. Current state (for step calculation)
2. `rfp_analysis` object with extracted questions
3. `generated_responses` array (can be partial/progressive)
4. Timestamps for tracking

**Request:**
```
GET /api/v1/workflows/WF-RFP-20241120123456
```

**Response Structure:**

```json
{
  "workflow_id": "WF-RFP-20241120123456",
  "state": "generating",
  "created_at": "2024-11-20T10:30:00.000000",
  "updated_at": "2024-11-20T10:30:45.000000",

  // STEP 1 RESULT: Questions extracted from RFP
  "rfp_analysis": {
    "questions": [
      "What is your approach to data security and privacy?",
      "Describe your implementation timeline and methodology",
      "What are your pricing tiers and payment terms?",
      "Do you have experience in the healthcare industry?",
      "What post-implementation support do you provide?"
    ],
    "total_questions": 5,
    "sections": [
      "Technical Requirements",
      "Pricing and Terms",
      "Company Background",
      "Implementation Plan"
    ]
  },

  // STEP 2 RESULT: Generated answers (progressive)
  // This array grows as answers are generated
  "generated_responses": [
    {
      "question": "What is your approach to data security and privacy?",
      "answer": "# Data Security Approach\n\nOur comprehensive approach to data security includes:\n\n## Encryption\n- AES-256 encryption at rest\n- TLS 1.3 for data in transit\n\n## Access Controls\n- Role-based access control (RBAC)\n- Multi-factor authentication\n- Regular access audits\n\n## Compliance\n- SOC 2 Type II certified\n- GDPR compliant\n- HIPAA ready",
      "sources": [
        {
          "text": "Our security framework follows industry best practices...",
          "score": 0.92,
          "metadata": {
            "source": "Security_Policy_2024.pdf",
            "section": "Data Protection"
          }
        }
      ],
      "confidence": 0.95
    },
    {
      "question": "Describe your implementation timeline and methodology",
      "answer": "# Implementation Timeline\n\n## Phase 1: Planning (2 weeks)\n- Requirements gathering\n- Technical setup\n\n## Phase 2: Development (6 weeks)\n- Core functionality\n- Integration testing\n\n## Phase 3: Deployment (2 weeks)\n- Production rollout\n- User training",
      "sources": [...],
      "confidence": 0.88
    }
    // More responses added as they're generated
  ],

  // STEP 3 RESULT: Quality review
  "review_result": {
    "overall_quality": "high",
    "completeness_score": 0.95,
    "issues_found": [],
    "reviewed_at": "2024-11-20T10:31:30.000000"
  },

  // STEP 4 RESULT: Final output
  "output_file_path": "/proposals/WF-RFP-20241120123456/response.docx",
  "proposal_content": null  // Not used for RFP responses
}
```

**Key Implementation Points:**

1. **Progressive Response Population:**
   ```python
   # As each answer is generated, append to the array
   workflow.generated_responses.append(new_response)
   save_workflow(workflow)
   # Frontend polls and sees new answers appear
   ```

2. **State-Dependent Fields:**
   ```python
   response = {
       "workflow_id": workflow.id,
       "state": workflow.state,
       "created_at": workflow.created_at,
       "updated_at": workflow.updated_at
   }

   # Only include if step 1 complete
   if workflow.state in ["routing", "generating", "reviewing", "formatting", "ready"]:
       response["rfp_analysis"] = workflow.rfp_analysis

   # Only include if step 2 started
   if workflow.state in ["generating", "reviewing", "formatting", "ready"]:
       response["generated_responses"] = workflow.generated_responses

   # Only include if step 3 complete
   if workflow.state in ["formatting", "ready"]:
       response["review_result"] = workflow.review_result

   # Only include if step 4 complete
   if workflow.state == "ready":
       response["output_file_path"] = workflow.output_file_path
   ```

---

## Document Edit and Save APIs

### 1. Save/Update Document Endpoint

**Endpoint:** `PUT /api/v1/documents/{workflow_id}`

**Current Status:** ⚠️ Exists but needs verification

**Purpose:** Save edited proposal content from Quick Proposal page

**Request:**
```
PUT /api/v1/documents/WF-QUICK-20241120123456?title=Proposal+for+Acme+Corp&content=...

Query Parameters:
- title: string (required) - Document title
- content: string (required) - Updated markdown content (URL encoded)
- user_id: int (optional) - User making the edit
```

**Response:**
```json
{
  "status": "success",
  "message": "Document saved successfully",
  "document": {
    "id": 1,
    "workflow_id": "WF-QUICK-20241120123456",
    "title": "Proposal for Acme Corp",
    "client_name": "Acme Corp",
    "document_type": "proposal",
    "content": "# Proposal for Acme Corp\n\n...",
    "created_at": "2024-11-20T10:30:00",
    "updated_at": "2024-11-20T10:35:00",
    "last_edited_by": {
      "id": 1,
      "name": "Sales Rep",
      "email": "sales@company.com"
    }
  }
}
```

**Implementation Notes:**

```python
@app.put("/api/v1/documents/{workflow_id}")
async def update_document(
    workflow_id: str,
    title: str = Query(...),
    content: str = Query(...),
    user_id: Optional[int] = Query(None)
):
    # Find existing document
    document = get_document_by_workflow_id(workflow_id)

    if not document:
        # Create new document if doesn't exist
        document = create_document(
            workflow_id=workflow_id,
            title=title,
            content=content,
            user_id=user_id or get_default_user_id()
        )
    else:
        # Update existing document
        document.title = title
        document.content = content
        document.updated_at = datetime.now()
        document.last_edited_by_id = user_id or get_default_user_id()
        save_document(document)

    return {
        "status": "success",
        "message": "Document saved successfully",
        "document": document.to_dict()
    }
```

---

### 2. Get Document Endpoint

**Endpoint:** `GET /api/v1/documents/{workflow_id}`

**Current Status:** ⚠️ Needs verification

**Purpose:** Retrieve saved document for editing

**Request:**
```
GET /api/v1/documents/WF-QUICK-20241120123456
```

**Response:**
```json
{
  "id": 1,
  "workflow_id": "WF-QUICK-20241120123456",
  "title": "Proposal for Acme Corp",
  "client_name": "Acme Corp",
  "document_type": "proposal",
  "content": "# Proposal for Acme Corp\n\n## Executive Summary\n...",
  "created_at": "2024-11-20T10:30:00",
  "updated_at": "2024-11-20T10:35:00",
  "last_edited_by": {
    "id": 1,
    "name": "Sales Rep",
    "email": "sales@company.com"
  }
}
```

---

## Missing API Endpoints

### 1. Download RFP Response Document

**Endpoint:** `GET /api/v1/download/{workflow_id}`

**Current Status:** ⚠️ Exists for proposals, needs to support RFP workflows

**Purpose:** Download the generated DOCX file for RFP responses

**Request:**
```
GET /api/v1/download/WF-RFP-20241120123456
```

**Response:**
- Content-Type: `application/vnd.openxmlformats-officedocument.wordprocessingml.document`
- Content-Disposition: `attachment; filename="RFP_Response_Acme_Corp_20241120.docx"`
- Binary DOCX file data

**Implementation:**

```python
@app.get("/api/v1/download/{workflow_id}")
async def download_document(workflow_id: str):
    workflow = get_workflow(workflow_id)

    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    if not workflow.output_file_path or not os.path.exists(workflow.output_file_path):
        raise HTTPException(status_code=404, detail="Output file not found")

    # Generate filename
    client_name = workflow.client_name.replace(" ", "_")
    timestamp = workflow.created_at.strftime("%Y%m%d")
    filename = f"RFP_Response_{client_name}_{timestamp}.docx"

    # Return file
    return FileResponse(
        path=workflow.output_file_path,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=filename
    )
```

---

### 2. Create Document Endpoint

**Endpoint:** `POST /api/v1/documents`

**Current Status:** 🔴 May not exist

**Purpose:** Create a new editable document from workflow

**Request:**
```json
{
  "workflow_id": "WF-QUICK-20241120123456",
  "title": "Proposal for Acme Corp",
  "content": "# Proposal...",
  "client_name": "Acme Corp",
  "document_type": "proposal"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Document created successfully",
  "document": {
    "id": 1,
    "workflow_id": "WF-QUICK-20241120123456",
    "title": "Proposal for Acme Corp",
    "content": "...",
    "created_at": "2024-11-20T10:30:00"
  }
}
```

---

## Database Schema Requirements

### Workflows Table

**Table:** `workflows`

**Required Columns:**

```sql
CREATE TABLE workflows (
    id SERIAL PRIMARY KEY,
    workflow_id VARCHAR(50) UNIQUE NOT NULL,
    state VARCHAR(20) NOT NULL,  -- created, analyzing, routing, generating, reviewing, formatting, ready, closed
    workflow_type VARCHAR(20),    -- quick_proposal, rfp_response
    client_name VARCHAR(255) NOT NULL,
    industry VARCHAR(100),
    file_path VARCHAR(500),

    -- Step 1: RFP Analysis
    rfp_analysis JSONB,  -- { questions: [...], sections: [...] }

    -- Step 2: Generated Responses
    generated_responses JSONB,  -- [{ question, answer, sources, confidence }, ...]

    -- Step 3: Review Result
    review_result JSONB,  -- { overall_quality, completeness_score, issues_found }

    -- Step 4: Output
    output_file_path VARCHAR(500),
    proposal_content TEXT,

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,

    CONSTRAINT valid_state CHECK (state IN (
        'created', 'analyzing', 'routing', 'generating',
        'reviewing', 'formatting', 'ready', 'submitted', 'closed'
    ))
);

-- Index for fast workflow lookups
CREATE INDEX idx_workflow_id ON workflows(workflow_id);
CREATE INDEX idx_workflow_state ON workflows(state);
CREATE INDEX idx_workflow_created ON workflows(created_at DESC);
```

**Example Data:**

```json
{
  "workflow_id": "WF-RFP-20241120123456",
  "state": "generating",
  "workflow_type": "rfp_response",
  "client_name": "Acme Corp",
  "industry": "Healthcare",
  "file_path": "/uploads/rfp_20241120123456.pdf",

  "rfp_analysis": {
    "questions": [
      "What is your approach to data security?",
      "Describe your implementation timeline"
    ],
    "sections": ["Technical", "Timeline", "Pricing"]
  },

  "generated_responses": [
    {
      "question": "What is your approach to data security?",
      "answer": "# Data Security\n\n...",
      "sources": [
        {
          "text": "Our security framework...",
          "score": 0.92,
          "metadata": {"source": "Security_Policy.pdf"}
        }
      ],
      "confidence": 0.95
    }
  ],

  "review_result": null,
  "output_file_path": null,
  "proposal_content": null,

  "created_at": "2024-11-20T10:30:00",
  "updated_at": "2024-11-20T10:30:45"
}
```

---

### Documents Table

**Table:** `documents`

**Required Columns:**

```sql
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    workflow_id VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    client_name VARCHAR(255),
    document_type VARCHAR(50) DEFAULT 'proposal',  -- proposal, rfp_response
    content TEXT NOT NULL,  -- Markdown content

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_edited_by_id INTEGER REFERENCES users(id),

    CONSTRAINT fk_workflow FOREIGN KEY (workflow_id) REFERENCES workflows(workflow_id) ON DELETE CASCADE
);

CREATE INDEX idx_document_workflow ON documents(workflow_id);
```

---

### Users Table

**Table:** `users`

**Required Columns:**

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    role VARCHAR(50) DEFAULT 'sales_rep',  -- sales_rep, manager, admin
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Default user for development
INSERT INTO users (name, email, role) VALUES
('Sales Rep', 'sales@company.com', 'sales_rep');
```

---

## Implementation Priority

### Phase 1: Critical (Required for Stepwise RFP)

1. ✅ **Enhanced Workflow Status Endpoint**
   - Add `rfp_analysis` field
   - Add progressive `generated_responses` array
   - Add `review_result` field

2. 🔴 **Background RFP Processing**
   - Implement `process_rfp()` function
   - Extract questions (Step 1)
   - Generate answers progressively (Step 2)
   - Quality review (Step 3)
   - Create output file (Step 4)

3. 🔴 **State Management**
   - Update workflow state at each step
   - Save intermediate results to database
   - Handle errors and set error states

### Phase 2: Important (Required for Full UX)

4. ⚠️ **Document Save/Edit**
   - Verify `PUT /api/v1/documents/{workflow_id}` works
   - Verify `GET /api/v1/documents/{workflow_id}` works
   - Test with Quick Proposal edit feature

5. ⚠️ **Download Endpoint**
   - Verify `GET /api/v1/download/{workflow_id}` works for RFP workflows
   - Generate appropriate filenames
   - Handle missing files gracefully

### Phase 3: Nice to Have

6. 🔴 **List Documents Endpoint**
   - `GET /api/v1/documents?limit=50`
   - Return all editable documents

7. 🔴 **User Management**
   - Track who edited which document
   - Return user info in document responses

---

## Testing Checklist

### Quick Proposal Flow

- [ ] Generate proposal via `POST /api/v1/proposals/quick`
- [ ] Proposal content returned in markdown
- [ ] Workflow ID returned
- [ ] Edit proposal via `PUT /api/v1/documents/{workflow_id}`
- [ ] Retrieve edited proposal via `GET /api/v1/documents/{workflow_id}`
- [ ] Download DOCX via `GET /api/v1/download/{workflow_id}`

### RFP Upload Flow

- [ ] Upload RFP via `POST /api/v1/rfp/upload`
- [ ] Workflow created with state `created`
- [ ] Poll `GET /api/v1/workflows/{id}` - returns state `analyzing`
- [ ] After step 1: `rfp_analysis.questions` populated
- [ ] Poll again - state changes to `generating`
- [ ] After step 2: `generated_responses` array grows
- [ ] Poll again - state changes to `reviewing`
- [ ] After step 3: `review_result` populated
- [ ] Poll again - state changes to `ready`
- [ ] After step 4: `output_file_path` populated
- [ ] Download file via `GET /api/v1/download/{workflow_id}`

### Q&A Flow

- [ ] Ask question via `POST /api/v1/qa/ask`
- [ ] Response includes markdown answer
- [ ] Sources array populated
- [ ] Confidence score included

### Knowledge Base Flow

- [ ] Search via `GET /api/v1/knowledge/search?query=...`
- [ ] Results returned with scores
- [ ] Add content via `POST /api/v1/knowledge/add`

---

## Example Implementation: Question Extraction

**Function:** `extract_questions_from_rfp(document_text: str) -> List[str]`

**Implementation using OpenAI/Anthropic:**

```python
async def extract_questions_from_rfp(document_text: str) -> List[str]:
    """
    Extract all questions and requirements from RFP document.
    Returns a list of questions in plain text format.
    """

    prompt = f"""
You are an RFP analysis expert. Extract ALL questions and requirements from this RFP document.

Rules:
1. Extract explicit questions (sentences ending with ?)
2. Extract implicit requirements (e.g., "Vendor must provide...")
3. Rephrase as questions if needed
4. Group related sub-questions together
5. Return as a numbered list

RFP Document:
{document_text[:4000]}  # Truncate if too long

Return ONLY the numbered list of questions, nothing else.
"""

    # Call LLM
    response = await llm_client.create_completion(
        model="claude-3-5-sonnet-20241022",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=2000
    )

    # Parse response into list
    questions_text = response.content
    questions = []

    for line in questions_text.split('\n'):
        line = line.strip()
        # Remove numbering (1. 2. etc)
        if re.match(r'^\d+\.', line):
            question = re.sub(r'^\d+\.\s*', '', line)
            questions.append(question)

    return questions
```

---

## Example Implementation: Answer Generation

**Function:** `generate_answer_for_question(question, context, knowledge_base) -> dict`

**Implementation:**

```python
async def generate_answer_for_question(
    question: str,
    context: str,
    knowledge_base
) -> dict:
    """
    Generate answer for a single RFP question using RAG.
    Returns dict with answer, sources, and confidence.
    """

    # 1. Retrieve relevant knowledge
    relevant_docs = knowledge_base.search(question, top_k=5)

    # 2. Build context from sources
    sources_context = "\n\n".join([
        f"Source: {doc.metadata['source']}\n{doc.text}"
        for doc in relevant_docs
    ])

    # 3. Create prompt
    prompt = f"""
You are answering an RFP question. Use ONLY the provided sources to answer.

Question: {question}

Available Information:
{sources_context}

Instructions:
1. Answer the question thoroughly using the sources
2. Format your answer in markdown
3. Include relevant details like timelines, pricing, features
4. Use bullet points and sections for clarity
5. Be specific and professional

Answer:
"""

    # 4. Generate answer
    response = await llm_client.create_completion(
        model="claude-3-5-sonnet-20241022",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1500
    )

    answer_text = response.content

    # 5. Format sources
    sources = [
        {
            "text": doc.text,
            "score": doc.score,
            "metadata": doc.metadata
        }
        for doc in relevant_docs
    ]

    # 6. Calculate confidence (based on source scores)
    avg_score = sum(doc.score for doc in relevant_docs) / len(relevant_docs)
    confidence = min(avg_score * 1.1, 1.0)  # Boost slightly, cap at 1.0

    return {
        "answer": answer_text,
        "sources": sources,
        "confidence": confidence
    }
```

---

## Next Steps

1. **Review this document** with the backend team
2. **Prioritize Phase 1** implementations
3. **Set up database schema** (workflows, documents, users tables)
4. **Implement background processing** for RFP workflows
5. **Test with frontend** using the provided test checklist
6. **Iterate** based on frontend feedback

---

**Document Version:** 1.0
**Last Updated:** 2024-11-20
**Author:** Frontend Integration Team
**Status:** Draft - Pending Backend Review
