"""
Model Monitor Setup
Configure SageMaker Model Monitor for data quality and model quality monitoring

Environment Variables (override config.yaml):
- AWS_REGION: AWS region for monitoring
- SAGEMAKER_ROLE_ARN: IAM role ARN for SageMaker
- S3_BUCKET: S3 bucket for monitoring outputs
"""

import os
import boto3
import sagemaker
from sagemaker.model_monitor import (
    DataCaptureConfig,
    CronExpressionGenerator,
)

# Note: DataQualityMonitoringConfig and ModelQualityMonitoringConfig may not be available in all SDK versions
# Use DefaultModelMonitor and ModelQualityMonitor classes instead
try:
    from sagemaker.model_monitor.dataset_format import DatasetFormat
except ImportError:
    DatasetFormat = None
import logging
import yaml

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ModelMonitor:
    """
    Sets up and manages SageMaker Model Monitor
    """

    def __init__(self, config_path="config/config.yaml"):
        """Initialize Model Monitor"""
        logger.info("Initializing Model Monitor...")

        # Load configuration
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)

        # Override sensitive values from environment variables
        self.region = os.environ.get("AWS_REGION", self.config["aws"]["region"])
        self.role = os.environ.get(
            "SAGEMAKER_ROLE_ARN", self.config["sagemaker"]["role"]
        )
        self.bucket = os.environ.get("S3_BUCKET", self.config["s3"]["bucket_name"])
        self.prefix = self.config["s3"]["prefix"]

        logger.info(f"Using AWS Region: {self.region}")
        logger.info(f"Using S3 Bucket: {self.bucket}")

        self.sagemaker_session = sagemaker.Session(
            boto_session=boto3.Session(region_name=self.region)
        )
        self.sagemaker_client = boto3.client("sagemaker", region_name=self.region)

    def find_active_endpoint(self, endpoint_name_prefix):
        """
        Find the latest InService endpoint matching the prefix
        Returns the full endpoint name or None
        """
        try:
            response = self.sagemaker_client.list_endpoints(
                SortBy='CreationTime',
                SortOrder='Descending',
                MaxResults=100,
                StatusEquals='InService'
            )
            
            # Find endpoints matching the prefix
            matching_endpoints = [
                ep for ep in response['Endpoints'] 
                if ep['EndpointName'].startswith(endpoint_name_prefix)
            ]
            
            if matching_endpoints:
                latest = matching_endpoints[0]['EndpointName']
                logger.info(f"Found active endpoint: {latest}")
                return latest
            else:
                logger.warning(f"No InService endpoints found with prefix: {endpoint_name_prefix}")
                return None
                
        except Exception as e:
            logger.error(f"Error finding active endpoint: {str(e)}")
            return None

    def enable_data_capture(self, endpoint_name, sampling_percentage=100):
        """
        Enable data capture for an endpoint
        """
        logger.info(f"Enabling data capture for endpoint: {endpoint_name}")

        # Data capture S3 path
        data_capture_uri = f"s3://{self.bucket}/{self.prefix}/monitoring/data-capture"

        try:
            # Get current endpoint config
            endpoint_desc = self.sagemaker_client.describe_endpoint(
                EndpointName=endpoint_name
            )
            
            # Check endpoint status
            endpoint_status = endpoint_desc["EndpointStatus"]
            if endpoint_status == "Failed":
                logger.error(f"Endpoint {endpoint_name} is in Failed state")
                logger.error("Please delete the failed endpoint first:")
                logger.error(f"  aws sagemaker delete-endpoint --endpoint-name {endpoint_name}")
                logger.error("Then redeploy a new endpoint with:")
                logger.error(f"  python src/deployment/deploy.py --endpoint-name {endpoint_name} --allow-unapproved")
                raise ValueError(f"Endpoint {endpoint_name} is in Failed state and cannot be updated")
            
            if endpoint_status != "InService":
                logger.warning(f"Endpoint {endpoint_name} is in {endpoint_status} state, not InService")
                logger.warning("Data capture can only be enabled on InService endpoints")
                return None
            
            current_config = endpoint_desc["EndpointConfigName"]

            # Get production variants
            config_desc = self.sagemaker_client.describe_endpoint_config(
                EndpointConfigName=current_config
            )
            production_variants = config_desc["ProductionVariants"]

            # Create new endpoint config with data capture
            import datetime

            timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
            new_config_name = f"{endpoint_name}-datacapture-{timestamp}"

            self.sagemaker_client.create_endpoint_config(
                EndpointConfigName=new_config_name,
                ProductionVariants=production_variants,
                DataCaptureConfig={
                    "EnableCapture": True,
                    "InitialSamplingPercentage": sampling_percentage,
                    "DestinationS3Uri": data_capture_uri,
                    "CaptureOptions": [
                        {"CaptureMode": "Input"},
                        {"CaptureMode": "Output"},
                    ],
                },
            )

            # Update endpoint
            self.sagemaker_client.update_endpoint(
                EndpointName=endpoint_name, EndpointConfigName=new_config_name
            )

            logger.info(
                f"Data capture enabled. Data will be saved to {data_capture_uri}"
            )
            logger.info("Endpoint is being updated. This may take a few minutes...")

            return data_capture_uri

        except Exception as e:
            logger.error(f"Error enabling data capture: {str(e)}")
            raise

    def create_baseline(self, endpoint_name, baseline_dataset_path):
        """
        Create baseline for model monitoring
        """
        logger.info("Creating monitoring baseline...")

        from sagemaker.model_monitor import DefaultModelMonitor

        # Create baseline output path
        baseline_uri = f"s3://{self.bucket}/{self.prefix}/monitoring/baseline"

        try:
            # Create monitor
            my_monitor = DefaultModelMonitor(
                role=self.role,
                instance_count=1,
                instance_type=self.config["sagemaker"]["monitoring"]["instance_type"],
                volume_size_in_gb=self.config["sagemaker"]["monitoring"][
                    "volume_size_gb"
                ],
                max_runtime_in_seconds=self.config["sagemaker"]["monitoring"][
                    "max_runtime_seconds"
                ],
                sagemaker_session=self.sagemaker_session,
            )

            # Suggest baseline
            logger.info(f"Analyzing baseline dataset: {baseline_dataset_path}")

            my_monitor.suggest_baseline(
                baseline_dataset=baseline_dataset_path,
                dataset_format=DatasetFormat.csv(header=False),
                output_s3_uri=baseline_uri,
                wait=True,
            )

            logger.info(f"Baseline created successfully at {baseline_uri}")
            return baseline_uri

        except Exception as e:
            logger.error(f"Error creating baseline: {str(e)}")
            raise

    def create_monitoring_schedule(
        self, endpoint_name, baseline_uri, schedule_name=None
    ):
        """
        Create monitoring schedule for continuous monitoring
        """
        if schedule_name is None:
            schedule_name = f"{endpoint_name}-monitoring-schedule"

        logger.info(f"Creating monitoring schedule: {schedule_name}")

        from sagemaker.model_monitor import DefaultModelMonitor, CronExpressionGenerator

        # Monitoring output path
        monitoring_output_uri = f"s3://{self.bucket}/{self.prefix}/monitoring/reports"

        try:
            # Create monitor
            my_monitor = DefaultModelMonitor(
                role=self.role,
                instance_count=1,
                instance_type=self.config["sagemaker"]["monitoring"]["instance_type"],
                volume_size_in_gb=self.config["sagemaker"]["monitoring"][
                    "volume_size_gb"
                ],
                max_runtime_in_seconds=self.config["sagemaker"]["monitoring"][
                    "max_runtime_seconds"
                ],
                sagemaker_session=self.sagemaker_session,
            )

            # Create monitoring schedule (hourly)
            my_monitor.create_monitoring_schedule(
                monitor_schedule_name=schedule_name,
                endpoint_input=endpoint_name,
                output_s3_uri=monitoring_output_uri,
                statistics=f"{baseline_uri}/statistics.json",
                constraints=f"{baseline_uri}/constraints.json",
                schedule_cron_expression=CronExpressionGenerator.hourly(),
                enable_cloudwatch_metrics=True,
            )

            logger.info(f"Monitoring schedule created: {schedule_name}")
            logger.info(f"Monitoring reports will be saved to {monitoring_output_uri}")

            return schedule_name

        except Exception as e:
            logger.error(f"Error creating monitoring schedule: {str(e)}")
            raise

    def get_monitoring_results(self, schedule_name):
        """
        Get latest monitoring results
        """
        logger.info(f"Getting monitoring results for {schedule_name}")

        try:
            response = self.sagemaker_client.list_monitoring_executions(
                MonitoringScheduleName=schedule_name,
                SortOrder="Descending",
                MaxResults=1,
            )

            if not response["MonitoringExecutionSummaries"]:
                logger.info("No monitoring executions found")
                return None

            latest_execution = response["MonitoringExecutionSummaries"][0]

            logger.info(
                f"Latest execution status: {latest_execution['MonitoringExecutionStatus']}"
            )

            if latest_execution["MonitoringExecutionStatus"] == "Completed":
                # Get processing job details
                processing_job_arn = latest_execution["ProcessingJobArn"]
                job_name = processing_job_arn.split("/")[-1]

                job_desc = self.sagemaker_client.describe_processing_job(
                    ProcessingJobName=job_name
                )

                # Get output location
                output_config = job_desc.get("ProcessingOutputConfig", {})
                outputs = output_config.get("Outputs", [])

                if outputs:
                    output_uri = outputs[0]["S3Output"]["S3Uri"]
                    logger.info(f"Monitoring report available at: {output_uri}")
                    return output_uri

            return None

        except Exception as e:
            logger.error(f"Error getting monitoring results: {str(e)}")
            raise

    def delete_monitoring_schedule(self, schedule_name):
        """
        Delete monitoring schedule
        """
        logger.info(f"Deleting monitoring schedule: {schedule_name}")

        try:
            self.sagemaker_client.delete_monitoring_schedule(
                MonitoringScheduleName=schedule_name
            )
            logger.info(f"Monitoring schedule {schedule_name} deleted successfully")

        except Exception as e:
            logger.error(f"Error deleting monitoring schedule: {str(e)}")
            raise


def main():
    """Main monitoring setup function"""
    import argparse

    parser = argparse.ArgumentParser(description="Setup Model Monitoring")
    parser.add_argument(
        "--config",
        type=str,
        default="config/config.yaml",
        help="Path to configuration file",
    )
    parser.add_argument(
        "--endpoint-name",
        type=str,
        required=True,
        help="Name of the endpoint to monitor",
    )
    parser.add_argument(
        "--baseline-data",
        type=str,
        required=False,
        help="S3 path to baseline dataset (required only for --create-baseline)",
    )
    parser.add_argument(
        "--enable-capture", action="store_true", help="Enable data capture"
    )
    parser.add_argument(
        "--create-baseline", action="store_true", help="Create monitoring baseline"
    )
    parser.add_argument(
        "--create-schedule", action="store_true", help="Create monitoring schedule"
    )

    args = parser.parse_args()

    # Initialize monitor
    monitor = ModelMonitor(config_path=args.config)

    # Try to find the actual active endpoint if the provided name doesn't exist or is failed
    actual_endpoint_name = args.endpoint_name
    
    try:
        endpoint_desc = monitor.sagemaker_client.describe_endpoint(
            EndpointName=args.endpoint_name
        )
        if endpoint_desc["EndpointStatus"] != "InService":
            logger.warning(f"Endpoint {args.endpoint_name} is in {endpoint_desc['EndpointStatus']} state")
            logger.info(f"Searching for active endpoint with prefix: {args.endpoint_name}")
            actual_endpoint_name = monitor.find_active_endpoint(args.endpoint_name)
            if actual_endpoint_name is None:
                logger.error(f"No active endpoint found with prefix: {args.endpoint_name}")
                logger.info("Available InService endpoints:")
                endpoints = monitor.sagemaker_client.list_endpoints(StatusEquals='InService')
                for ep in endpoints['Endpoints']:
                    logger.info(f"  - {ep['EndpointName']}")
                return
    except monitor.sagemaker_client.exceptions.ClientError:
        # Endpoint doesn't exist, try to find it by prefix
        logger.info(f"Endpoint {args.endpoint_name} not found. Searching for active endpoint with prefix...")
        actual_endpoint_name = monitor.find_active_endpoint(args.endpoint_name)
        if actual_endpoint_name is None:
            logger.error(f"No active endpoint found with prefix: {args.endpoint_name}")
            return

    logger.info(f"Using endpoint: {actual_endpoint_name}")

    # Enable data capture
    if args.enable_capture:
        monitor.enable_data_capture(actual_endpoint_name)

    # Create baseline
    baseline_uri = None
    if args.create_baseline:
        if not args.baseline_data:
            logger.error("--baseline-data is required when using --create-baseline")
            return
        baseline_uri = monitor.create_baseline(actual_endpoint_name, args.baseline_data)

    # Create monitoring schedule
    if args.create_schedule:
        if baseline_uri is None:
            baseline_uri = f"s3://{monitor.bucket}/{monitor.prefix}/monitoring/baseline"

        monitor.create_monitoring_schedule(actual_endpoint_name, baseline_uri)

    logger.info("Model monitoring setup completed!")


if __name__ == "__main__":
    main()
