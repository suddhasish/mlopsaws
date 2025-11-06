# =============================================================================
# S3 MODULE - Secure storage for ML data, models, and artifacts
# =============================================================================

# Main ML data bucket
resource "aws_s3_bucket" "ml_data" {
  bucket = "${var.project_name}-${var.environment}-${data.aws_caller_identity.current.account_id}"

  tags = merge(
    var.additional_tags,
    {
      Name        = "${var.project_name}-ml-data-${var.environment}"
      Purpose     = "ML data storage"
      Environment = var.environment
    }
  )
}

# Enable versioning (track changes to datasets and models)
resource "aws_s3_bucket_versioning" "ml_data" {
  bucket = aws_s3_bucket.ml_data.id

  versioning_configuration {
    status = var.enable_versioning ? "Enabled" : "Disabled"
  }
}

# Enable server-side encryption
resource "aws_s3_bucket_server_side_encryption_configuration" "ml_data" {
  bucket = aws_s3_bucket.ml_data.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = var.kms_key_id != null ? "aws:kms" : "AES256"
      kms_master_key_id = var.kms_key_id
    }
    bucket_key_enabled = var.kms_key_id != null ? true : false
  }
}

# Block all public access (CRITICAL security measure)
resource "aws_s3_bucket_public_access_block" "ml_data" {
  bucket = aws_s3_bucket.ml_data.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Lifecycle policy - archive old data to reduce costs
resource "aws_s3_bucket_lifecycle_configuration" "ml_data" {
  bucket = aws_s3_bucket.ml_data.id

  # Archive old model artifacts to Glacier
  rule {
    id     = "archive-old-models"
    status = "Enabled"

    filter {
      prefix = "models/"
    }

    transition {
      days          = var.glacier_transition_days
      storage_class = "GLACIER"
    }

    expiration {
      days = var.expiration_days
    }

    noncurrent_version_transition {
      noncurrent_days = 30
      storage_class   = "GLACIER"
    }

    noncurrent_version_expiration {
      noncurrent_days = 90
    }
  }

  # Delete old processing job outputs
  rule {
    id     = "cleanup-processing-outputs"
    status = "Enabled"

    filter {
      prefix = "processing/"
    }

    expiration {
      days = 30 # Processing outputs are temporary
    }
  }

  # Archive old monitoring data
  rule {
    id     = "archive-monitoring-data"
    status = "Enabled"

    filter {
      prefix = "monitoring/"
    }

    transition {
      days          = 30
      storage_class = "STANDARD_IA" # Infrequent Access
    }

    transition {
      days          = 90
      storage_class = "GLACIER"
    }

    expiration {
      days = 180
    }
  }
}

# Bucket policy - grant SageMaker and GitHub Actions access
resource "aws_s3_bucket_policy" "ml_data" {
  bucket = aws_s3_bucket.ml_data.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = concat(
      [
        {
          Sid    = "AllowSageMakerAccess"
          Effect = "Allow"
          Principal = {
            AWS = var.sagemaker_execution_role_arn
          }
          Action = [
            "s3:GetObject",
            "s3:PutObject",
            "s3:DeleteObject",
            "s3:ListBucket",
            "s3:GetBucketLocation"
          ]
          Resource = [
            aws_s3_bucket.ml_data.arn,
            "${aws_s3_bucket.ml_data.arn}/*"
          ]
        }
      ],
      var.github_actions_role_arn != null ? [
        {
          Sid    = "AllowGitHubActionsAccess"
          Effect = "Allow"
          Principal = {
            AWS = var.github_actions_role_arn
          }
          Action = [
            "s3:GetObject",
            "s3:PutObject",
            "s3:DeleteObject",
            "s3:ListBucket",
            "s3:GetBucketLocation"
          ]
          Resource = [
            aws_s3_bucket.ml_data.arn,
            "${aws_s3_bucket.ml_data.arn}/*"
          ]
        }
      ] : [],
      [
        {
          Sid       = "DenyInsecureTransport"
          Effect    = "Deny"
          Principal = "*"
          Action    = "s3:*"
          Resource = [
            aws_s3_bucket.ml_data.arn,
            "${aws_s3_bucket.ml_data.arn}/*"
          ]
          Condition = {
            Bool = {
              "aws:SecureTransport" = "false"
            }
          }
        }
      ]
    )
  })
}

# Enable bucket logging (audit S3 access)
resource "aws_s3_bucket" "access_logs" {
  count  = var.enable_access_logging ? 1 : 0
  bucket = "${var.project_name}-access-logs-${var.environment}-${data.aws_caller_identity.current.account_id}"

  tags = {
    Name    = "${var.project_name}-access-logs-${var.environment}"
    Purpose = "S3 access logs"
  }
}

resource "aws_s3_bucket_public_access_block" "access_logs" {
  count  = var.enable_access_logging ? 1 : 0
  bucket = aws_s3_bucket.access_logs[0].id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_logging" "ml_data" {
  count  = var.enable_access_logging ? 1 : 0
  bucket = aws_s3_bucket.ml_data.id

  target_bucket = aws_s3_bucket.access_logs[0].id
  target_prefix = "s3-access-logs/"
}

# Intelligent-Tiering for automatic cost optimization
resource "aws_s3_bucket_intelligent_tiering_configuration" "ml_data" {
  count  = var.enable_intelligent_tiering ? 1 : 0
  bucket = aws_s3_bucket.ml_data.id
  name   = "EntireBucket"

  tiering {
    access_tier = "DEEP_ARCHIVE_ACCESS"
    days        = 180 # Move to Deep Archive after 180 days of no access
  }

  tiering {
    access_tier = "ARCHIVE_ACCESS"
    days        = 90 # Move to Archive after 90 days of no access
  }
}

# CORS configuration (if using from web applications)
resource "aws_s3_bucket_cors_configuration" "ml_data" {
  count  = var.enable_cors ? 1 : 0
  bucket = aws_s3_bucket.ml_data.id

  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["GET", "PUT", "POST"]
    allowed_origins = var.cors_allowed_origins
    expose_headers  = ["ETag"]
    max_age_seconds = 3000
  }
}

# Object lock for compliance (prevents deletion for retention period)
resource "aws_s3_bucket_object_lock_configuration" "ml_data" {
  count  = var.enable_object_lock ? 1 : 0
  bucket = aws_s3_bucket.ml_data.id

  rule {
    default_retention {
      mode = "GOVERNANCE" # COMPLIANCE mode prevents deletion by anyone
      days = 365
    }
  }
}

# =============================================================================
# DATA SOURCES
# =============================================================================

data "aws_caller_identity" "current" {}

# =============================================================================
# OUTPUTS
# =============================================================================

output "bucket_name" {
  description = "Name of the S3 bucket"
  value       = aws_s3_bucket.ml_data.id
}

output "bucket_arn" {
  description = "ARN of the S3 bucket"
  value       = aws_s3_bucket.ml_data.arn
}

output "bucket_domain_name" {
  description = "Domain name of the S3 bucket"
  value       = aws_s3_bucket.ml_data.bucket_domain_name
}

output "bucket_regional_domain_name" {
  description = "Regional domain name of the S3 bucket"
  value       = aws_s3_bucket.ml_data.bucket_regional_domain_name
}

output "access_logs_bucket_name" {
  description = "Name of the access logs bucket"
  value       = var.enable_access_logging ? aws_s3_bucket.access_logs[0].id : null
}
