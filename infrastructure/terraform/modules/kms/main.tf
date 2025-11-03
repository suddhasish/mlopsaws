# =============================================================================
# KMS Module - Encryption Keys
# =============================================================================

# -----------------------------------------------------------------------------
# KMS Key for Encryption
# -----------------------------------------------------------------------------
resource "aws_kms_key" "main" {
  description             = "KMS key for ${var.project_name} ${var.environment} encryption"
  deletion_window_in_days = var.deletion_window_in_days
  enable_key_rotation     = var.enable_key_rotation

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-kms-${var.environment}"
    }
  )
}

# -----------------------------------------------------------------------------
# KMS Key Alias
# -----------------------------------------------------------------------------
resource "aws_kms_alias" "main" {
  name          = "alias/${var.project_name}-${var.environment}"
  target_key_id = aws_kms_key.main.key_id
}

# -----------------------------------------------------------------------------
# KMS Grant for SageMaker
# -----------------------------------------------------------------------------
resource "aws_kms_grant" "sagemaker" {
  count             = var.sagemaker_role_arn != null ? 1 : 0
  name              = "${var.project_name}-sagemaker-grant-${var.environment}"
  key_id            = aws_kms_key.main.key_id
  grantee_principal = var.sagemaker_role_arn

  operations = [
    "Encrypt",
    "Decrypt",
    "GenerateDataKey",
    "GenerateDataKeyWithoutPlaintext",
    "CreateGrant",
    "RetireGrant",
    "DescribeKey"
  ]
}

# -----------------------------------------------------------------------------
# KMS Key Policy
# -----------------------------------------------------------------------------
resource "aws_kms_key_policy" "main" {
  key_id = aws_kms_key.main.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "Enable IAM User Permissions"
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
        }
        Action   = "kms:*"
        Resource = "*"
      },
      {
        Sid    = "Allow SageMaker to use the key"
        Effect = "Allow"
        Principal = {
          Service = "sagemaker.amazonaws.com"
        }
        Action = [
          "kms:Decrypt",
          "kms:Encrypt",
          "kms:GenerateDataKey",
          "kms:GenerateDataKeyWithoutPlaintext",
          "kms:CreateGrant",
          "kms:DescribeKey"
        ]
        Resource = "*"
        Condition = {
          StringEquals = {
            "kms:ViaService" = [
              "sagemaker.${data.aws_region.current.name}.amazonaws.com"
            ]
          }
        }
      },
      {
        Sid    = "Allow CloudWatch Logs to use the key"
        Effect = "Allow"
        Principal = {
          Service = "logs.${data.aws_region.current.name}.amazonaws.com"
        }
        Action = [
          "kms:Decrypt",
          "kms:Encrypt",
          "kms:GenerateDataKey"
        ]
        Resource = "*"
        Condition = {
          ArnLike = {
            "kms:EncryptionContext:aws:logs:arn" = "arn:aws:logs:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:log-group:/aws/sagemaker/*"
          }
        }
      }
    ]
  })
}

# -----------------------------------------------------------------------------
# Data Sources
# -----------------------------------------------------------------------------
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}
