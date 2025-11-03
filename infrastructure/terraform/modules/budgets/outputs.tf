# =============================================================================
# Budgets Module Outputs
# =============================================================================

output "budget_name" {
  description = "Name of the AWS Budget"
  value       = aws_budgets_budget.monthly.name
}

output "budget_arn" {
  description = "ARN of the AWS Budget"
  value       = aws_budgets_budget.monthly.arn
}

output "budget_amount" {
  description = "Budget limit amount"
  value       = var.budget_amount
}
