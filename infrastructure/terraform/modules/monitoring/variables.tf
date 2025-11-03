# =============================================================================
# Monitoring Module Variables
# =============================================================================

variable "project_name" {
  description = "Name of the project"
  type        = string
}

variable "environment" {
  description = "Environment name (dev, staging, production)"
  type        = string
}

variable "log_retention_days" {
  description = "Number of days to retain CloudWatch logs"
  type        = number
  default     = 7
}

variable "kms_key_arn" {
  description = "ARN of the KMS key for encryption (optional)"
  type        = string
  default     = null
}

variable "alert_email_endpoints" {
  description = "List of email addresses for SNS alerts"
  type        = list(string)
  default     = []
}

variable "pagerduty_endpoint" {
  description = "PagerDuty HTTPS endpoint for critical alerts (optional)"
  type        = string
  default     = null
}

variable "enable_alarms" {
  description = "Enable CloudWatch alarms"
  type        = bool
  default     = true
}

variable "endpoint_latency_threshold_ms" {
  description = "Threshold for endpoint latency alarm in milliseconds"
  type        = number
  default     = 500
}

variable "endpoint_error_threshold" {
  description = "Threshold for endpoint error count"
  type        = number
  default     = 10
}

variable "enable_cloudtrail" {
  description = "Enable CloudTrail for audit logging"
  type        = bool
  default     = true
}

variable "s3_data_bucket_arn" {
  description = "ARN of the S3 data bucket to monitor with CloudTrail"
  type        = string
}

variable "tags" {
  description = "Common tags to apply to all resources"
  type        = map(string)
  default     = {}
}
