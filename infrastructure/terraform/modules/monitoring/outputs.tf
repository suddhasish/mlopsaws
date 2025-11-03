# =============================================================================
# Monitoring Module Outputs
# =============================================================================

output "training_log_group_name" {
  description = "Name of the CloudWatch log group for training jobs"
  value       = aws_cloudwatch_log_group.training_jobs.name
}

output "endpoint_log_group_name" {
  description = "Name of the CloudWatch log group for endpoints"
  value       = aws_cloudwatch_log_group.endpoints.name
}

output "alerts_topic_arn" {
  description = "ARN of the SNS topic for general alerts"
  value       = aws_sns_topic.alerts.arn
}

output "critical_alerts_topic_arn" {
  description = "ARN of the SNS topic for critical alerts"
  value       = aws_sns_topic.critical_alerts.arn
}

output "cloudtrail_name" {
  description = "Name of the CloudTrail"
  value       = var.enable_cloudtrail ? aws_cloudtrail.main[0].name : null
}

output "cloudtrail_arn" {
  description = "ARN of the CloudTrail"
  value       = var.enable_cloudtrail ? aws_cloudtrail.main[0].arn : null
}
