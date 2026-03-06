import numpy as np

def calculate_sharpe_ratio(returns):
    """
    Computes to annualized Sharpe Ratio.
    Assume 252 trading days in a year.
    If the standard deviation is 0, returns 0.
    """
    returns_array = np.array(returns)
    std_dev = np.std(returns_array)
    
    if std_dev == 0 or np.isnan(std_dev):
        return 0.0
    
    # 252 trading days approximation
    sharpe_ratio = np.sqrt(252) * np.mean(returns_array) / std_dev
    return sharpe_ratio

def calculate_max_drawdown(portfolio_values):
    """
    Computes the maximum drawdown of the portfolio.
    Maximum drawdown is the maximum observed loss from a peak to a trough.
    """
    if len(portfolio_values) == 0:
        return 0.0
        
    values = np.array(portfolio_values)
    # Calculate the running maximum
    running_max = np.maximum.accumulate(values)
    running_max[running_max < 1] = 1 # Avoid division by zero
    
    # Calculate drawdowns
    drawdowns = (values - running_max) / running_max
    
    # Max drawdown is the minimum of drawdowns
    max_dd = np.min(drawdowns)
    return max_dd

def calculate_total_return(initial_value, final_value):
    """
    Computes the total percentage return of the portfolio.
    """
    if initial_value == 0:
        return 0.0
    return ((final_value - initial_value) / initial_value) * 100
