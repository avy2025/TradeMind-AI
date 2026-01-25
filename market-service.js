/**
 * Market Data Service for TradeMind AI
 * Handles real-time crypto prices via Binance WebSockets
 * and stock data via Alpha Vantage REST API.
 */

class MarketService {
    constructor() {
        this.binanceWsUrl = 'wss://stream.binance.com:9443/ws';
        this.alphaVantageUrl = 'https://www.alphavantage.co/query';
        this.apiKey = localStorage.getItem('alpha_vantage_api_key') || 'demo';
        this.subscribers = new Set();
        this.binanceWs = null;
        this.currentPrices = {};
        this.priceHistory = {};

        // Symbols we want to track by default
        this.cryptoSymbols = ['btcusdt', 'ethusdt', 'bnbusdt', 'solusdt', 'xrpusdt'];
        this.stockSymbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META', 'JPM'];

        this.initBinance();
    }

    // Initialize Binance WebSocket for crypto updates
    initBinance() {
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

        this.binanceWs.onerror = (error) => {
            console.error('Binance WebSocket error:', error);
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

    // Proxy for market indices using ETFs
    async getMarketIndices() {
        const indices = {
            'SPY': 'S&P 500',
            'DIA': 'Dow Jones',
            'QQQ': 'NASDAQ',
            'IWM': 'Russell 2000'
        };

        const results = {};
        for (const [symbol, name] of Object.entries(indices)) {
            const data = await this.getStockPrice(symbol);
            if (data) {
                results[name] = data;
            }
        }
        return results;
    }

    // Subscriber pattern to update UI components
    subscribe(callback) {
        this.subscribers.add(callback);
        return () => this.subscribers.delete(callback);
    }

    notifySubscribers(symbol, data) {
        this.subscribers.forEach(callback => callback(symbol, data));
    }

    // Helper to get formatted data for a table
    getMarketOverview() {
        return Object.entries(this.currentPrices).map(([symbol, data]) => ({
            symbol,
            ...data
        }));
    }
}

// Global instance
window.marketService = new MarketService();
