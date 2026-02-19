import aiohttp
import asyncio
import json
import pandas as pd
import ta
from datetime import datetime
import os

class MarketService:
    def __init__(self):
        self.crypto_symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'XRPUSDT']
        self.stock_symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META', 'JPM']
        self.binance_ws_url = "wss://stream.binance.com:9443/ws"
        self.current_prices = {}
        self.price_history = {s: [] for s in self.crypto_symbols + self.stock_symbols}
        self.alpha_vantage_key = os.getenv("ALPHA_VANTAGE_API_KEY", "demo")

    async def fetch_binance_data(self):
        """Continuously fetch crypto data from Binance via WebSockets."""
        streams = "/".join([f"{s.lower()}@ticker" for s in self.crypto_symbols])
        url = f"{self.binance_ws_url}/{streams}"
        
        async with aiohttp.ClientSession() as session:
            async with session.ws_connect(url) as ws:
                async for msg in ws:
                    if msg.type == aiohttp.WSMsgType.TEXT:
                        data = json.loads(msg.data)
                        symbol = data['s']
                        price = float(data['c'])
                        change = float(data['P'])
                        self._update_price(symbol, price, change, 'crypto')

    def _update_price(self, symbol, price, change, asset_type):
        self.current_prices[symbol] = {
            "price": price,
            "changePercent": change,
            "type": asset_type,
            "lastUpdated": datetime.now().isoformat()
        }
        # Maintain short history for signals (last 100 points)
        self.price_history[symbol].append(price)
        if len(self.price_history[symbol]) > 100:
            self.price_history[symbol].pop(0)

class SignalService:
    @staticmethod
    def generate_signals(symbol, prices):
        """Generate trade signals using Technical Analysis (RSI, Moving Averages)."""
        if len(prices) < 20:
            return {"symbol": symbol, "signal": "NEUTRAL", "reason": "Insufficient data"}
        
        df = pd.DataFrame(prices, columns=['close'])
        
        # Calculate RSI
        rsi = ta.momentum.RSIIndicator(df['close'], window=14).rsi().iloc[-1]
        
        # Calculate SMA
        sma_short = df['close'].rolling(window=5).mean().iloc[-1]
        sma_long = df['close'].rolling(window=20).mean().iloc[-1]
        
        signal = "NEUTRAL"
        reason = "Market stable"
        
        if rsi < 30:
            signal = "BUY"
            reason = f"Oversold (RSI: {rsi:.2f})"
        elif rsi > 70:
            signal = "SELL"
            reason = f"Overbought (RSI: {rsi:.2f})"
        elif sma_short > sma_long:
            signal = "BUY"
            reason = "Bullish SMA Crossover"
        elif sma_short < sma_long:
            signal = "SELL"
            reason = "Bearish SMA Crossover"
            
        return {
            "symbol": symbol,
            "signal": signal,
            "reason": reason,
            "rsi": rsi,
            "timestamp": datetime.now().isoformat()
        }

class AIService:
    @staticmethod
    async def get_market_sentiment(symbol, context_data):
        """Mock AI inference for market sentiment."""
        # In a real app, this would call an LLM (OpenAI/Anthropic)
        # For now, we simulate AI insights based on technicals and randomness
        prices = context_data.get('prices', [])
        if not prices:
            return "Stable trend expected."
            
        last_price = prices[-1]
        trend = "upward" if prices[-1] > prices[0] else "downward"
        
        insights = [
            f"AI Analysis for {symbol}: The current price of ${last_price:.2f} shows a persistent {trend} trend.",
            f"Machine Learning models predict high volatility for {symbol} in the next session.",
            f"Sentiment analysis from recent news for {symbol} is predominantly bullish."
        ]
        import random
        return random.choice(insights)
