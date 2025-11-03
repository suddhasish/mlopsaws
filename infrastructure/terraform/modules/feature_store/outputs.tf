# =============================================================================
# Feature Store Module Outputs
# =============================================================================

output "rds_endpoint" {
  description = "RDS instance endpoint"
  value       = aws_db_instance.feature_store.endpoint
}

output "rds_instance_id" {
  description = "RDS instance ID"
  value       = aws_db_instance.feature_store.id
}

output "rds_arn" {
  description = "ARN of the RDS instance"
  value       = aws_db_instance.feature_store.arn
}

output "database_name" {
  description = "Name of the database"
  value       = aws_db_instance.feature_store.db_name
}

output "master_username" {
  description = "Master username"
  value       = aws_db_instance.feature_store.username
  sensitive   = true
}
