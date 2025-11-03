# =============================================================================
# IAM Module Variables
# =============================================================================

variable "project_name" {
  description = "Name of the project"
  type        = string
}

variable "environment" {
  description = "Environment name (dev, staging, production)"
  type        = string
}

variable "s3_bucket_arn" {
  description = "ARN of the S3 bucket for SageMaker access"
  type        = string
}

variable "kms_key_arn" {
  description = "ARN of the KMS key for encryption (optional)"
  type        = string
  default     = null
}

variable "tags" {
  description = "Common tags to apply to all resources"
  type        = map(string)
  default     = {}
}
