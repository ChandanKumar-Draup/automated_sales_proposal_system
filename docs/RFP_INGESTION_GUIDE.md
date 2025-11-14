# RFP Knowledge Base Ingestion Guide

## 🎯 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run Ingestion Pipeline

```bash
# Preview files (dry run)
python scripts/ingest_rfp_knowledge.py --dry-run

# Ingest with sentence-transformers (free, offline)
python scripts/ingest_rfp_knowledge.py

# Ingest with OpenAI embeddings (better quality, ~$0.02 cost)
python scripts/ingest_rfp_knowledge.py --use-openai
```

### 3. Validate Embeddings

```bash
python scripts/validate_embeddings.py
```

---

## 📊 What Gets Ingested?

The script processes **91 RFP documents** across **10 clients**:

| Client | Industry | Document Count |
|--------|----------|----------------|
| ASM | Semiconductor | 4 docs |
| ARM (Job Listings) | Technology | 5 docs |
| ARM (Training) | Technology | 5 docs |
| Atlassian | SaaS/Technology | 17 docs |
| Denso | Automotive | 7 docs |
| GMR Group | Aviation/Infra | 20 docs |
| Liberty Mutual | Insurance | 5 docs |
| TE | Manufacturing | 8 docs |
| Tennessee | Government | 3 docs |
| Lockheed | Aerospace/Defense | 1 doc |

---

## 🔄 Ingestion Process

### Step-by-Step

```
1. Document Discovery
   ├─ Scan resources/RFP_Hackathon/
   ├─ Find all PDF, DOCX, XLSX, TXT files
   └─ Total: 91 files

2. Text Extraction
   ├─ PDF → PyPDF2
   ├─ DOCX → python-docx
   ├─ XLSX → openpyxl (tables to text)
   └─ TXT → direct read

3. Metadata Extraction (LLM-powered)
   ├─ Client name (from path)
   ├─ Industry (from content)
   ├─ Document type (Received/Final/Attachment)
   ├─ Categories (talent, skills, pricing, etc.)
   ├─ Key requirements (extracted by LLM)
   ├─ Geographic focus
   ├─ Timeline/dates
   └─ Q&A pairs (if structured RFP)

4. Chunking (Hybrid Strategy)
   ├─ Detect Q&A pairs → Structural chunks
   ├─ Long narratives → Semantic chunks (512 tokens, 50 overlap)
   └─ Each chunk: {text, type, metadata}

5. Embedding Generation
   ├─ Option A: sentence-transformers (all-MiniLM-L6-v2)
   │   - Dimension: 384
   │   - Speed: ~100 chunks/sec
   │   - Cost: FREE
   │
   └─ Option B: OpenAI (text-embedding-3-small)
       - Dimension: 1536
       - Speed: ~2000 chunks/sec
       - Cost: $0.02 total

6. Vector Store Ingestion
   ├─ Add chunks to FAISS index
   ├─ Store metadata in parallel
   └─ Save to data/vector_store/

7. RFP-Response Linking
   ├─ Match Received/ ← → Final/Sent/
   ├─ Link by client name
   └─ Store bidirectional references

8. Persistence
   ├─ FAISS index → data/vector_store/faiss.index
   ├─ Documents → data/vector_store/documents.pkl
   ├─ Metadata → data/vector_store/metadata.pkl
   └─ RFP metadata → data/vector_store/rfp_metadata.json
```

---

## 📈 Expected Output

After ingestion, you should see:

```
==================================================
INGESTION COMPLETE
==================================================
Total files discovered: 91
Successfully processed: 88
Failed: 3
Total chunks created: 245
Avg chunks per doc: 2.8
Unique clients: 10
Clients: ARM, ASM, Atlassian, Denso, GMR Group, Liberty Mutual, Lockheed, TE, Tennessee
==================================================
```

**Why ~245 chunks from 91 docs?**
- Most RFPs split into 2-4 chunks (sections, Q&A pairs)
- Large proposals (Atlassian, GMR) → 10-15 chunks
- Short docs (Lockheed RFI) → 1 chunk

---

## 🧪 Validation Tests

Run `python scripts/validate_embeddings.py` to check quality:

### Test 1: Semantic Coherence
```
Query: "semiconductor talent intelligence"
Expected: ASM RFP should rank #1
```

### Test 2: Client Retrieval
```
Query: "Atlassian RFP requirements"
Expected: Atlassian docs in top-5
```

### Test 3: Category Filtering
```
Query: "skills taxonomy implementation"
Expected: TE and GMR docs ranked high
```

### Test 4: Knowledge Coverage
```
Check: Total chunks > 200
Check: All 10 clients present
```

### Test 5: Retrieval Speed
```
Target: <500ms per search
Good: <100ms per search
```

---

## 🔍 Example Searches After Ingestion

### Search 1: Find Similar Client RFPs

```python
from services.vector_store import VectorStore

vs = VectorStore()

# Find semiconductor-related RFPs
results = vs.search("semiconductor talent intelligence platform", top_k=5)

for doc, score, meta in results:
    print(f"Client: {meta.get('client_name')}")
    print(f"Score: {score:.3f}")
    print(f"Excerpt: {doc[:150]}...\n")
```

**Expected Output:**
```
Client: ASM
Score: 0.892
Excerpt: ASM is issuing a Request for Proposal for Talent Intelligence platform. Focus on semiconductor industry data coverage...

Client: Denso
Score: 0.745
Excerpt: Scope of Work for Skills Architecture. Technical skills taxonomy for manufacturing workforce...
```

### Search 2: Find Answers to Specific Questions

```python
# Search for pricing-related content
results = vs.search("competitive pricing proposal commercial terms", top_k=3)

for doc, score, meta in results:
    client = meta.get('client_name')
    doc_type = meta.get('doc_type')
    print(f"[{client}] {doc_type}: {doc[:100]}...")
```

### Search 3: Find Client-Specific Context

```python
# Find all Atlassian-related content
results = vs.search(
    "Atlassian requirements",
    top_k=10
)

# Group by document type
received = [r for r in results if r[2].get('doc_type') == 'rfp_received']
responses = [r for r in results if r[2].get('doc_type') == 'rfp_response']

print(f"Found {len(received)} request docs")
print(f"Found {len(responses)} response docs")
```

---

## 🎨 Advanced Usage

### Custom Metadata Filtering

```python
# Search only in RFP responses (not requests)
results = vs.search(
    "implementation approach",
    filters={"doc_type": "rfp_response"},
    top_k=5
)
```

### Multi-Query Search

```python
# Find documents matching multiple criteria
queries = [
    "talent intelligence",
    "labor market analysis",
    "workforce analytics"
]

all_results = []
for query in queries:
    results = vs.search(query, top_k=3)
    all_results.extend(results)

# Deduplicate and re-rank
unique_docs = {}
for doc, score, meta in all_results:
    doc_id = meta.get('file_path')
    if doc_id not in unique_docs or score > unique_docs[doc_id][1]:
        unique_docs[doc_id] = (doc, score, meta)

top_results = sorted(unique_docs.values(), key=lambda x: x[1], reverse=True)[:5]
```

---

## 🐛 Troubleshooting

### Issue: "No documents found"
**Solution**: Check that `resources/RFP_Hackathon/` exists

```bash
ls -la resources/RFP_Hackathon/
```

### Issue: "Failed to extract text from PDF"
**Possible Causes**:
- Scanned PDF (image-based, needs OCR)
- Encrypted PDF
- Corrupted file

**Solution**: Check which PDFs failed:
```python
# Add --verbose flag to see which files fail
python scripts/ingest_rfp_knowledge.py --verbose
```

### Issue: "OpenAI API key not found"
**Solution**: Add to `.env` file:
```bash
echo "OPENAI_API_KEY=sk-..." >> .env
```

### Issue: "Low embedding quality scores"
**Possible Causes**:
- Using MiniLM (lower quality than OpenAI)
- Chunking too aggressive (losing context)
- Metadata not extracted properly

**Solution**: Re-ingest with OpenAI embeddings:
```bash
# Clear existing
rm -rf data/vector_store/

# Re-ingest with better embeddings
python scripts/ingest_rfp_knowledge.py --use-openai
```

---

## 📚 Next Steps

After ingestion, you can:

1. **Use in RFP Generation**
   ```python
   from agents.retriever import RetrieverAgent
   from services.vector_store import VectorStore

   vs = VectorStore()
   retriever = RetrieverAgent(vs)

   # Find relevant past responses
   results = retriever.retrieve(
       query="Provide demo of talent intelligence platform",
       client_context={"industry": "Semiconductor"},
       top_k=5
   )
   ```

2. **Build Similar Client Finder**
   ```python
   from services.metadata_extractor import ClientMatcher

   # Find clients similar to new prospect
   similar = ClientMatcher.find_similar_clients(
       target_metadata={"industry": "Semiconductor", "categories": ["talent_intelligence"]},
       all_metadata=all_rfp_metadata,
       top_k=3
   )
   ```

3. **Create RFP Analytics Dashboard**
   - Win rate by industry
   - Common requirements across clients
   - Category distribution
   - Geographic coverage heatmap

---

## 💰 Cost Analysis

### Option A: Sentence-Transformers (FREE)
- Compute: Local CPU/GPU
- Storage: ~50MB (FAISS index + metadata)
- Quality: Good (7/10)

### Option B: OpenAI Embeddings ($0.02)
- 91 docs × ~500 tokens avg = ~45K tokens
- Cost: 45K tokens × $0.00002/token = ~$0.02
- Storage: ~150MB (larger embeddings)
- Quality: Excellent (9/10)

**Recommendation**: Use OpenAI for production ($0.02 is negligible for quality gain)

---

## 🎯 Success Metrics

After ingestion, you should achieve:

| Metric | Target | How to Measure |
|--------|--------|----------------|
| Retrieval Accuracy | >90% | Validation test pass rate |
| Search Speed | <500ms | `validate_embeddings.py` |
| Coverage | 100% | All 91 docs indexed |
| Metadata Quality | >95% | Spot-check 10 random docs |
| Client Linkage | >80% | RFP-Response pairs linked |

Run `python scripts/validate_embeddings.py` to verify all metrics!

