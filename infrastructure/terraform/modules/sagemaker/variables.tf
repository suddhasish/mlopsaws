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

variable "create_model_package_group" {
  description = "Whether to create SageMaker Model Package Group (requires quota approval if currently 0)"
  type        = bool
  default     = true
}
