import yaml
import os
from stable_baselines3.common.vec_env import DummyVecEnv

from data.load_data import load_csv_data, generate_sample_data
from indicators.indicators import add_technical_indicators
from rl_trading.trading_env import TradingEnv
from rl_trading.agent import create_agent, train_agent, save_agent

def run_training():
    """
    Executes the training pipeline for the RL trading agent.
    """
    print("=== Starting RL Trading Agent Training Pipeline ===")
    
    # Load configuration
    config_path = "configs/config.yaml"
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
        
    initial_cash = config.get("initial_cash", 10000)
    transaction_cost = config.get("transaction_cost", 0.001)
    training_timesteps = config.get("training_timesteps", 10000)
    
    # 1. Load stock data from CSV
    data_path = "data/sample_data.csv"
    if not os.path.exists(data_path):
        print(f"Data file not found at {data_path}. Generating sample data...")
        df = generate_sample_data(data_path, num_days=1500)
    else:
        print(f"Loading data from {data_path}...")
        df = load_csv_data(data_path)
        
    # 2. Compute technical indicators
    print("Computing technical indicators (RSI, MACD, MA20, MA50, Bollinger Bands)...")
    df_with_indicators = add_technical_indicators(df)
    
    # Use the first 80% of data for training
    train_size = int(len(df_with_indicators) * 0.8)
    train_df = df_with_indicators.iloc[:train_size].copy()
    
    print(f"Dataset split: {len(train_df)} rows for training.")
    
    # 3. Initialize TradingEnv
    print("Initializing Custom Trading Environment...")
    def make_env():
        return TradingEnv(
            df=train_df, 
            initial_cash=initial_cash, 
            transaction_cost=transaction_cost
        )
        
    # Wrap in DummyVecEnv as required by Stable-Baselines3
    env = DummyVecEnv([make_env])
    
    # 4. Create PPO agent
    print("Creating PPO Agent...")
    agent = create_agent(env, verbose=1)
    
    # 5. Train for at least defined timesteps
    agent = train_agent(agent, timesteps=training_timesteps)
    
    # 6. Save trained model
    model_export_path = "models/ppo_trading_agent"
    save_agent(agent, model_export_path)
    
    print("=== Training Pipeline Completed Successfully ===")

if __name__ == "__main__":
    run_training()
