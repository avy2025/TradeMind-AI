import pandas as pd
import os

def load_csv_data(filepath):
    """
    Loads stock data from a CSV file.
    
    Args:
        filepath (str): Path to the CSV file.
        
    Returns:
        pd.DataFrame: A dataframe with Date, Open, High, Low, Close, Volume.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Data file not found at {filepath}. Please provide a valid dataset.")
        
    df = pd.read_csv(filepath)
    
    # Ensure standard column names
    required_cols = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
    
    # Case-insensitive column matching fallback
    col_mapping = {col.lower(): col for col in df.columns}
    rename_dict = {}
    for req_col in required_cols:
        req_lower = req_col.lower()
        if req_lower in col_mapping:
            rename_dict[col_mapping[req_lower]] = req_col
            
    if rename_dict:
        df = df.rename(columns=rename_dict)
        
    for col in required_cols:
        if col not in df.columns:
            # Check if this is a minimal dataset and we need to fill missing columns
            print(f"Warning: {col} column is missing. Some indicators might fail if they require this column.")
            
    if 'Date' in df.columns:
        # Sort chronologically by Date
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.sort_values('Date').reset_index(drop=True)
        
    return df

def generate_sample_data(filepath="data/sample_data.csv", num_days=1000):
    """
    Helper function to generate sample data if none exists.
    """
    import numpy as np
    
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    np.random.seed(42)
    dates = pd.date_range(start='2020-01-01', periods=num_days, freq='B')
    
    # Random walk for prices
    returns = np.random.normal(0.0005, 0.015, num_days)
    close_prices = 100 * np.exp(np.cumsum(returns))
    
    # Generate OHL and Volume based on Close
    high_prices = close_prices * (1 + np.random.uniform(0, 0.02, num_days))
    low_prices = close_prices * (1 - np.random.uniform(0, 0.02, num_days))
    open_prices = low_prices + np.random.uniform(0, 1, num_days) * (high_prices - low_prices)
    volumes = np.random.randint(100000, 1000000, num_days)
    
    df = pd.DataFrame({
        'Date': dates,
        'Open': open_prices,
        'High': high_prices,
        'Low': low_prices,
        'Close': close_prices,
        'Volume': volumes
    })
    
    df.to_csv(filepath, index=False)
    print(f"Generated sample data at {filepath}")
    return df
