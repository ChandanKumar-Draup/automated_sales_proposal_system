# Workflows Feature - Backend Requirements

## Overview

This document specifies the backend requirements for the Workflows feature. The good news: **Most of the required APIs already exist!** This document clarifies what's implemented and what needs enhancement.

**Status**: ✅ Core API exists, 🔧 Minor enhancements recommended

---

## Table of Contents

1. [Existing API](#existing-api)
2. [Required Enhancements](#required-enhancements)
3. [Database Schema](#database-schema)
4. [Implementation Examples](#implementation-examples)
5. [Testing Checklist](#testing-checklist)

---

## Existing API

### ✅ GET `/api/v1/documents`

**Status**: Already implemented (as per API_REFERENCE.md)

**Description**: List all editable documents (workflows)

**Request**:
```http
GET /api/v1/documents?limit=50 HTTP/1.1
Host: localhost:8000
Accept: application/json
```

**Query Parameters**:
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `limit` | int | No | 50 | Maximum number of documents to return |

**Response** (200 OK):
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
      "content": "# Proposal for Acme Corporation\n\n...",
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

**Response Fields**:
- `count`: Total number of documents
- `documents`: Array of document objects

**Document Object**:
- `id`: Database primary key
- `workflow_id`: Unique workflow identifier
- `title`: Human-readable title
- `client_name`: Client company name
- `document_type`: Either `"proposal"` or `"rfp_response"`
- `content`: Markdown content of the document
- `created_at`: ISO 8601 timestamp
- `updated_at`: ISO 8601 timestamp
- `last_edited_by`: Optional user information

---

## Required Enhancements

### 🔧 Enhancement 1: Sorting by Updated Date

**Current Behavior**: Documents returned in database order (likely by `id`)

**Desired Behavior**: Documents sorted by `updated_at` DESC (most recent first)

**Why**: Users want to see their most recent workflows first

**Implementation**:

```python
@app.get("/api/v1/documents")
def list_documents(limit: int = 50):
    """List all documents sorted by most recently updated"""
    documents = db.query(Document)\
        .order_by(Document.updated_at.desc())\
        .limit(limit)\
        .all()

    return {
        "count": len(documents),
        "documents": [doc.to_dict() for doc in documents]
    }
```

**SQL Equivalent**:
```sql
SELECT * FROM documents
ORDER BY updated_at DESC
LIMIT 50;
```

### 🔧 Enhancement 2: Pagination Support

**Current Limitation**: Only supports `limit` parameter

**Desired**: Support `offset` for pagination

**Implementation**:

```python
@app.get("/api/v1/documents")
def list_documents(limit: int = 50, offset: int = 0):
    """List documents with pagination"""
    query = db.query(Document).order_by(Document.updated_at.desc())

    # Get total count for pagination metadata
    total = query.count()

    # Apply pagination
    documents = query.offset(offset).limit(limit).all()

    return {
        "count": total,
        "limit": limit,
        "offset": offset,
        "documents": [doc.to_dict() for doc in documents]
    }
```

**Example Requests**:
```http
GET /api/v1/documents?limit=20&offset=0   # Page 1
GET /api/v1/documents?limit=20&offset=20  # Page 2
GET /api/v1/documents?limit=20&offset=40  # Page 3
```

### 🔧 Enhancement 3: Filter by Document Type

**Use Case**: User wants to see only proposals or only RFP responses

**Implementation**:

```python
from typing import Optional
from enum import Enum

class DocumentType(str, Enum):
    PROPOSAL = "proposal"
    RFP_RESPONSE = "rfp_response"

@app.get("/api/v1/documents")
def list_documents(
    limit: int = 50,
    offset: int = 0,
    document_type: Optional[DocumentType] = None
):
    """List documents with optional type filtering"""
    query = db.query(Document).order_by(Document.updated_at.desc())

    # Apply filter if specified
    if document_type:
        query = query.filter(Document.document_type == document_type)

    total = query.count()
    documents = query.offset(offset).limit(limit).all()

    return {
        "count": total,
        "limit": limit,
        "offset": offset,
        "filter": document_type.value if document_type else None,
        "documents": [doc.to_dict() for doc in documents]
    }
```

**Example Requests**:
```http
GET /api/v1/documents?document_type=proposal       # Only proposals
GET /api/v1/documents?document_type=rfp_response   # Only RFP responses
GET /api/v1/documents                              # All documents
```

### 🔧 Enhancement 4: Search by Client Name or Title

**Use Case**: User searches for specific client or proposal

**Implementation**:

```python
@app.get("/api/v1/documents")
def list_documents(
    limit: int = 50,
    offset: int = 0,
    document_type: Optional[DocumentType] = None,
    search: Optional[str] = None
):
    """List documents with search"""
    query = db.query(Document).order_by(Document.updated_at.desc())

    # Apply filters
    if document_type:
        query = query.filter(Document.document_type == document_type)

    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Document.title.ilike(search_term),
                Document.client_name.ilike(search_term)
            )
        )

    total = query.count()
    documents = query.offset(offset).limit(limit).all()

    return {
        "count": total,
        "limit": limit,
        "offset": offset,
        "filter": document_type.value if document_type else None,
        "search": search,
        "documents": [doc.to_dict() for doc in documents]
    }
```

**Example Requests**:
```http
GET /api/v1/documents?search=Acme          # Search for "Acme"
GET /api/v1/documents?search=RFP&document_type=rfp_response
```

---

## Database Schema

### Documents Table

**Table**: `documents`

**Expected Schema**:

```sql
CREATE TABLE documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workflow_id VARCHAR(50) UNIQUE NOT NULL,
    title VARCHAR(255) NOT NULL,
    client_name VARCHAR(255) NOT NULL,
    document_type VARCHAR(20) NOT NULL,  -- 'proposal' or 'rfp_response'
    content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_edited_by_id INTEGER,

    CONSTRAINT fk_user FOREIGN KEY (last_edited_by_id)
        REFERENCES users(id) ON DELETE SET NULL
);

-- Indexes for performance
CREATE INDEX idx_documents_updated ON documents(updated_at DESC);
CREATE INDEX idx_documents_workflow ON documents(workflow_id);
CREATE INDEX idx_documents_type ON documents(document_type);
CREATE INDEX idx_documents_client ON documents(client_name);
```

**Field Descriptions**:
- `id`: Auto-increment primary key
- `workflow_id`: Unique identifier from workflow (e.g., `WF-QUICK-20241118103000`)
- `title`: User-facing title (e.g., "Proposal for Acme Corp")
- `client_name`: Client company name
- `document_type`: Either `"proposal"` or `"rfp_response"`
- `content`: Full markdown content
- `created_at`: When workflow was first created
- `updated_at`: When workflow was last modified
- `last_edited_by_id`: Foreign key to users table

### Users Table

**Table**: `users`

**Schema**:

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    role VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Purpose**: Track who edited each workflow

---

## Implementation Examples

### Example 1: Basic Document Listing

**Python (FastAPI)**:

```python
from fastapi import FastAPI, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

app = FastAPI()

@app.get("/api/v1/documents")
def list_documents(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    List all documents sorted by most recent update.

    Args:
        limit: Maximum documents to return (1-100)
        offset: Number of documents to skip
        db: Database session

    Returns:
        JSON response with count and documents array
    """
    # Query with sorting
    query = db.query(Document)\
        .order_by(Document.updated_at.desc())

    # Get total count
    total = query.count()

    # Apply pagination
    documents = query.offset(offset).limit(limit).all()

    # Convert to response format
    return {
        "count": total,
        "limit": limit,
        "offset": offset,
        "documents": [
            {
                "id": doc.id,
                "workflow_id": doc.workflow_id,
                "title": doc.title,
                "client_name": doc.client_name,
                "document_type": doc.document_type,
                "content": doc.content,
                "created_at": doc.created_at.isoformat(),
                "updated_at": doc.updated_at.isoformat(),
                "last_edited_by": get_user_info(doc.last_edited_by_id)
                    if doc.last_edited_by_id else None
            }
            for doc in documents
        ]
    }

def get_user_info(user_id: int) -> Optional[dict]:
    """Get user information for last_edited_by field"""
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        return {
            "id": user.id,
            "name": user.name,
            "email": user.email
        }
    return None
```

### Example 2: Document Creation (When Workflow Completes)

**Purpose**: Create a document record when a workflow finishes

```python
@app.post("/api/v1/proposals/quick")
async def create_quick_proposal(request: ProposalRequest):
    """Generate quick proposal and create document record"""

    # 1. Generate proposal
    workflow_id = generate_workflow_id()
    proposal_content = await generate_proposal_content(
        client_name=request.client_name,
        requirements=request.requirements
    )

    # 2. Create workflow record
    workflow = Workflow(
        workflow_id=workflow_id,
        state="ready",
        proposal_content=proposal_content
    )
    db.add(workflow)

    # 3. Create document record for Workflows page
    document = Document(
        workflow_id=workflow_id,
        title=f"Proposal for {request.client_name}",
        client_name=request.client_name,
        document_type="proposal",
        content=proposal_content,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(document)
    db.commit()

    return {
        "workflow_id": workflow_id,
        "state": "ready",
        "proposal_content": proposal_content
    }
```

### Example 3: Document Update (When User Edits)

**Endpoint**: `PUT /api/v1/documents/{workflow_id}`

```python
@app.put("/api/v1/documents/{workflow_id}")
def update_document(
    workflow_id: str,
    title: str = Query(...),
    content: str = Query(...),
    user_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """Update document title and content"""

    # Find document
    document = db.query(Document)\
        .filter(Document.workflow_id == workflow_id)\
        .first()

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    # Update fields
    document.title = title
    document.content = content
    document.updated_at = datetime.utcnow()

    if user_id:
        document.last_edited_by_id = user_id

    db.commit()
    db.refresh(document)

    return {
        "status": "success",
        "message": "Document saved successfully",
        "document": document.to_dict()
    }
```

---

## API Contract

### Complete API Specification

**Endpoint**: `GET /api/v1/documents`

**Query Parameters**:
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `limit` | int | No | 50 | Max documents (1-100) |
| `offset` | int | No | 0 | Skip N documents |
| `document_type` | string | No | null | Filter: "proposal" or "rfp_response" |
| `search` | string | No | null | Search in title/client name |

**Response Schema**:
```typescript
{
  count: number;           // Total matching documents
  limit: number;           // Applied limit
  offset: number;          // Applied offset
  filter: string | null;   // Applied document_type filter
  search: string | null;   // Applied search term
  documents: Array<{
    id: number;
    workflow_id: string;
    title: string;
    client_name: string;
    document_type: "proposal" | "rfp_response";
    content: string;
    created_at: string;    // ISO 8601
    updated_at: string;    // ISO 8601
    last_edited_by?: {
      id: number;
      name: string;
      email: string;
    };
  }>;
}
```

**Error Responses**:

```json
// 400 Bad Request
{
  "detail": "Invalid limit value. Must be between 1 and 100."
}

// 500 Internal Server Error
{
  "detail": "Database connection failed"
}
```

---

## Testing Checklist

### Unit Tests

- [ ] **Test 1**: List documents returns correct count
- [ ] **Test 2**: Documents are sorted by updated_at DESC
- [ ] **Test 3**: Limit parameter works correctly
- [ ] **Test 4**: Offset parameter works correctly
- [ ] **Test 5**: Filter by document_type works
- [ ] **Test 6**: Search by title works
- [ ] **Test 7**: Search by client_name works
- [ ] **Test 8**: Empty results handled correctly
- [ ] **Test 9**: Invalid limit returns 400 error
- [ ] **Test 10**: Database error returns 500 error

### Integration Tests

**Test Script** (Python):

```python
import requests

API_BASE = "http://localhost:8000"

def test_list_documents():
    """Test basic document listing"""
    response = requests.get(f"{API_BASE}/api/v1/documents?limit=10")

    assert response.status_code == 200
    data = response.json()

    assert "count" in data
    assert "documents" in data
    assert isinstance(data["documents"], list)

    if data["count"] > 0:
        doc = data["documents"][0]
        assert "workflow_id" in doc
        assert "title" in doc
        assert "client_name" in doc
        assert "document_type" in doc
        assert doc["document_type"] in ["proposal", "rfp_response"]

def test_pagination():
    """Test pagination works correctly"""
    # Page 1
    page1 = requests.get(f"{API_BASE}/api/v1/documents?limit=5&offset=0")
    # Page 2
    page2 = requests.get(f"{API_BASE}/api/v1/documents?limit=5&offset=5")

    assert page1.status_code == 200
    assert page2.status_code == 200

    docs1 = page1.json()["documents"]
    docs2 = page2.json()["documents"]

    # Ensure no overlap
    ids1 = {doc["id"] for doc in docs1}
    ids2 = {doc["id"] for doc in docs2}
    assert ids1.isdisjoint(ids2)

def test_filtering():
    """Test document type filtering"""
    response = requests.get(
        f"{API_BASE}/api/v1/documents?document_type=proposal"
    )

    assert response.status_code == 200
    data = response.json()

    # All results should be proposals
    for doc in data["documents"]:
        assert doc["document_type"] == "proposal"

def test_search():
    """Test search functionality"""
    response = requests.get(
        f"{API_BASE}/api/v1/documents?search=Acme"
    )

    assert response.status_code == 200
    data = response.json()

    # All results should contain "Acme"
    for doc in data["documents"]:
        assert "acme" in doc["title"].lower() or \
               "acme" in doc["client_name"].lower()
```

### Manual Testing

**curl Commands**:

```bash
# Test 1: Basic listing
curl "http://localhost:8000/api/v1/documents?limit=10"

# Test 2: Pagination
curl "http://localhost:8000/api/v1/documents?limit=20&offset=20"

# Test 3: Filter by type
curl "http://localhost:8000/api/v1/documents?document_type=proposal"

# Test 4: Search
curl "http://localhost:8000/api/v1/documents?search=Acme"

# Test 5: Combined filters
curl "http://localhost:8000/api/v1/documents?document_type=rfp_response&search=Tech&limit=10"
```

---

## Performance Considerations

### Database Indexing

**Critical Indexes**:

```sql
-- Most important: speeds up sorting
CREATE INDEX idx_documents_updated_desc ON documents(updated_at DESC);

-- For filtering by type
CREATE INDEX idx_documents_type ON documents(document_type);

-- For search queries
CREATE INDEX idx_documents_client ON documents(client_name);
CREATE INDEX idx_documents_title ON documents(title);

-- Compound index for filtered + sorted queries
CREATE INDEX idx_documents_type_updated ON documents(document_type, updated_at DESC);
```

**Query Performance**:

```sql
-- Without index: Full table scan (SLOW)
SELECT * FROM documents ORDER BY updated_at DESC LIMIT 50;

-- With index: Index scan (FAST)
-- Uses idx_documents_updated_desc
```

### Caching Strategy

**Option 1**: Cache recent documents in memory

```python
from functools import lru_cache
from datetime import datetime, timedelta

@lru_cache(maxsize=10)
def get_cached_documents(cache_key: str):
    """Cache documents for 30 seconds"""
    return list_documents()

@app.get("/api/v1/documents")
def list_documents_cached():
    # Generate cache key that expires every 30 seconds
    cache_key = datetime.now().replace(second=0, microsecond=0)
    return get_cached_documents(str(cache_key))
```

**Option 2**: Use Redis for distributed caching

```python
import redis
import json

redis_client = redis.Redis(host='localhost', port=6379)

@app.get("/api/v1/documents")
def list_documents_with_redis(limit: int = 50):
    cache_key = f"documents:list:{limit}"

    # Try cache first
    cached = redis_client.get(cache_key)
    if cached:
        return json.loads(cached)

    # Fetch from database
    result = fetch_documents_from_db(limit)

    # Cache for 60 seconds
    redis_client.setex(cache_key, 60, json.dumps(result))

    return result
```

### Pagination Best Practices

**Limit Maximum Results**:

```python
limit: int = Query(50, ge=1, le=100)  # Max 100
```

**Return Pagination Metadata**:

```json
{
  "count": 250,
  "limit": 50,
  "offset": 100,
  "has_more": true,
  "next_offset": 150,
  "documents": [...]
}
```

---

## Implementation Priority

### Phase 1: Essential (Implement First)

1. ✅ **Basic listing endpoint** - Already exists
2. 🔧 **Sort by updated_at DESC** - Quick fix, high impact
3. 🔧 **Ensure last_edited_by is populated** - Needed for UI

### Phase 2: Enhancements (Next Sprint)

4. 🔧 **Pagination support** - Needed as data grows
5. 🔧 **Document type filtering** - Nice UX improvement
6. 🔧 **Database indexes** - Performance optimization

### Phase 3: Advanced Features (Future)

7. 📋 **Search functionality** - Advanced feature
8. 📋 **Caching layer** - Optimization for scale
9. 📋 **Bulk operations** - Power user feature

---

## Conclusion

The Workflows feature backend is **90% complete** with the existing `GET /api/v1/documents` endpoint. The main enhancements needed are:

1. **Sorting** - Ensure documents are returned in reverse chronological order
2. **Pagination** - Add offset parameter for large datasets
3. **Indexing** - Add database indexes for query performance

All other features (filtering, search) are optional enhancements that can be added incrementally based on user needs.

**Estimated Implementation Time**:
- Phase 1 (Essential): 2-4 hours
- Phase 2 (Enhancements): 1-2 days
- Phase 3 (Advanced): 3-5 days
