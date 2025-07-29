from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from insight_bridge import InsightBridge
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="INSIGHT Intelligence Platform API",
    description="Backend API for the INSIGHT Mark I Foundation Engine",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the bridge to Mark I Foundation Engine
bridge = InsightBridge()

# Request models
class BriefingRequest(BaseModel):
    date: str  # Format: "YYYY-MM-DD"

@app.get("/")
async def root():
    return {
        "message": "INSIGHT Intelligence Platform API", 
        "version": "1.0.0",
        "engine": "Mark I Foundation Engine",
        "status": "operational"
    }

@app.get("/hello")
async def hello():
    return {"message": "Hello World"}

@app.get("/api/sources")
async def sources():
    try:
        logger.info("📋 Fetching sources configuration")
        sources = bridge.get_sources()
        return {"success": True, "data": sources}
    except Exception as e:
        logger.error(f"❌ Failed to get sources: {e}")
        return {"success": False, "error": str(e)}

@app.get("/api/enabled-sources")
async def enabled_sources():
    try:
        logger.info("📋 Fetching enabled sources")
        enabled = bridge.get_enabled_sources()
        return {"success": True, "data": enabled}
    except Exception as e:
        logger.error(f"❌ Failed to get enabled sources: {e}")
        return {"success": False, "error": str(e)}

@app.post("/api/sources")
async def update_config(new_config: dict):
    try:
        logger.info("🔧 Updating sources configuration")
        result = bridge.update_config(new_config)
        if result:
            return {"success": True, "message": "Sources updated successfully", "data": result}
        else:
            return {"success": False, "error": "Failed to update sources - validation failed"}
    except Exception as e:
        logger.error(f"❌ Failed to update config: {e}")
        return {"success": False, "error": str(e)}
    
@app.post("/api/daily")
async def generate_daily_briefing(request: BriefingRequest):
    try:
        date = request.date
        logger.info(f"🚀 Generating daily briefing for date: {date}")
        
        if not date:
            raise HTTPException(status_code=400, detail="Date parameter required")
        
        # Call the Mark I Foundation Engine
        result = await bridge.daily_briefing(date)
        
        if isinstance(result, dict) and "error" in result:
            logger.error(f"❌ Engine error: {result['error']}")
            return {"success": False, "error": result["error"]}
        
        logger.info("✅ Briefing generated successfully")
        return {
            "success": True, 
            "briefing": result.get("briefing", result) if isinstance(result, dict) else result,
            "date": date,
            "posts_processed": result.get("posts_processed", 0) if isinstance(result, dict) else 0,
            "total_posts_fetched": result.get("total_posts_fetched", 0) if isinstance(result, dict) else 0
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to generate briefing: {e}")
        return {"success": False, "error": str(e)}

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    import time
    return {
        "status": "healthy",
        "engine": "Mark I Foundation Engine",
        "timestamp": str(time.time())
    }