import os
from stable_baselines3 import PPO

def create_agent(env, learning_rate=0.0003, verbose=1):
    """
    Initializes a PPO agent for the trading environment.
    
    Args:
        env (gym.Env): The configured trading learning environment vector.
        learning_rate (float): Step rate mapping weight updates.
        verbose (int): Model reporting verbosity.
        
    Returns:
        PPO: Configured model object instance.
    """
    model = PPO("MlpPolicy", env, learning_rate=learning_rate, verbose=verbose)
    return model

def train_agent(agent, timesteps):
    """
    Trains the initialized agent mapped to environmental steps.
    
    Args:
        agent (PPO): Initialized agent model.
        timesteps (int): Expected step iterations.
        
    Returns:
        PPO: Agent containing updated policy weights.
    """
    print(f"Starting agent training for {timesteps} timesteps...")
    agent.learn(total_timesteps=timesteps)
    print("Training sequence completed.")
    return agent

def save_agent(agent, path):
    """
    Serializes logic weights and agent configuration natively into a zip structure.
    """
    # Create directory if it explicitly defines folders
    dir_name = os.path.dirname(path)
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)
        
    agent.save(path)
    print(f"Agent successfully exported to {path}")

def load_agent(path, env=None):
    """
    Reconstructs the agent payload and assigns it to environment inputs upon loading.
    
    Args:
        path (str): Relative path pointing to exported .zip model payload.
        env (gym.Env, optional): Context environment.
    """
    if not path.endswith('.zip') and not os.path.exists(path):
        # Adding expected extension implicitly if missing in raw lookup map
        path += '.zip'
        
    if os.path.exists(path):
        model = PPO.load(path, env=env)
        print(f"Resolved agent payload from {path}")
        return model
    else:
        raise FileNotFoundError(f"Model dependency payload not resolved at {path}")
