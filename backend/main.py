from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
from .services import MarketService, SignalService, AIService

app = FastAPI(title="TradeMind AI Backend")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

market_service = MarketService()

@app.on_event("startup")
async def startup_event():
    # Start Binance WebSocket in background
    asyncio.create_task(market_service.fetch_binance_data())

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/api/signals/{symbol}")
async def get_signals(symbol: str):
    symbol = symbol.upper()
    prices = market_service.price_history.get(symbol, [])
    return SignalService.generate_signals(symbol, prices)

@app.get("/api/ai/insight/{symbol}")
async def get_ai_insight(symbol: str):
    symbol = symbol.upper()
    prices = market_service.price_history.get(symbol, [])
    insight = await AIService.get_market_sentiment(symbol, {"prices": prices})
    return {"symbol": symbol, "insight": insight}

@app.websocket("/ws/market")
async def websocket_market(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # Stream current prices every second
            data = {
                "type": "all_prices",
                "data": market_service.current_prices,
                "timestamp": market_service.current_prices.get('BTCUSDT', {}).get('lastUpdated')
            }
            await websocket.send_json(data)
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        print("Client disconnected from market WebSocket")
