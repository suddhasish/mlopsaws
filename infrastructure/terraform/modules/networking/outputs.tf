# =============================================================================
# Networking Module Outputs
# =============================================================================

output "vpc_id" {
  description = "ID of the VPC"
  value       = aws_vpc.main.id
}

output "vpc_cidr" {
  description = "CIDR block of the VPC"
  value       = aws_vpc.main.cidr_block
}

output "private_subnet_ids" {
  description = "IDs of private subnets"
  value       = aws_subnet.private[*].id
}

output "private_subnet_cidrs" {
  description = "CIDR blocks of private subnets"
  value       = aws_subnet.private[*].cidr_block
}

output "security_group_id" {
  description = "ID of the SageMaker security group"
  value       = aws_security_group.sagemaker.id
}

output "vpc_endpoint_s3_id" {
  description = "ID of the S3 VPC endpoint"
  value       = var.enable_vpc_endpoints ? aws_vpc_endpoint.s3[0].id : null
}

output "vpc_endpoint_sagemaker_api_id" {
  description = "ID of the SageMaker API VPC endpoint"
  value       = var.enable_vpc_endpoints ? aws_vpc_endpoint.sagemaker_api[0].id : null
}

output "vpc_endpoint_sagemaker_runtime_id" {
  description = "ID of the SageMaker Runtime VPC endpoint"
  value       = var.enable_vpc_endpoints ? aws_vpc_endpoint.sagemaker_runtime[0].id : null
}
