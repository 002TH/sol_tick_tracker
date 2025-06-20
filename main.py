from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from tick_data import start_tick_tracking, get_ohlc_bars
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI()

# Allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    # Start background task for SOL TICK tracking
    import asyncio
    asyncio.create_task(start_tick_tracking())

@app.get("/")
async def index():
    return {"message": "SOL TICK Tracker is live."}

@app.get("/tick-ohlc")
async def get_tick_ohlc():
    return get_ohlc_bars()
    
@app.get("/test")
async def test():
    return {"ok": True}
    
if __name__ == "__main__":
    uvicorn.run("main:app", port=8000, reload=True)
