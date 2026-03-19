import gymnasium as gym
from gymnasium import spaces
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

class TradingEnv(gym.Env):
    """
    A custom trading environment for Gymnasium.
    """
    metadata = {'render_modes': ['human']}

    def __init__(self, df, initial_balance=10000.0):
        super(TradingEnv, self).__init__()
        
        self.df = df
        self.initial_balance = initial_balance
        
        # Action space: 0 = HOLD, 1 = BUY, 2 = SELL
        self.action_space = spaces.Discrete(3)
        
        # Observation space: 
        # [closing_price, moving_average, RSI, current_cash, current_shares_held]
        # We use float32 to be compatible with Stable-Baselines3 wrappers
        self.observation_space = spaces.Box(
            low=-np.inf, high=np.inf, shape=(5,), dtype=np.float32
        )
        
        self.current_step = 0
        self.balance = self.initial_balance
        self.shares_held = 0
        self.net_worth = self.initial_balance
        self.max_net_worth = self.initial_balance
        
        # History for rendering purposes
        self.net_worth_history = []
        
    def reset(self, seed=None, options=None):
        """
        Resets the environment to its initial state.
        """
        super().reset(seed=seed)
        
        self.current_step = 0
        self.balance = self.initial_balance
        self.shares_held = 0
        self.net_worth = self.initial_balance
        self.max_net_worth = self.initial_balance
        self.net_worth_history = [self.net_worth]
        
        return self._next_observation(), {}

    def _next_observation(self):
        """
        Returns the current state observation.
        """
        # Fetch current step's data row safely
        obs = np.array([
            self.df.loc[self.current_step, 'Close'],
            self.df.loc[self.current_step, 'MA'],
            self.df.loc[self.current_step, 'RSI'],
            self.balance,
            self.shares_held
        ], dtype=np.float32)
        return obs

    def step(self, action):
        """
        Executes one time step within the environment based on the given action.
        """
        current_price = self.df.loc[self.current_step, 'Close']
        
        # Execute action
        if action == 1: # BUY
            # Strategy: Buy as many shares as possible with the current balance
            shares_bought = int(self.balance // current_price)
            if shares_bought > 0:
                self.balance -= shares_bought * current_price
                self.shares_held += shares_bought
                
        elif action == 2: # SELL
            # Strategy: Sell all currently held shares
            if self.shares_held > 0:
                self.balance += self.shares_held * current_price
                self.shares_held = 0
                
        # HOLD (action == 0) does nothing
        
        # Move to the next step
        self.current_step += 1
        
        # Calculate new net worth
        new_net_worth = self.balance + self.shares_held * current_price
        
        # The reward is strictly based on the change in portfolio value
        reward = new_net_worth - self.net_worth
        
        # Update trackers
        self.net_worth = new_net_worth
        self.max_net_worth = max(self.max_net_worth, self.net_worth)
        self.net_worth_history.append(self.net_worth)
        
        # Check if episode is done (reached end of data)
        terminated = self.current_step >= len(self.df) - 1
        # Truncated is typically used for explicit time limits
        truncated = False 
        
        return self._next_observation(), float(reward), terminated, truncated, {}

    def render(self, mode='human'):
        """
        Renders the current state of the environment.
        """
        print(f"Step: {self.current_step}")
        print(f"Balance: ${self.balance:.2f}")
        print(f"Shares held: {self.shares_held}")
        print(f"Net worth: ${self.net_worth:.2f}")
        print("-" * 30)
