variable "project_name" {
  description = "Name of the project"
  type        = string
}

variable "environment" {
  description = "Environment name (dev, staging, production)"
  type        = string
}

variable "enable_versioning" {
  description = "Enable S3 bucket versioning"
  type        = bool
  default     = true
}

variable "kms_key_id" {
  description = "KMS key ID for encryption (null for AES256)"
  type        = string
  default     = null
}

variable "sagemaker_execution_role_arn" {
  description = "ARN of the SageMaker execution role"
  type        = string
}

variable "glacier_transition_days" {
  description = "Days before transitioning to Glacier"
  type        = number
  default     = 90
}

variable "expiration_days" {
  description = "Days before expiring objects"
  type        = number
  default     = 365
}

variable "enable_access_logging" {
  description = "Enable S3 access logging"
  type        = bool
  default     = false
}

variable "enable_intelligent_tiering" {
  description = "Enable S3 Intelligent-Tiering"
  type        = bool
  default     = false
}

variable "enable_cors" {
  description = "Enable CORS configuration"
  type        = bool
  default     = false
}

variable "cors_allowed_origins" {
  description = "Allowed origins for CORS"
  type        = list(string)
  default     = []
}

variable "enable_object_lock" {
  description = "Enable S3 Object Lock for compliance"
  type        = bool
  default     = false
}

variable "additional_tags" {
  description = "Additional tags"
  type        = map(string)
  default     = {}
}

variable "github_actions_role_arn" {
  description = "ARN of the GitHub Actions IAM role (optional)"
  type        = string
  default     = null
}
