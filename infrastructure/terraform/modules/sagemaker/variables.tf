# =============================================================================
# SageMaker Module Variables
# =============================================================================

variable "project_name" {
  description = "Name of the project"
  type        = string
}

variable "environment" {
  description = "Environment name (dev, staging, production)"
  type        = string
}

variable "tags" {
  description = "Common tags to apply to all resources"
  type        = map(string)
  default     = {}
}

variable "enable_model_package_group" {
  description = "Whether to create SageMaker Model Package Group (requires quota approval if currently 0)"
  type        = bool
  default     = true
}

variable "enable_monitoring" {
  description = "Enable SageMaker Model Monitor and CloudWatch alarms for drift detection and performance tracking"
  type        = bool
  default     = false
}

variable "sagemaker_execution_role_arn" {
  description = "ARN of the SageMaker execution role"
  type        = string
  default     = ""
}

variable "bucket_name" {
  description = "S3 bucket name for monitoring data"
  type        = string
  default     = ""
}

variable "endpoint_name" {
  description = "SageMaker endpoint name to monitor (required if enable_monitoring = true)"
  type        = string
  default     = ""
}

variable "aws_region" {
  description = "AWS region for SageMaker Model Monitor container images"
  type        = string
  default     = "us-east-1"
}

variable "sns_topic_arns" {
  description = "List of SNS topic ARNs for CloudWatch alarm notifications"
  type        = list(string)
  default     = []
}

