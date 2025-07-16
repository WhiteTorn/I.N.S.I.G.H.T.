from fastapi import FastAPI
from insight_bridge import InsightBridge

app = FastAPI()

bridge = InsightBridge()

@app.get("/hello")
async def root():
    return {"message": "Hello World"}

@app.get("/sources")
async def sources():
    return bridge.get_sources()

@app.get("/enabled-sources")
async def enabled_sources():
    return bridge.get_enabled_sources()

@app.post("/update-config/{new_config}")
async def update_config(new_config):
    return bridge.update_config(new_config)