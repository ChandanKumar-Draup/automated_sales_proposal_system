# Web UI Setup and Usage Guide

This guide provides complete instructions for setting up and using the web-based user interface for the Automated Sales Proposal System.

## 📋 Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Detailed Setup](#detailed-setup)
- [Using the UI](#using-the-ui)
- [Features](#features)
- [Troubleshooting](#troubleshooting)
- [API Integration](#api-integration)

---

## 🎯 Overview

The Web UI provides an intuitive interface for:
- Creating quick sales proposals
- Uploading and processing RFP documents
- Managing workflows and tracking proposal generation
- Searching and managing the knowledge base

**Technology Stack:**
- Pure HTML5/CSS3/JavaScript (no frameworks required)
- FastAPI backend with CORS enabled
- RESTful API integration

---

## ✅ Prerequisites

Before you begin, ensure you have:

1. **Python 3.8+** installed
2. **Backend dependencies** installed:
   ```bash
   pip install -r requirements.txt
   ```

3. **API Keys configured** (one of the following):
   - Anthropic API key (Claude)
   - Google API key (Gemini)
   - OpenAI API key

4. **Environment variables** set up in `.env` file

---

## 🚀 Quick Start

### Step 1: Start the Backend Server

```bash
# Navigate to project directory
cd /home/user/automated_sales_proposal_system

# Start the FastAPI server
python main.py
```

You should see output like:
```
================================================================================
🚀 Automated Sales Proposal System
================================================================================
Starting server on 0.0.0.0:8000
LLM Provider: anthropic
Model: claude-3-5-sonnet-20241022
Vector Store: ./data/vector_store
Output Directory: ./outputs
================================================================================

Endpoints:
  - API Docs: http://0.0.0.0:8000/docs
  - Health Check: http://0.0.0.0:8000/health
  - Quick Proposal: POST http://0.0.0.0:8000/api/v1/proposals/quick
  - Upload RFP: POST http://0.0.0.0:8000/api/v1/rfp/upload
================================================================================
```

### Step 2: Open the Web UI

1. **Option A: Open directly in browser**
   ```bash
   # Open the UI file
   open ui/index.html
   # OR on Linux
   xdg-open ui/index.html
   # OR navigate manually to:
   file:///home/user/automated_sales_proposal_system/ui/index.html
   ```

2. **Option B: Serve with Python HTTP server** (Recommended)
   ```bash
   # In a new terminal, navigate to the ui directory
   cd /home/user/automated_sales_proposal_system/ui

   # Start a simple HTTP server
   python -m http.server 3000

   # Open browser to:
   # http://localhost:3000
   ```

3. **Option C: Serve with Node.js http-server**
   ```bash
   # Install http-server globally (one-time)
   npm install -g http-server

   # Navigate to ui directory
   cd /home/user/automated_sales_proposal_system/ui

   # Start server
   http-server -p 3000

   # Open browser to:
   # http://localhost:3000
   ```

### Step 3: Verify Connection

Once the UI loads:
1. Check the header status indicator
2. It should show "System Online" in green
3. If it shows "Offline" or "System Error", verify the backend is running on port 8000

---

## 📖 Detailed Setup

### Backend Configuration

1. **Create/Edit `.env` file:**
   ```bash
   # Create .env file if it doesn't exist
   touch .env
   ```

2. **Add required environment variables:**
   ```env
   # Choose your LLM provider
   DEFAULT_LLM_PROVIDER=anthropic  # Options: anthropic, google, openai

   # Add your API key (use only one)
   ANTHROPIC_API_KEY=your_anthropic_key_here
   # OR
   GOOGLE_API_KEY=your_google_key_here
   # OR
   OPENAI_API_KEY=your_openai_key_here

   # Server configuration
   API_HOST=0.0.0.0
   API_PORT=8000

   # Paths
   VECTOR_STORE_PATH=./data/vector_store
   OUTPUT_DIR=./outputs
   UPLOAD_DIR=./uploads
   ```

3. **Create required directories:**
   ```bash
   mkdir -p data outputs uploads
   ```

4. **Initialize vector store (optional but recommended):**
   ```bash
   # Add sample knowledge to the system
   python scripts/ingest_rfp_knowledge.py
   ```

### Frontend Configuration

The UI is pre-configured to connect to `http://localhost:8000`. If your backend runs on a different host/port:

1. **Edit `ui/app.js`:**
   ```javascript
   // Change this line (at the top of the file)
   const API_BASE_URL = 'http://localhost:8000';

   // To your backend URL, e.g.:
   const API_BASE_URL = 'http://192.168.1.100:8000';
   ```

2. **Ensure CORS is enabled** (already configured in `api/routes.py`):
   ```python
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["*"],  # In production, specify your domain
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

---

## 🎨 Using the UI

### Tab 1: Quick Proposal

Generate fast proposals for sales outreach.

**Steps:**
1. Navigate to "Quick Proposal" tab
2. Fill in the form:
   - **Client Name** (required): Company name
   - **Industry**: e.g., "Healthcare", "Finance"
   - **Requirements** (required): What the client needs
   - **Tone**: Choose presentation style
3. Click "Generate Proposal"
4. Wait for generation (usually 10-30 seconds)
5. Review the proposal preview
6. Download the full proposal if satisfied

**Example Input:**
```
Client Name: TechCorp Solutions
Industry: Technology
Requirements: Need a comprehensive CRM system to manage 500+ sales reps across
              10 countries. Must integrate with existing Salesforce data and
              provide real-time analytics.
Tone: Professional
```

### Tab 2: Upload RFP

Process formal RFP documents.

**Steps:**
1. Navigate to "Upload RFP" tab
2. Fill in the form:
   - **Client Name** (required): Company name
   - **Industry**: Optional industry specification
   - **RFP Document** (required): Upload PDF, DOCX, or TXT
3. Click "Upload & Process RFP"
4. Note the Workflow ID provided
5. Use the Workflow ID to check status later

**Supported File Formats:**
- PDF (.pdf)
- Word Documents (.doc, .docx)
- Text Files (.txt)

### Tab 3: Workflows

Track and manage your proposal workflows.

**Features:**
- **Check Workflow Status**: Enter a Workflow ID to see details
- **Recent Workflows**: View your last 10 workflows
- **Download Proposals**: Get completed proposals

**Workflow States:**
- `created`: Just created, not yet processed
- `processing`: Currently being generated
- `completed`: Successfully generated
- `failed`: Error occurred (see error message)

### Tab 4: Knowledge Base

Manage the system's knowledge repository.

**Add Content:**
1. Enter text (case studies, proposals, product info)
2. Optionally add JSON metadata:
   ```json
   {"category": "case_study", "industry": "healthcare", "year": 2024}
   ```
3. Click "Add to Knowledge Base"

**Search Content:**
1. Enter search query
2. Click "Search"
3. Review results with relevance scores
4. Higher scores = more relevant

---

## 🌟 Features

### Real-Time Health Monitoring
- Status indicator in header
- Automatic health checks every 30 seconds
- Visual feedback (green = online, red = offline)

### Workflow Management
- Track multiple proposals simultaneously
- Store last 10 workflows in session
- Quick access to recent work

### Responsive Design
- Works on desktop, tablet, and mobile
- Professional, modern interface
- Intuitive navigation

### Error Handling
- Clear error messages
- Toast notifications for all actions
- Helpful troubleshooting information

### File Upload
- Drag-and-drop support
- File validation
- Progress indication

---

## 🔧 Troubleshooting

### Issue: UI shows "Offline"

**Solutions:**
1. Verify backend is running:
   ```bash
   # Check if server is running
   curl http://localhost:8000/health
   ```

2. Check backend logs for errors

3. Verify port 8000 is not in use:
   ```bash
   # Check port usage
   lsof -i :8000
   # OR
   netstat -an | grep 8000
   ```

4. Ensure firewall allows connections to port 8000

### Issue: CORS Errors in Browser Console

**Error message:**
```
Access to fetch at 'http://localhost:8000/...' from origin 'file://'
has been blocked by CORS policy
```

**Solution:**
Serve the UI through a web server (see Quick Start Step 2, Option B or C) instead of opening the HTML file directly.

### Issue: File Upload Fails

**Possible causes:**
1. File too large (check backend logs)
2. Unsupported file format
3. Backend can't write to uploads directory

**Solutions:**
1. Check file is PDF, DOC, DOCX, or TXT
2. Ensure uploads directory exists and is writable:
   ```bash
   mkdir -p uploads
   chmod 755 uploads
   ```

### Issue: Proposal Generation Fails

**Solutions:**
1. Verify API keys are set correctly in `.env`
2. Check you have internet connection (for LLM APIs)
3. Review backend logs for specific errors
4. Ensure vector store is initialized:
   ```bash
   python scripts/ingest_rfp_knowledge.py
   ```

### Issue: Can't Download Proposals

**Solutions:**
1. Verify workflow is in "completed" state
2. Check outputs directory exists and is readable
3. Look for the file in the outputs directory:
   ```bash
   ls -la outputs/
   ```

---

## 🔌 API Integration

The UI integrates with these backend endpoints:

### Health Check
```
GET /health
```
Response:
```json
{
  "status": "healthy",
  "timestamp": "2024-03-15T10:30:00",
  "services": {
    "llm": true,
    "vector_store": true,
    "orchestrator": true
  }
}
```

### Create Quick Proposal
```
POST /api/v1/proposals/quick
Content-Type: application/json

{
  "client_name": "TechCorp",
  "industry": "Technology",
  "requirements": "Need a CRM system...",
  "tone": "professional"
}
```

### Upload RFP
```
POST /api/v1/rfp/upload
Content-Type: multipart/form-data

file: [binary]
client_name: "TechCorp"
industry: "Technology" (optional)
```

### Check Workflow Status
```
GET /api/v1/workflows/{workflow_id}
```

### Download Proposal
```
GET /api/v1/download/{workflow_id}
```

### Add Knowledge
```
POST /api/v1/knowledge/add?text=...&metadata=...
```

### Search Knowledge
```
GET /api/v1/knowledge/search?query=...&top_k=5
```

---

## 🎯 Best Practices

1. **Always start the backend first** before opening the UI

2. **Use a web server** to serve the UI (not direct file:// access) to avoid CORS issues

3. **Save workflow IDs** - Keep track of important workflows for later reference

4. **Populate knowledge base** - Add relevant case studies and content for better proposals

5. **Monitor health status** - Green indicator confirms system is ready

6. **Check logs** - Backend logs provide detailed error information

---

## 📞 Support

For issues or questions:

1. **Check FastAPI docs**: `http://localhost:8000/docs` (interactive API documentation)

2. **Review logs**: Backend terminal shows detailed execution logs

3. **Browser console**: Press F12 to see JavaScript errors and network requests

4. **System requirements**: Ensure all prerequisites are met

---

## 🚀 Production Deployment

For production use:

1. **Update CORS settings** in `api/routes.py`:
   ```python
   allow_origins=["https://yourdomain.com"]
   ```

2. **Use production web server**:
   - Nginx or Apache for static UI files
   - Gunicorn or Uvicorn for FastAPI backend

3. **Enable HTTPS** for secure communication

4. **Set up database** for workflow persistence (currently using in-memory storage)

5. **Configure environment variables** properly for production

6. **Implement authentication** if needed

7. **Set up monitoring** and logging

---

## 📝 License

Part of the Automated Sales Proposal System project.

---

**Last Updated**: 2024-03-15
**Version**: 1.0.0
