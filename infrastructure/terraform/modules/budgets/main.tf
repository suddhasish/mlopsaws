# =============================================================================
# Budgets Module - AWS Cost Control
# =============================================================================

# -----------------------------------------------------------------------------
# AWS Budget for Cost Control
# -----------------------------------------------------------------------------
resource "aws_budgets_budget" "monthly" {
  name              = "${var.project_name}-${var.environment}-budget"
  budget_type       = "COST"
  limit_amount      = var.budget_amount
  limit_unit        = "USD"
  time_unit         = "MONTHLY"
  time_period_start = "2024-01-01_00:00"

  cost_filter {
    name = "TagKeyValue"
    values = [
      "user:Environment$${var.environment}",
      "user:Project$${var.project_name}"
    ]
  }

  # Dynamic notification blocks for each threshold
  dynamic "notification" {
    for_each = var.budget_alert_thresholds
    content {
      comparison_operator        = "GREATER_THAN"
      threshold                  = notification.value
      threshold_type             = notification.value <= 100 ? "PERCENTAGE" : "PERCENTAGE"
      notification_type          = notification.value <= 80 ? "FORECASTED" : "ACTUAL"
      subscriber_email_addresses = var.budget_notification_emails
    }
  }

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-budget-${var.environment}"
    }
  )
}
