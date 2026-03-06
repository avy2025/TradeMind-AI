import gymnasium as gym
from gymnasium import spaces
import numpy as np
import pandas as pd

class TradingEnv(gym.Env):
    """
    A reinforcement learning trading environment.
    """
    metadata = {'render_modes': ['human']}

    def __init__(self, df, initial_cash=10000.0, transaction_cost=0.001):
        super(TradingEnv, self).__init__()
        
        self.df = df.reset_index(drop=True)
        self.initial_cash = initial_cash
        self.transaction_cost = transaction_cost
        
        # Action Space: 0 = HOLD, 1 = BUY, 2 = SELL
        self.action_space = spaces.Discrete(3)
        
        # Observation Space features:
        # [Close price, RSI, MACD, MA20, MA50, Current cash balance, Current shares held]
        # Using 7 dimensions
        self.observation_space = spaces.Box(
            low=-np.inf, high=np.inf, shape=(7,), dtype=np.float32
        )
        
        # Portfolio Variables
        self.current_step = 0
        self.cash_balance = self.initial_cash
        self.shares_held = 0
        self.portfolio_value = self.initial_cash
        
        # For rendering/tracking
        self.portfolio_history = [self.portfolio_value]

    def reset(self, seed=None, options=None):
        """
        Resets the environment to initial state.
        """
        super().reset(seed=seed)
        
        self.current_step = 0
        self.cash_balance = self.initial_cash
        self.shares_held = 0
        self.portfolio_value = self.initial_cash
        self.portfolio_history = [self.portfolio_value]
        
        return self._get_observation(), {}

    def _get_observation(self):
        """
        Fetches the current state space metrics from the dataframe.
        """
        obs = np.array([
            self.df.loc[self.current_step, 'Close'],
            self.df.loc[self.current_step, 'RSI'],
            self.df.loc[self.current_step, 'MACD'],
            self.df.loc[self.current_step, 'MA20'],
            self.df.loc[self.current_step, 'MA50'],
            self.cash_balance,
            self.shares_held
        ], dtype=np.float32)
        
        # Handle potential NaNs from indicator initialization windows by zeroing out
        obs = np.nan_to_num(obs)
        return obs

    def step(self, action):
        """
        Executes one timestep passing an action to modifying balance.
        """
        current_price = self.df.loc[self.current_step, 'Close']
        previous_portfolio_value = self.portfolio_value
        
        # Execute Action
        if action == 1: # BUY
            # Strategy assumes buying as many entire shares as afforded
            max_shares = int(self.cash_balance / (current_price * (1 + self.transaction_cost)))
            if max_shares > 0:
                cost = max_shares * current_price * (1 + self.transaction_cost)
                self.cash_balance -= cost
                self.shares_held += max_shares
                
        elif action == 2: # SELL
            # Strategy assumes liquidating all currently held shares
            if self.shares_held > 0:
                revenue = self.shares_held * current_price * (1 - self.transaction_cost)
                self.cash_balance += revenue
                self.shares_held = 0
                
        # HOLD (action == 0) has no effects
        
        # Transition to next timestep
        self.current_step += 1
        
        # Check termination condition (end of dataset)
        terminated = self.current_step >= len(self.df) - 1
        truncated = False
        
        # Update metrics
        # Use next day's price to calculate value if not terminated, otherwise current
        calc_price = self.df.loc[self.current_step, 'Close'] if not terminated else current_price
        
        self.portfolio_value = self.cash_balance + (self.shares_held * calc_price)
        self.portfolio_history.append(self.portfolio_value)
        
        # Reward Function mapping
        reward = self.portfolio_value - previous_portfolio_value
        
        info = {
            'portfolio_value': self.portfolio_value,
            'cash': self.cash_balance,
            'shares': self.shares_held
        }
        
        # Note returned obs will map to the new current_step (next day properties)
        return self._get_observation(), float(reward), terminated, truncated, info

    def render(self, mode='human'):
        """
        Outputs state and portfolio summary to the console.
        """
        print(f"Step: {self.current_step} | Date: {self.df.loc[self.current_step, 'Date']}")
        print(f"Action Window:")
        print(f"Cash: ${self.cash_balance:.2f} | Shares: {self.shares_held}")
        print(f"Portfolio Value: ${self.portfolio_value:.2f}")
        print("-" * 40)
