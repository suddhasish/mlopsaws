# =============================================================================
# IAM Module - Roles and Policies for SageMaker
# =============================================================================

# -----------------------------------------------------------------------------
# SageMaker Execution Role
# -----------------------------------------------------------------------------
resource "aws_iam_role" "sagemaker_execution" {
  name = "${var.project_name}-sagemaker-execution-${var.environment}"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "sagemaker.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-sagemaker-execution-${var.environment}"
    }
  )
}

# -----------------------------------------------------------------------------
# S3 Access Policy for SageMaker
# -----------------------------------------------------------------------------
resource "aws_iam_role_policy" "sagemaker_s3_access" {
  name = "s3-access"
  role = aws_iam_role.sagemaker_execution.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ]
        Resource = [
          var.s3_bucket_arn,
          "${var.s3_bucket_arn}/*"
        ]
      }
    ]
  })
}

# -----------------------------------------------------------------------------
# CloudWatch Logs Policy for SageMaker
# -----------------------------------------------------------------------------
resource "aws_iam_role_policy" "sagemaker_cloudwatch" {
  name = "cloudwatch-logs"
  role = aws_iam_role.sagemaker_execution.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "logs:DescribeLogStreams"
        ]
        Resource = "arn:aws:logs:*:*:log-group:/aws/sagemaker/*"
      }
    ]
  })
}

# -----------------------------------------------------------------------------
# ECR Access Policy for SageMaker (for custom Docker images)
# -----------------------------------------------------------------------------
resource "aws_iam_role_policy" "sagemaker_ecr_access" {
  name = "ecr-access"
  role = aws_iam_role.sagemaker_execution.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ecr:GetAuthorizationToken",
          "ecr:BatchCheckLayerAvailability",
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage"
        ]
        Resource = "*"
      }
    ]
  })
}

# -----------------------------------------------------------------------------
# KMS Access Policy for SageMaker (conditional)
# -----------------------------------------------------------------------------
resource "aws_iam_role_policy" "sagemaker_kms_access" {
  count = var.kms_key_arn != null ? 1 : 0
  name  = "kms-access"
  role  = aws_iam_role.sagemaker_execution.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "kms:Decrypt",
          "kms:Encrypt",
          "kms:GenerateDataKey",
          "kms:DescribeKey"
        ]
        Resource = var.kms_key_arn
      }
    ]
  })
}

# -----------------------------------------------------------------------------
# Data Scientist Role (for human users)
# -----------------------------------------------------------------------------
resource "aws_iam_role" "data_scientist" {
  name = "${var.project_name}-data-scientist-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
        }
        Action = "sts:AssumeRole"
        Condition = {
          Bool = {
            "aws:MultiFactorAuthPresent" = "true"
          }
        }
      }
    ]
  })

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-data-scientist-${var.environment}"
    }
  )
}

# -----------------------------------------------------------------------------
# Attach SageMaker Full Access to Data Scientist Role
# -----------------------------------------------------------------------------
resource "aws_iam_role_policy_attachment" "data_scientist_sagemaker" {
  role       = aws_iam_role.data_scientist.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSageMakerFullAccess"
}

# -----------------------------------------------------------------------------
# PassRole Policy for Data Scientist
# -----------------------------------------------------------------------------
resource "aws_iam_role_policy" "data_scientist_pass_role" {
  name = "pass-role"
  role = aws_iam_role.data_scientist.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = "iam:PassRole"
        Resource = aws_iam_role.sagemaker_execution.arn
        Condition = {
          StringEquals = {
            "iam:PassedToService" = "sagemaker.amazonaws.com"
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

# =============================================================================
# GITHUB ACTIONS OIDC INTEGRATION
# =============================================================================

# -----------------------------------------------------------------------------
# OIDC Provider for GitHub Actions
# -----------------------------------------------------------------------------
resource "aws_iam_openid_connect_provider" "github_actions" {
  count = var.enable_github_oidc ? 1 : 0

  url = "https://token.actions.githubusercontent.com"

  client_id_list = [
    "sts.amazonaws.com"
  ]

  thumbprint_list = [
    "6938fd4d98bab03faadb97b34396831e3780aea1",
    "1c58a3a8518e8759bf075b76b750d4f2df264fcd"
  ]

  tags = merge(
    var.tags,
    {
      Name = "GitHub Actions OIDC Provider"
    }
  )
}

# -----------------------------------------------------------------------------
# GitHub Actions IAM Role
# -----------------------------------------------------------------------------
resource "aws_iam_role" "github_actions" {
  count = var.enable_github_oidc ? 1 : 0

  name = "${var.project_name}-github-actions-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Federated = aws_iam_openid_connect_provider.github_actions[0].arn
        }
        Action = "sts:AssumeRoleWithWebIdentity"
        Condition = {
          StringEquals = {
            "token.actions.githubusercontent.com:aud" = "sts.amazonaws.com"
          }
          StringLike = {
            "token.actions.githubusercontent.com:sub" = "repo:${var.github_org}/${var.github_repo}:*"
          }
        }
      }
    ]
  })

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-github-actions-${var.environment}"
    }
  )
}

# -----------------------------------------------------------------------------
# GitHub Actions - SageMaker Access
# -----------------------------------------------------------------------------
resource "aws_iam_role_policy_attachment" "github_actions_sagemaker" {
  count = var.enable_github_oidc ? 1 : 0

  role       = aws_iam_role.github_actions[0].name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSageMakerFullAccess"
}

# -----------------------------------------------------------------------------
# GitHub Actions - S3 Access
# -----------------------------------------------------------------------------
resource "aws_iam_role_policy_attachment" "github_actions_s3" {
  count = var.enable_github_oidc ? 1 : 0

  role       = aws_iam_role.github_actions[0].name
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
}

# -----------------------------------------------------------------------------
# GitHub Actions - IAM Read Access
# -----------------------------------------------------------------------------
resource "aws_iam_role_policy_attachment" "github_actions_iam_read" {
  count = var.enable_github_oidc ? 1 : 0

  role       = aws_iam_role.github_actions[0].name
  policy_arn = "arn:aws:iam::aws:policy/IAMReadOnlyAccess"
}

# -----------------------------------------------------------------------------
# GitHub Actions - ECR Access
# -----------------------------------------------------------------------------
resource "aws_iam_role_policy_attachment" "github_actions_ecr" {
  count = var.enable_github_oidc ? 1 : 0

  role       = aws_iam_role.github_actions[0].name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryFullAccess"
}

# -----------------------------------------------------------------------------
# GitHub Actions - Custom Policy (PassRole, CloudWatch Logs)
# -----------------------------------------------------------------------------
resource "aws_iam_role_policy" "github_actions_custom" {
  count = var.enable_github_oidc ? 1 : 0

  name = "github-actions-custom-policy"
  role = aws_iam_role.github_actions[0].id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid      = "PassRoleToSageMaker"
        Effect   = "Allow"
        Action   = "iam:PassRole"
        Resource = aws_iam_role.sagemaker_execution.arn
        Condition = {
          StringEquals = {
            "iam:PassedToService" = "sagemaker.amazonaws.com"
          }
        }
      },
      {
        Sid    = "CloudWatchLogsAccess"
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "logs:DescribeLogStreams"
        ]
        Resource = "arn:aws:logs:*:*:log-group:/aws/sagemaker/*"
      }
    ]
  })
}
