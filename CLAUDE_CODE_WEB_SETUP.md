# Claude Code Web - Environment Setup & Execution Guide

## Table of Contents
1. [What is Claude Code Web?](#what-is-claude-code-web)
2. [Environment Overview](#environment-overview)
3. [Setting Up Your Project](#setting-up-your-project)
4. [Executing Code](#executing-code)
5. [Working with Dependencies](#working-with-dependencies)
6. [File Operations](#file-operations)
7. [Environment Variables & Secrets](#environment-variables--secrets)
8. [Best Practices](#best-practices)
9. [Troubleshooting](#troubleshooting)
10. [Project-Specific Setup](#project-specific-setup)

---

## What is Claude Code Web?

**Claude Code** is an AI-powered development assistant that can:
- Read and understand your codebase
- Write and modify code
- Execute commands and scripts
- Run tests and debug issues
- Manage dependencies and configuration
- Interact with APIs and databases

The **web version** provides a sandboxed Linux environment where you can run your code directly in the browser without local setup.

---

## Environment Overview

### System Specifications

```
OS: Linux (Ubuntu-based)
Python: 3.x (available by default)
Node.js: Available
Shell: Bash
Working Directory: /home/user/<project_name>
```

### Pre-installed Tools

Claude Code web comes with many common development tools:
- Python 3 with pip
- Node.js with npm
- Git
- curl, wget
- Common Unix utilities (grep, sed, awk, etc.)

### Storage

- **Persistent**: Files in your project directory persist between sessions
- **Temporary**: System packages may need reinstallation between sessions
- **Outputs**: Generated files (like proposals) are stored in `data/` directory

---

## Setting Up Your Project

### Step 1: Verify Environment

First, check what's available in your environment:

```bash
# Check Python version
python --version

# Check pip
pip --version

# Check current directory
pwd

# List files
ls -la
```

### Step 2: Create Virtual Environment

**CRITICAL for Python projects**: Always use a virtual environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate

# Verify activation (should show venv path)
which python
```

**Why?**: Virtual environments ensure:
- Isolated dependencies
- No conflicts with system packages
- Reproducible builds
- Clean package management

### Step 3: Install Dependencies

```bash
# Make sure venv is activated!
source venv/bin/activate

# Install from requirements.txt
pip install -r requirements.txt

# Verify installation
pip list
```

### Step 4: Configure Environment Variables

```bash
# Create .env file from template
cp .env.example .env

# Edit .env file with your API keys
# You can use Claude Code to edit files directly
```

**For this project**:
```bash
# Required environment variables
OPENAI_API_KEY=sk-...              # or
ANTHROPIC_API_KEY=sk-ant-...       # or
GEMINI_API_KEY=...                 # Choose one

# Optional configurations
DEFAULT_LLM_PROVIDER=openai
DEFAULT_MODEL=gpt-4-turbo-preview
TEMPERATURE=0.7
```

### Step 5: Initialize Data Directories

```bash
# Create necessary directories
mkdir -p data/vector_store
mkdir -p data/uploads
mkdir -p data/outputs

# Verify structure
tree data/  # or ls -R data/
```

---

## Executing Code

### Running Python Scripts

#### Method 1: Direct Execution

```bash
# Make sure venv is activated
source venv/bin/activate

# Run the main application
python main.py
```

#### Method 2: With Module Syntax

```bash
python -m main
```

#### Method 3: Background Process

```bash
# Start server in background
python main.py &

# Get process ID
echo $!

# Check if running
ps aux | grep main.py

# Kill when done
kill <PID>
```

### Running FastAPI Server

```bash
# Option 1: Using main.py
python main.py

# Option 2: Using uvicorn directly
uvicorn main:app --host 0.0.0.0 --port 8000

# Option 3: With auto-reload (development)
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Expected Output**:
```
🚀 Automated Sales Proposal System
Starting server on 0.0.0.0:8000
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Testing Your Code

```bash
# Run test suite
python test_system.py

# Run specific test
python -m pytest test_system.py::test_quick_proposal

# Run with verbose output
python test_system.py -v
```

### Making API Requests

Once server is running, test endpoints:

```bash
# Health check
curl http://localhost:8000/health

# Quick proposal generation
curl -X POST "http://localhost:8000/api/v1/proposals/quick" \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "Test Corp",
    "contact_title": "CEO",
    "industry": "Technology"
  }'

# Search knowledge base
curl "http://localhost:8000/api/v1/knowledge/search?query=talent+sourcing&top_k=5"
```

---

## Working with Dependencies

### Installing Packages

```bash
# Always activate venv first!
source venv/bin/activate

# Install single package
pip install package-name

# Install specific version
pip install package-name==1.2.3

# Install from requirements.txt
pip install -r requirements.txt

# Install with extras
pip install "package-name[extra]"
```

### Managing Requirements

```bash
# View installed packages
pip list

# Export current environment
pip freeze > requirements.txt

# Check for outdated packages
pip list --outdated

# Upgrade package
pip install --upgrade package-name
```

### Common Dependencies for This Project

```bash
# Core framework
pip install fastapi uvicorn pydantic

# LLM providers
pip install openai anthropic google-generativeai

# Vector store
pip install faiss-cpu sentence-transformers

# Document processing
pip install PyPDF2 python-docx openpyxl

# Database
pip install sqlalchemy aiosqlite
```

---

## File Operations

### Reading Files

Claude Code can read files directly, but you can also use shell:

```bash
# View file contents
cat main.py

# View first 20 lines
head -20 config.py

# View last 20 lines
tail -20 test_system.py

# Search in files
grep -r "def process_rfp" agents/

# Find files
find . -name "*.py" -type f
```

### Modifying Files

Claude Code has specialized tools, but you can also:

```bash
# Edit with sed (simple replacements)
sed -i 's/old_text/new_text/g' file.py

# Append to file
echo "NEW_CONFIG=value" >> .env

# Create new file
cat > new_file.txt << EOF
Content here
EOF
```

### File Permissions

```bash
# Make script executable
chmod +x script.sh

# Run executable script
./script.sh
```

---

## Environment Variables & Secrets

### Setting Environment Variables

#### Method 1: .env File (Recommended)

```bash
# Create/edit .env
cat > .env << EOF
OPENAI_API_KEY=sk-...
DEFAULT_LLM_PROVIDER=openai
DEFAULT_MODEL=gpt-4-turbo-preview
TEMPERATURE=0.7
MAX_TOKENS=2000
EOF

# Load .env automatically (if using python-dotenv)
# This is handled by config.py in this project
```

#### Method 2: Export in Shell

```bash
# Set for current session
export OPENAI_API_KEY="sk-..."
export DEFAULT_LLM_PROVIDER="openai"

# Verify
echo $OPENAI_API_KEY
```

#### Method 3: Inline with Command

```bash
# Set for single command
OPENAI_API_KEY=sk-... python main.py
```

### Security Best Practices

**DO**:
- Use `.env` file for secrets
- Add `.env` to `.gitignore`
- Use `.env.example` as template (without real keys)
- Rotate API keys regularly

**DON'T**:
- Commit real API keys to git
- Share `.env` file
- Hardcode secrets in code
- Log sensitive information

---

## Best Practices

### 1. Always Use Virtual Environment

```bash
# Create once
python -m venv venv

# Activate every session
source venv/bin/activate

# Deactivate when done
deactivate
```

### 2. Keep Dependencies Updated

```bash
# Update requirements.txt after changes
pip freeze > requirements.txt

# Document in comments
pip install package-name  # Required for feature X
```

### 3. Check Before Running

```bash
# Verify environment
which python  # Should show venv path
pip list      # Check packages
cat .env      # Verify config (be careful with secrets!)
```

### 4. Handle Errors Gracefully

```bash
# Check exit codes
python main.py
echo $?  # 0 = success, non-zero = error

# Use set -e in scripts (exit on error)
set -e
```

### 5. Clean Up Resources

```bash
# Remove generated files
rm -rf data/outputs/*

# Clean Python cache
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
```

---

## Troubleshooting

### Issue: "Module not found" Error

**Cause**: Virtual environment not activated or package not installed

**Solution**:
```bash
# Activate venv
source venv/bin/activate

# Verify python location
which python  # Should show: .../venv/bin/python

# Install missing package
pip install -r requirements.txt

# Check if package is installed
pip show package-name
```

---

### Issue: "Permission denied" Error

**Cause**: File doesn't have execute permissions

**Solution**:
```bash
# Add execute permission
chmod +x script.py

# Or run with python explicitly
python script.py
```

---

### Issue: "Address already in use"

**Cause**: Port 8000 is occupied by another process

**Solution**:
```bash
# Find process using port 8000
lsof -i :8000
# or
netstat -tulpn | grep 8000

# Kill the process
kill -9 <PID>

# Or use different port
API_PORT=8001 python main.py
```

---

### Issue: "API key not found"

**Cause**: Environment variables not loaded

**Solution**:
```bash
# Check .env file exists
ls -la .env

# Verify contents (be careful!)
cat .env | grep API_KEY

# Check if loaded in Python
python -c "from config import settings; print(settings.openai_api_key)"

# Set manually if needed
export OPENAI_API_KEY="sk-..."
```

---

### Issue: "FAISS index not found"

**Cause**: Vector store not initialized

**Solution**:
```bash
# Initialize by ingesting knowledge base
python scripts/ingest_rfp_knowledge.py \
  --input_dir resources/RFP_Hackathon \
  --metadata '{"source": "hackathon"}'

# Or create empty store
mkdir -p data/vector_store
```

---

### Issue: "Connection refused" when testing API

**Cause**: Server not running

**Solution**:
```bash
# Check if server is running
ps aux | grep "python main.py"
# or
curl http://localhost:8000/health

# Start server if not running
python main.py

# Check logs
tail -f logs/app.log  # if logging to file
```

---

### Issue: "Import error" after adding new code

**Cause**: Python cache or circular imports

**Solution**:
```bash
# Clear Python cache
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete

# Restart Python interpreter
# (or restart server)
```

---

## Project-Specific Setup

### Complete Setup for This Project

Here's the complete sequence to get the Automated Sales Proposal System running:

```bash
# 1. Verify you're in project directory
cd /home/user/automated_sales_proposal_system
pwd

# 2. Create virtual environment
python -m venv venv

# 3. Activate venv
source venv/bin/activate

# 4. Verify activation
which python  # Should show venv path

# 5. Install dependencies
pip install -r requirements.txt

# 6. Configure environment
cp .env.example .env
# Edit .env to add your API key (Claude Code can help with this)

# 7. Create data directories
mkdir -p data/vector_store data/uploads data/outputs

# 8. (Optional) Populate knowledge base
python scripts/ingest_rfp_knowledge.py \
  --input_dir resources/RFP_Hackathon \
  --metadata '{"source": "hackathon", "type": "rfp"}'

# 9. Start the server
python main.py

# 10. In another terminal/session, test it
source venv/bin/activate  # Don't forget!
python test_system.py
```

### Quick Verification Checklist

Before running the application, verify:

```bash
# ✓ Virtual environment activated
which python | grep venv

# ✓ Dependencies installed
pip show fastapi uvicorn openai

# ✓ .env file exists
test -f .env && echo "✓ .env exists" || echo "✗ .env missing"

# ✓ API key configured
grep -q "API_KEY=" .env && echo "✓ API key set" || echo "✗ API key missing"

# ✓ Data directories exist
test -d data/vector_store && echo "✓ Directories exist" || echo "✗ Create directories"

# ✓ Port available
! lsof -i :8000 > /dev/null && echo "✓ Port 8000 free" || echo "✗ Port in use"
```

---

## Running Different Components

### 1. Start API Server

```bash
source venv/bin/activate
python main.py
# Server runs on http://localhost:8000
# Access docs at http://localhost:8000/docs
```

### 2. Run Tests

```bash
source venv/bin/activate
python test_system.py
```

### 3. Ingest Knowledge Base

```bash
source venv/bin/activate
python scripts/ingest_rfp_knowledge.py \
  --input_dir resources/RFP_Hackathon \
  --metadata '{"source": "hackathon"}'
```

### 4. Validate Embeddings

```bash
source venv/bin/activate
python scripts/validate_embeddings.py
```

### 5. Interactive Python Shell

```bash
source venv/bin/activate
python
>>> from config import settings
>>> from services.llm_service import LLMService
>>> llm = LLMService()
>>> # Interact with components
```

---

## Working with Claude Code

### What Claude Code Can Do

1. **Read your entire codebase**
2. **Edit files** - Make precise changes
3. **Run commands** - Execute bash commands
4. **Install packages** - Manage dependencies
5. **Debug issues** - Analyze errors and fix them
6. **Write new code** - Create new features
7. **Run tests** - Execute and debug tests
8. **Manage git** - Commit, push, create PRs

### How to Ask Claude Code for Help

**Good Examples**:
```
"Set up the environment and start the server"
"Install missing dependencies"
"Run the tests and fix any failures"
"Add my OpenAI API key to .env"
"Debug why the API isn't responding"
"Create a new endpoint for user management"
```

**What Claude Code Needs**:
- Clear description of what you want
- API keys (when needed)
- Specific errors (if debugging)
- Context about your project

---

## Advanced Tips

### Working with Long-Running Processes

```bash
# Start server in background
nohup python main.py > server.log 2>&1 &

# Save PID
echo $! > server.pid

# Check logs
tail -f server.log

# Stop server
kill $(cat server.pid)
```

### Debugging Python Code

```bash
# Run with verbose output
python -v main.py

# Run with debugger
python -m pdb main.py

# Enable debug logging
export LOG_LEVEL=DEBUG
python main.py
```

### Performance Monitoring

```bash
# Monitor resource usage
top
# or
htop

# Check disk space
df -h

# Check memory
free -h
```

---

## Session Hooks (Advanced)

Claude Code supports session hooks that run automatically when you start a session. This is useful for:
- Activating virtual environment
- Setting environment variables
- Starting services
- Running checks

**Example**: Create `.claude/SessionStart` to auto-activate venv:
```bash
#!/bin/bash
source venv/bin/activate
echo "Virtual environment activated"
```

---

## Quick Reference Card

```bash
# Essential Commands
source venv/bin/activate          # Activate venv
pip install -r requirements.txt   # Install deps
python main.py                    # Start server
python test_system.py             # Run tests
curl http://localhost:8000/health # Test API

# File Operations
cat file.py                       # View file
ls -la                           # List files
find . -name "*.py"              # Find files
grep -r "search_term" .          # Search in files

# Process Management
ps aux | grep python             # Find processes
kill -9 <PID>                    # Kill process
lsof -i :8000                    # Check port usage

# Environment
export VAR=value                 # Set variable
echo $VAR                        # Print variable
printenv                         # Show all variables
```

---

## Additional Resources

- **FastAPI Docs**: https://fastapi.tiangolo.com
- **Python venv**: https://docs.python.org/3/library/venv.html
- **pip Guide**: https://pip.pypa.io/en/stable/user_guide/

---

**Last Updated**: 2024-11-14
**For**: Automated Sales Proposal System
**Environment**: Claude Code Web

**Need Help?** Ask Claude Code:
- "Help me set up the environment"
- "Debug this error: [paste error]"
- "Run the tests"
