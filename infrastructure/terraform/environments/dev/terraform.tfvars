# =============================================================================
# DEV ENVIRONMENT CONFIGURATION
# Optimized for cost savings and rapid iteration
# =============================================================================

# General
project_name   = "mlops-diabetes"
environment    = "dev"
region         = "us-east-1"
owner_email    = "your-email@company.com"  # CHANGE THIS
repository_url = "https://github.com/your-org/mlops-diabetes"  # CHANGE THIS

# Networking - Use default VPC for dev (simplest setup)
enable_vpc          = false  # Set to true for production-like testing
enable_vpc_endpoints = false  # Set to true to test VPC endpoints

# S3
enable_s3_versioning       = false  # Save costs in dev
s3_lifecycle_glacier_days  = 30    # Quick archival in dev
s3_lifecycle_expiration_days = 90   # Delete old data faster

# SageMaker - Small instances for dev
sagemaker_processing_instance_type = "ml.t3.medium"  # Cheapest option
sagemaker_processing_instance_count = 1

sagemaker_training_instance_type = "ml.m5.large"  # Smaller than prod
sagemaker_training_instance_count = 1

sagemaker_endpoint_instance_type = "ml.t2.medium"  # Cheapest endpoint
sagemaker_endpoint_initial_instance_count = 1
sagemaker_endpoint_min_capacity = 1
sagemaker_endpoint_max_capacity = 2

enable_sagemaker_spot_instances = true  # 90% cost savings
model_approval_status = "Approved"  # Auto-approve in dev

# Monitoring
enable_model_monitor = false  # Optional in dev
model_monitor_schedule_expression = "cron(0 */12 * * ? *)"  # Every 12 hours
cloudwatch_log_retention_days = 7  # Short retention in dev

enable_cloudtrail = false  # Not needed in dev
enable_config = false

# Alerting - Minimal for dev
alert_email_endpoints = []  # No alerts in dev
enable_pagerduty_alerts = false

endpoint_latency_threshold_ms = 1000  # Relaxed threshold
endpoint_error_rate_threshold = 50

# Security - Simplified for dev
enable_kms_encryption = false  # Use AES256 to save costs
kms_key_rotation = false
enable_guardduty = false

# Cost Optimization
enable_auto_shutdown = true  # Save money overnight
auto_shutdown_schedule = "cron(0 19 ? * MON-FRI *)"  # 7 PM weekdays
auto_startup_schedule = "cron(0 8 ? * MON-FRI *)"   # 8 AM weekdays

budget_amount = 100  # $100/month budget for dev
budget_alert_thresholds = [80, 100]  # Alert at 80% and 100%

# Feature Store - Disabled for dev
enable_feature_store = false

# Additional Tags
additional_tags = {
  Team        = "ML-Engineering"
  CostCenter  = "ML-Dev"
  AutoShutdown = "true"
  Terraform   = "true"
}
