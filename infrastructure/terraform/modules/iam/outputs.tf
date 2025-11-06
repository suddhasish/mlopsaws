# =============================================================================
# IAM Module Outputs
# =============================================================================

output "sagemaker_execution_role_arn" {
  description = "ARN of the SageMaker execution role"
  value       = aws_iam_role.sagemaker_execution.arn
}

output "sagemaker_execution_role_name" {
  description = "Name of the SageMaker execution role"
  value       = aws_iam_role.sagemaker_execution.name
}

output "data_scientist_role_arn" {
  description = "ARN of the data scientist role"
  value       = aws_iam_role.data_scientist.arn
}

output "data_scientist_role_name" {
  description = "Name of the data scientist role"
  value       = aws_iam_role.data_scientist.name
}

# =============================================================================
# GitHub Actions OIDC Outputs
# =============================================================================

output "github_actions_role_arn" {
  description = "ARN of the GitHub Actions IAM role"
  value       = var.enable_github_oidc ? aws_iam_role.github_actions[0].arn : null
}

output "github_actions_role_name" {
  description = "Name of the GitHub Actions IAM role"
  value       = var.enable_github_oidc ? aws_iam_role.github_actions[0].name : null
}

output "oidc_provider_arn" {
  description = "ARN of the GitHub OIDC provider"
  value       = var.enable_github_oidc ? aws_iam_openid_connect_provider.github_actions[0].arn : null
}
