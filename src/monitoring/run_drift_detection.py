"""
On-Demand Data Drift Detection and Model Quality Monitoring
Run this script to check for data/model drift without continuous monitoring costs
"""

import boto3
import json
import time
from datetime import datetime
import argparse
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class OnDemandMonitor:
    """Run data drift and model quality checks on-demand"""

    def __init__(self, environment="dev", region="us-east-1"):
        self.environment = environment
        self.sm_client = boto3.client("sagemaker", region_name=region)
        self.cw_client = boto3.client("cloudwatch", region_name=region)
        self.s3_client = boto3.client("s3", region_name=region)

    def run_data_quality_job(self, job_definition_name, endpoint_name):
        """Execute data quality monitoring job on-demand"""
        logger.info(f"Starting data quality monitoring for endpoint: {endpoint_name}")

        job_name = f"data-quality-{int(time.time())}"

        try:
            response = self.sm_client.start_data_quality_job_definition(
                JobDefinitionName=job_definition_name, MonitoringJobName=job_name
            )

            logger.info(f"Data quality job started: {job_name}")
            logger.info(f"Job ARN: {response['MonitoringJobArn']}")

            # Wait for completion
            self.wait_for_job_completion(job_name)

            # Get results
            results = self.get_monitoring_results(job_name)
            return results

        except Exception as e:
            logger.error(f"Failed to run data quality job: {e}")
            return None

    def run_model_quality_job(self, job_definition_name, endpoint_name):
        """Execute model quality monitoring job on-demand"""
        logger.info(f"Starting model quality monitoring for endpoint: {endpoint_name}")

        job_name = f"model-quality-{int(time.time())}"

        try:
            response = self.sm_client.start_model_quality_job_definition(
                JobDefinitionName=job_definition_name, MonitoringJobName=job_name
            )

            logger.info(f"Model quality job started: {job_name}")
            logger.info(f"Job ARN: {response['MonitoringJobArn']}")

            # Wait for completion
            self.wait_for_job_completion(job_name)

            # Get results
            results = self.get_monitoring_results(job_name)
            return results

        except Exception as e:
            logger.error(f"Failed to run model quality job: {e}")
            return None

    def wait_for_job_completion(self, job_name, timeout=3600):
        """Wait for monitoring job to complete"""
        start_time = time.time()

        while True:
            response = self.sm_client.describe_processing_job(
                ProcessingJobName=job_name
            )
            status = response["ProcessingJobStatus"]

            logger.info(f"Job status: {status}")

            if status in ["Completed", "Failed", "Stopped"]:
                break

            if time.time() - start_time > timeout:
                logger.error("Job timeout")
                break

            time.sleep(30)

        if status == "Completed":
            logger.info("✅ Monitoring job completed successfully")
            return True
        else:
            logger.error(f"❌ Monitoring job failed with status: {status}")
            return False

    def get_monitoring_results(self, job_name):
        """Retrieve monitoring results from S3"""
        try:
            response = self.sm_client.describe_processing_job(
                ProcessingJobName=job_name
            )
            outputs = response["ProcessingOutputConfig"]["Outputs"]

            results = {}
            for output in outputs:
                s3_uri = output["S3Output"]["S3Uri"]
                logger.info(f"Results location: {s3_uri}")
                results[output["OutputName"]] = s3_uri

            return results
        except Exception as e:
            logger.error(f"Failed to get results: {e}")
            return None

    def get_endpoint_metrics(self, endpoint_name, hours=24):
        """Get CloudWatch metrics for endpoint"""
        logger.info(f"Fetching endpoint metrics for: {endpoint_name}")

        end_time = datetime.utcnow()
        start_time = datetime.utcnow() - timedelta(hours=hours)

        metrics = {}

        # Invocations
        try:
            response = self.cw_client.get_metric_statistics(
                Namespace="AWS/SageMaker",
                MetricName="Invocations",
                Dimensions=[
                    {"Name": "EndpointName", "Value": endpoint_name},
                    {"Name": "VariantName", "Value": "AllTraffic"},
                ],
                StartTime=start_time,
                EndTime=end_time,
                Period=3600,  # 1 hour
                Statistics=["Sum"],
            )
            metrics["invocations"] = response["Datapoints"]
        except Exception as e:
            logger.warning(f"Failed to get invocations: {e}")

        # Model Latency
        try:
            response = self.cw_client.get_metric_statistics(
                Namespace="AWS/SageMaker",
                MetricName="ModelLatency",
                Dimensions=[
                    {"Name": "EndpointName", "Value": endpoint_name},
                    {"Name": "VariantName", "Value": "AllTraffic"},
                ],
                StartTime=start_time,
                EndTime=end_time,
                Period=3600,
                Statistics=["Average", "Maximum"],
            )
            metrics["latency"] = response["Datapoints"]
        except Exception as e:
            logger.warning(f"Failed to get latency: {e}")

        # Invocation Errors
        try:
            response = self.cw_client.get_metric_statistics(
                Namespace="AWS/SageMaker",
                MetricName="ModelInvocationErrors",
                Dimensions=[
                    {"Name": "EndpointName", "Value": endpoint_name},
                    {"Name": "VariantName", "Value": "AllTraffic"},
                ],
                StartTime=start_time,
                EndTime=end_time,
                Period=3600,
                Statistics=["Sum"],
            )
            metrics["errors"] = response["Datapoints"]
        except Exception as e:
            logger.warning(f"Failed to get errors: {e}")

        self.print_metrics_summary(metrics)
        return metrics

    def print_metrics_summary(self, metrics):
        """Print a summary of endpoint metrics"""
        print("\n" + "=" * 60)
        print("ENDPOINT METRICS SUMMARY (Last 24 Hours)")
        print("=" * 60)

        # Invocations
        if "invocations" in metrics and metrics["invocations"]:
            total_invocations = sum(dp["Sum"] for dp in metrics["invocations"])
            print(f"📊 Total Invocations: {int(total_invocations):,}")
        else:
            print("📊 Total Invocations: 0")

        # Latency
        if "latency" in metrics and metrics["latency"]:
            avg_latency = sum(dp["Average"] for dp in metrics["latency"]) / len(
                metrics["latency"]
            )
            max_latency = max(dp["Maximum"] for dp in metrics["latency"])
            print(f"⏱️  Average Latency: {avg_latency:.2f}ms")
            print(f"⏱️  Maximum Latency: {max_latency:.2f}ms")
        else:
            print("⏱️  Latency: No data")

        # Errors
        if "errors" in metrics and metrics["errors"]:
            total_errors = sum(dp["Sum"] for dp in metrics["errors"])
            if total_errors > 0:
                print(f"❌ Total Errors: {int(total_errors)}")
            else:
                print("✅ No Errors")
        else:
            print("✅ No Errors")

        print("=" * 60 + "\n")


def main():
    parser = argparse.ArgumentParser(description="Run on-demand model monitoring")
    parser.add_argument(
        "--environment",
        default="dev",
        choices=["dev", "staging", "production"],
        help="Environment name",
    )
    parser.add_argument(
        "--endpoint-name", required=True, help="SageMaker endpoint name to monitor"
    )
    parser.add_argument(
        "--check-data-drift", action="store_true", help="Run data drift detection"
    )
    parser.add_argument(
        "--check-model-quality", action="store_true", help="Run model quality check"
    )
    parser.add_argument(
        "--get-metrics", action="store_true", help="Get CloudWatch metrics"
    )
    parser.add_argument(
        "--hours", type=int, default=24, help="Hours of metrics to retrieve"
    )

    args = parser.parse_args()

    monitor = OnDemandMonitor(environment=args.environment)

    # Get CloudWatch metrics
    if args.get_metrics:
        monitor.get_endpoint_metrics(args.endpoint_name, args.hours)

    # Run data drift detection
    if args.check_data_drift:
        job_def = f"mlops-diabetes-data-quality-{args.environment}"
        results = monitor.run_data_quality_job(job_def, args.endpoint_name)
        if results:
            print(f"\n✅ Data drift detection completed")
            print(f"Results: {json.dumps(results, indent=2)}")

    # Run model quality check
    if args.check_model_quality:
        job_def = f"mlops-diabetes-model-quality-{args.environment}"
        results = monitor.run_model_quality_job(job_def, args.environment)
        if results:
            print(f"\n✅ Model quality check completed")
            print(f"Results: {json.dumps(results, indent=2)}")


if __name__ == "__main__":
    main()
