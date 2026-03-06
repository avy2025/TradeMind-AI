import pandas as pd
import ta

def add_technical_indicators(df):
    """
    Computes and adds RSI, MACD, MA20, MA50, and Bollinger Bands to the dataframe.
    
    Args:
        df (pd.DataFrame): Dataframe containing at least 'Close' column.
        
    Returns:
        pd.DataFrame: Dataframe with added indicator columns.
    """
    df = df.copy()
    
    if 'Close' not in df.columns:
        raise ValueError("DataFrame must contain 'Close' price column.")
        
    # Relative Strength Index (RSI)
    df['RSI'] = ta.momentum.RSIIndicator(close=df['Close'], window=14).rsi()
    
    # Moving Average Convergence Divergence (MACD)
    macd = ta.trend.MACD(close=df['Close'])
    df['MACD'] = macd.macd()
    
    # Moving Average (20 and 50)
    df['MA20'] = ta.trend.SMAIndicator(close=df['Close'], window=20).sma_indicator()
    df['MA50'] = ta.trend.SMAIndicator(close=df['Close'], window=50).sma_indicator()
    
    # Bollinger Bands
    bollinger = ta.volatility.BollingerBands(close=df['Close'], window=20, window_dev=2)
    df['BB_High'] = bollinger.bollinger_hband()
    df['BB_Low'] = bollinger.bollinger_lband()
    
    # Fill NaN values created by window calculations
    df = df.bfill()
    
    return df
