# =============================================================================
# STAGING ENVIRONMENT CONFIGURATION
# Production-like configuration for pre-production testing
# =============================================================================

# General
project_name   = "mlops-diabetes"
environment    = "staging"
region         = "us-east-1"
owner_email    = "your-email@company.com"  # CHANGE THIS
repository_url = "https://github.com/your-org/mlops-diabetes"  # CHANGE THIS

# Networking - Custom VPC for security
enable_vpc          = true
vpc_cidr            = "10.0.0.0/16"
availability_zones_count = 2
enable_vpc_endpoints = true  # Cost savings and security

# S3
enable_s3_versioning       = true  # Track dataset changes
s3_lifecycle_glacier_days  = 90
s3_lifecycle_expiration_days = 365

# SageMaker - Production-like instances
sagemaker_processing_instance_type = "ml.m5.xlarge"
sagemaker_processing_instance_count = 1

sagemaker_training_instance_type = "ml.m5.xlarge"
sagemaker_training_instance_count = 1

sagemaker_endpoint_instance_type = "ml.m5.large"
sagemaker_endpoint_initial_instance_count = 1
sagemaker_endpoint_min_capacity = 1
sagemaker_endpoint_max_capacity = 3

enable_sagemaker_spot_instances = true  # Still use spot for cost savings
model_approval_status = "PendingManualApproval"  # Manual approval required

# Monitoring
enable_model_monitor = true
model_monitor_schedule_expression = "cron(0 */6 * * ? *)"  # Every 6 hours
cloudwatch_log_retention_days = 30

enable_cloudtrail = true  # Enable audit logging
enable_config = false  # Can be enabled if needed

# Alerting
alert_email_endpoints = ["ml-team@company.com"]  # CHANGE THIS
enable_pagerduty_alerts = false

endpoint_latency_threshold_ms = 500
endpoint_error_rate_threshold = 10

# Security - Enhanced
enable_kms_encryption = true  # Encrypt with KMS
kms_key_rotation = true
kms_key_deletion_window = 30
enable_guardduty = false  # Can be enabled if needed

# Cost Optimization
enable_auto_shutdown = false  # Keep staging running 24/7

budget_amount = 300  # $300/month budget for staging
budget_alert_thresholds = [50, 80, 100]

# Feature Store - Optional
enable_feature_store = false
rds_instance_class = "db.t3.small"
rds_allocated_storage = 50

# Additional Tags
additional_tags = {
  Team        = "ML-Engineering"
  CostCenter  = "ML-Staging"
  Environment = "staging"
  Terraform   = "true"
  Criticality = "Medium"
}
