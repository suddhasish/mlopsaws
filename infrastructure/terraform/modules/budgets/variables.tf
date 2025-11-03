# =============================================================================
# Budgets Module Variables
# =============================================================================

variable "project_name" {
  description = "Name of the project"
  type        = string
}

variable "environment" {
  description = "Environment name (dev, staging, production)"
  type        = string
}

variable "budget_amount" {
  description = "Monthly budget limit in USD"
  type        = number
}

variable "budget_alert_thresholds" {
  description = "List of percentage thresholds for budget alerts"
  type        = list(number)
  default     = [50, 80, 100, 120]
}

variable "budget_notification_emails" {
  description = "List of email addresses for budget notifications"
  type        = list(string)
}

variable "tags" {
  description = "Common tags to apply to all resources"
  type        = map(string)
  default     = {}
}
