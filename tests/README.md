# RFP Processing System - Test Suite

This directory contains comprehensive tests for the RFP upload and processing workflow.

## Test Structure

```
tests/
├── README.md                      # This file
├── test_rfp_workflow.py          # Unit and integration tests (pytest)
├── integration_test_rfp.py       # End-to-end integration test script
└── __init__.py                   # Package initialization
```

## Running Tests

### Prerequisites

1. **Install dependencies:**
   ```bash
   pip install pytest pytest-asyncio requests
   ```

2. **Start the API server:**
   ```bash
   python main.py
   ```

   The API should be running at `http://localhost:8000`

### Unit Tests (pytest)

Run all unit tests:
```bash
pytest tests/test_rfp_workflow.py -v
```

Run specific test class:
```bash
pytest tests/test_rfp_workflow.py::TestQuestionExtraction -v
```

Run with detailed output:
```bash
pytest tests/test_rfp_workflow.py -v -s
```

### Integration Test

Run the end-to-end integration test:

```bash
# With default sample RFP
python tests/integration_test_rfp.py

# With custom RFP file
python tests/integration_test_rfp.py --rfp-file /path/to/rfp.pdf --client "Acme Corp"

# With different API URL
python tests/integration_test_rfp.py --api-url http://localhost:8080
```

**What it tests:**
1. ✅ API health check
2. ✅ RFP file upload
3. ✅ Workflow creation in database
4. ✅ State transitions (created → analyzing → routing → generating → reviewing → formatting → ready)
5. ✅ Progressive response generation
6. ✅ Question extraction from RFP
7. ✅ Answer generation with confidence scores
8. ✅ Quality review
9. ✅ Document generation
10. ✅ Document download

## Test Coverage

### 1. Question Extraction (`TestQuestionExtraction`)
- Question extraction from RFP text
- Section detection
- Fallback extraction when LLM fails

### 2. Database Operations (`TestWorkflowDatabase`)
- Workflow creation
- State transitions
- Analysis updates
- Progressive response updates
- Workflow retrieval

### 3. RFP Processing (`TestRFPProcessor`)
- End-to-end RFP processing
- All 4 workflow steps
- Document generation
- Error handling

### 4. State Management (`TestStateTransitions`)
- Correct state sequence
- State persistence

### 5. API Integration (`TestAPIIntegration`)
- Workflow retrieval endpoint
- Workflow listing endpoint

## Expected Test Results

### Successful Test Run Output

```
tests/test_rfp_workflow.py::TestQuestionExtraction::test_question_extractor_initialization PASSED
tests/test_rfp_workflow.py::TestQuestionExtraction::test_extract_questions_from_rfp PASSED
✓ Extracted 10 questions
✓ Detected 4 sections

tests/test_rfp_workflow.py::TestWorkflowDatabase::test_create_workflow PASSED
✓ Created workflow: TEST-WF-20241120123456

tests/test_rfp_workflow.py::TestWorkflowDatabase::test_update_workflow_state PASSED
✓ Updated workflow state to: analyzing

tests/test_rfp_workflow.py::TestRFPProcessor::test_end_to_end_rfp_processing PASSED
✓ RFP processing complete!
  - State: ready
  - Questions extracted: 10
  - Responses generated: 10
  - Quality: high
  - Document: /path/to/output.docx

========================== X passed in Y.YYs ==========================
```

### Integration Test Output

```
================================================================================
                    RFP UPLOAD WORKFLOW - INTEGRATION TEST
================================================================================

[Step 0] Pre-flight checks...
✓ API is healthy and running
✓ All pre-flight checks passed

[Step 1] Uploading RFP document...
✓ RFP uploaded successfully!
ℹ Workflow ID: WF-RFP-20241120123456
ℹ Status: processing

[Step 2] Monitoring workflow progress...
ℹ State: analyzing - Extracting questions from RFP...
ℹ State: routing - Routing questions to agents...
ℹ State: generating - Generating answers...
ℹ   Progress: 5/20 answers generated
ℹ State: reviewing - Performing quality review...
ℹ State: formatting - Formatting final document...
✓ State: ready - RFP processing complete! ✓
✓ Workflow completed in 45.3 seconds

State Transition Summary:
  1. created        @    0.0s (duration: 2.1s)
  2. analyzing      @    2.1s (duration: 5.3s)
  3. routing        @    7.4s (duration: 1.2s)
  4. generating     @    8.6s (duration: 28.4s)
  5. reviewing      @   37.0s (duration: 3.1s)
  6. formatting     @   40.1s (duration: 5.2s)
  7. ready          @   45.3s (duration: 0.0s)

[Step 3] Workflow Results Summary...

RFP Analysis:
  Total Questions: 20
  Sections Detected: 6

  Sample Questions:
    1. Please provide a brief history of your company, including years in...
    2. Describe your experience developing enterprise software for Fortune...
    3. What industries have you served in the past 5 years?

Generated Responses:
  Total Responses: 20
  Average Confidence: 87.5%
  Confidence Distribution:
    High (≥80%):   16
    Medium (50-80%): 3
    Low (<50%):    1

Quality Review:
  Overall Quality: HIGH
  Completeness Score: 89.2%
  Issues Found: 1
    - Low confidence answer - may need manual review

Output File:
  Path: /home/user/automated_sales_proposal_system/data/outputs/RFP_Response_TechCorp_20241120.docx
✓ Document generated successfully!

[Step 4] Downloading generated document...
✓ Document downloaded successfully!
ℹ Saved to: ./data/outputs/rfp_response_WF-RFP-20241120123456.docx

================================================================================
                              TEST SUMMARY
================================================================================

✓ All tests passed! ✓
ℹ Total execution time: 47.8 seconds
ℹ Workflow ID: WF-RFP-20241120123456
ℹ Output document: ./data/outputs/rfp_response_WF-RFP-20241120123456.docx

Next steps:
  1. Review the generated document at: ./data/outputs/rfp_response_WF-RFP-20241120123456.docx
  2. Check the workflow in database: SELECT * FROM workflows WHERE workflow_id='WF-RFP-20241120123456'
  3. Test the document editing API: PUT /api/v1/documents/WF-RFP-20241120123456
```

## Manual Testing with curl

### 1. Upload RFP

```bash
curl -X POST "http://localhost:8000/api/v1/rfp/upload" \
  -F "file=@sample_rfp.pdf" \
  -F "client_name=Acme Corp" \
  -F "industry=Technology"
```

### 2. Check Workflow Status

```bash
curl "http://localhost:8000/api/v1/workflows/WF-RFP-20241120123456"
```

### 3. Download Document

```bash
curl "http://localhost:8000/api/v1/download/WF-RFP-20241120123456" \
  --output rfp_response.docx
```

### 4. List All Workflows

```bash
curl "http://localhost:8000/api/v1/workflows?limit=10"
```

## Troubleshooting

### Tests Fail to Connect to API

**Problem:** `Cannot connect to API: Connection refused`

**Solution:**
1. Ensure the API is running: `python main.py`
2. Check the API port: default is `8000`
3. Use `--api-url` flag to specify different URL

### Database Errors

**Problem:** `No such table: workflows`

**Solution:**
1. Delete the database: `rm data/proposals.db`
2. Restart the API server (it will recreate tables)

### LLM Service Errors

**Problem:** `LLM service failed: API key not found`

**Solution:**
1. Set environment variables:
   ```bash
   export ANTHROPIC_API_KEY=your_key_here
   # or
   export OPENAI_API_KEY=your_key_here
   ```
2. Or create `.env` file:
   ```
   ANTHROPIC_API_KEY=your_key_here
   DEFAULT_LLM_PROVIDER=anthropic
   ```

### Slow Test Execution

**Problem:** Integration test takes too long

**Solution:**
- Expected time: 30-60 seconds for a full RFP with 10-20 questions
- If longer, check:
  - LLM API response times
  - Vector store indexing
  - Network connection

## Performance Benchmarks

| Operation | Expected Time | Notes |
|-----------|--------------|-------|
| RFP Upload | < 2s | File parsing and workflow creation |
| Question Extraction | 3-8s | Depends on document size |
| Answer Generation | 1-3s per question | Depends on LLM provider |
| Quality Review | 1-2s | Local processing |
| Document Formatting | 2-5s | DOCX generation |
| **Total (10 questions)** | **30-60s** | End-to-end |
| **Total (20 questions)** | **50-90s** | End-to-end |

## Continuous Integration

To run tests in CI/CD:

```bash
#!/bin/bash
set -e

# Start API in background
python main.py &
API_PID=$!

# Wait for API to start
sleep 5

# Run tests
pytest tests/test_rfp_workflow.py -v
python tests/integration_test_rfp.py

# Cleanup
kill $API_PID
```

## Contributing

When adding new features:

1. Add unit tests to `test_rfp_workflow.py`
2. Update integration test if workflow changes
3. Update this README with new test cases
4. Ensure all tests pass before committing

## Questions?

- Check API docs: http://localhost:8000/docs
- Review code: `api/routes.py`, `services/rfp_processor.py`
- See examples: `tests/integration_test_rfp.py`
