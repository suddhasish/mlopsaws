"""
Model Deployment Module
Deploy trained models to SageMaker endpoints with auto-scaling

Environment Variables (override config.yaml):
- AWS_REGION: AWS region for deployment
- SAGEMAKER_ROLE_ARN: IAM role ARN for SageMaker
- MODEL_PACKAGE_GROUP_NAME: Model Registry group name
- ENDPOINT_INSTANCE_TYPE: EC2 instance type for endpoint
"""

import os
import json
import boto3
import sagemaker
from sagemaker.model import Model
from sagemaker import ModelPackage
from sagemaker.predictor import Predictor
from sagemaker.serializers import CSVSerializer
from sagemaker.deserializers import JSONDeserializer
import logging
import yaml

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ModelDeployer:
    """
    Handles model deployment to SageMaker endpoints
    """

    def __init__(self, config_path="config/config.yaml"):
        """Initialize deployer with configuration"""
        logger.info("Initializing Model Deployer...")

        # Load configuration
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)

        # Override sensitive values from environment variables
        self.region = os.environ.get("AWS_REGION", self.config["aws"]["region"])
        self.role = os.environ.get("SAGEMAKER_ROLE_ARN", self.config["sagemaker"]["role"])
        
        logger.info(f"Using AWS Region: {self.region}")
        logger.info(f"Using SageMaker Role: {self.role}")
        
        self.sagemaker_session = sagemaker.Session(
            boto_session=boto3.Session(region_name=self.region)
        )
        self.sagemaker_client = boto3.client("sagemaker", region_name=self.region)

    def get_approved_model(self, model_package_group_name=None):
        """Get the latest approved model from Model Registry"""
        if model_package_group_name is None:
            model_package_group_name = os.environ.get(
                "MODEL_PACKAGE_GROUP_NAME",
                self.config["sagemaker"]["model_registry"]["model_package_group_name"]
            )

        logger.info(f"Getting approved model from {model_package_group_name}...")

        try:
            # List model packages
            response = self.sagemaker_client.list_model_packages(
                ModelPackageGroupName=model_package_group_name,
                ModelApprovalStatus="Approved",
                SortBy="CreationTime",
                SortOrder="Descending",
                MaxResults=1,
            )

            if not response["ModelPackageSummaryList"]:
                logger.warning(f"No approved models found in {model_package_group_name}")
                
                # Check if there are any models at all (any status)
                all_models_response = self.sagemaker_client.list_model_packages(
                    ModelPackageGroupName=model_package_group_name,
                    SortBy="CreationTime",
                    SortOrder="Descending",
                    MaxResults=5,
                )
                
                if all_models_response["ModelPackageSummaryList"]:
                    logger.info(f"Found {len(all_models_response['ModelPackageSummaryList'])} model(s) with other statuses:")
                    for pkg in all_models_response["ModelPackageSummaryList"]:
                        logger.info(f"  - {pkg['ModelPackageArn']}")
                        logger.info(f"    Status: {pkg.get('ModelApprovalStatus', 'Unknown')}")
                    logger.info("Please approve a model in the SageMaker console to deploy it.")
                else:
                    logger.warning("No models found at all. Please run the training pipeline first.")
                
                return None

            model_package_arn = response["ModelPackageSummaryList"][0][
                "ModelPackageArn"
            ]
            logger.info(f"Found approved model: {model_package_arn}")

            return model_package_arn

        except self.sagemaker_client.exceptions.ResourceNotFound:
            logger.error(f"Model package group '{model_package_group_name}' does not exist.")
            logger.info("Please run the training pipeline first to create the model package group.")
            return None
        except Exception as e:
            logger.error(f"Error getting approved model: {str(e)}")
            raise

    def create_model(self, model_package_arn=None, model_name=None):
        """Create SageMaker model from model package"""
        if model_package_arn is None:
            model_package_arn = self.get_approved_model()
        
        # Check if we have a valid model package ARN
        if model_package_arn is None:
            error_msg = (
                "No approved model found in Model Registry. "
                "Please ensure you have:\n"
                "1. Executed the SageMaker pipeline\n"
                "2. Approved a model in the Model Registry\n"
                f"Model Package Group: {os.environ.get('MODEL_PACKAGE_GROUP_NAME', self.config['sagemaker']['model_registry']['model_package_group_name'])}"
            )
            logger.error(error_msg)
            raise ValueError(error_msg)

        if model_name is None:
            import datetime

            timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
            model_name = f"diabetes-model-{timestamp}"

        logger.info(f"Creating model from package: {model_package_arn}")
        logger.info(f"Model name: {model_name}")

        try:
            # Create model package (for deploying from Model Registry)
            model = ModelPackage(
                role=self.role,
                model_package_arn=model_package_arn,
                sagemaker_session=self.sagemaker_session,
                name=model_name,
            )

            logger.info(f"Model package {model_name} created successfully")
            return model

        except Exception as e:
            logger.error(f"Error creating model: {str(e)}")
            raise
    def deploy_model(
        self, model=None, endpoint_name=None, instance_type=None, instance_count=1
    ):
        """Deploy model to SageMaker endpoint"""
        if instance_type is None:
            instance_type = os.environ.get(
                "ENDPOINT_INSTANCE_TYPE",
                self.config["sagemaker"]["endpoint"]["instance_type"]
            )
            instance_type = self.config["sagemaker"]["endpoint"]["instance_type"]

        if endpoint_name is None:
            import datetime

            timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
            endpoint_name = f"diabetes-endpoint-{timestamp}"

        if model is None:
            model_package_arn = self.get_approved_model()
            model = self.create_model(model_package_arn)

        logger.info(f"Deploying model to endpoint: {endpoint_name}")
        logger.info(f"Instance type: {instance_type}, Instance count: {instance_count}")

        try:
            # Deploy model
            predictor = model.deploy(
                initial_instance_count=instance_count,
                instance_type=instance_type,
                endpoint_name=endpoint_name,
                serializer=CSVSerializer(),
                deserializer=JSONDeserializer(),
            )

            logger.info(f"Model deployed successfully to endpoint: {endpoint_name}")
            return predictor, endpoint_name

        except Exception as e:
            logger.error(f"Error deploying model: {str(e)}")
            raise

    def update_endpoint(self, endpoint_name, new_model_name):
        """Update existing endpoint with new model"""
        logger.info(f"Updating endpoint {endpoint_name} with model {new_model_name}")

        try:
            # Create endpoint config
            import datetime

            timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
            endpoint_config_name = f"{endpoint_name}-config-{timestamp}"

            self.sagemaker_client.create_endpoint_config(
                EndpointConfigName=endpoint_config_name,
                ProductionVariants=[
                    {
                        "VariantName": "AllTraffic",
                        "ModelName": new_model_name,
                        "InitialInstanceCount": 1,
                        "InstanceType": os.environ.get(
                            "ENDPOINT_INSTANCE_TYPE",
                            self.config["sagemaker"]["endpoint"]["instance_type"]
                        ),
                    }
                ],
            )

            # Update endpoint
            self.sagemaker_client.update_endpoint(
                EndpointName=endpoint_name, EndpointConfigName=endpoint_config_name
            )

            logger.info(f"Endpoint {endpoint_name} updated successfully")

        except Exception as e:
            logger.error(f"Error updating endpoint: {str(e)}")
            raise

    def delete_endpoint(self, endpoint_name):
        """Delete SageMaker endpoint"""
        logger.info(f"Deleting endpoint: {endpoint_name}")

        try:
            self.sagemaker_client.delete_endpoint(EndpointName=endpoint_name)
            logger.info(f"Endpoint {endpoint_name} deleted successfully")

        except Exception as e:
            logger.error(f"Error deleting endpoint: {str(e)}")
            raise

    def test_endpoint(self, endpoint_name, test_data):
        """Test endpoint with sample data"""
        logger.info(f"Testing endpoint: {endpoint_name}")

        try:
            # Create predictor
            predictor = Predictor(
                endpoint_name=endpoint_name,
                sagemaker_session=self.sagemaker_session,
                serializer=CSVSerializer(),
                deserializer=JSONDeserializer(),
            )

            # Make prediction
            response = predictor.predict(test_data)
            logger.info(f"Prediction response: {response}")

            return response

        except Exception as e:
            logger.error(f"Error testing endpoint: {str(e)}")
            raise


class EndpointScaler:
    """
    Manages auto-scaling for SageMaker endpoints
    """

    def __init__(self, region="us-east-1"):
        self.region = region
        self.autoscaling_client = boto3.client(
            "application-autoscaling", region_name=region
        )

    def configure_autoscaling(
        self,
        endpoint_name,
        variant_name="AllTraffic",
        min_capacity=1,
        max_capacity=5,
        target_invocations=1000,
    ):
        """Configure auto-scaling for endpoint"""
        logger.info(f"Configuring auto-scaling for endpoint: {endpoint_name}")
        logger.info(f"Min capacity: {min_capacity}, Max capacity: {max_capacity}")
        logger.info(f"Target invocations: {target_invocations}")

        try:
            # Define resource ID
            resource_id = f"endpoint/{endpoint_name}/variant/{variant_name}"

            # Register scalable target
            self.autoscaling_client.register_scalable_target(
                ServiceNamespace="sagemaker",
                ResourceId=resource_id,
                ScalableDimension="sagemaker:variant:DesiredInstanceCount",
                MinCapacity=min_capacity,
                MaxCapacity=max_capacity,
            )

            logger.info("Scalable target registered")

            # Define scaling policy
            self.autoscaling_client.put_scaling_policy(
                PolicyName=f"{endpoint_name}-scaling-policy",
                ServiceNamespace="sagemaker",
                ResourceId=resource_id,
                ScalableDimension="sagemaker:variant:DesiredInstanceCount",
                PolicyType="TargetTrackingScaling",
                TargetTrackingScalingPolicyConfiguration={
                    "TargetValue": float(target_invocations),
                    "PredefinedMetricSpecification": {
                        "PredefinedMetricType": "SageMakerVariantInvocationsPerInstance"
                    },
                    "ScaleInCooldown": 300,
                    "ScaleOutCooldown": 60,
                },
            )

            logger.info("Auto-scaling policy configured successfully")

        except Exception as e:
            logger.error(f"Error configuring auto-scaling: {str(e)}")
            raise

    def remove_autoscaling(self, endpoint_name, variant_name="AllTraffic"):
        """Remove auto-scaling configuration"""
        logger.info(f"Removing auto-scaling from endpoint: {endpoint_name}")

        try:
            resource_id = f"endpoint/{endpoint_name}/variant/{variant_name}"

            # Delete scaling policy
            self.autoscaling_client.delete_scaling_policy(
                PolicyName=f"{endpoint_name}-scaling-policy",
                ServiceNamespace="sagemaker",
                ResourceId=resource_id,
                ScalableDimension="sagemaker:variant:DesiredInstanceCount",
            )

            # Deregister scalable target
            self.autoscaling_client.deregister_scalable_target(
                ServiceNamespace="sagemaker",
                ResourceId=resource_id,
                ScalableDimension="sagemaker:variant:DesiredInstanceCount",
            )

            logger.info("Auto-scaling removed successfully")

        except Exception as e:
            logger.error(f"Error removing auto-scaling: {str(e)}")
            raise


def main():
    """Main deployment function"""
    import argparse

    parser = argparse.ArgumentParser(description="Deploy Diabetes Classification Model")
    parser.add_argument(
        "--config",
        type=str,
        default="config/config.yaml",
        help="Path to configuration file",
    )
    parser.add_argument(
        "--endpoint-name",
        type=str,
        default="diabetes-classifier",
        help="Name for the endpoint",
    )
    parser.add_argument(
        "--enable-autoscaling",
        action="store_true",
        help="Enable auto-scaling for the endpoint",
    )
    parser.add_argument(
        "--test", action="store_true", help="Test the endpoint after deployment"
    )

    args = parser.parse_args()

    # Deploy model
    deployer = ModelDeployer(config_path=args.config)

    # Get approved model and deploy
    predictor, endpoint_name = deployer.deploy_model(endpoint_name=args.endpoint_name)

    logger.info(f"Endpoint deployed: {endpoint_name}")

    # Configure auto-scaling if requested
    if args.enable_autoscaling:
        scaler = EndpointScaler(region=deployer.region)
        scaler.configure_autoscaling(
            endpoint_name=endpoint_name,
            min_capacity=1,
            max_capacity=5,
            target_invocations=1000,
        )

    # Test endpoint if requested
    if args.test:
        # Sample test data (8 features)
        test_data = [[6, 148, 72, 35, 0, 33.6, 0.627, 50]]

        logger.info("Testing endpoint with sample data...")
        response = deployer.test_endpoint(endpoint_name, test_data)
        logger.info(f"Test prediction: {response}")

    logger.info("Deployment completed successfully!")


if __name__ == "__main__":
    main()
