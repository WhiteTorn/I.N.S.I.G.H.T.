from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from insight_bridge import InsightBridge

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

bridge = InsightBridge()

@app.get("/hello")
async def root():
    return {"message": "Hello World"}

@app.get("/api/sources")
async def sources():
    try:
        sources = bridge.get_sources()
        return {"success": True, "data": sources}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/enabled-sources")
async def enabled_sources():
    try:
        enabled = bridge.get_enabled_sources()
        return {"success": True, "data": enabled}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/sources")
async def update_sources(sources_data: dict):
    try:
        result = bridge.update_config(sources_data)
        if result:
            return {"success": True, "message": "Sources updated successfully", "data": result}
        else:
            return {"success": False, "error": "Failed to update sources - validation failed"}
    except Exception as e:
        return {"success": False, "error": str(e)}