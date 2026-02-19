# TradeMind-AI 🚀
TradeMind AI is a powerful, intelligent trading assistant platform with a futuristic, AI-themed user interface. It provides real-time market data, portfolio tracking, and AI-driven insights to help traders make informed decisions.

## ✨ Key Features
- **Real-Time Market Tracking**: Live crypto prices via Binance WebSockets and stock prices via Alpha Vantage.
- **Interactive Technical Charts**: Historical price data visualization for over 10,000+ symbols.
- **Smart Dashboard**: Real-time portfolio valuation and P&L tracking (simulated).
- **AI Insights**: Automated market trend analysis and risk alerts.
- **AI Assistant**: Conversational interface for trading education and strategy advice.

## 🛠️ Technical Stack
- **Frontend**: HTML5, Vanilla CSS3 (Custom Design System), JavaScript (ES6+).
- **Backend**: Python 3.10+, FastAPI, Uvicorn (Asynchronous Server).
- **Data Processing**: Pandas, Technical Analysis Library (`ta`).
- **Charts**: [Chart.js](https://www.chartjs.org/) for high-performance visualizations.
- **Live Data**: 
  - **Crypto**: Binance WebSockets & Local Backend WebSocket.
  - **Stocks/Indices**: Alpha Vantage REST API.
- **Design**: Futuristic "Glassmorphism" UI with neon accents.

## 🚀 Getting Started

### Backend Setup
1. Navigate to the project root.
2. Install dependencies: `pip install -r backend/requirements.txt`
3. Run the backend server: `python -m uvicorn backend.main:app --reload`
4. The backend will be available at `http://localhost:8000`.

### Frontend Setup
1. Open `index.html` in your browser.
2. Sign up or log in to access the dashboard.
3. **API Setup**: The platform uses Alpha Vantage for stock data. You can update the API key in `market-service.js` or via `localStorage.setItem('alpha_vantage_api_key', 'YOUR_KEY')`.

## 🤖 Architecture
The project follows a modern full-stack architecture:
- **Backend (`/backend`)**:
  - `main.py`: FastAPI application with WebSocket streaming.
  - `services.py`: Logic for market data fetching, technical signals (RSI/SMA), and AI sentiment analysis.
- **Frontend**:
  - `market-service.js`: Unified service that connects to the backend WebSocket with a direct API fallback.
  - `dashboard.html`: Real-time portfolio, P&L tracking, and AI-driven trade signals.
  - `assistant.html`: Interactive AI knowledge base powered by backend intelligence.

---
*Disclaimer: TradeMind AI is for educational and experimental purposes. Always practice risk management when trading live markets.*
