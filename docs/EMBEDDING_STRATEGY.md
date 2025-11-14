# RFP Knowledge Base: Embedding Strategy & Process

## 📊 Analysis of RFP Files

### File Structure Discovered

```
resources/RFP_Hackathon/
├── ASM/                                    # Semiconductor - Talent Intelligence
├── ARM - Job Listings/                    # Job Postings Data
├── ARM - Training Provider Database/      # Training Provider RFP
├── Atlassian/                             # Market Data RFP (SaaS)
├── Denso/                                 # Skills Architecture
├── GMR Group/                             # Learning Tech Solution
├── Liberty Mutual - Workforce Analytics/  # Labor Market Analytics
├── TE - Skills Taxonomy/                  # Skills Taxonomy
├── Tennessee/                             # Labor Market Analysis
└── Lockheed/                              # Labor Market RFI

Total: ~91 documents (PDF, DOCX, XLSX, TXT)
```

### Document Categories

**Three Main Types:**
1. **Received/** - Client RFP documents (Questions, Requirements)
2. **Final/Sent/** - Draup's responses (Answers, Proposals)
3. **Attachments/** - Supporting documents (Policies, Reports, Data Dictionaries)

---

## 🎯 Embedding Strategy

### First Principles: What Are We Really Embedding?

**Mental Model**: Each RFP is a *knowledge triplet*:
- **Question** (What the client asked)
- **Answer** (How Draup responded)
- **Context** (Client industry, requirements, outcome)

### Key Insight:
Traditional embedding approaches treat documents as isolated text. But RFPs are **paired conversations**. We need to:
1. Link questions to answers
2. Preserve client context
3. Enable "similar client" searches
4. Support "similar question" retrieval

---

## 📐 Chunking Strategy

### Challenge: RFPs Have Different Structures

**Three Chunking Approaches:**

### 1. **Structural Chunking** (Best for RFPs)

```
Document → Sections → Questions → Answers
```

**Example from ASM RFP:**
```
Section: "Our Request"
├── Q1: Provide demo of Talent Intelligence platform
├── Q2: Focus on hiring analysis functionality
├── Q3: Focus on labor market analysis
└── ... (13 questions total)
```

**Chunk Size**: Each question-answer pair = 1 chunk
- **Pros**: Preserves semantic meaning, enables QA retrieval
- **Cons**: Some chunks may be large (3000+ chars)

### 2. **Semantic Chunking** (For long documents)

```python
# For documents >2000 tokens
- Split by semantic boundaries (paragraphs, sections)
- Max chunk size: 512 tokens
- Overlap: 50 tokens (to preserve context at boundaries)
```

**When to use**: Long proposal documents, case studies

### 3. **Hybrid Chunking** (Recommended)

```
1. Extract structured Q&A pairs → Store as linked chunks
2. For narrative sections → Use semantic chunking
3. For tables/data → Store as structured metadata
```

---

## 🧠 Embedding Techniques

### Current Approach: `sentence-transformers/all-MiniLM-L6-v2`

**Pros:**
- Fast (6 layers, 384 dimensions)
- Good for general semantic search
- Works offline

**Cons:**
- Limited domain knowledge (not trained on RFPs)
- 512 token limit

### Recommended: **Multi-Model Embedding Strategy**

#### **Option 1: Hybrid Embeddings** (Best for MVP)

```python
# Combine multiple embedding models
primary_model = "all-MiniLM-L6-v2"        # Fast, general
domain_model = "all-mpnet-base-v2"       # Better quality, slower

# For each chunk:
# 1. Generate both embeddings
# 2. Store both in vector DB
# 3. At search time, use weighted combination
```

**Why**: Different models capture different aspects
- MiniLM: Fast syntactic similarity
- MPNet: Deeper semantic understanding

#### **Option 2: Fine-Tuned Embeddings** (For Production)

```python
# Fine-tune on RFP-specific data
base_model = "sentence-transformers/all-mpnet-base-v2"

# Training data: Question-Answer pairs from past RFPs
# Loss function: ContrastiveLoss (similar Q&A close, dissimilar apart)
```

**Training Set:**
- Positive pairs: (Question, Its Answer)
- Negative pairs: (Question, Unrelated Answer)

#### **Option 3: OpenAI Embeddings** (Highest Quality)

```python
# Use OpenAI's text-embedding-3-large
model = "text-embedding-3-large"
dimensions = 3072  # vs 384 for MiniLM

# Pros: Best quality, handles long context
# Cons: API cost, requires internet
```

**Cost Analysis:**
- 91 documents × ~5000 tokens avg = 455K tokens
- Cost: ~$0.06 total (one-time)
- **Recommendation**: Use for production, worth the quality

---

## 🗂️ Metadata Extraction Strategy

### Critical Metadata Fields

```python
{
    # Document Identifiers
    "doc_id": "ASM-RFP-2025-Talent-Intelligence",
    "doc_type": "rfp_received",  # rfp_received, rfp_response, attachment
    "file_path": "resources/RFP_Hackathon/ASM/Received/...",

    # Client Context
    "client_name": "ASM",
    "industry": "Semiconductor",
    "company_size": "4500+",
    "geographic_focus": ["Japan", "Korea", "Taiwan", "China", "Europe", "US"],

    # RFP Metadata
    "rfp_date": "2025-05-20",
    "deadline": "2025-05-30",
    "decision_date": "2025-06-30",

    # Content Classification
    "category": "talent_intelligence",  # technical, legal, pricing, case_study
    "subcategories": [
        "hiring_analysis",
        "labor_market_analysis",
        "peer_analysis",
        "compensation_analysis"
    ],

    # Requirements
    "key_requirements": [
        "Global talent data coverage",
        "Asia-Pacific data (Japan, Korea, Taiwan, China)",
        "Semiconductor industry focus",
        "Peer benchmarking",
        "Strategic reporting"
    ],

    # Outcome Tracking
    "win_status": True,  # True, False, None (pending)
    "contract_value": 150000,  # if known
    "renewal_status": "active",  # active, churned, pending

    # Linked Documents
    "related_docs": [
        "ASM-Response-2025-Final.pdf",
        "ASM-Demo-Presentation.pdf"
    ],

    # Searchability
    "keywords": [
        "talent intelligence",
        "semiconductor",
        "hiring analysis",
        "labor market",
        "Asia Pacific"
    ],

    # Usage Tracking
    "times_retrieved": 0,
    "last_used": None,
    "quality_score": 0.95  # based on win rate, recency
}
```

### Metadata Extraction Process

```python
def extract_metadata(file_path: str, doc_text: str) -> dict:
    """
    Extract metadata using LLM + heuristics
    """
    # 1. Extract from file path
    path_parts = file_path.split("/")
    client_name = path_parts[2]  # "ASM"
    doc_type = "received" if "Received" in file_path else "final"

    # 2. Extract from document content (LLM)
    prompt = f"""
    Extract structured metadata from this RFP document:

    {doc_text[:2000]}

    Extract:
    - Client industry
    - Key requirements (list)
    - Geographic focus
    - Categories (technical, legal, pricing, etc.)
    - Timeline/dates mentioned
    - Success criteria

    Return as JSON.
    """

    metadata = llm.generate_structured(prompt)

    # 3. Enhance with domain knowledge
    metadata["client_name"] = client_name
    metadata["doc_type"] = doc_type
    metadata["file_path"] = file_path

    return metadata
```

---

## 🔄 Complete Knowledge Ingestion Process

### **Step-by-Step Pipeline**

```
┌─────────────────────────────────────────────────────────────┐
│                1. DOCUMENT DISCOVERY                         │
│  • Scan resources/RFP_Hackathon/ recursively                │
│  • Filter by file type (PDF, DOCX, XLSX, TXT)               │
│  • Group by client folders                                  │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                2. DOCUMENT EXTRACTION                        │
│  • PDF → PyPDF2 / pdfplumber                                │
│  • DOCX → python-docx                                       │
│  • XLSX → openpyxl (convert tables to text)                 │
│  • TXT → direct read                                        │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                3. STRUCTURE DETECTION                        │
│  • Detect Q&A pairs (regex patterns)                        │
│  • Identify sections (headers, numbering)                   │
│  • Extract tables and structured data                       │
│  • Link Request → Response documents                        │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                4. METADATA EXTRACTION                        │
│  • LLM-based extraction (client, industry, reqs)            │
│  • Path-based extraction (client name, doc type)            │
│  • Date extraction (NER for timeline)                       │
│  • Keyword extraction (TF-IDF + LLM)                        │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                5. CHUNKING                                   │
│  • Structural chunks: Q&A pairs                             │
│  • Semantic chunks: Long narratives (512 tokens max)        │
│  • Preserve overlap (50 tokens)                             │
│  • Attach metadata to each chunk                            │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                6. EMBEDDING GENERATION                       │
│  • Generate embeddings (sentence-transformers)              │
│  • Option: Multi-model (MiniLM + MPNet)                     │
│  • Option: OpenAI embeddings for critical docs              │
│  • Store: [embedding_vector, chunk_text, metadata]          │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                7. VECTOR STORE INGESTION                     │
│  • Add to FAISS index                                       │
│  • Store metadata in parallel array                         │
│  • Create client-specific indices (optional)                │
│  • Build reverse index (metadata → chunks)                  │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                8. POST-PROCESSING                            │
│  • Link Q&A pairs (bidirectional)                           │
│  • Create summary embeddings (per document)                 │
│  • Build client similarity graph                            │
│  • Index for faceted search (industry, category, etc.)      │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                9. VALIDATION & QA                            │
│  • Test retrieval: "semiconductor talent intelligence"      │
│  • Verify metadata accuracy (spot check)                    │
│  • Measure embedding quality (cosine similarity tests)      │
│  • Log statistics (chunks per doc, avg chunk size)          │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔍 Advanced Retrieval Strategies

### 1. **Hybrid Search** (Recommended)

```python
def hybrid_search(query: str, filters: dict = None, top_k: int = 5):
    """
    Combine semantic search + metadata filtering
    """
    # Step 1: Semantic search (cast wide net)
    semantic_results = vector_store.search(query, top_k=top_k*3)

    # Step 2: Apply metadata filters
    filtered = [
        r for r in semantic_results
        if matches_filters(r.metadata, filters)
    ]

    # Step 3: Re-rank by:
    # - Semantic similarity (40%)
    # - Industry match (30%)
    # - Win rate (20%)
    # - Recency (10%)
    reranked = rerank(filtered, weights=[0.4, 0.3, 0.2, 0.1])

    return reranked[:top_k]
```

### 2. **Question-Answer Linking**

```python
# When a query matches a question chunk:
# 1. Return the question chunk
# 2. ALSO return its linked answer chunk
# 3. Include context from related questions

def retrieve_with_context(query: str):
    """
    Retrieve Q&A pairs with context
    """
    # Find matching question
    question_chunk = vector_store.search(query, filters={"type": "question"}, top_k=1)[0]

    # Get linked answer
    answer_chunk = get_linked_chunk(question_chunk.metadata["answer_id"])

    # Get related questions from same RFP
    related_qs = vector_store.search(
        query,
        filters={"rfp_id": question_chunk.metadata["rfp_id"]},
        top_k=3
    )

    return {
        "question": question_chunk,
        "answer": answer_chunk,
        "related_questions": related_qs
    }
```

### 3. **Client Similarity Search**

```python
# Find similar clients to personalize responses
def find_similar_clients(target_client: str, top_k: int = 3):
    """
    Find clients with similar characteristics
    """
    target_metadata = get_client_metadata(target_client)

    similar_clients = []
    for client in all_clients:
        similarity = calculate_client_similarity(
            target_metadata,
            get_client_metadata(client),
            weights={
                "industry": 0.4,
                "company_size": 0.2,
                "geographic_focus": 0.2,
                "categories": 0.2
            }
        )
        similar_clients.append((client, similarity))

    return sorted(similar_clients, key=lambda x: x[1], reverse=True)[:top_k]
```

---

## 📈 Quality Metrics

### Embedding Quality Tests

```python
# Test 1: Semantic Coherence
query = "semiconductor talent intelligence platform"
results = search(query)
# Expected: ASM RFP should be top result

# Test 2: Cross-Client Similarity
query = "skills taxonomy implementation"
results = search(query)
# Expected: TE (Skills Taxonomy) and GMR (Skills Architecture) should rank high

# Test 3: Geographic Filtering
query = "Asia Pacific talent data"
results = search(query, filters={"geographic_focus": "Asia"})
# Expected: ASM (Japan/Korea/Taiwan/China focus) should be top

# Test 4: Q&A Pair Linking
query = "Provide demo of your platform"
qa_pair = retrieve_with_context(query)
# Expected: Question from ASM RFP + linked Answer from Draup response
```

---

## 🚀 Implementation Priorities

### **Phase 1: MVP (Week 1)**
1. ✅ Basic document extraction (PDF, DOCX, TXT)
2. ✅ Simple chunking (paragraph-based, 512 tokens)
3. ✅ Single embedding model (MiniLM)
4. ✅ FAISS vector store
5. ✅ Basic metadata (client, doc_type, file_path)

### **Phase 2: Enhanced (Week 2)**
1. 🔄 Structural Q&A detection
2. 🔄 LLM-based metadata extraction
3. 🔄 Hybrid search (semantic + filters)
4. 🔄 Q&A linking
5. 🔄 Client similarity scoring

### **Phase 3: Production (Week 3-4)**
1. ⏳ Fine-tuned embeddings (RFP-specific)
2. ⏳ Multi-model embedding
3. ⏳ Advanced re-ranking
4. ⏳ Automatic win/loss outcome tracking
5. ⏳ Analytics dashboard

---

## 💡 Recommendations

### **For Hackathon (Next 48 hours):**

1. **Use OpenAI Embeddings** (`text-embedding-3-small`)
   - Cost: ~$0.02 for entire dataset
   - Quality: 10x better than MiniLM
   - Time saved: No need for fine-tuning

2. **Focus on Metadata Extraction**
   - Client name, industry, categories
   - This is 70% of retrieval quality
   - Use LLM to extract in batch

3. **Implement Q&A Linking**
   - Manually map Received/ → Final/ pairs
   - Store as linked chunks
   - Huge impact on response quality

4. **Build Simple Web UI**
   - Search box → Results with metadata
   - Filter by client, industry, category
   - Show Q&A pairs side-by-side

### **Key Success Metrics:**

1. **Retrieval Accuracy**: 90%+ relevant results in top-3
2. **Speed**: <500ms for search queries
3. **Coverage**: All 91 documents embedded
4. **Metadata Quality**: 95%+ fields populated correctly

---

## 📝 Next Steps

See implementation in:
- `services/embedding_service.py` - Enhanced embedding logic
- `services/metadata_extractor.py` - LLM-based metadata extraction
- `scripts/ingest_rfp_knowledge.py` - Batch ingestion pipeline
- `scripts/validate_embeddings.py` - Quality validation tests

