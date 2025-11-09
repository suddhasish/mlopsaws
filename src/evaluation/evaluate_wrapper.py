#!/usr/bin/env python3
"""
Evaluation Wrapper Script
Installs dependencies and runs evaluation
"""

import subprocess
import sys
import os

# Install required dependencies
print("Installing dependencies...")
subprocess.check_call([
    sys.executable, "-m", "pip", "install", "--quiet",
    "xgboost==1.7.6",
    "scikit-learn>=1.0.0",
    "matplotlib>=3.5.0",
    "seaborn>=0.11.0"
])

print("Dependencies installed successfully")

# Now import and run the actual evaluation script
print("Starting evaluation...")

# Add the code directory to path
sys.path.insert(0, '/opt/ml/processing/input/code')

# Import the main evaluation module
from evaluate import *

if __name__ == "__main__":
    import argparse
    import joblib
    import pandas as pd
    import xgboost as xgb
    import json

    parser = argparse.ArgumentParser()
    parser.add_argument("--model-dir", type=str, default="/opt/ml/processing/model")
    parser.add_argument("--test-data", type=str, default="/opt/ml/processing/test")
    parser.add_argument(
        "--output-dir", type=str, default="/opt/ml/processing/evaluation"
    )
    parser.add_argument("--threshold", type=float, default=0.5)

    args = parser.parse_args()

    logger.info("Loading model...")
    model_path = os.path.join(args.model_dir, "xgboost-model")
    booster = xgb.Booster()
    booster.load_model(model_path)

    logger.info("Loading test data...")
    test_df = pd.read_csv(os.path.join(args.test_data, "test.csv"), header=None)
    y_test = test_df.iloc[:, 0]
    X_test = test_df.iloc[:, 1:]

    logger.info(f"Test data shape: {X_test.shape}")

    # Evaluate model
    evaluator = ModelEvaluator(booster, threshold=args.threshold)
    results = evaluator.evaluate(X_test, y_test, output_dir=args.output_dir)

    # Check approval
    approval = evaluator.check_approval_criteria()

    # Save approval status
    with open(os.path.join(args.output_dir, "approval_status.json"), "w") as f:
        json.dump(approval, f, indent=2)

    logger.info("Evaluation completed successfully")
