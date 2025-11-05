"""
Experiment Tracking for SageMaker
Tracks model experiments, metrics, and parameters using SageMaker Experiments
NO ADDITIONAL COST - Uses S3 storage only
"""

import boto3
import json
import time
from datetime import datetime
from sagemaker.analytics import ExperimentAnalytics
from sagemaker.experiments import Run
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ExperimentTracker:
    """Track ML experiments with metrics and parameters"""

    def __init__(self, experiment_name, run_name=None, region="us-east-1"):
        self.experiment_name = experiment_name
        self.run_name = run_name or f"run-{int(time.time())}"
        self.region = region
        self.sm_client = boto3.client("sagemaker", region_name=region)

        # Create experiment if doesn't exist
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

            # Convert metrics to SageMaker format
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

    def get_best_run(self, metric_name="accuracy", maximize=True):
        """Get best run based on metric"""
        try:
            analytics = ExperimentAnalytics(
                experiment_name=self.experiment_name,
                sagemaker_session=boto3.Session(region_name=self.region),
            )

            df = analytics.dataframe()

            if df.empty:
                logger.warning("No runs found")
                return None

            if metric_name in df.columns:
                if maximize:
                    best_run = df.loc[df[metric_name].idxmax()]
                else:
                    best_run = df.loc[df[metric_name].idxmin()]

                logger.info(f"✅ Best run: {best_run['TrialComponentName']}")
                logger.info(f"   {metric_name}: {best_run[metric_name]}")
                return best_run
            else:
                logger.warning(f"Metric '{metric_name}' not found in runs")
                return None

        except Exception as e:
            logger.error(f"Failed to get best run: {e}")
            return None

    def compare_runs(self, run_names=None):
        """Compare multiple runs"""
        try:
            analytics = ExperimentAnalytics(
                experiment_name=self.experiment_name,
                sagemaker_session=boto3.Session(region_name=self.region),
            )

            df = analytics.dataframe()

            if run_names:
                df = df[df["TrialComponentName"].isin(run_names)]

            print("\n" + "=" * 80)
            print("EXPERIMENT COMPARISON")
            print("=" * 80)
            print(df.to_string())
            print("=" * 80 + "\n")

            return df

        except Exception as e:
            logger.error(f"Failed to compare runs: {e}")
            return None

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

            for trial in trials[:10]:  # Show last 10 runs
                print(f"  - {trial['TrialName']}")
                print(f"    Created: {trial['CreationTime']}")
                if "LastModifiedTime" in trial:
                    print(f"    Modified: {trial['LastModifiedTime']}")

            print("=" * 80 + "\n")

        except Exception as e:
            logger.error(f"Failed to get experiment summary: {e}")


def track_training_run(experiment_name, hyperparameters, metrics, model_artifact_uri):
    """
    Convenience function to track a complete training run

    Args:
        experiment_name: Name of the experiment
        hyperparameters: Dict of hyperparameters
        metrics: Dict of performance metrics
        model_artifact_uri: S3 URI of model artifact
    """
    tracker = ExperimentTracker(experiment_name)

    # Start new run
    run_name = f"run-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    tracker.start_run(run_name)

    # Log everything
    tracker.log_parameters(hyperparameters)
    tracker.log_metrics(metrics)
    tracker.log_artifact(model_artifact_uri, "model")

    logger.info(f"✅ Tracking completed for run: {run_name}")

    return tracker


# Example usage
if __name__ == "__main__":
    # Example: Track a training run
    tracker = ExperimentTracker("diabetes-classification-experiments")

    # Log hyperparameters
    tracker.log_parameters(
        {"max_depth": 5, "eta": 0.2, "subsample": 0.8, "num_round": 100}
    )

    # Log metrics
    tracker.log_metrics(
        {
            "accuracy": 0.85,
            "precision": 0.82,
            "recall": 0.80,
            "f1_score": 0.81,
            "roc_auc": 0.88,
        }
    )

    # Log model artifact
    tracker.log_artifact("s3://bucket/models/model.tar.gz", "model")

    # Get best run
    tracker.get_best_run("accuracy")

    # Print summary
    tracker.print_experiment_summary()
