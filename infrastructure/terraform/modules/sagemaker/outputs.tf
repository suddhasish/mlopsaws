# =============================================================================
# SageMaker Module Outputs
# =============================================================================

output "model_package_group_name" {
  description = "Name of the SageMaker Model Package Group"
  value       = try(aws_sagemaker_model_package_group.main[0].model_package_group_name, null)
}

output "model_package_group_arn" {
  description = "ARN of the SageMaker Model Package Group"
  value       = try(aws_sagemaker_model_package_group.main[0].arn, null)
}

output "data_quality_job_definition_name" {
  description = "Name of the Data Quality Monitoring Job Definition"
  value       = try(aws_sagemaker_data_quality_job_definition.drift_monitor[0].name, null)
}

output "model_quality_job_definition_name" {
  description = "Name of the Model Quality Monitoring Job Definition"
  value       = try(aws_sagemaker_model_quality_job_definition.model_monitor[0].name, null)
}

output "monitoring_enabled" {
  description = "Whether monitoring is enabled"
  value       = var.enable_monitoring
}

output "cloudwatch_alarms" {
  description = "CloudWatch alarm names for model monitoring"
  value = var.enable_monitoring ? {
    model_errors      = try(aws_cloudwatch_metric_alarm.model_invocation_errors[0].alarm_name, null)
    model_latency     = try(aws_cloudwatch_metric_alarm.model_latency[0].alarm_name, null)
    invocations_high  = try(aws_cloudwatch_metric_alarm.invocations_high[0].alarm_name, null)
  } : {}
}

