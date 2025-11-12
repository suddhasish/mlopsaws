"""
Setup CloudWatch Alarms for SageMaker Endpoints
Automated monitoring with SNS notifications
"""

import boto3
import argparse
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EndpointAlarmsManager:
    """Manage CloudWatch alarms for SageMaker endpoints"""
    
    def __init__(self, region="us-east-1"):
        self.cloudwatch = boto3.client("cloudwatch", region_name=region)
        self.sns = boto3.client("sns", region_name=region)
        self.region = region
    
    def create_sns_topic(self, topic_name="sagemaker-endpoint-alerts"):
        """Create SNS topic for alarm notifications"""
        try:
            response = self.sns.create_topic(Name=topic_name)
            topic_arn = response["TopicArn"]
            logger.info(f"✓ SNS topic created/exists: {topic_arn}")
            return topic_arn
        except Exception as e:
            logger.error(f"Error creating SNS topic: {e}")
            raise
    
    def subscribe_email(self, topic_arn, email):
        """Subscribe email to SNS topic"""
        try:
            self.sns.subscribe(
                TopicArn=topic_arn,
                Protocol="email",
                Endpoint=email
            )
            logger.info(f"✓ Email subscription created for {email}")
            logger.info("  Please confirm the subscription via email")
        except Exception as e:
            logger.error(f"Error subscribing email: {e}")
            raise
    
    def create_error_rate_alarm(
        self,
        endpoint_name,
        variant_name="AllTraffic",
        threshold=5.0,
        sns_topic_arn=None
    ):
        """
        Create alarm for high error rate
        Triggers when 5xx errors exceed threshold (default: 5%)
        """
        alarm_name = f"{endpoint_name}-high-error-rate"
        
        alarm_actions = [sns_topic_arn] if sns_topic_arn else []
        
        try:
            self.cloudwatch.put_metric_alarm(
                AlarmName=alarm_name,
                AlarmDescription=f"Alert when {endpoint_name} error rate exceeds {threshold}%",
                ActionsEnabled=True,
                AlarmActions=alarm_actions,
                MetricName="Invocation5XXErrors",
                Namespace="AWS/SageMaker",
                Statistic="Sum",
                Dimensions=[
                    {"Name": "EndpointName", "Value": endpoint_name},
                    {"Name": "VariantName", "Value": variant_name}
                ],
                Period=300,  # 5 minutes
                EvaluationPeriods=2,  # 2 consecutive periods
                Threshold=threshold,
                ComparisonOperator="GreaterThanThreshold",
                TreatMissingData="notBreaching"
            )
            logger.info(f"✓ Created alarm: {alarm_name}")
        except Exception as e:
            logger.error(f"Error creating error rate alarm: {e}")
            raise
    
    def create_latency_alarm(
        self,
        endpoint_name,
        variant_name="AllTraffic",
        threshold_ms=1000,
        sns_topic_arn=None
    ):
        """
        Create alarm for high latency
        Triggers when P95 latency exceeds threshold (default: 1000ms)
        """
        alarm_name = f"{endpoint_name}-high-latency"
        
        alarm_actions = [sns_topic_arn] if sns_topic_arn else []
        
        try:
            self.cloudwatch.put_metric_alarm(
                AlarmName=alarm_name,
                AlarmDescription=f"Alert when {endpoint_name} latency exceeds {threshold_ms}ms",
                ActionsEnabled=True,
                AlarmActions=alarm_actions,
                MetricName="ModelLatency",
                Namespace="AWS/SageMaker",
                Statistic="Average",
                Dimensions=[
                    {"Name": "EndpointName", "Value": endpoint_name},
                    {"Name": "VariantName", "Value": variant_name}
                ],
                Period=300,  # 5 minutes
                EvaluationPeriods=2,
                Threshold=threshold_ms,
                ComparisonOperator="GreaterThanThreshold",
                TreatMissingData="notBreaching"
            )
            logger.info(f"✓ Created alarm: {alarm_name}")
        except Exception as e:
            logger.error(f"Error creating latency alarm: {e}")
            raise
    
    def create_invocation_alarm(
        self,
        endpoint_name,
        variant_name="AllTraffic",
        threshold=10,
        sns_topic_arn=None
    ):
        """
        Create alarm for low invocations
        Triggers when invocations drop below threshold (potential endpoint issue)
        """
        alarm_name = f"{endpoint_name}-low-invocations"
        
        alarm_actions = [sns_topic_arn] if sns_topic_arn else []
        
        try:
            self.cloudwatch.put_metric_alarm(
                AlarmName=alarm_name,
                AlarmDescription=f"Alert when {endpoint_name} invocations drop below {threshold}",
                ActionsEnabled=True,
                AlarmActions=alarm_actions,
                MetricName="Invocations",
                Namespace="AWS/SageMaker",
                Statistic="Sum",
                Dimensions=[
                    {"Name": "EndpointName", "Value": endpoint_name},
                    {"Name": "VariantName", "Value": variant_name}
                ],
                Period=300,  # 5 minutes
                EvaluationPeriods=2,
                Threshold=threshold,
                ComparisonOperator="LessThanThreshold",
                TreatMissingData="breaching"  # Treat missing data as alarm
            )
            logger.info(f"✓ Created alarm: {alarm_name}")
        except Exception as e:
            logger.error(f"Error creating invocation alarm: {e}")
            raise
    
    def setup_all_alarms(
        self,
        endpoint_name,
        email=None,
        environment="production"
    ):
        """
        Setup all recommended alarms for an endpoint
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"Setting up CloudWatch alarms for: {endpoint_name}")
        logger.info(f"Environment: {environment}")
        logger.info(f"{'='*60}\n")
        
        # Create SNS topic
        topic_arn = self.create_sns_topic(
            topic_name=f"sagemaker-{environment}-alerts"
        )
        
        # Subscribe email if provided
        if email:
            self.subscribe_email(topic_arn, email)
        
        # Set thresholds based on environment
        if environment == "production":
            error_threshold = 5.0  # 5% error rate
            latency_threshold = 500  # 500ms
            invocation_threshold = 100  # Min 100 invocations per 5 min
        elif environment == "staging":
            error_threshold = 10.0
            latency_threshold = 1000
            invocation_threshold = 10
        else:  # dev
            error_threshold = 20.0
            latency_threshold = 2000
            invocation_threshold = 1
        
        logger.info(f"Alarm thresholds:")
        logger.info(f"  Error rate: {error_threshold}%")
        logger.info(f"  Latency: {latency_threshold}ms")
        logger.info(f"  Min invocations: {invocation_threshold}/5min\n")
        
        # Create alarms
        self.create_error_rate_alarm(
            endpoint_name,
            threshold=error_threshold,
            sns_topic_arn=topic_arn
        )
        
        self.create_latency_alarm(
            endpoint_name,
            threshold_ms=latency_threshold,
            sns_topic_arn=topic_arn
        )
        
        self.create_invocation_alarm(
            endpoint_name,
            threshold=invocation_threshold,
            sns_topic_arn=topic_arn
        )
        
        logger.info(f"\n{'='*60}")
        logger.info("✓ All alarms configured successfully")
        logger.info(f"{'='*60}\n")
        logger.info(f"SNS Topic ARN: {topic_arn}")
        logger.info(f"View alarms: https://console.aws.amazon.com/cloudwatch/home?region={self.region}#alarmsV2:")
    
    def delete_alarms(self, endpoint_name):
        """Delete all alarms for an endpoint"""
        alarm_names = [
            f"{endpoint_name}-high-error-rate",
            f"{endpoint_name}-high-latency",
            f"{endpoint_name}-low-invocations"
        ]
        
        try:
            self.cloudwatch.delete_alarms(AlarmNames=alarm_names)
            logger.info(f"✓ Deleted alarms for {endpoint_name}")
        except Exception as e:
            logger.error(f"Error deleting alarms: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Setup CloudWatch alarms for SageMaker endpoints"
    )
    parser.add_argument(
        "--endpoint-name",
        required=True,
        help="SageMaker endpoint name"
    )
    parser.add_argument(
        "--environment",
        choices=["dev", "staging", "production"],
        default="production",
        help="Environment (affects thresholds)"
    )
    parser.add_argument(
        "--email",
        help="Email address for alarm notifications"
    )
    parser.add_argument(
        "--region",
        default="us-east-1",
        help="AWS region"
    )
    parser.add_argument(
        "--delete",
        action="store_true",
        help="Delete alarms instead of creating"
    )
    
    args = parser.parse_args()
    
    manager = EndpointAlarmsManager(region=args.region)
    
    if args.delete:
        manager.delete_alarms(args.endpoint_name)
    else:
        manager.setup_all_alarms(
            endpoint_name=args.endpoint_name,
            email=args.email,
            environment=args.environment
        )


if __name__ == "__main__":
    main()
