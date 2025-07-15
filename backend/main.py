from fastapi import FastAPI
from insight_bridge import InsightBridge

app = FastAPI()

@app.get("/hello")
async def root():
    return {"message": "Hello World"}

@app.get("/sources")
async def sources():
    bridge = InsightBridge()
    return bridge.get_sources()

@app.get("/enabled-sources")
async def sources():
    bridge = InsightBridge()
    return bridge.get_enabled_sources()