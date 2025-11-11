"""
Training Script for SageMaker XGBoost Model
This script trains a diabetes classification model using XGBoost
"""

import argparse
import os
import json
import logging
import pandas as pd
import xgboost as xgb
import joblib
import sys
from datetime import datetime

# Add src directory to Python path for imports
sys.path.append("/opt/ml/code")
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def train(args):
    """
    Train XGBoost model for diabetes classification
    """
    logger.info("Starting model training...")
    logger.info(f"Hyperparameters: {vars(args)}")

    # Load training data
    logger.info("Loading training data...")
    train_df = pd.read_csv(os.path.join(args.train, "train.csv"), header=None)

    # Load validation data
    logger.info("Loading validation data...")
    val_df = pd.read_csv(os.path.join(args.validation, "validation.csv"), header=None)

    # Separate features and labels
    y_train = train_df.iloc[:, 0]
    X_train = train_df.iloc[:, 1:]

    y_val = val_df.iloc[:, 0]
    X_val = val_df.iloc[:, 1:]

    logger.info(f"Training data shape: {X_train.shape}")
    logger.info(f"Validation data shape: {X_val.shape}")
    logger.info(f"Class distribution in training: {y_train.value_counts().to_dict()}")

    # Create DMatrix for XGBoost
    dtrain = xgb.DMatrix(X_train, label=y_train)
    dval = xgb.DMatrix(X_val, label=y_val)

    # Set up parameters
    params = {
        "max_depth": args.max_depth,
        "eta": args.eta,
        "gamma": args.gamma,
        "min_child_weight": args.min_child_weight,
        "subsample": args.subsample,
        "objective": args.objective,
        "eval_metric": args.eval_metric,
        "seed": args.seed,
    }

    logger.info(f"XGBoost parameters: {params}")

    # Set up evaluation list
    evallist = [(dtrain, "train"), (dval, "validation")]

    # Train model
    logger.info("Training XGBoost model...")
    num_round = args.num_round
    early_stopping_rounds = (
        args.early_stopping_rounds if args.early_stopping_rounds > 0 else None
    )

    evals_result = {}
    bst = xgb.train(
        params=params,
        dtrain=dtrain,
        num_boost_round=num_round,
        evals=evallist,
        early_stopping_rounds=early_stopping_rounds,
        evals_result=evals_result,
        verbose_eval=True,
    )

    logger.info("Model training completed")

    # Log training metrics
    logger.info("Training metrics:")
    for metric_name, metric_values in evals_result.items():
        logger.info(f"{metric_name}: {metric_values}")

    # Save model
    model_dir = args.model_dir
    os.makedirs(model_dir, exist_ok=True)

    # IMPORTANT: SageMaker XGBoost built-in container only needs the model file
    # Any other files in model.tar.gz will confuse the serving container
    model_path = os.path.join(model_dir, "xgboost-model")
    bst.save_model(model_path)
    logger.info(f"Model saved to {model_path}")

    # Log feature importance (don't save to model dir - causes serving issues)
    importance = bst.get_score(importance_type="weight")
    importance_sorted = dict(
        sorted(importance.items(), key=lambda x: x[1], reverse=True)
    )
    logger.info(f"Feature importance: {importance_sorted}")

    # Log training metadata (don't save to model dir)
    metadata = {
        "hyperparameters": params,
        "num_boost_rounds": num_round,
        "best_iteration": bst.best_iteration if early_stopping_rounds else num_round,
        "training_samples": len(X_train),
        "validation_samples": len(X_val),
        "features": X_train.shape[1],
    }
    logger.info(f"Training metadata: {metadata}")

    logger.info("Model saved successfully (xgboost-model only)")

    # Track experiment with SageMaker Experiments
    try:
        from src.monitoring.experiment_tracker import ExperimentTracker

        logger.info("Logging experiment to SageMaker Experiments...")

        # Initialize experiment tracker
        experiment_name = os.environ.get(
            "EXPERIMENT_NAME", "diabetes-classification-experiments"
        )
        run_name = f"training-run-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

        # Get training job name if available (when running on SageMaker)
        training_job_name = os.environ.get("TRAINING_JOB_NAME", run_name)

        tracker = ExperimentTracker(
            experiment_name=experiment_name, run_name=training_job_name
        )
        tracker.start_run()

        # Log hyperparameters
        hyperparameters = {
            "max_depth": args.max_depth,
            "eta": args.eta,
            "gamma": args.gamma,
            "min_child_weight": args.min_child_weight,
            "subsample": args.subsample,
            "num_round": num_round,
            "early_stopping_rounds": (
                early_stopping_rounds if early_stopping_rounds else 0
            ),
        }
        tracker.log_parameters(hyperparameters)

        # Log training metrics (final values)
        final_metrics = {}
        for eval_set, metrics in evals_result.items():
            for metric_name, values in metrics.items():
                final_metrics[f"{eval_set}_{metric_name}"] = values[-1] if values else 0

        tracker.log_metrics(final_metrics)

        # Log model artifact (will be available after SageMaker uploads)
        # The actual S3 URI will be set by SageMaker after training completes
        if "SM_MODEL_DIR" in os.environ:
            tracker.log_artifact(os.environ["SM_MODEL_DIR"], "model")

        logger.info(f"✅ Experiment logged successfully: {training_job_name}")

    except ImportError:
        logger.warning("ExperimentTracker not available. Skipping experiment logging.")
    except Exception as e:
        logger.warning(f"Failed to log experiment: {e}. Continuing with training.")

    return bst


def model_fn(model_dir):
    """
    Load model for inference
    This function is called by SageMaker to load the model
    """
    model_file = os.path.join(model_dir, "xgboost-model")
    booster = xgb.Booster()
    booster.load_model(model_file)
    return booster


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    # Hyperparameters
    parser.add_argument("--max-depth", type=int, default=5)
    parser.add_argument("--eta", type=float, default=0.2)
    parser.add_argument("--gamma", type=float, default=4)
    parser.add_argument("--min-child-weight", type=int, default=6)
    parser.add_argument("--subsample", type=float, default=0.7)
    parser.add_argument("--objective", type=str, default="binary:logistic")
    parser.add_argument("--num-round", type=int, default=100)
    parser.add_argument("--eval-metric", type=str, default="auc")
    parser.add_argument("--early-stopping-rounds", type=int, default=10)
    parser.add_argument("--seed", type=int, default=42)

    # SageMaker specific arguments
    parser.add_argument(
        "--model-dir", type=str, default=os.environ.get("SM_MODEL_DIR", "/opt/ml/model")
    )
    parser.add_argument(
        "--train",
        type=str,
        default=os.environ.get("SM_CHANNEL_TRAIN", "/opt/ml/input/data/train"),
    )
    parser.add_argument(
        "--validation",
        type=str,
        default=os.environ.get(
            "SM_CHANNEL_VALIDATION", "/opt/ml/input/data/validation"
        ),
    )
    parser.add_argument(
        "--output-data-dir",
        type=str,
        default=os.environ.get("SM_OUTPUT_DATA_DIR", "/opt/ml/output"),
    )

    args = parser.parse_args()

    # Train model
    train(args)
