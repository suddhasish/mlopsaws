"""
Hyperparameter Configuration and Tuning Setup
"""

import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class HyperparameterConfig:
    """
    Manages hyperparameter configurations for different scenarios
    """

    # Default hyperparameters (optimized from tuning)
    DEFAULT_PARAMS = {
        "max_depth": 5,
        "eta": 0.2,
        "gamma": 4,
        "min_child_weight": 6,
        "subsample": 0.7,
        "colsample_bytree": 0.8,
        "objective": "binary:logistic",
        "eval_metric": "auc",
        "num_round": 100,
        "early_stopping_rounds": 10,  # Stop if no improvement after 10 rounds
        "seed": 42,
    }

    # Aggressive hyperparameters for faster training
    FAST_PARAMS = {
        "max_depth": 3,
        "eta": 0.3,
        "gamma": 0,
        "min_child_weight": 1,
        "subsample": 0.8,
        "colsample_bytree": 0.8,
        "objective": "binary:logistic",
        "eval_metric": "auc",
        "num_round": 50,
        "early_stopping_rounds": 5,
        "seed": 42,
    }

    # Conservative hyperparameters for better generalization
    CONSERVATIVE_PARAMS = {
        "max_depth": 3,
        "eta": 0.1,
        "gamma": 5,
        "min_child_weight": 10,
        "subsample": 0.6,
        "colsample_bytree": 0.6,
        "objective": "binary:logistic",
        "eval_metric": "auc",
        "num_round": 200,
        "early_stopping_rounds": 20,
        "seed": 42,
    }

    @staticmethod
    def get_hyperparameters(config_type="default"):
        """Get hyperparameters based on configuration type"""
        if config_type == "fast":
            return HyperparameterConfig.FAST_PARAMS.copy()
        elif config_type == "conservative":
            return HyperparameterConfig.CONSERVATIVE_PARAMS.copy()
        else:
            return HyperparameterConfig.DEFAULT_PARAMS.copy()

    @staticmethod
    def get_hyperparameter_ranges(phase="exploration"):
        """
        Get hyperparameter ranges for SageMaker Hyperparameter Tuning

        Args:
            phase: "exploration" for wide ranges, "optimization" for narrow ranges

        Best Practice: Start with exploration phase, then narrow based on results
        Priority: Focus on high-impact parameters (max_depth, eta) first
        """
        from sagemaker.tuner import (
            IntegerParameter,
            ContinuousParameter,
            CategoricalParameter,
        )

        if phase == "exploration":
            # Phase 1: Wide ranges for initial discovery
            hyperparameter_ranges = {
                # High-impact parameters (tune these first)
                "max_depth": IntegerParameter(3, 12),
                "eta": ContinuousParameter(0.01, 0.5),
                # Regularization parameters
                "gamma": ContinuousParameter(0, 5),
                "min_child_weight": IntegerParameter(1, 10),
                # Sampling parameters
                "subsample": ContinuousParameter(0.5, 1.0),
                "colsample_bytree": ContinuousParameter(0.5, 1.0),
            }
        else:  # "optimization"
            # Phase 2: Narrow ranges around best values from exploration
            hyperparameter_ranges = {
                "max_depth": IntegerParameter(4, 7),
                "eta": ContinuousParameter(0.1, 0.3),
                "gamma": ContinuousParameter(2, 6),
                "min_child_weight": IntegerParameter(4, 8),
                "subsample": ContinuousParameter(0.6, 0.8),
                "colsample_bytree": ContinuousParameter(0.7, 0.9),
            }

        logger.info(f"Using {phase} phase hyperparameter ranges")
        return hyperparameter_ranges

    @staticmethod
    def get_objective_metric():
        """
        Get objective metric configuration for hyperparameter tuning

        Best Practice: Use AUC for imbalanced classification (diabetes dataset)
        Alternative: Use 'validation:aucpr' for extreme imbalance
        """
        objective_metric = {
            "Name": "validation:auc",
            "Regex": "validation-auc:([0-9\\.]+)",
        }

        return objective_metric

    @staticmethod
    def get_metric_definitions():
        """
        Get all metric definitions for training job monitoring
        Required for SageMaker to parse training logs
        """
        metric_definitions = [
            {"Name": "train:auc", "Regex": "train-auc:([0-9\\.]+)"},
            {"Name": "validation:auc", "Regex": "validation-auc:([0-9\\.]+)"},
            {"Name": "train:error", "Regex": "train-error:([0-9\\.]+)"},
            {"Name": "validation:error", "Regex": "validation-error:([0-9\\.]+)"},
        ]
        return metric_definitions

    @staticmethod
    def validate_hyperparameters(params):
        """Validate hyperparameter values"""
        logger.info("Validating hyperparameters...")

        issues = []

        # Check eta
        if "eta" in params:
            if not 0 < params["eta"] <= 1:
                issues.append("eta should be between 0 and 1")

        # Check max_depth
        if "max_depth" in params:
            if params["max_depth"] < 0:
                issues.append("max_depth should be positive")

        # Check subsample
        if "subsample" in params:
            if not 0 < params["subsample"] <= 1:
                issues.append("subsample should be between 0 and 1")

        # Check colsample_bytree
        if "colsample_bytree" in params:
            if not 0 < params["colsample_bytree"] <= 1:
                issues.append("colsample_bytree should be between 0 and 1")

        if issues:
            for issue in issues:
                logger.warning(f"Hyperparameter validation: {issue}")
            return False, issues

        logger.info("Hyperparameter validation passed")
        return True, []


class HyperparameterTuner:
    """
    Manages hyperparameter tuning jobs with best practices

    Best Practices:
    - Use Bayesian strategy for 10-100 jobs
    - Limit parallel jobs (2-3) to balance cost vs speed
    - Enable early stopping to save 30-50% cost
    - Monitor tuning progress and convergence
    """

    def __init__(
        self,
        estimator,
        hyperparameter_ranges,
        objective_metric,
        metric_definitions=None,
    ):
        self.estimator = estimator
        self.hyperparameter_ranges = hyperparameter_ranges
        self.objective_metric = objective_metric
        self.metric_definitions = (
            metric_definitions or HyperparameterConfig.get_metric_definitions()
        )

    def create_tuner(
        self, max_jobs=10, max_parallel_jobs=2, strategy="Bayesian", early_stopping=True
    ):
        """
        Create SageMaker HyperparameterTuner with best practices

        Args:
            max_jobs: Total tuning budget (10-20 recommended for production)
            max_parallel_jobs: Concurrent jobs (2-3 recommended to control cost)
            strategy: "Bayesian" (smart), "Random" (baseline), or "Grid" (exhaustive)
            early_stopping: Enable to save 30-50% of training time/cost

        Best Practice Cost Examples:
        - Conservative: max_jobs=10, max_parallel_jobs=1
        - Balanced: max_jobs=15, max_parallel_jobs=2
        - Aggressive: max_jobs=30, max_parallel_jobs=5
        """
        try:
            from sagemaker.tuner import HyperparameterTuner

            tuner_config = {
                "estimator": self.estimator,
                "objective_metric_name": self.objective_metric["Name"],
                "hyperparameter_ranges": self.hyperparameter_ranges,
                "metric_definitions": self.metric_definitions,
                "max_jobs": max_jobs,
                "max_parallel_jobs": max_parallel_jobs,
                "strategy": strategy,
                "objective_type": "Maximize",
            }

            # Enable early stopping (best practice for cost savings)
            if early_stopping:
                tuner_config["early_stopping_type"] = "Auto"
                logger.info("Early stopping enabled - will save ~30-50% training cost")

            tuner = HyperparameterTuner(**tuner_config)

            logger.info(f"HyperparameterTuner created:")
            logger.info(f"  - Strategy: {strategy}")
            logger.info(f"  - Max jobs: {max_jobs}")
            logger.info(f"  - Parallel jobs: {max_parallel_jobs}")
            logger.info(f"  - Early stopping: {early_stopping}")
            logger.info(f"  - Objective: {self.objective_metric['Name']} (Maximize)")

            return tuner

        except ImportError:
            logger.error("SageMaker SDK not available")
            raise

    def get_best_hyperparameters(self, tuning_job_name):
        """
        Retrieve best hyperparameters from completed tuning job

        Best Practice: After tuning completes, review these parameters and
        update config.yaml DEFAULT_PARAMS for future runs
        """
        try:
            import boto3

            sagemaker_client = boto3.client("sagemaker")

            response = sagemaker_client.describe_hyper_parameter_tuning_job(
                HyperParameterTuningJobName=tuning_job_name
            )

            best_training_job = response["BestTrainingJob"]["TrainingJobName"]
            best_objective_value = response["BestTrainingJob"][
                "FinalHyperParameterTuningJobObjectiveMetric"
            ]["Value"]

            training_job_response = sagemaker_client.describe_training_job(
                TrainingJobName=best_training_job
            )

            best_params = training_job_response["HyperParameters"]

            logger.info("=" * 80)
            logger.info("TUNING RESULTS - UPDATE YOUR CONFIG WITH THESE VALUES")
            logger.info("=" * 80)
            logger.info(f"Best Training Job: {best_training_job}")
            logger.info(
                f"Best {self.objective_metric['Name']}: {best_objective_value:.4f}"
            )
            logger.info(f"\nBest Hyperparameters:")
            for key, value in best_params.items():
                logger.info(f"  {key}: {value}")
            logger.info("=" * 80)
            logger.info("ACTION REQUIRED: Update config/config.yaml with these values")
            logger.info("=" * 80)

            return best_params, best_objective_value

        except Exception as e:
            logger.error(f"Error retrieving best hyperparameters: {str(e)}")
            raise

    def get_tuning_job_analytics(self, tuning_job_name):
        """
        Get tuning job analytics for analysis and debugging

        Helps identify:
        - Parameter convergence
        - Whether ranges are too wide/narrow
        - Cost vs performance tradeoffs
        """
        try:
            from sagemaker.analytics import HyperparameterTuningJobAnalytics

            analytics = HyperparameterTuningJobAnalytics(
                hyperparameter_tuning_job_name=tuning_job_name
            )

            df = analytics.dataframe()
            logger.info(f"\nTuning Analytics Summary:")
            logger.info(f"  Total jobs: {len(df)}")
            logger.info(f"  Best score: {df['FinalObjectiveValue'].max():.4f}")
            logger.info(f"  Worst score: {df['FinalObjectiveValue'].min():.4f}")
            logger.info(f"  Mean score: {df['FinalObjectiveValue'].mean():.4f}")

            return df

        except ImportError:
            logger.warning("SageMaker Analytics not available")
            return None
        except Exception as e:
            logger.error(f"Error getting tuning analytics: {str(e)}")
            return None


# Example usage
if __name__ == "__main__":
    # Test hyperparameter configuration
    logger.info("Testing hyperparameter configuration...")

    # Get default params
    params = HyperparameterConfig.get_hyperparameters("default")
    logger.info(f"Default params: {params}")

    # Validate params
    valid, issues = HyperparameterConfig.validate_hyperparameters(params)
    logger.info(f"Validation result: {valid}")

    # Get hyperparameter ranges
    ranges = HyperparameterConfig.get_hyperparameter_ranges()
    logger.info(f"Hyperparameter ranges configured: {list(ranges.keys())}")
