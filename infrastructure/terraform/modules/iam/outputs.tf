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
