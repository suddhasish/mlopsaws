# =============================================================================
# Monitoring Module - CloudWatch, SNS, CloudTrail
# =============================================================================

# -----------------------------------------------------------------------------
# CloudWatch Log Group for Training Jobs
# -----------------------------------------------------------------------------
resource "aws_cloudwatch_log_group" "training_jobs" {
  name              = "/aws/sagemaker/TrainingJobs"
  retention_in_days = var.log_retention_days
  kms_key_id        = var.kms_key_arn

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-training-logs-${var.environment}"
    }
  )
}

# -----------------------------------------------------------------------------
# CloudWatch Log Group for Endpoints
# -----------------------------------------------------------------------------
resource "aws_cloudwatch_log_group" "endpoints" {
  name              = "/aws/sagemaker/Endpoints/${var.project_name}-${var.environment}"
  retention_in_days = var.log_retention_days
  kms_key_id        = var.kms_key_arn

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-endpoint-logs-${var.environment}"
    }
  )
}

# -----------------------------------------------------------------------------
# SNS Topic for General Alerts
# -----------------------------------------------------------------------------
resource "aws_sns_topic" "alerts" {
  name              = "${var.project_name}-alerts-${var.environment}"
  kms_master_key_id = var.kms_key_arn

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-alerts-${var.environment}"
    }
  )
}

# -----------------------------------------------------------------------------
# SNS Topic for Critical Alerts
# -----------------------------------------------------------------------------
resource "aws_sns_topic" "critical_alerts" {
  name              = "${var.project_name}-critical-alerts-${var.environment}"
  kms_master_key_id = var.kms_key_arn

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-critical-alerts-${var.environment}"
    }
  )
}

# -----------------------------------------------------------------------------
# SNS Email Subscriptions
# -----------------------------------------------------------------------------
resource "aws_sns_topic_subscription" "email_alerts" {
  count     = length(var.alert_email_endpoints)
  topic_arn = aws_sns_topic.alerts.arn
  protocol  = "email"
  endpoint  = var.alert_email_endpoints[count.index]
}

# -----------------------------------------------------------------------------
# SNS PagerDuty Subscription (Production Only)
# -----------------------------------------------------------------------------
resource "aws_sns_topic_subscription" "pagerduty" {
  count     = var.pagerduty_endpoint != null ? 1 : 0
  topic_arn = aws_sns_topic.critical_alerts.arn
  protocol  = "https"
  endpoint  = var.pagerduty_endpoint
}

# -----------------------------------------------------------------------------
# CloudWatch Metric Alarm - Endpoint Latency
# -----------------------------------------------------------------------------
resource "aws_cloudwatch_metric_alarm" "endpoint_latency" {
  count               = var.enable_alarms ? 1 : 0
  alarm_name          = "${var.project_name}-endpoint-high-latency-${var.environment}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "ModelLatency"
  namespace           = "AWS/SageMaker"
  period              = 300
  statistic           = "Average"
  threshold           = var.endpoint_latency_threshold_ms
  alarm_description   = "Alert when endpoint latency exceeds ${var.endpoint_latency_threshold_ms}ms"
  alarm_actions       = [aws_sns_topic.alerts.arn]

  dimensions = {
    EndpointName = "${var.project_name}-endpoint-${var.environment}"
  }

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-latency-alarm-${var.environment}"
    }
  )
}

# -----------------------------------------------------------------------------
# CloudWatch Metric Alarm - Endpoint Errors
# -----------------------------------------------------------------------------
resource "aws_cloudwatch_metric_alarm" "endpoint_errors" {
  count               = var.enable_alarms ? 1 : 0
  alarm_name          = "${var.project_name}-endpoint-high-errors-${var.environment}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "ModelInvocation4XXErrors"
  namespace           = "AWS/SageMaker"
  period              = 300
  statistic           = "Sum"
  threshold           = var.endpoint_error_threshold
  alarm_description   = "Alert when endpoint errors exceed ${var.endpoint_error_threshold}"
  alarm_actions       = [aws_sns_topic.critical_alerts.arn]

  dimensions = {
    EndpointName = "${var.project_name}-endpoint-${var.environment}"
  }

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-error-alarm-${var.environment}"
    }
  )
}

# -----------------------------------------------------------------------------
# S3 Bucket for CloudTrail Logs
# -----------------------------------------------------------------------------
resource "aws_s3_bucket" "cloudtrail_logs" {
  count  = var.enable_cloudtrail ? 1 : 0
  bucket = "${var.project_name}-cloudtrail-logs-${data.aws_caller_identity.current.account_id}-${var.environment}"

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-cloudtrail-logs-${var.environment}"
    }
  )
}

# -----------------------------------------------------------------------------
# S3 Bucket Policy for CloudTrail
# -----------------------------------------------------------------------------
resource "aws_s3_bucket_policy" "cloudtrail_logs" {
  count  = var.enable_cloudtrail ? 1 : 0
  bucket = aws_s3_bucket.cloudtrail_logs[0].id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AWSCloudTrailAclCheck"
        Effect = "Allow"
        Principal = {
          Service = "cloudtrail.amazonaws.com"
        }
        Action   = "s3:GetBucketAcl"
        Resource = aws_s3_bucket.cloudtrail_logs[0].arn
      },
      {
        Sid    = "AWSCloudTrailWrite"
        Effect = "Allow"
        Principal = {
          Service = "cloudtrail.amazonaws.com"
        }
        Action   = "s3:PutObject"
        Resource = "${aws_s3_bucket.cloudtrail_logs[0].arn}/*"
        Condition = {
          StringEquals = {
            "s3:x-amz-acl" = "bucket-owner-full-control"
          }
        }
      }
    ]
  })
}

# -----------------------------------------------------------------------------
# CloudTrail
# -----------------------------------------------------------------------------
resource "aws_cloudtrail" "main" {
  count                         = var.enable_cloudtrail ? 1 : 0
  name                          = "${var.project_name}-trail-${var.environment}"
  s3_bucket_name                = aws_s3_bucket.cloudtrail_logs[0].id
  include_global_service_events = true
  is_multi_region_trail         = true
  enable_log_file_validation    = true

  event_selector {
    read_write_type           = "All"
    include_management_events = true

    data_resource {
      type   = "AWS::S3::Object"
      values = ["${var.s3_data_bucket_arn}/*"]
    }

    data_resource {
      type   = "AWS::SageMaker::TrainingJob"
      values = ["arn:aws:sagemaker:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:training-job/*"]
    }

    data_resource {
      type   = "AWS::SageMaker::Endpoint"
      values = ["arn:aws:sagemaker:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:endpoint/*"]
    }
  }

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-cloudtrail-${var.environment}"
    }
  )

  depends_on = [aws_s3_bucket_policy.cloudtrail_logs]
}

# -----------------------------------------------------------------------------
# Data Sources
# -----------------------------------------------------------------------------
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}
