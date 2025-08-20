# 🚀 INSIGHT Intelligence Platform - Deployment Guide

## Overview
Complete deployment guide for the INSIGHT Mark I Foundation Engine with sophisticated frontend integration.

## 📋 Prerequisites

### Backend Requirements
```bash
- Python 3.8+ 
- pip (Python package manager)
- All dependencies from requirements.txt
```

### Frontend Requirements  
```bash
- Node.js 20.19.0+ (or 22.12.0+)
- npm 10.7.0+
- Modern web browser
```

## 🔧 Quick Start (Development Mode)

### 1. Start Backend (Terminal 1)
```bash
# Install Python dependencies (if not done)
pip install -r requirements.txt

# Navigate to backend directory
cd backend

# Start the API server
python start_api.py
```

**Expected Output:**
```
🚀 Starting INSIGHT Intelligence Platform API...
📡 Frontend URL: http://localhost:5173
🔧 Backend URL: http://localhost:8000
📋 API Docs: http://localhost:8000/docs
--------------------------------------------------
INFO: Started server process [12345]
INFO: Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### 2. Start Frontend (Terminal 2)
```bash
# Navigate to frontend directory  
cd frontend

# Install dependencies (if not done)
npm install

# Start development server
npm run dev
```

**Expected Output:**
```
  VITE v7.0.4  ready in 523 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
  ➜  press h + enter to show help
```

### 3. Access Application
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000  
- **API Documentation**: http://localhost:8000/docs

## 🎯 Testing the Integration

### Complete User Flow Test
1. **Open Frontend**: Navigate to http://localhost:5173
2. **Go to Daily Briefing**: Click "Access Daily Briefing" or navigate to `/briefing`
3. **Select Date**: Choose any date in the date picker
4. **Generate Briefing**: Click "Generate Briefing" button
5. **Wait for Processing**: Watch the loading state ("Analyzing intelligence sources...")
6. **View Results**: See the AI-generated briefing from Mark I Foundation Engine

### Expected Behavior
✅ **Success Case:**
- Loading spinner appears
- Backend processes sources using Mark I Foundation Engine
- Real AI-generated briefing displays
- Statistics show actual post counts
- Status changes to "Generated"

❌ **Error Cases:**
- No sources configured → Clear error message
- Invalid date → Validation error  
- Network issues → Connection error
- Engine failures → Descriptive error from Mark I

## 🔍 API Endpoints

### Core Briefing Endpoint
```http
POST /api/daily
Content-Type: application/json

{
  "date": "2025-01-29"
}
```

**Success Response:**
```json
{
  "success": true,
  "briefing": "AI-generated briefing content...",
  "date": "2025-01-29",
  "posts_processed": 15,
  "total_posts_fetched": 47
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "No posts found for date 2025-01-29"
}
```

### Other Endpoints
- `GET /api/sources` - Get source configuration
- `GET /api/enabled-sources` - Get enabled sources  
- `POST /api/sources` - Update source configuration
- `GET /health` - Health check

## 🏗️ Architecture Overview

```
┌─────────────────┐    HTTP/JSON    ┌─────────────────┐
│   Frontend      │◄──────────────►│   Backend       │
│   (React/Vite)  │    Port 5173    │   (FastAPI)     │
│   Tailwind CSS  │    Port 8000    │   Port 8000     │
└─────────────────┘                 └─────────────────┘
                                            │
                                            ▼
                                    ┌─────────────────┐
                                    │  InsightBridge  │
                                    └─────────────────┘
                                            │
                                            ▼
                                    ┌─────────────────┐
                                    │ Mark I Foundation│
                                    │     Engine      │
                                    │                 │
                                    │ • RSS Sources   │
                                    │ • AI Processing │
                                    │ • Date Filtering│
                                    │ • Gemini AI     │
                                    └─────────────────┘
```

## 🛠️ Troubleshooting

### Backend Issues

**"ModuleNotFoundError: No module named 'insight_core'"**
```bash
# Make sure you're in the backend directory
cd backend
python start_api.py
```

**"Failed to setup connector"**
- Check your configuration files
- Ensure sources are properly configured
- Verify API keys (if required)

### Frontend Issues

**"API request failed: 404"**
- Ensure backend is running on http://localhost:8000
- Check CORS configuration in main.py

**"Network error occurred"**  
- Verify backend is accessible
- Check firewall/proxy settings

### Integration Issues

**Loading forever, no results**
- Check backend logs for errors
- Verify Mark I Foundation Engine configuration
- Test backend endpoint directly: http://localhost:8000/docs

**Empty briefing content**
- Check if sources have data for the selected date
- Review engine logs for processing errors

## 📊 Production Deployment

### Backend (Production)
```bash
# Install production dependencies
pip install gunicorn

# Start with Gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Frontend (Production)
```bash
# Build production version
npm run build

# Serve with static server (example with serve)
npm install -g serve
serve -s dist -p 5173
```

### Environment Variables
```bash
# Backend
export ENVIRONMENT=production
export LOG_LEVEL=info

# Frontend  
export VITE_API_URL=http://your-api-domain.com

In Codespaces or when long-running requests exceed dev proxy limits, you can bypass the Vite proxy by pointing the frontend directly at the backend:

```
export VITE_API_URL="https://<your-codespace>-8000.app.github.dev"
```

Restart the Vite dev server after changing this.
```

## ✅ Success Metrics

**Application is working correctly when:**
- ✅ Frontend displays sophisticated design
- ✅ Date picker and controls work
- ✅ "Generate Briefing" calls backend API
- ✅ Real AI briefings display (not mock data)
- ✅ Actual post statistics appear  
- ✅ Error handling works gracefully
- ✅ Loading states provide feedback

## 🎯 Next Steps

Once basic integration is working:
1. **Enhanced Error Handling** - More specific error messages
2. **Real-time Updates** - WebSocket integration for progress
3. **Caching** - Store completed briefings  
4. **Export Features** - PDF/email functionality
5. **Source Management** - Frontend configuration UI

---

**🎉 You now have a complete, working INSIGHT Intelligence Platform with Mark I Foundation Engine integration!** 