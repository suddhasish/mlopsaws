"""
SageMaker Pipeline Step - Track Experiment
This script is executed as a processing step to log experiment data to SageMaker Experiments
"""

import argparse
import json
import os
import sys
import logging
import time
import boto3
from datetime import datetime

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# Inline ExperimentTracker to avoid import issues in SageMaker
class ExperimentTracker:
    """Track ML experiments with metrics and parameters"""

    def __init__(self, experiment_name, run_name=None, region="us-east-1"):
        self.experiment_name = experiment_name
        self.run_name = run_name or f"run-{int(time.time())}"
        self.region = region
        self.sm_client = boto3.client("sagemaker", region_name=region)
        self._create_experiment()

    def _create_experiment(self):
        """Create SageMaker experiment"""
        try:
            self.sm_client.create_experiment(
                ExperimentName=self.experiment_name,
                Description=f"Diabetes classification model experiments - {datetime.now().strftime('%Y-%m-%d')}",
            )
            logger.info(f"✅ Created experiment: {self.experiment_name}")
        except self.sm_client.exceptions.ResourceInUse:
            logger.info(f"📊 Using existing experiment: {self.experiment_name}")
        except Exception as e:
            logger.error(f"Failed to create experiment: {e}")

    def start_run(self, run_name=None):
        """Start a new experiment run"""
        if run_name:
            self.run_name = run_name
        try:
            self.sm_client.create_trial(
                ExperimentName=self.experiment_name, TrialName=self.run_name
            )
            logger.info(f"✅ Started run: {self.run_name}")
        except self.sm_client.exceptions.ResourceInUse:
            logger.info(f"📊 Using existing run: {self.run_name}")
        except Exception as e:
            logger.error(f"Failed to start run: {e}")

    def log_parameters(self, parameters):
        """Log hyperparameters for the run"""
        try:
            for key, value in parameters.items():
                self.sm_client.create_trial_component(
                    TrialComponentName=f"{self.run_name}-{key}-{int(time.time())}",
                    DisplayName=key,
                    Parameters={
                        key: {
                            "NumberValue": (
                                float(value) if isinstance(value, (int, float)) else 0
                            )
                        }
                    },
                )
            logger.info(f"✅ Logged {len(parameters)} parameters")
        except Exception as e:
            logger.error(f"Failed to log parameters: {e}")

    def log_metrics(self, metrics):
        """Log performance metrics"""
        try:
            trial_component_name = f"{self.run_name}-metrics-{int(time.time())}"
            metric_data = {}
            for key, value in metrics.items():
                if isinstance(value, (int, float)):
                    metric_data[key] = {"NumberValue": float(value)}
                else:
                    metric_data[key] = {"StringValue": str(value)}
            self.sm_client.create_trial_component(
                TrialComponentName=trial_component_name,
                DisplayName="Metrics",
                Metrics=metric_data,
            )
            logger.info(f"✅ Logged metrics: {', '.join(metrics.keys())}")
        except Exception as e:
            logger.error(f"Failed to log metrics: {e}")

    def log_artifact(self, artifact_uri, artifact_type="model"):
        """Log model artifacts or other files"""
        try:
            self.sm_client.create_trial_component(
                TrialComponentName=f"{self.run_name}-artifact-{int(time.time())}",
                DisplayName=f"{artifact_type}_artifact",
                InputArtifacts={
                    artifact_type: {"Value": artifact_uri, "MediaType": "text/plain"}
                },
            )
            logger.info(f"✅ Logged artifact: {artifact_uri}")
        except Exception as e:
            logger.error(f"Failed to log artifact: {e}")

    def print_experiment_summary(self):
        """Print summary of all experiment runs"""
        try:
            response = self.sm_client.list_trials(ExperimentName=self.experiment_name)
            trials = response["TrialSummaries"]
            print("\n" + "=" * 80)
            print(f"EXPERIMENT: {self.experiment_name}")
            print("=" * 80)
            print(f"Total Runs: {len(trials)}")
            print("\nRecent Runs:")
            for trial in trials[:10]:
                print(f"  - {trial['TrialName']}")
                print(f"    Created: {trial['CreationTime']}")
            print("=" * 80 + "\n")
        except Exception as e:
            logger.error(f"Failed to get experiment summary: {e}")


def track_training_experiment(args):
    """
    Track training experiment in SageMaker Experiments

    Args:
        args: Command-line arguments with training metadata
    """
    logger.info("=" * 80)
    logger.info("TRACKING EXPERIMENT TO SAGEMAKER EXPERIMENTS")
    logger.info("=" * 80)

    # Load evaluation results
    logger.info(f"Loading evaluation results from: {args.evaluation_results}")
    with open(args.evaluation_results, "r") as f:
        eval_results = json.load(f)

    logger.info(f"Evaluation results loaded: {eval_results}")

    # Initialize experiment tracker
    logger.info(f"Experiment name: {args.experiment_name}")
    logger.info(f"Training job name: {args.training_job_name}")

    tracker = ExperimentTracker(
        experiment_name=args.experiment_name, run_name=args.training_job_name
    )

    # Start run
    tracker.start_run()

    # Extract and log hyperparameters from training job name or evaluation results
    # Hyperparameters are already logged during training, but we can add metadata here
    if "hyperparameters" in eval_results:
        logger.info("Logging hyperparameters...")
        tracker.log_parameters(eval_results["hyperparameters"])

    # Log evaluation metrics
    if "metrics" in eval_results:
        logger.info("Logging evaluation metrics...")
        metrics = eval_results["metrics"]

        # Log all metrics
        tracker.log_metrics(metrics)

        logger.info(f"Metrics logged:")
        for metric_name, metric_value in metrics.items():
            logger.info(f"  {metric_name}: {metric_value:.4f}")

    # Log model artifact
    logger.info(f"Logging model artifact: {args.model_artifact_uri}")
    tracker.log_artifact(args.model_artifact_uri, "model")

    # Print experiment summary
    tracker.print_experiment_summary()

    # Save tracking confirmation
    output_dir = "/opt/ml/processing/output"
    os.makedirs(output_dir, exist_ok=True)

    tracking_summary = {
        "experiment_name": args.experiment_name,
        "run_name": args.training_job_name,
        "model_artifact": args.model_artifact_uri,
        "metrics": eval_results.get("metrics", {}),
        "timestamp": datetime.now().isoformat(),
        "status": "success",
    }

    with open(os.path.join(output_dir, "experiment_tracking.json"), "w") as f:
        json.dump(tracking_summary, f, indent=2)

    logger.info("=" * 80)
    logger.info("✅ EXPERIMENT TRACKING COMPLETED SUCCESSFULLY")
    logger.info("=" * 80)
    logger.info(f"View in SageMaker Console:")
    logger.info(f"  SageMaker → Experiments → {args.experiment_name}")
    logger.info("=" * 80)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Track experiment in SageMaker Experiments"
    )

    parser.add_argument(
        "--training-job-name",
        type=str,
        required=True,
        help="SageMaker training job name (used as run name)",
    )
    parser.add_argument(
        "--model-artifact-uri",
        type=str,
        required=True,
        help="S3 URI of trained model artifact",
    )
    parser.add_argument(
        "--evaluation-results",
        type=str,
        required=True,
        help="Path to evaluation_results.json file",
    )
    parser.add_argument(
        "--experiment-name",
        type=str,
        default="diabetes-classification-experiments",
        help="SageMaker Experiment name",
    )

    args = parser.parse_args()

    try:
        track_training_experiment(args)
    except Exception as e:
        logger.error(f"❌ Failed to track experiment: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
