// Configuration
const API_BASE_URL = 'http://localhost:8000';
let recentWorkflows = [];

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    initializeTabs();
    initializeForms();
    checkHealth();
    initializeFileUpload();

    // Check health every 30 seconds
    setInterval(checkHealth, 30000);
});

// Tab Management
function initializeTabs() {
    const tabs = document.querySelectorAll('.tab');
    const tabContents = document.querySelectorAll('.tab-content');

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const tabName = tab.dataset.tab;

            // Remove active class from all tabs and contents
            tabs.forEach(t => t.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));

            // Add active class to clicked tab and corresponding content
            tab.classList.add('active');
            document.getElementById(`${tabName}-tab`).classList.add('active');
        });
    });
}

// Health Check
async function checkHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        const data = await response.json();

        const healthStatus = document.getElementById('healthStatus');
        if (data.status === 'healthy') {
            healthStatus.classList.add('healthy');
            healthStatus.classList.remove('error');
            healthStatus.querySelector('.status-text').textContent = 'System Online';
        } else {
            healthStatus.classList.add('error');
            healthStatus.classList.remove('healthy');
            healthStatus.querySelector('.status-text').textContent = 'System Error';
        }
    } catch (error) {
        const healthStatus = document.getElementById('healthStatus');
        healthStatus.classList.add('error');
        healthStatus.classList.remove('healthy');
        healthStatus.querySelector('.status-text').textContent = 'Offline';
    }
}

// Initialize Forms
function initializeForms() {
    // Quick Proposal Form
    document.getElementById('quickProposalForm').addEventListener('submit', handleQuickProposal);

    // RFP Upload Form
    document.getElementById('rfpUploadForm').addEventListener('submit', handleRfpUpload);

    // Workflow Check
    document.getElementById('checkWorkflowBtn').addEventListener('click', checkWorkflowStatus);

    // Add Knowledge Form
    document.getElementById('addKnowledgeForm').addEventListener('submit', handleAddKnowledge);

    // Search Knowledge
    document.getElementById('searchKnowledgeBtn').addEventListener('click', handleSearchKnowledge);

    // Enter key for search
    document.getElementById('searchQuery').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            handleSearchKnowledge();
        }
    });

    // Enter key for workflow check
    document.getElementById('workflowId').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            checkWorkflowStatus();
        }
    });
}

// File Upload Handling
function initializeFileUpload() {
    const fileInput = document.getElementById('rfpFile');
    const fileLabel = document.querySelector('.file-input-label');
    const fileName = document.getElementById('fileName');

    fileInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
            fileName.textContent = `Selected: ${file.name}`;
            fileName.classList.add('show');
        } else {
            fileName.textContent = '';
            fileName.classList.remove('show');
        }
    });

    // Drag and drop
    fileLabel.addEventListener('dragover', (e) => {
        e.preventDefault();
        fileLabel.style.borderColor = 'var(--primary-color)';
    });

    fileLabel.addEventListener('dragleave', () => {
        fileLabel.style.borderColor = 'var(--border-color)';
    });

    fileLabel.addEventListener('drop', (e) => {
        e.preventDefault();
        fileLabel.style.borderColor = 'var(--border-color)';

        const file = e.dataTransfer.files[0];
        if (file) {
            fileInput.files = e.dataTransfer.files;
            fileName.textContent = `Selected: ${file.name}`;
            fileName.classList.add('show');
        }
    });
}

// Quick Proposal Handler
async function handleQuickProposal(e) {
    e.preventDefault();

    const submitBtn = document.getElementById('submitQuickProposal');
    const btnText = submitBtn.querySelector('.btn-text');
    const btnLoader = submitBtn.querySelector('.btn-loader');
    const resultBox = document.getElementById('quickProposalResult');

    // Disable button and show loader
    submitBtn.disabled = true;
    btnText.textContent = 'Generating...';
    btnLoader.style.display = 'inline-block';
    resultBox.style.display = 'none';

    try {
        const formData = {
            client_name: document.getElementById('clientName').value,
            industry: document.getElementById('industry').value || undefined,
            requirements: document.getElementById('requirements').value,
            tone: document.getElementById('tone').value,
        };

        const response = await fetch(`${API_BASE_URL}/api/v1/proposals/quick`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData),
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        // Add to recent workflows
        addToRecentWorkflows(data);

        // Display result
        displayProposalResult(data, resultBox);
        showToast('Proposal generated successfully!', 'success');

        // Reset form
        e.target.reset();

    } catch (error) {
        console.error('Error:', error);
        showToast(`Error: ${error.message}`, 'error');
        displayError(resultBox, error.message);
    } finally {
        submitBtn.disabled = false;
        btnText.textContent = 'Generate Proposal';
        btnLoader.style.display = 'none';
    }
}

// RFP Upload Handler
async function handleRfpUpload(e) {
    e.preventDefault();

    const submitBtn = document.getElementById('submitRfpUpload');
    const btnText = submitBtn.querySelector('.btn-text');
    const btnLoader = submitBtn.querySelector('.btn-loader');
    const resultBox = document.getElementById('rfpUploadResult');

    // Disable button and show loader
    submitBtn.disabled = true;
    btnText.textContent = 'Uploading...';
    btnLoader.style.display = 'inline-block';
    resultBox.style.display = 'none';

    try {
        const formData = new FormData();
        formData.append('file', document.getElementById('rfpFile').files[0]);
        formData.append('client_name', document.getElementById('rfpClientName').value);
        const industry = document.getElementById('rfpIndustry').value;
        if (industry) {
            formData.append('industry', industry);
        }

        const response = await fetch(`${API_BASE_URL}/api/v1/rfp/upload`, {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        // Display result
        displayRfpUploadResult(data, resultBox);
        showToast('RFP uploaded successfully! Processing...', 'success');

        // Reset form
        e.target.reset();
        document.getElementById('fileName').classList.remove('show');

        // If we have a workflow, add it to recent
        if (data.workflow) {
            addToRecentWorkflows(data.workflow);
        }

    } catch (error) {
        console.error('Error:', error);
        showToast(`Error: ${error.message}`, 'error');
        displayError(resultBox, error.message);
    } finally {
        submitBtn.disabled = false;
        btnText.textContent = 'Upload & Process RFP';
        btnLoader.style.display = 'none';
    }
}

// Workflow Status Check
async function checkWorkflowStatus() {
    const workflowId = document.getElementById('workflowId').value.trim();
    const resultBox = document.getElementById('workflowResult');

    if (!workflowId) {
        showToast('Please enter a workflow ID', 'warning');
        return;
    }

    const btn = document.getElementById('checkWorkflowBtn');
    btn.disabled = true;
    btn.textContent = 'Checking...';

    try {
        const response = await fetch(`${API_BASE_URL}/api/v1/workflows/${workflowId}`);

        if (!response.ok) {
            if (response.status === 404) {
                throw new Error('Workflow not found');
            }
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        displayWorkflowDetails(data, resultBox);
        showToast('Workflow status retrieved', 'success');

    } catch (error) {
        console.error('Error:', error);
        showToast(`Error: ${error.message}`, 'error');
        displayError(resultBox, error.message);
    } finally {
        btn.disabled = false;
        btn.textContent = 'Check Status';
    }
}

// Add Knowledge Handler
async function handleAddKnowledge(e) {
    e.preventDefault();

    const submitBtn = document.getElementById('submitKnowledge');
    const btnText = submitBtn.querySelector('.btn-text');
    const btnLoader = submitBtn.querySelector('.btn-loader');
    const resultBox = document.getElementById('addKnowledgeResult');

    submitBtn.disabled = true;
    btnText.textContent = 'Adding...';
    btnLoader.style.display = 'inline-block';

    try {
        const text = document.getElementById('knowledgeText').value;
        const metadataStr = document.getElementById('knowledgeMetadata').value.trim();

        let metadata = null;
        if (metadataStr) {
            try {
                metadata = JSON.parse(metadataStr);
            } catch (e) {
                throw new Error('Invalid JSON in metadata field');
            }
        }

        const params = new URLSearchParams({ text });
        if (metadata) {
            params.append('metadata', JSON.stringify(metadata));
        }

        const response = await fetch(`${API_BASE_URL}/api/v1/knowledge/add?${params}`, {
            method: 'POST',
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        resultBox.style.display = 'block';
        resultBox.className = 'result-box';
        resultBox.querySelector('.result-content').innerHTML = `
            <p style="color: var(--success-color);">✓ ${data.message}</p>
        `;

        showToast('Content added to knowledge base', 'success');
        e.target.reset();

    } catch (error) {
        console.error('Error:', error);
        showToast(`Error: ${error.message}`, 'error');
        displayError(resultBox, error.message);
    } finally {
        submitBtn.disabled = false;
        btnText.textContent = 'Add to Knowledge Base';
        btnLoader.style.display = 'none';
    }
}

// Search Knowledge Handler
async function handleSearchKnowledge() {
    const query = document.getElementById('searchQuery').value.trim();
    const resultsDiv = document.getElementById('searchResults');
    const resultsList = resultsDiv.querySelector('.results-list');

    if (!query) {
        showToast('Please enter a search query', 'warning');
        return;
    }

    const btn = document.getElementById('searchKnowledgeBtn');
    btn.disabled = true;
    btn.textContent = 'Searching...';

    try {
        const response = await fetch(
            `${API_BASE_URL}/api/v1/knowledge/search?query=${encodeURIComponent(query)}&top_k=5`
        );

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        if (data.results.length === 0) {
            resultsList.innerHTML = '<p class="empty-state">No results found</p>';
        } else {
            resultsList.innerHTML = data.results.map((result, index) => `
                <div class="search-result-item">
                    <div class="search-result-header">
                        <strong>Result ${index + 1}</strong>
                        <span class="search-result-score">Score: ${result.score.toFixed(3)}</span>
                    </div>
                    <div class="search-result-text">${escapeHtml(result.text)}</div>
                    ${result.metadata ? `
                        <div class="search-result-metadata">
                            Metadata: ${JSON.stringify(result.metadata)}
                        </div>
                    ` : ''}
                </div>
            `).join('');
        }

        resultsDiv.style.display = 'block';
        showToast(`Found ${data.results.length} results`, 'success');

    } catch (error) {
        console.error('Error:', error);
        showToast(`Error: ${error.message}`, 'error');
        resultsList.innerHTML = `<p class="empty-state" style="color: var(--error-color);">Error: ${error.message}</p>`;
        resultsDiv.style.display = 'block';
    } finally {
        btn.disabled = false;
        btn.textContent = 'Search';
    }
}

// Display Functions
function displayProposalResult(data, resultBox) {
    resultBox.style.display = 'block';
    resultBox.className = 'result-box';

    const content = resultBox.querySelector('.result-content');
    content.innerHTML = `
        <div class="result-item">
            <strong>Workflow ID:</strong>
            <span>${data.workflow_id}</span>
        </div>
        <div class="result-item">
            <strong>Status:</strong>
            <span class="workflow-state ${data.state}">${data.state}</span>
        </div>
        ${data.proposal_content ? `
            <div class="result-item">
                <strong>Proposal Preview:</strong>
                <div style="margin-top: 10px; padding: 15px; background: white; border-radius: 6px; max-height: 300px; overflow-y: auto;">
                    <pre style="white-space: pre-wrap; font-family: inherit;">${escapeHtml(data.proposal_content.substring(0, 500))}${data.proposal_content.length > 500 ? '...' : ''}</pre>
                </div>
            </div>
        ` : ''}
        ${data.output_file_path ? `
            <button class="btn btn-primary download-btn" onclick="downloadProposal('${data.workflow_id}')">
                Download Full Proposal
            </button>
        ` : ''}
    `;
}

function displayRfpUploadResult(data, resultBox) {
    resultBox.style.display = 'block';
    resultBox.className = 'result-box';

    const content = resultBox.querySelector('.result-content');
    content.innerHTML = `
        <div class="result-item">
            <strong>Workflow ID:</strong>
            <span>${data.workflow_id}</span>
        </div>
        <div class="result-item">
            <strong>Status:</strong>
            <span class="workflow-state ${data.status}">${data.status}</span>
        </div>
        <div class="result-item">
            <strong>Message:</strong>
            <span>${data.message}</span>
        </div>
        <button class="btn btn-secondary" onclick="checkSpecificWorkflow('${data.workflow_id}')" style="margin-top: 15px;">
            Check Status
        </button>
    `;
}

function displayWorkflowDetails(data, resultBox) {
    resultBox.style.display = 'block';
    resultBox.className = 'result-box';

    const detailsDiv = resultBox.querySelector('.workflow-details');
    detailsDiv.innerHTML = `
        <div class="workflow-item">
            <span class="label">Workflow ID:</span>
            <span class="value">${data.workflow_id}</span>
        </div>
        <div class="workflow-item">
            <span class="label">Status:</span>
            <span class="workflow-state ${data.state}">${data.state}</span>
        </div>
        <div class="workflow-item">
            <span class="label">Created:</span>
            <span class="value">${new Date(data.created_at).toLocaleString()}</span>
        </div>
        <div class="workflow-item">
            <span class="label">Updated:</span>
            <span class="value">${new Date(data.updated_at).toLocaleString()}</span>
        </div>
        ${data.error_message ? `
            <div class="workflow-item" style="border-left: 3px solid var(--error-color);">
                <span class="label">Error:</span>
                <span class="value" style="color: var(--error-color);">${data.error_message}</span>
            </div>
        ` : ''}
        ${data.output_file_path ? `
            <button class="btn btn-primary download-btn" onclick="downloadProposal('${data.workflow_id}')">
                Download Proposal
            </button>
        ` : ''}
    `;
}

function displayError(resultBox, message) {
    resultBox.style.display = 'block';
    resultBox.className = 'result-box error';

    const content = resultBox.querySelector('.result-content') || resultBox;
    content.innerHTML = `<p style="color: var(--error-color);">Error: ${escapeHtml(message)}</p>`;
}

// Recent Workflows Management
function addToRecentWorkflows(workflow) {
    // Add to beginning of array
    recentWorkflows.unshift(workflow);

    // Keep only last 10
    if (recentWorkflows.length > 10) {
        recentWorkflows = recentWorkflows.slice(0, 10);
    }

    updateRecentWorkflowsUI();
}

function updateRecentWorkflowsUI() {
    const container = document.getElementById('recentWorkflows');

    if (recentWorkflows.length === 0) {
        container.innerHTML = '<p class="empty-state">No workflows yet. Create a proposal to get started!</p>';
        return;
    }

    container.innerHTML = recentWorkflows.map(workflow => `
        <div class="workflow-card" onclick="checkSpecificWorkflow('${workflow.workflow_id}')">
            <div class="workflow-card-header">
                <span class="workflow-id">${workflow.workflow_id}</span>
                <span class="workflow-state ${workflow.state}">${workflow.state}</span>
            </div>
            <div class="workflow-card-info">
                Created: ${new Date(workflow.created_at).toLocaleString()}
            </div>
        </div>
    `).join('');
}

// Utility Functions
function checkSpecificWorkflow(workflowId) {
    document.getElementById('workflowId').value = workflowId;

    // Switch to workflows tab
    const workflowsTab = document.querySelector('.tab[data-tab="workflows"]');
    workflowsTab.click();

    // Check status
    setTimeout(() => {
        checkWorkflowStatus();
    }, 100);
}

async function downloadProposal(workflowId) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/v1/download/${workflowId}`);

        if (!response.ok) {
            throw new Error('Download failed');
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `proposal_${workflowId}.docx`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);

        showToast('Download started', 'success');
    } catch (error) {
        showToast(`Download failed: ${error.message}`, 'error');
    }
}

function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast ${type} show`;

    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
