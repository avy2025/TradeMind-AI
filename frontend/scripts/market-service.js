/**
 * Market Data Service for TradeMind AI
 * Handles real-time crypto prices via Binance WebSockets
 * and stock data via Alpha Vantage REST API.
 */

class MarketService {
    constructor() {
        this.binanceWsUrl = 'wss://stream.binance.com:9443/ws';
        this.backendWsUrl = 'ws://localhost:8000/ws/market';
        this.alphaVantageUrl = 'https://www.alphavantage.co/query';
        this.apiKey = localStorage.getItem('alpha_vantage_api_key') || 'demo';
        this.subscribers = new Set();
        this.binanceWs = null;
        this.backendWs = null;
        this.currentPrices = {};
        this.priceHistory = {};

        // Symbols we want to track by default
        this.cryptoSymbols = ['btcusdt', 'ethusdt', 'bnbusdt', 'solusdt', 'xrpusdt'];
        this.stockSymbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META', 'JPM'];

        this.initBackend();
    }

    // Initialize Connection to Python Backend
    initBackend() {
        try {
            this.backendWs = new WebSocket(this.backendWsUrl);

            this.backendWs.onopen = () => {
                console.log('Connected to TradeMind Backend');
            };

            this.backendWs.onmessage = (event) => {
                const message = JSON.parse(event.data);
                if (message.type === 'all_prices') {
                    Object.entries(message.data).forEach(([symbol, data]) => {
                        this.updatePrice(symbol, data);
                    });
                }
            };

            this.backendWs.onclose = () => {
                console.log('Backend WebSocket closed. Falling back to direct Binance stream...');
                this.initBinance();
            };

            this.backendWs.onerror = () => {
                console.warn('Backend unavailable. Using direct API fallback.');
                this.initBinance();
            };
        } catch (e) {
            this.initBinance();
        }
    }

    // Initialize Binance WebSocket for crypto updates (Fallback)
    initBinance() {
        if (this.binanceWs) return; // Already running

        const streams = this.cryptoSymbols.map(s => `${s}@ticker`).join('/');
        const url = `${this.binanceWsUrl}/${streams}`;

        this.binanceWs = new WebSocket(url);

        this.binanceWs.onmessage = (event) => {
            const data = JSON.parse(event.data);
            const symbol = data.s; // e.g., BTCUSDT
            const price = parseFloat(data.c); // current price
            const changePercent = parseFloat(data.P); // price change percentage

            this.updatePrice(symbol, {
                price: price,
                changePercent: changePercent,
                type: 'crypto',
                name: symbol.replace('USDT', '')
            });
        };

        this.binanceWs.onclose = () => {
            console.log('Binance WebSocket closed. Reconnecting...');
            setTimeout(() => this.initBinance(), 5000);
        };
    }

    // Fetch Stock Data from Alpha Vantage
    async getStockPrice(symbol) {
        try {
            const response = await fetch(`${this.alphaVantageUrl}?function=GLOBAL_QUOTE&symbol=${symbol}&apikey=${this.apiKey}`);
            const data = await response.json();

            if (data['Global Quote']) {
                const quote = data['Global Quote'];
                const price = parseFloat(quote['05. price']);
                const changePercent = parseFloat(quote['10. change percent'].replace('%', ''));

                this.updatePrice(symbol, {
                    price: price,
                    changePercent: changePercent,
                    type: 'stock',
                    volume: quote['06. volume'],
                    marketCap: 'N/A' // Not available in Global Quote
                });
                return this.currentPrices[symbol];
            }
            return null;
        } catch (error) {
            console.error(`Error fetching stock ${symbol}:`, error);
            return null;
        }
    }

    // Update internal price store and notify subscribers
    updatePrice(symbol, data) {
        // Normalize symbol case
        const normSymbol = symbol.toUpperCase();
        this.currentPrices[normSymbol] = {
            ...this.currentPrices[normSymbol],
            ...data,
            lastUpdated: new Date()
        };

        // Also keep a small history for charts if needed
        if (!this.priceHistory[normSymbol]) this.priceHistory[normSymbol] = [];
        this.priceHistory[normSymbol].push({
            time: new Date(),
            price: data.price
        });
        if (this.priceHistory[normSymbol].length > 100) this.priceHistory[normSymbol].shift();

        this.notifySubscribers(normSymbol, this.currentPrices[normSymbol]);
    }

    // Fetch historical data for charts
    async getHistoricalData(symbol, type = 'stock', interval = '1h') {
        if (type === 'crypto') {
            try {
                const binanceSymbol = symbol.toUpperCase();
                const response = await fetch(`https://api.binance.com/api/v3/klines?symbol=${binanceSymbol}&interval=${interval}&limit=24`);
                const data = await response.json();
                return data.map(d => ({
                    time: new Date(d[0]),
                    price: parseFloat(d[4]) // Close price
                }));
            } catch (error) {
                console.error(`Error fetching crypto history for ${symbol}:`, error);
                return [];
            }
        } else {
            try {
                const func = interval === '1d' ? 'TIME_SERIES_DAILY' : 'TIME_SERIES_INTRADAY';
                const intervalParam = interval === '1d' ? '' : `&interval=${interval === '1h' ? '60min' : '5min'}`;
                const response = await fetch(`${this.alphaVantageUrl}?function=${func}${intervalParam}&symbol=${symbol}&apikey=${this.apiKey}`);
                const data = await response.json();

                const timeSeriesKey = interval === '1d' ? 'Time Series (Daily)' : `Time Series (${interval === '1h' ? '60min' : '5min'})`;
                if (data[timeSeriesKey]) {
                    const series = data[timeSeriesKey];
                    return Object.entries(series).map(([time, values]) => ({
                        time: new Date(time),
                        price: parseFloat(values['4. close'])
                    })).reverse();
                }
                return [];
            } catch (error) {
                console.error(`Error fetching stock history for ${symbol}:`, error);
                return [];
            }
        }
    }

    // New: Fetch Trade Signal from Backend
    async getSignal(symbol) {
        try {
            const response = await fetch(`http://localhost:8000/api/signals/${symbol}`);
            return await response.json();
        } catch (e) {
            return { signal: 'NEUTRAL', reason: 'Backend offline' };
        }
    }

    // New: Fetch AI Insight from Backend
    async getAIInsight(symbol) {
        try {
            const response = await fetch(`http://localhost:8000/api/ai/insight/${symbol}`);
            return await response.json();
        } catch (e) {
            return { insight: 'Market data currently being analyzed by local models...' };
        }
    }

    // Subscriber pattern to update UI components
    subscribe(callback) {
        this.subscribers.add(callback);
        return () => this.subscribers.delete(callback);
    }

    notifySubscribers(symbol, data) {
        this.subscribers.forEach(callback => callback(symbol, data));
    }
}

// Global instance
window.marketService = new MarketService();


// Global instance
window.marketService = new MarketService();
