# =============================================================================
# SageMaker Module Outputs
# =============================================================================

output "model_package_group_name" {
  description = "Name of the SageMaker Model Package Group"
  value       = var.create_model_package_group ? aws_sagemaker_model_package_group.main[0].model_package_group_name : null
}

output "model_package_group_arn" {
  description = "ARN of the SageMaker Model Package Group"
  value       = var.create_model_package_group ? aws_sagemaker_model_package_group.main[0].arn : null
}
