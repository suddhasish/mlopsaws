# =============================================================================
# GENERAL VARIABLES
# =============================================================================

variable "project_name" {
  description = "Name of the MLOps project"
  type        = string
  default     = "mlops-diabetes"
}

variable "environment" {
  description = "Environment name (dev, staging, production)"
  type        = string
  validation {
    condition     = contains(["dev", "staging", "production"], var.environment)
    error_message = "Environment must be dev, staging, or production."
  }
}

variable "region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-east-1"
}

variable "aws_region" {
  description = "AWS region for resources (alias for compatibility)"
  type        = string
  default     = "us-east-1"
}

variable "owner_email" {
  description = "Email of the infrastructure owner"
  type        = string
}

variable "repository_url" {
  description = "GitHub repository URL"
  type        = string
  default     = "https://github.com/your-org/mlops-diabetes"
}

# =============================================================================
# GITHUB ACTIONS OIDC VARIABLES
# =============================================================================

variable "enable_github_oidc" {
  description = "Enable GitHub Actions OIDC integration for CI/CD"
  type        = bool
  default     = false
}

variable "github_org" {
  description = "GitHub organization or username"
  type        = string
  default     = "suddhasish"
}

variable "github_repo" {
  description = "GitHub repository name"
  type        = string
  default     = "mlopsaws"
}

# =============================================================================
# NETWORKING VARIABLES
# =============================================================================

variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "enable_vpc" {
  description = "Whether to create custom VPC (true) or use default VPC (false)"
  type        = bool
  default     = true
}

variable "enable_vpc_endpoints" {
  description = "Whether to create VPC endpoints (cost savings and security)"
  type        = bool
  default     = true
}

variable "availability_zones_count" {
  description = "Number of availability zones to use (for high availability)"
  type        = number
  default     = 2
  validation {
    condition     = var.availability_zones_count >= 2
    error_message = "At least 2 availability zones required for high availability."
  }
}

# =============================================================================
# S3 VARIABLES
# =============================================================================

variable "enable_s3_versioning" {
  description = "Enable versioning on S3 buckets (recommended for production)"
  type        = bool
  default     = true
}

variable "s3_lifecycle_glacier_days" {
  description = "Days before moving old model artifacts to Glacier"
  type        = number
  default     = 90
}

variable "s3_lifecycle_expiration_days" {
  description = "Days before deleting old model artifacts"
  type        = number
  default     = 365
}

# =============================================================================
# SAGEMAKER VARIABLES
# =============================================================================

variable "sagemaker_processing_instance_type" {
  description = "Instance type for SageMaker processing jobs"
  type        = string
  default     = "ml.m5.xlarge"
}

variable "sagemaker_processing_instance_count" {
  description = "Number of instances for processing jobs"
  type        = number
  default     = 1
}

variable "sagemaker_training_instance_type" {
  description = "Instance type for SageMaker training jobs"
  type        = string
  default     = "ml.m5.xlarge"
}

variable "sagemaker_training_instance_count" {
  description = "Number of instances for training jobs"
  type        = number
  default     = 1
}

variable "sagemaker_endpoint_instance_type" {
  description = "Instance type for SageMaker endpoints"
  type        = string
}

variable "sagemaker_endpoint_initial_instance_count" {
  description = "Initial number of endpoint instances"
  type        = number
}

variable "sagemaker_endpoint_min_capacity" {
  description = "Minimum number of endpoint instances for auto-scaling"
  type        = number
}

variable "sagemaker_endpoint_max_capacity" {
  description = "Maximum number of endpoint instances for auto-scaling"
  type        = number
}

variable "enable_sagemaker_spot_instances" {
  description = "Use spot instances for training (up to 90% cost savings)"
  type        = bool
  default     = true
}

variable "model_package_group_name" {
  description = "Name for SageMaker Model Registry package group"
  type        = string
  default     = "diabetes-classification-models"
}

variable "model_approval_status" {
  description = "Default approval status for registered models"
  type        = string
  validation {
    condition     = contains(["Approved", "PendingManualApproval"], var.model_approval_status)
    error_message = "Approval status must be Approved or PendingManualApproval."
  }
}

# =============================================================================
# MONITORING VARIABLES
# =============================================================================

variable "enable_model_monitor" {
  description = "Enable SageMaker Model Monitor for drift detection"
  type        = bool
  default     = true
}

variable "model_monitor_schedule_expression" {
  description = "Cron expression for model monitoring schedule"
  type        = string
  default     = "cron(0 * * * ? *)" # Hourly
}

variable "cloudwatch_log_retention_days" {
  description = "Number of days to retain CloudWatch logs"
  type        = number
}

variable "enable_cloudtrail" {
  description = "Enable CloudTrail for audit logging"
  type        = bool
  default     = true
}

variable "enable_config" {
  description = "Enable AWS Config for compliance monitoring"
  type        = bool
  default     = false # Can be expensive
}

# =============================================================================
# ALERTING VARIABLES
# =============================================================================

variable "alert_email_endpoints" {
  description = "Email addresses for SNS alerts"
  type        = list(string)
  default     = []
}

variable "enable_pagerduty_alerts" {
  description = "Enable PagerDuty integration for critical alerts"
  type        = bool
  default     = false
}

variable "pagerduty_endpoint" {
  description = "PagerDuty integration endpoint URL"
  type        = string
  default     = ""
  sensitive   = true
}

variable "endpoint_latency_threshold_ms" {
  description = "CloudWatch alarm threshold for endpoint latency (milliseconds)"
  type        = number
  default     = 500
}

variable "endpoint_error_rate_threshold" {
  description = "CloudWatch alarm threshold for endpoint error count"
  type        = number
  default     = 10
}

# =============================================================================
# SECURITY VARIABLES
# =============================================================================

variable "enable_kms_encryption" {
  description = "Use KMS for encryption (recommended for production)"
  type        = bool
  default     = true
}

variable "kms_key_rotation" {
  description = "Enable automatic KMS key rotation (every 365 days)"
  type        = bool
  default     = true
}

variable "kms_key_deletion_window" {
  description = "Days before KMS key is permanently deleted (7-30)"
  type        = number
  default     = 30
  validation {
    condition     = var.kms_key_deletion_window >= 7 && var.kms_key_deletion_window <= 30
    error_message = "KMS key deletion window must be between 7 and 30 days."
  }
}

variable "enable_guardduty" {
  description = "Enable GuardDuty for threat detection"
  type        = bool
  default     = false # Additional cost
}

# =============================================================================
# COST OPTIMIZATION VARIABLES
# =============================================================================

variable "enable_model_package_group" {
  description = "Enable SageMaker Model Package Group creation (disable if quota is 0)"
  type        = bool
  default     = true
}

variable "enable_sagemaker_monitoring" {
  description = "Enable SageMaker Model Monitor for data drift and model quality tracking (adds ~$6.50/day if enabled)"
  type        = bool
  default     = false
}

variable "sagemaker_endpoint_name" {
  description = "Name of the SageMaker endpoint to monitor (required if enable_sagemaker_monitoring = true)"
  type        = string
  default     = ""
}

variable "enable_auto_shutdown" {
  description = "Enable auto-shutdown of dev endpoints after business hours"
  type        = bool
  default     = false
}

variable "auto_shutdown_schedule" {
  description = "Cron expression for auto-shutdown (e.g., 7 PM weekdays)"
  type        = string
  default     = "cron(0 19 ? * MON-FRI *)"
}

variable "auto_startup_schedule" {
  description = "Cron expression for auto-startup (e.g., 8 AM weekdays)"
  type        = string
  default     = "cron(0 8 ? * MON-FRI *)"
}

variable "budget_amount" {
  description = "Monthly budget amount in USD"
  type        = number
}

variable "budget_alert_thresholds" {
  description = "Budget alert thresholds (percentage of budget)"
  type        = list(number)
  default     = [50, 80, 100]
}

# =============================================================================
# FEATURE STORE VARIABLES (Optional)
# =============================================================================

variable "enable_feature_store" {
  description = "Enable RDS database for offline feature store"
  type        = bool
  default     = false
}

variable "rds_instance_class" {
  description = "RDS instance class for feature store"
  type        = string
  default     = "db.t3.micro"
}

variable "rds_allocated_storage" {
  description = "RDS allocated storage in GB"
  type        = number
  default     = 20
}

variable "rds_master_password" {
  description = "Master password for RDS (CRITICAL: Use AWS Secrets Manager in production)"
  type        = string
  sensitive   = true
  default     = null
}

# =============================================================================
# TAGGING VARIABLES
# =============================================================================

variable "additional_tags" {
  description = "Additional tags to apply to all resources"
  type        = map(string)
  default     = {}
}
