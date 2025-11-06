"""
SageMaker Training Pipeline
End-to-end ML pipeline orchestration for diabetes classification
"""

import os
import json
import boto3
import sagemaker
from sagemaker.workflow.pipeline import Pipeline
from sagemaker.workflow.steps import ProcessingStep, TrainingStep, CreateModelStep
from sagemaker.workflow.step_collections import RegisterModel
from sagemaker.workflow.conditions import ConditionGreaterThanOrEqualTo
from sagemaker.workflow.condition_step import ConditionStep
from sagemaker.workflow.functions import JsonGet, Join
from sagemaker.workflow.parameters import (
    ParameterInteger,
    ParameterFloat,
    ParameterString,
)
from sagemaker.workflow.properties import PropertyFile
from sagemaker.processing import ProcessingInput, ProcessingOutput
from sagemaker.sklearn.processing import SKLearnProcessor
from sagemaker.inputs import TrainingInput
from sagemaker.estimator import Estimator
from sagemaker.model_metrics import MetricsSource, ModelMetrics
from sagemaker.xgboost import XGBoost
import logging
import yaml

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class DiabetesPipeline:
    """
    Diabetes Classification ML Pipeline
    """

    def __init__(self, config_path="config/config.yaml", environment="dev"):
        """
        Initialize pipeline with configuration

        Args:
            config_path: Path to base configuration file
            environment: Target environment (dev, staging, production)
        """
        logger.info(
            f"Initializing Diabetes Classification Pipeline for environment: {environment}"
        )

        # Load base configuration
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)

        # Load environment-specific configuration if exists
        env_config_path = "config/environment_config.yaml"
        if os.path.exists(env_config_path):
            with open(env_config_path, "r") as f:
                env_configs = yaml.safe_load_all(f)
                for env_config in env_configs:
                    if environment in env_config:
                        # Merge environment config with base config
                        self._merge_configs(self.config, env_config[environment])
                        logger.info(
                            f"Loaded environment-specific configuration for {environment}"
                        )
                        break

        self.environment = environment

        # Initialize SageMaker session
        self.region = self.config["aws"]["region"]
        self.role = self.config["sagemaker"]["role"]
        self.sagemaker_session = sagemaker.Session(
            boto_session=boto3.Session(region_name=self.region)
        )
        self.bucket = self.config["s3"]["bucket_name"]
        self.prefix = self.config["s3"]["prefix"]

    def _merge_configs(self, base, override):
        """Recursively merge override config into base config"""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_configs(base[key], value)
            else:
                base[key] = value

    def _format_tags(self, tags_dict):
        """Convert a simple dict of tags into AWS SageMaker tag list format

        Example:
            {"Project": "Diabetes", "Env": "Dev"} ->
            [{"Key": "Project", "Value": "Diabetes"}, {"Key": "Env", "Value": "Dev"}]
        """
        if not tags_dict:
            return []
        return [{"Key": str(k), "Value": str(v)} for k, v in tags_dict.items()]

    def create_pipeline_parameters(self):
        """Define pipeline parameters"""
        logger.info("Creating pipeline parameters...")

        parameters = {
            "processing_instance_type": ParameterString(
                name="ProcessingInstanceType",
                default_value=self.config["sagemaker"]["processing"]["instance_type"],
            ),
            "training_instance_type": ParameterString(
                name="TrainingInstanceType",
                default_value=self.config["sagemaker"]["training"]["instance_type"],
            ),
            "model_approval_status": ParameterString(
                name="ModelApprovalStatus",
                default_value=self.config["sagemaker"]["model_registry"][
                    "approval_status"
                ],
            ),
            "input_data": ParameterString(
                name="InputData",
                default_value=f"s3://{self.bucket}/{self.prefix}/data/raw/diabetes.csv",
            ),
            # Hyperparameters
            "max_depth": ParameterInteger(
                name="MaxDepth",
                default_value=self.config["model"]["hyperparameters"]["max_depth"],
            ),
            "eta": ParameterFloat(
                name="Eta", default_value=self.config["model"]["hyperparameters"]["eta"]
            ),
            "num_round": ParameterInteger(
                name="NumRound",
                default_value=self.config["model"]["hyperparameters"]["num_round"],
            ),
        }

        return parameters

    def create_preprocessing_step(self, parameters):
        """Create data preprocessing step"""
        logger.info("Creating preprocessing step...")

        # SKLearn processor for data preprocessing
        sklearn_processor = SKLearnProcessor(
            framework_version="1.0-1",
            role=self.role,
            instance_type=parameters["processing_instance_type"],
            instance_count=1,
            base_job_name="diabetes-preprocessing",
            sagemaker_session=self.sagemaker_session,
        )

        # Define processing step
        step_process = ProcessingStep(
            name="PreprocessData",
            processor=sklearn_processor,
            inputs=[
                ProcessingInput(
                    source=parameters["input_data"],
                    destination="/opt/ml/processing/input",
                )
            ],
            outputs=[
                ProcessingOutput(
                    output_name="train",
                    source="/opt/ml/processing/output/train",
                    destination=f"s3://{self.bucket}/{self.prefix}/data/train",
                ),
                ProcessingOutput(
                    output_name="validation",
                    source="/opt/ml/processing/output/validation",
                    destination=f"s3://{self.bucket}/{self.prefix}/data/validation",
                ),
                ProcessingOutput(
                    output_name="test",
                    source="/opt/ml/processing/output/test",
                    destination=f"s3://{self.bucket}/{self.prefix}/data/test",
                ),
                ProcessingOutput(
                    output_name="model",
                    source="/opt/ml/processing/output/model",
                    destination=f"s3://{self.bucket}/{self.prefix}/preprocessing/model",
                ),
            ],
            code="src/processing/preprocessing.py",
        )

        return step_process

    def create_training_step(self, parameters, step_process):
        """Create model training step"""
        logger.info("Creating training step...")

        # XGBoost estimator
        xgb_estimator = XGBoost(
            entry_point="src/training/train.py",
            role=self.role,
            instance_type=parameters["training_instance_type"],
            instance_count=1,
            framework_version="1.5-1",
            base_job_name="diabetes-training",
            sagemaker_session=self.sagemaker_session,
            hyperparameters={
                "max_depth": parameters["max_depth"],
                "eta": parameters["eta"],
                "num_round": parameters["num_round"],
                "objective": self.config["model"]["hyperparameters"]["objective"],
                "eval_metric": self.config["model"]["hyperparameters"]["eval_metric"],
            },
            output_path=f"s3://{self.bucket}/{self.prefix}/models",
            # Managed Spot Training and Checkpointing
            use_spot_instances=self.config["sagemaker"]["training"].get(
                "use_spot_instances", False
            ),
            max_wait=self.config["sagemaker"]["training"].get("max_wait_seconds"),
            max_run=self.config["sagemaker"]["training"].get("max_runtime_seconds"),
            checkpoint_s3_uri=self.config["sagemaker"]["training"].get(
                "checkpoint_s3_uri"
            ),
            tags=self._format_tags(self.config.get("tags", {})),
        )

        # Define training step
        step_train = TrainingStep(
            name="TrainModel",
            estimator=xgb_estimator,
            inputs={
                "train": TrainingInput(
                    s3_data=step_process.properties.ProcessingOutputConfig.Outputs[
                        "train"
                    ].S3Output.S3Uri,
                    content_type="text/csv",
                ),
                "validation": TrainingInput(
                    s3_data=step_process.properties.ProcessingOutputConfig.Outputs[
                        "validation"
                    ].S3Output.S3Uri,
                    content_type="text/csv",
                ),
            },
        )

        return step_train

    def create_evaluation_step(self, step_train, step_process):
        """Create model evaluation step"""
        logger.info("Creating evaluation step...")

        # SKLearn processor for evaluation
        sklearn_processor = SKLearnProcessor(
            framework_version="1.0-1",
            role=self.role,
            instance_type="ml.m5.xlarge",
            instance_count=1,
            base_job_name="diabetes-evaluation",
            sagemaker_session=self.sagemaker_session,
        )

        # Evaluation report property file
        evaluation_report = PropertyFile(
            name="EvaluationReport",
            output_name="evaluation",
            path="evaluation_results.json",
        )

        # Define evaluation step
        step_eval = ProcessingStep(
            name="EvaluateModel",
            processor=sklearn_processor,
            inputs=[
                ProcessingInput(
                    source=step_train.properties.ModelArtifacts.S3ModelArtifacts,
                    destination="/opt/ml/processing/model",
                ),
                ProcessingInput(
                    source=step_process.properties.ProcessingOutputConfig.Outputs[
                        "test"
                    ].S3Output.S3Uri,
                    destination="/opt/ml/processing/test",
                ),
            ],
            outputs=[
                ProcessingOutput(
                    output_name="evaluation",
                    source="/opt/ml/processing/evaluation",
                    destination=f"s3://{self.bucket}/{self.prefix}/evaluation",
                )
            ],
            code="src/evaluation/evaluate.py",
            property_files=[evaluation_report],
        )

        return step_eval, evaluation_report

    def create_experiment_tracking_step(self, step_train, step_eval, evaluation_report):
        """Create experiment tracking step to log to SageMaker Experiments"""
        logger.info("Creating experiment tracking step...")

        # SKLearn processor for experiment tracking
        sklearn_processor = SKLearnProcessor(
            framework_version="1.0-1",
            role=self.role,
            instance_type="ml.t3.medium",  # Small instance is sufficient
            instance_count=1,
            base_job_name="diabetes-experiment-tracking",
            sagemaker_session=self.sagemaker_session,
        )

        # Define experiment tracking step
        step_experiment = ProcessingStep(
            name="TrackExperiment",
            processor=sklearn_processor,
            inputs=[
                ProcessingInput(
                    source=step_eval.properties.ProcessingOutputConfig.Outputs[
                        "evaluation"
                    ].S3Output.S3Uri,
                    destination="/opt/ml/processing/evaluation",
                )
            ],
            outputs=[
                ProcessingOutput(
                    output_name="experiment_log",
                    source="/opt/ml/processing/output",
                    destination=f"s3://{self.bucket}/{self.prefix}/experiments",
                )
            ],
            code="src/monitoring/track_experiment.py",
            job_arguments=[
                "--training-job-name",
                step_train.properties.TrainingJobName,
                "--model-artifact-uri",
                step_train.properties.ModelArtifacts.S3ModelArtifacts,
                "--evaluation-results",
                "/opt/ml/processing/evaluation/evaluation_results.json",
                "--experiment-name",
                "diabetes-classification-experiments",
            ],
        )

        return step_experiment

    def create_model_registration_step(
        self, step_train, step_eval, evaluation_report, parameters
    ):
        """Create model registration step"""
        logger.info("Creating model registration step...")

        # Use Join to concatenate S3 URI with pipeline properties
        evaluation_s3_uri = Join(
            on="/",
            values=[
                step_eval.properties.ProcessingOutputConfig.Outputs[
                    "evaluation"
                ].S3Output.S3Uri,
                "evaluation_results.json",
            ],
        )

        # Model metrics
        model_metrics = ModelMetrics(
            model_statistics=MetricsSource(
                s3_uri=evaluation_s3_uri,
                content_type="application/json",
            )
        )

        # Register model step
        step_register = RegisterModel(
            name="RegisterModel",
            estimator=step_train.estimator,
            model_data=step_train.properties.ModelArtifacts.S3ModelArtifacts,
            content_types=["text/csv"],
            response_types=["application/json"],
            inference_instances=["ml.t2.medium", "ml.m5.large"],
            transform_instances=["ml.m5.large"],
            model_package_group_name=self.config["sagemaker"]["model_registry"][
                "model_package_group_name"
            ],
            approval_status=parameters["model_approval_status"],
            model_metrics=model_metrics,
        )

        return step_register

    def create_condition_step(self, step_eval, evaluation_report, step_register):
        """
        Create conditional step for model approval with multiple metric checks
        Model is only registered if ALL thresholds are met
        """
        logger.info("Creating conditional step with multiple metric checks...")

        # Condition 1: Accuracy >= threshold
        cond_accuracy = ConditionGreaterThanOrEqualTo(
            left=JsonGet(
                step_name=step_eval.name,
                property_file=evaluation_report,
                json_path="metrics.accuracy",
            ),
            right=self.config["evaluation"]["approval_thresholds"]["min_accuracy"],
        )

        # Condition 2: F1 Score >= threshold
        cond_f1 = ConditionGreaterThanOrEqualTo(
            left=JsonGet(
                step_name=step_eval.name,
                property_file=evaluation_report,
                json_path="metrics.f1_score",
            ),
            right=self.config["evaluation"]["approval_thresholds"]["min_f1_score"],
        )

        # Condition 3: ROC-AUC >= threshold
        cond_roc_auc = ConditionGreaterThanOrEqualTo(
            left=JsonGet(
                step_name=step_eval.name,
                property_file=evaluation_report,
                json_path="metrics.roc_auc",
            ),
            right=self.config["evaluation"]["approval_thresholds"]["min_roc_auc"],
        )

        # Conditional step - ALL conditions must be true
        step_cond = ConditionStep(
            name="CheckModelQualityThresholds",
            conditions=[cond_accuracy, cond_f1, cond_roc_auc],  # AND logic
            if_steps=[step_register],  # Only register if ALL metrics meet threshold
            else_steps=[],  # Do nothing if quality check fails
        )

        logger.info(f"Quality gates configured:")
        logger.info(
            f"  - Min Accuracy: {self.config['evaluation']['approval_thresholds']['min_accuracy']}"
        )
        logger.info(
            f"  - Min F1 Score: {self.config['evaluation']['approval_thresholds']['min_f1_score']}"
        )
        logger.info(
            f"  - Min ROC-AUC: {self.config['evaluation']['approval_thresholds']['min_roc_auc']}"
        )

        return step_cond

    def create_pipeline(self):
        """Create complete pipeline"""
        logger.info("=" * 50)
        logger.info("Creating SageMaker Pipeline")
        logger.info("=" * 50)

        # Create parameters
        parameters = self.create_pipeline_parameters()

        # Create preprocessing step
        step_process = self.create_preprocessing_step(parameters)

        # Create training step
        step_train = self.create_training_step(parameters, step_process)

        # Create evaluation step
        step_eval, evaluation_report = self.create_evaluation_step(
            step_train, step_process
        )

        # Create experiment tracking step (logs to SageMaker Experiments)
        step_experiment = self.create_experiment_tracking_step(
            step_train, step_eval, evaluation_report
        )

        # Create model registration step
        step_register = self.create_model_registration_step(
            step_train, step_eval, evaluation_report, parameters
        )

        # Create conditional step
        step_cond = self.create_condition_step(
            step_eval, evaluation_report, step_register
        )

        # Create pipeline - experiment tracking runs after evaluation, before conditional registration
        pipeline = Pipeline(
            name=self.config["pipeline"]["name"],
            parameters=list(parameters.values()),
            steps=[step_process, step_train, step_eval, step_experiment, step_cond],
            sagemaker_session=self.sagemaker_session,
        )

        logger.info(
            f"Pipeline '{pipeline.name}' created successfully for environment: {self.environment}"
        )
        logger.info("Pipeline includes experiment tracking to SageMaker Experiments")

        return pipeline

    def execute_pipeline(self, pipeline):
        """Execute the pipeline"""
        logger.info(f"Executing pipeline in {self.environment} environment...")

        # Upsert pipeline (create or update)
        pipeline.upsert(role_arn=self.role)

        # Start execution
        execution = pipeline.start()

        logger.info(f"Pipeline execution started: {execution.arn}")
        logger.info(f"Environment: {self.environment}")
        logger.info(
            f"Approval status: {self.config['sagemaker']['model_registry']['approval_status']}"
        )
        logger.info("You can monitor the execution in SageMaker Console")

        return execution


def main():
    """Main execution function"""
    import argparse

    parser = argparse.ArgumentParser(description="Diabetes Classification Pipeline")
    parser.add_argument(
        "--environment",
        type=str,
        default="dev",
        choices=["dev", "staging", "production"],
        help="Target environment (dev, staging, production)",
    )
    parser.add_argument(
        "--config",
        type=str,
        default="config/config.yaml",
        help="Path to configuration file",
    )
    parser.add_argument(
        "--execute", action="store_true", help="Execute the pipeline after creation"
    )

    args = parser.parse_args()

    # Create pipeline with environment
    pipeline_builder = DiabetesPipeline(
        config_path=args.config, environment=args.environment
    )
    pipeline = pipeline_builder.create_pipeline()

    # Print pipeline definition
    logger.info("Pipeline Definition:")
    logger.info(json.dumps(json.loads(pipeline.definition()), indent=2))

    # Execute if requested
    if args.execute:
        execution = pipeline_builder.execute_pipeline(pipeline)
        logger.info(f"Execution ARN: {execution.arn}")
    else:
        logger.info("Pipeline created but not executed. Use --execute flag to run.")


if __name__ == "__main__":
    main()
