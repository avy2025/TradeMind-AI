import argparse
import sys

from backend.core.train_agent import run_training
from backend.core.evaluate_agent import run_evaluation

def main():
    """
    Main entrypoint for the TradeMind-AI reinforcement learning trading system.
    """
    parser = argparse.ArgumentParser(description="TradeMind-AI: RL Trading System")
    parser.add_argument(
        "--mode", 
        type=str, 
        choices=["train", "evaluate"],
        required=True,
        help="Execution mode: 'train' to train a new agent, 'evaluate' to test an existing trained agent."
    )
    
    args = parser.parse_args()
    
    if args.mode == "train":
        run_training()
    elif args.mode == "evaluate":
        try:
            run_evaluation()
        except Exception as e:
            print(f"Error during evaluation: {e}")
            sys.exit(1)
    else:
        print(f"Unknown mode specified: {args.mode}")
        sys.exit(1)

if __name__ == "__main__":
    main()
