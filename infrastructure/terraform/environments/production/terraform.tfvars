# =============================================================================
# PRODUCTION ENVIRONMENT CONFIGURATION
# Maximum security, reliability, and performance
# =============================================================================

# General
project_name   = "mlops-diabetes"
environment    = "production"
region         = "us-east-1"
owner_email    = "ml-ops@company.com" # CHANGE THIS
repository_url = "https://github.com/your-org/mlops-diabetes" # CHANGE THIS

# Networking - Fully isolated VPC
enable_vpc               = true
vpc_cidr                 = "10.0.0.0/16"
availability_zones_count = 2 # Multi-AZ for high availability
enable_vpc_endpoints     = true # Required for security

# S3
enable_s3_versioning         = true # Required for audit trail
s3_lifecycle_glacier_days    = 90
s3_lifecycle_expiration_days = 365

# SageMaker - Production-grade instances
sagemaker_processing_instance_type  = "ml.m5.2xlarge" # Larger for production
sagemaker_processing_instance_count = 1

sagemaker_training_instance_type  = "ml.m5.2xlarge"
sagemaker_training_instance_count = 2 # Distributed training

sagemaker_endpoint_instance_type          = "ml.m5.xlarge" # Production grade
sagemaker_endpoint_initial_instance_count = 2 # High availability
sagemaker_endpoint_min_capacity           = 2 # Always 2+ for HA
sagemaker_endpoint_max_capacity           = 10 # Handle traffic spikes

enable_sagemaker_spot_instances = false # Reliability over cost
model_approval_status           = "PendingManualApproval" # STRICT approval required

# Monitoring - Comprehensive
enable_model_monitor              = true
model_monitor_schedule_expression = "cron(0 * * * ? *)" # Hourly
cloudwatch_log_retention_days     = 90 # Longer retention for compliance

enable_cloudtrail = true # Required for audit
enable_config     = true # Compliance monitoring

# Alerting - Multi-channel
alert_email_endpoints = [
  "ml-ops@company.com",
  "ml-lead@company.com"
] # CHANGE THIS
enable_pagerduty_alerts = true
pagerduty_endpoint      = "PAGERDUTY_INTEGRATION_URL" # CHANGE THIS

endpoint_latency_threshold_ms = 300 # Strict SLA
endpoint_error_rate_threshold = 5 # Low tolerance

# Security - Maximum
enable_kms_encryption   = true # Required
kms_key_rotation        = true # Automatic rotation
kms_key_deletion_window = 30
enable_guardduty        = true # Threat detection

# Cost Optimization
enable_auto_shutdown = false # Never shutdown production

budget_amount           = 1500 # $1500/month budget for production
budget_alert_thresholds = [50, 75, 90, 100]

# Feature Store - Production database
enable_feature_store  = false # Enable if needed
rds_instance_class    = "db.r5.large" # Production-grade
rds_allocated_storage = 100

# Additional Tags
additional_tags = {
  Team           = "ML-Engineering"
  CostCenter     = "ML-Production"
  Environment    = "production"
  Terraform      = "true"
  Criticality    = "High"
  Compliance     = "Required"
  BackupRequired = "true"
}
