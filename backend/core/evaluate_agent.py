import yaml
import os
import matplotlib.pyplot as plt
import numpy as np

from backend.data.load_data import load_csv_data
from backend.indicators.indicators import add_technical_indicators
from backend.core.trading_env import TradingEnv
from backend.core.agent import load_agent
from backend.utils.metrics import calculate_sharpe_ratio, calculate_max_drawdown, calculate_total_return

def run_evaluation():
    """
    Evaluates a trained RL agent on unseen test data and plots performance.
    """
    print("=== Starting RL Trading Agent Evaluation Pipeline ===")
    
    config_path = "configs/config.yaml"
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
        
    initial_cash = config.get("initial_cash", 10000)
    transaction_cost = config.get("transaction_cost", 0.001)
    
    data_path = "data/sample_data.csv"
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Test data missing at {data_path}. Please run training first to generate sample data.")
        
    df = load_csv_data(data_path)
    df_with_indicators = add_technical_indicators(df)
    
    # Use the last 20% of data for pure testing/evaluation
    train_size = int(len(df_with_indicators) * 0.8)
    test_df = df_with_indicators.iloc[train_size:].copy().reset_index(drop=True)
    
    print(f"Dataset split: {len(test_df)} rows for evaluation.")
    
    env = TradingEnv(
        df=test_df,
        initial_cash=initial_cash,
        transaction_cost=transaction_cost
    )
    
    model_path = "models/ppo_trading_agent"
    print(f"Loading trained agent from {model_path}...")
    try:
        agent = load_agent(model_path)
    except FileNotFoundError:
        print("Error: Trained model not found. Run training mode before evaluation.")
        return
        
    obs, _ = env.reset()
    done = False
    
    # Trackers for plotting and metrics
    portfolio_values = [initial_cash]
    buy_signals = []
    sell_signals = []
    daily_returns = []
    
    prev_portfolio_value = initial_cash
    
    print("Running evaluation across test dataset...")
    while not done:
        # Evaluate deterministically
        action, _ = agent.predict(obs, deterministic=True)
        action_val = int(action)
        
        # Record structural action indicators mapping timestamps
        if action_val == 1:
            buy_signals.append((env.current_step, test_df.loc[env.current_step, 'Close']))
        elif action_val == 2:
            sell_signals.append((env.current_step, test_df.loc[env.current_step, 'Close']))
            
        obs, reward, terminated, truncated, info = env.step(action_val)
        
        current_value = env.portfolio_value
        portfolio_values.append(current_value)
        
        if prev_portfolio_value > 0:
            daily_returns.append((current_value - prev_portfolio_value) / prev_portfolio_value)
        else:
            daily_returns.append(0.0)
            
        prev_portfolio_value = current_value
        done = terminated or truncated

    # Compute Metrices
    final_value = env.portfolio_value
    total_return = calculate_total_return(initial_cash, final_value)
    sharpe_ratio = calculate_sharpe_ratio(daily_returns)
    max_drawdown = calculate_max_drawdown(portfolio_values)
    
    # Print Metrics Output
    print("\n--- EVALUATION RESULTS ---")
    print(f"Final Portfolio Value: ${final_value:.2f}")
    if total_return >= 0:
        print(f"Total Return: +{total_return:.2f}%")
    else:
        print(f"Total Return: {total_return:.2f}%")
    print(f"Sharpe Ratio: {sharpe_ratio:.2f}")
    print(f"Maximum Drawdown: {max_drawdown*100:.2f}%")
    
    # Generate Plots
    print("\nGenerating performance plots...")
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), sharex=True)
    
    # Plot 1: Price Chart with Buy/Sell Markers
    ax1.plot(test_df.index, test_df['Close'], label='Close Price', color='blue', alpha=0.6)
    
    if buy_signals:
        buy_xs, buy_ys = zip(*buy_signals)
        ax1.scatter(buy_xs, buy_ys, marker='^', color='green', label='Buy Signal', alpha=1, s=100)
    if sell_signals:
        sell_xs, sell_ys = zip(*sell_signals)
        ax1.scatter(sell_xs, sell_ys, marker='v', color='red', label='Sell Signal', alpha=1, s=100)
        
    ax1.set_title('Asset Price and Trading Actions')
    ax1.set_ylabel('Price')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Portfolio Value Curve
    ax2.plot(test_df.index, portfolio_values, label='Portfolio Value', color='purple')
    ax2.axhline(initial_cash, color='black', linestyle='--', label='Initial Cash')
    ax2.set_title('Portfolio Value vs Time')
    ax2.set_xlabel('Trading Steps')
    ax2.set_ylabel('Value ($)')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plots_path = "evaluation_plots.png"
    plt.savefig(plots_path)
    print(f"Plots saved beautifully to {plots_path}")
    print("=== Evaluation Pipeline Completed ===")

if __name__ == "__main__":
    run_evaluation()
