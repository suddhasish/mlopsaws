# =============================================================================
# OUTPUT VALUES - Use these in other configurations or display after apply
# =============================================================================

# =============================================================================
# S3 OUTPUTS
# =============================================================================

output "s3_bucket_name" {
  description = "Name of the ML data S3 bucket"
  value       = module.s3.bucket_name
}

output "s3_bucket_arn" {
  description = "ARN of the ML data S3 bucket"
  value       = module.s3.bucket_arn
}

output "s3_bucket_url" {
  description = "URL of the ML data S3 bucket"
  value       = "s3://${module.s3.bucket_name}"
}

# =============================================================================
# IAM OUTPUTS
# =============================================================================

output "sagemaker_execution_role_arn" {
  description = "ARN of the SageMaker execution role"
  value       = module.iam.sagemaker_execution_role_arn
}

output "sagemaker_execution_role_name" {
  description = "Name of the SageMaker execution role"
  value       = module.iam.sagemaker_execution_role_name
}

output "data_scientist_role_arn" {
  description = "ARN of the data scientist IAM role"
  value       = module.iam.data_scientist_role_arn
}

# =============================================================================
# NETWORKING OUTPUTS
# =============================================================================

output "vpc_id" {
  description = "ID of the VPC (empty if using default VPC)"
  value       = var.enable_vpc ? module.networking[0].vpc_id : ""
}

output "private_subnet_ids" {
  description = "IDs of private subnets for SageMaker"
  value       = var.enable_vpc ? module.networking[0].private_subnet_ids : []
}

output "security_group_id" {
  description = "ID of the SageMaker security group"
  value       = var.enable_vpc ? module.networking[0].security_group_id : ""
}

output "vpc_endpoint_s3_id" {
  description = "ID of the S3 VPC endpoint"
  value       = var.enable_vpc && var.enable_vpc_endpoints ? module.networking[0].vpc_endpoint_s3_id : ""
}

# =============================================================================
# KMS OUTPUTS
# =============================================================================

output "kms_key_id" {
  description = "ID of the KMS encryption key"
  value       = var.enable_kms_encryption ? module.kms[0].kms_key_id : ""
}

output "kms_key_arn" {
  description = "ARN of the KMS encryption key"
  value       = var.enable_kms_encryption ? module.kms[0].kms_key_arn : ""
}

output "kms_key_alias" {
  description = "Alias of the KMS encryption key"
  value       = var.enable_kms_encryption ? module.kms[0].kms_key_alias : ""
}

# =============================================================================
# SAGEMAKER OUTPUTS
# =============================================================================

output "model_package_group_name" {
  description = "Name of the SageMaker Model Registry package group"
  value       = module.sagemaker.model_package_group_name
}

output "model_package_group_arn" {
  description = "ARN of the SageMaker Model Registry package group"
  value       = module.sagemaker.model_package_group_arn
}

# =============================================================================
# MONITORING OUTPUTS
# =============================================================================

output "cloudwatch_log_group_training" {
  description = "CloudWatch log group for SageMaker training jobs"
  value       = module.monitoring.training_log_group_name
}

output "cloudwatch_log_group_endpoints" {
  description = "CloudWatch log group for SageMaker endpoints"
  value       = module.monitoring.endpoint_log_group_name
}

output "sns_topic_alerts_arn" {
  description = "ARN of the SNS topic for alerts"
  value       = module.monitoring.alerts_topic_arn
}

output "sns_topic_critical_arn" {
  description = "ARN of the SNS topic for critical alerts"
  value       = module.monitoring.critical_alerts_topic_arn
}

# =============================================================================
# CLOUDTRAIL OUTPUTS
# =============================================================================

output "cloudtrail_name" {
  description = "Name of the CloudTrail trail"
  value       = var.enable_cloudtrail ? module.monitoring.cloudtrail_name : ""
}

output "cloudtrail_arn" {
  description = "ARN of the CloudTrail trail"
  value       = var.enable_cloudtrail ? module.monitoring.cloudtrail_arn : ""
}

# =============================================================================
# CONFIGURATION OUTPUTS (for use in Python code)
# =============================================================================

output "config_yaml" {
  description = "Configuration values for config.yaml file"
  value = {
    aws = {
      region     = var.region
      account_id = data.aws_caller_identity.current.account_id
    }
    s3 = {
      bucket_name = module.s3.bucket_name
      prefix      = "${var.project_name}-${var.environment}"
    }
    sagemaker = {
      role                = module.iam.sagemaker_execution_role_arn
      processing_instance = var.sagemaker_processing_instance_type
      training_instance   = var.sagemaker_training_instance_type
      endpoint_instance   = var.sagemaker_endpoint_instance_type
      model_package_group = module.sagemaker.model_package_group_name
      use_spot_instances  = var.enable_sagemaker_spot_instances
      vpc_config = var.enable_vpc ? {
        subnets         = module.networking[0].private_subnet_ids
        security_groups = [module.networking[0].sagemaker_security_group_id]
      } : null
    }
    monitoring = {
      log_group_training  = module.monitoring.training_log_group_name
      log_group_endpoints = module.monitoring.endpoint_log_group_name
      sns_topic_arn       = module.monitoring.alerts_topic_arn
    }
    encryption = {
      kms_key_id = var.enable_kms_encryption ? module.kms[0].kms_key_id : null
    }
  }
}

# =============================================================================
# QUICK REFERENCE OUTPUT
# =============================================================================

output "quick_reference" {
  description = "Quick reference for common commands"
  value       = <<-EOT
  
  ╔═══════════════════════════════════════════════════════════════════════════╗
  ║                    🚀 MLOps Infrastructure Deployed                        ║
  ╚═══════════════════════════════════════════════════════════════════════════╝
  
  Environment: ${var.environment}
  Region:      ${var.region}
  Account:     ${data.aws_caller_identity.current.account_id}
  
  📦 S3 Bucket:
     aws s3 ls s3://${module.s3.bucket_name}/
  
  🔐 IAM Role (for SageMaker):
     ${module.iam.sagemaker_execution_role_arn}
  
  🧪 Model Registry:
     aws sagemaker list-model-packages --model-package-group-name ${module.sagemaker.model_package_group_name}
  
  📊 CloudWatch Logs:
     Training Jobs: ${module.monitoring.training_log_group_name}
     Endpoints:     ${module.monitoring.endpoint_log_group_name}
  
  🔔 SNS Alerts:
     ${module.monitoring.alerts_topic_arn}
  
  📝 Next Steps:
     1. Update config/config.yaml with the output values above
     2. Run: cd ../..
     3. Run: python pipelines/training_pipeline.py --environment ${var.environment} --execute
  
  💰 Estimated Monthly Cost: ${var.budget_amount} USD
  
  EOT
}

# =============================================================================
# TERRAFORM STATE INFO
# =============================================================================

output "terraform_state_info" {
  description = "Information about Terraform state management"
  value = {
    workspace = terraform.workspace
    backend   = "s3" # Remind users to configure backend
    message   = "Remember to configure S3 backend for team collaboration"
  }
}
