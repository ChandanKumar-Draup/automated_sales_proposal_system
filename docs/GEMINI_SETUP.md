# Using Google Gemini for Embeddings

This guide explains how to use Google Gemini embeddings instead of OpenAI for the automated sales proposal system.

## Why Use Gemini Embeddings?

- **High Quality**: Gemini's `text-embedding-004` model provides excellent embedding quality
- **768 Dimensions**: Good balance between quality and performance
- **Alternative to OpenAI**: Great option if you don't have OpenAI API access
- **Competitive Pricing**: Cost-effective for embedding generation

## Prerequisites

1. **Get Gemini API Key**:
   - Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Click "Create API Key"
   - Copy your API key

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Setup Instructions

### 1. Configure Environment Variables

Create or update your `.env` file:

```bash
# Copy example file
cp .env.example .env

# Edit .env and add your Gemini API key
GEMINI_API_KEY=your_gemini_api_key_here
```

### 2. Using Gemini for Knowledge Ingestion

Run the ingestion script with the `--use-gemini` flag:

```bash
python scripts/ingest_rfp_knowledge.py --use-gemini
```

**Options:**
- `--use-gemini`: Use Gemini embeddings
- `--dry-run`: Preview files without processing
- `--root-dir`: Specify custom RFP directory (default: `resources/RFP_Hackathon`)

**Example:**
```bash
# Ingest with Gemini embeddings
python scripts/ingest_rfp_knowledge.py --use-gemini

# Dry run to preview files
python scripts/ingest_rfp_knowledge.py --use-gemini --dry-run

# Custom directory
python scripts/ingest_rfp_knowledge.py --use-gemini --root-dir ./my_rfps
```

### 3. Using Gemini in Your Code

```python
from services.embedding_service import EmbeddingService

# Initialize with Gemini
embedding_service = EmbeddingService(
    use_gemini=True,
    gemini_model="models/text-embedding-004"
)

# Embed single text
text = "Your text here"
embedding = embedding_service.embed_single(text)

# Embed batch
texts = ["Text 1", "Text 2", "Text 3"]
embeddings = embedding_service.embed_batch(texts)

# Get embedding dimension
dimension = embedding_service.get_dimension()  # Returns 768
```

## Embedding Models

### Available Gemini Models

- **`models/text-embedding-004`** (Recommended)
  - Latest embedding model
  - 768 dimensions
  - Best quality

### Task Types

Gemini supports different task types for embeddings:

- `retrieval_document`: For embedding documents (used by default)
- `retrieval_query`: For embedding search queries
- `semantic_similarity`: For general similarity tasks

## Performance Considerations

### Batch Processing

- **Recommended batch size**: 100 texts
- Gemini processes batches efficiently
- The embedding service automatically handles batching

### Embedding Dimensions

| Model | Dimensions | Use Case |
|-------|-----------|----------|
| MiniLM-L6-v2 | 384 | Fast, local processing |
| Gemini text-embedding-004 | 768 | High quality, API-based |
| OpenAI text-embedding-3-small | 1536 | Highest quality |
| OpenAI text-embedding-3-large | 3072 | Maximum quality |

## Troubleshooting

### API Key Not Found

**Error**: `GEMINI_API_KEY not found`

**Solution**:
1. Check your `.env` file exists
2. Verify `GEMINI_API_KEY` is set correctly
3. Ensure no extra spaces or quotes around the key

### Import Error

**Error**: `No module named 'google.generativeai'`

**Solution**:
```bash
pip install google-generativeai==0.3.2
```

### Rate Limiting

If you encounter rate limits:
- The embedding service processes in batches of 100
- Add delays between batches if needed
- Consider using smaller batch sizes

## Comparison: Gemini vs OpenAI vs Local

| Feature | Gemini | OpenAI | MiniLM (Local) |
|---------|--------|--------|----------------|
| Quality | High | Highest | Medium |
| Dimensions | 768 | 1536/3072 | 384 |
| Cost | Low | Low | Free |
| Speed | API-dependent | API-dependent | Fast |
| Offline | No | No | Yes |
| Setup | API Key | API Key | None |

## Next Steps

1. **Test Your Setup**:
   ```bash
   python scripts/validate_embeddings.py
   ```

2. **Ingest RFP Knowledge**:
   ```bash
   python scripts/ingest_rfp_knowledge.py --use-gemini
   ```

3. **Start the API Server**:
   ```bash
   python app.py
   ```

## Support

For more information:
- [Gemini API Documentation](https://ai.google.dev/docs)
- [Embedding Strategy Guide](./EMBEDDING_STRATEGY.md)
- [RFP Ingestion Guide](./RFP_INGESTION_GUIDE.md)
