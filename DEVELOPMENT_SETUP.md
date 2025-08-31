# Development Setup Guide

## Quick Start - Running the User Interface

This guide documents the exact steps to start both the backend API and frontend user interface for development and testing.

### Prerequisites
- Python 3.10+ installed
- Node.js 18+ installed
- All dependencies installed (`pip install -r requirements.txt` and `npm install` in frontend/)

### Starting the Backend API Server

From the project root directory:

```bash
cd "C:\Users\nlaha\OneDrive\Documents\Personal\Real Estate\pro-forma-analytics-tool"

# Set Python path and start the backend API
set PYTHONPATH=. && uvicorn src.presentation.api.main:app --reload --host 127.0.0.1 --port 8000
```

**Important Notes:**
- Must be run from the project root directory
- The `PYTHONPATH=.` is crucial for proper module imports
- Backend will be available at: http://127.0.0.1:8000
- API documentation at: http://127.0.0.1:8000/docs
- Health check endpoint: http://127.0.0.1:8000/api/v1/health

### Starting the Frontend Development Server

In a separate terminal, from the frontend directory:

```bash
cd "C:\Users\nlaha\OneDrive\Documents\Personal\Real Estate\pro-forma-analytics-tool\frontend"

# Start the Next.js development server
npm run dev
```

**Frontend Access:**
- Local: http://localhost:3000
- Network: http://192.168.1.94:3000 (may vary by network)

### Verification

1. **Backend Health Check:**
   ```bash
   curl http://localhost:8000/api/v1/health
   ```
   Should return JSON with status "healthy"

2. **Frontend Access:**
   Open http://localhost:3000 in your browser

### Troubleshooting

**Backend Import Errors:**
- Ensure you're running from the project root directory
- Verify `PYTHONPATH=.` is set
- Check that `src` directory exists and contains the proper module structure

**Frontend Build Issues:**
- Run `npm install` in the frontend directory
- Check that `package.json` exists in frontend/
- Verify Node.js version is 18+

**Common Runtime Errors:**
- **AccessibilityProvider Error**: Fixed in layout.tsx by wrapping AuthProvider with AccessibilityProvider
- **Maximum Update Depth Error**: Fixed infinite re-render loop in useSkipLinks hook with proper memoization
- **Fast Refresh Warnings**: Expected during development hot reloading
- **TypeScript Errors**: Run `npm run type-check` to see current type issues (non-blocking for development)

### Production Deployment

For production deployment, see the CI/CD configuration in `.github/workflows/ci.yml` for the complete setup process.

## Development Workflow

1. Start backend API server (Terminal 1)
2. Start frontend development server (Terminal 2)  
3. Access the application at http://localhost:3000
4. Backend API available at http://127.0.0.1:8000
5. Make changes and both servers will auto-reload

## Stopping the Servers

- **Frontend**: Ctrl+C in the frontend terminal
- **Backend**: Ctrl+C in the backend terminal

---

*Last updated: 2025-08-13*
*Tested on: Windows 11, Python 3.13, Node.js 18+*