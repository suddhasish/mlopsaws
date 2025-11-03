# =============================================================================
# Auto Shutdown Module Outputs
# =============================================================================

output "shutdown_lambda_arn" {
  description = "ARN of the shutdown Lambda function"
  value       = aws_lambda_function.shutdown.arn
}

output "startup_lambda_arn" {
  description = "ARN of the startup Lambda function"
  value       = aws_lambda_function.startup.arn
}

output "shutdown_schedule" {
  description = "Shutdown schedule expression"
  value       = var.shutdown_schedule
}

output "startup_schedule" {
  description = "Startup schedule expression"
  value       = var.startup_schedule
}
