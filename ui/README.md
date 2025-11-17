# Sales Proposal System - Web UI

A modern, responsive web interface for the Automated Sales Proposal System.

## Quick Start

### 1. Install Dependencies (One-time setup)

```bash
# From project root
pip install -r requirements.txt
```

Note: This may take 5-10 minutes as it installs large ML libraries (PyTorch, etc.).

### 2. Start the Backend

```bash
# From project root
python main.py
```

Server will start on `http://localhost:8000`

### 3. Open the UI

**Option A: Direct File Access**
```bash
# Open in default browser
open ui/index.html  # macOS
xdg-open ui/index.html  # Linux
start ui/index.html  # Windows
```

**Option B: HTTP Server (Recommended - avoids CORS issues)**
```bash
# Navigate to UI directory
cd ui

# Start Python HTTP server
python -m http.server 3000

# Open browser to: http://localhost:3000
```

## Features

- **Quick Proposals**: Generate sales proposals in seconds
- **RFP Processing**: Upload and process RFP documents (PDF, DOCX, TXT)
- **Workflow Management**: Track proposal generation status
- **Knowledge Base**: Add and search company knowledge
- **Real-time Status**: Health monitoring and progress tracking

## Files

- `index.html` - Main UI application
- `styles.css` - Professional styling and responsive design
- `app.js` - API integration and UI logic
- `README.md` - This file

## Full Documentation

See `/docs/UI_SETUP.md` for complete setup instructions, troubleshooting, and usage guide.

## API Configuration

The UI connects to `http://localhost:8000` by default. To change:

1. Edit `app.js`
2. Update `const API_BASE_URL = 'http://localhost:8000';`
3. Set to your backend URL

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Need Help?

1. Check `/docs/UI_SETUP.md` for detailed troubleshooting
2. Verify backend is running at `http://localhost:8000/health`
3. Check browser console (F12) for errors
4. Review backend terminal for error logs

## Technologies

- Pure HTML5/CSS3/JavaScript (no frameworks)
- FastAPI backend with CORS enabled
- RESTful API integration
- Responsive design (mobile-ready)
