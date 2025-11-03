# =============================================================================
# Auto Shutdown Module Variables
# =============================================================================

variable "project_name" {
  description = "Name of the project"
  type        = string
}

variable "environment" {
  description = "Environment name (dev, staging, production)"
  type        = string
}

variable "shutdown_schedule" {
  description = "Cron expression for shutdown schedule (e.g., 'cron(0 19 ? * MON-FRI *)')"
  type        = string
  default     = "cron(0 19 ? * MON-FRI *)" # 7 PM weekdays
}

variable "startup_schedule" {
  description = "Cron expression for startup schedule (e.g., 'cron(0 8 ? * MON-FRI *)')"
  type        = string
  default     = "cron(0 8 ? * MON-FRI *)" # 8 AM weekdays
}

variable "tags" {
  description = "Common tags to apply to all resources"
  type        = map(string)
  default     = {}
}
