# MLOps Infrastructure - Complete Terraform Modules
# This file orchestrates all infrastructure components

# =============================================================================
# S3 MODULE - Data storage
# =============================================================================

module "s3" {
  source = "./modules/s3"

  project_name                 = var.project_name
  environment                  = var.environment
  enable_versioning            = var.enable_s3_versioning
  kms_key_id                   = var.enable_kms_encryption ? module.kms[0].kms_key_id : null
  sagemaker_execution_role_arn = module.iam.sagemaker_execution_role_arn
  glacier_transition_days      = var.s3_lifecycle_glacier_days
  expiration_days              = var.s3_lifecycle_expiration_days
  enable_access_logging        = var.environment == "production" ? true : false
  enable_intelligent_tiering   = var.environment == "production" ? true : false
  additional_tags              = var.additional_tags
}

# =============================================================================
# IAM MODULE - Roles and policies
# =============================================================================

module "iam" {
  source = "./modules/iam"

  project_name  = var.project_name
  environment   = var.environment
  s3_bucket_arn = module.s3.bucket_arn
  kms_key_arn   = var.enable_kms_encryption ? module.kms[0].kms_key_arn : null
  tags = merge(
    {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "Terraform"
    },
    var.additional_tags
  )
}

# =============================================================================
# KMS MODULE - Encryption keys
# =============================================================================

module "kms" {
  count  = var.enable_kms_encryption ? 1 : 0
  source = "./modules/kms"

  project_name            = var.project_name
  environment             = var.environment
  sagemaker_role_arn      = module.iam.sagemaker_execution_role_arn
  enable_key_rotation     = var.kms_key_rotation
  deletion_window_in_days = var.kms_key_deletion_window
  tags = merge(
    {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "Terraform"
    },
    var.additional_tags
  )
}

# =============================================================================
# NETWORKING MODULE - VPC, subnets, security groups
# =============================================================================

module "networking" {
  count  = var.enable_vpc ? 1 : 0
  source = "./modules/networking"

  project_name             = var.project_name
  environment              = var.environment
  vpc_cidr                 = var.vpc_cidr
  availability_zones_count = var.availability_zones_count
  enable_vpc_endpoints     = var.enable_vpc_endpoints
  tags = merge(
    {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "Terraform"
    },
    var.additional_tags
  )
}

# =============================================================================
# SAGEMAKER MODULE - Model Registry
# =============================================================================

module "sagemaker" {
  source = "./modules/sagemaker"

  project_name = var.project_name
  environment  = var.environment
  tags = merge(
    {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "Terraform"
    },
    var.additional_tags
  )
}

# =============================================================================
# MONITORING MODULE - CloudWatch, SNS, CloudTrail
# =============================================================================

module "monitoring" {
  source = "./modules/monitoring"

  project_name                  = var.project_name
  environment                   = var.environment
  log_retention_days            = var.cloudwatch_log_retention_days
  enable_cloudtrail             = var.enable_cloudtrail
  alert_email_endpoints         = var.alert_email_endpoints
  pagerduty_endpoint            = var.enable_pagerduty_alerts ? var.pagerduty_endpoint : null
  enable_alarms                 = var.environment != "dev"
  endpoint_latency_threshold_ms = var.endpoint_latency_threshold_ms
  endpoint_error_threshold      = var.endpoint_error_rate_threshold
  kms_key_arn                   = var.enable_kms_encryption ? module.kms[0].kms_key_arn : null
  s3_data_bucket_arn            = module.s3.bucket_arn
  tags = merge(
    {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "Terraform"
    },
    var.additional_tags
  )
}

# =============================================================================
# BUDGETS MODULE - Cost control
# =============================================================================

module "budgets" {
  source = "./modules/budgets"

  project_name               = var.project_name
  environment                = var.environment
  budget_amount              = var.budget_amount
  budget_alert_thresholds    = var.budget_alert_thresholds
  budget_notification_emails = concat([var.owner_email], var.alert_email_endpoints)
  tags = merge(
    {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "Terraform"
    },
    var.additional_tags
  )
}

# =============================================================================
# AUTO SHUTDOWN MODULE - Cost optimization for dev
# =============================================================================

module "auto_shutdown" {
  count  = var.enable_auto_shutdown ? 1 : 0
  source = "./modules/auto_shutdown"

  project_name      = var.project_name
  environment       = var.environment
  shutdown_schedule = var.auto_shutdown_schedule
  startup_schedule  = var.auto_startup_schedule
  tags = merge(
    {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "Terraform"
      Purpose     = "CostOptimization"
    },
    var.additional_tags
  )
}

# =============================================================================
# FEATURE STORE MODULE - Optional RDS database
# =============================================================================

module "feature_store" {
  count  = var.enable_feature_store ? 1 : 0
  source = "./modules/feature_store"

  project_name                = var.project_name
  environment                 = var.environment
  vpc_id                      = var.enable_vpc ? module.networking[0].vpc_id : null
  subnet_ids                  = var.enable_vpc ? module.networking[0].private_subnet_ids : []
  sagemaker_security_group_id = var.enable_vpc ? module.networking[0].security_group_id : null
  instance_class              = var.rds_instance_class
  allocated_storage           = var.rds_allocated_storage
  kms_key_arn                 = var.enable_kms_encryption ? module.kms[0].kms_key_arn : null
  master_password             = var.rds_master_password
  tags = merge(
    {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "Terraform"
    },
    var.additional_tags
  )
}
