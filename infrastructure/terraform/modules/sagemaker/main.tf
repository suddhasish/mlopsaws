# =============================================================================
# SageMaker Module - Model Registry & Monitoring
# =============================================================================

# -----------------------------------------------------------------------------
# SageMaker Model Package Group (Model Registry)
# -----------------------------------------------------------------------------
resource "aws_sagemaker_model_package_group" "main" {
  count = var.enable_model_package_group ? 1 : 0

  model_package_group_name        = "${var.project_name}-model-group-${var.environment}"
  model_package_group_description = "Model registry for ${var.project_name} ${var.environment} - Diabetes classification models"

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-model-group-${var.environment}"
    }
  )
}

# -----------------------------------------------------------------------------
# Data Quality Monitoring Job Definition (On-Demand Drift Detection)
# -----------------------------------------------------------------------------
resource "aws_sagemaker_data_quality_job_definition" "drift_monitor" {
  count = var.enable_monitoring ? 1 : 0

  name     = "${var.project_name}-data-quality-${var.environment}"
  role_arn = var.sagemaker_execution_role_arn

  data_quality_app_specification {
    image_uri = "156813124566.dkr.ecr.${var.aws_region}.amazonaws.com/sagemaker-model-monitor-analyzer"
  }

  data_quality_baseline_config {
    constraints_resource {
      s3_uri = "s3://${var.bucket_name}/monitoring/${var.environment}/constraints/constraints.json"
    }

    statistics_resource {
      s3_uri = "s3://${var.bucket_name}/monitoring/${var.environment}/statistics/statistics.json"
    }
  }

  data_quality_job_input {
    endpoint_input {
      endpoint_name             = var.endpoint_name
      local_path                = "/opt/ml/processing/input/endpoint"
      s3_input_mode             = "File"
      s3_data_distribution_type = "FullyReplicated"
    }
  }

  data_quality_job_output_config {
    monitoring_outputs {
      s3_output {
        s3_uri     = "s3://${var.bucket_name}/monitoring/${var.environment}/results"
        local_path = "/opt/ml/processing/output"
      }
    }
  }

  job_resources {
    cluster_config {
      instance_count    = 1
      instance_type     = "ml.m5.large"
      volume_size_in_gb = 20
    }
  }

  stopping_condition {
    max_runtime_in_seconds = 3600 # 1 hour max
  }

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-data-quality-${var.environment}"
      Type = "DataQualityMonitoring"
    }
  )
}

# -----------------------------------------------------------------------------
# Model Quality Monitoring Job Definition (Model Performance Tracking)
# COMMENTED OUT: Resource type not available in AWS provider 5.0
# Model monitoring will be configured via Python SDK in src/monitoring/
# -----------------------------------------------------------------------------
# resource "aws_sagemaker_model_quality_job_definition" "model_monitor" {
#   count = var.enable_monitoring ? 1 : 0
#
#   name     = "${var.project_name}-model-quality-${var.environment}"
#   role_arn = var.sagemaker_execution_role_arn
#
#   model_quality_app_specification {
#     image_uri                      = "156813124566.dkr.ecr.${var.aws_region}.amazonaws.com/sagemaker-model-monitor-analyzer"
#     problem_type                   = "BinaryClassification"
#     record_preprocessor_source_uri = "s3://${var.bucket_name}/monitoring/${var.environment}/preprocessor.py"
#   }
#
#   model_quality_baseline_config {
#     baselining_job_name = "${var.project_name}-model-baseline-${var.environment}"
#
#     constraints_resource {
#       s3_uri = "s3://${var.bucket_name}/monitoring/${var.environment}/model-constraints/constraints.json"
#     }
#   }
#
#   model_quality_job_input {
#     endpoint_input {
#       endpoint_name             = var.endpoint_name
#       local_path                = "/opt/ml/processing/input/endpoint"
#       s3_input_mode             = "File"
#       s3_data_distribution_type = "FullyReplicated"
#
#       probability_threshold_attribute = 0.5
#       inference_attribute             = "prediction"
#     }
#
#     ground_truth_s3_input {
#       s3_uri = "s3://${var.bucket_name}/monitoring/${var.environment}/ground-truth"
#     }
#   }
#
#   model_quality_job_output_config {
#     monitoring_outputs {
#       s3_output {
#         s3_uri     = "s3://${var.bucket_name}/monitoring/${var.environment}/model-results"
#         local_path = "/opt/ml/processing/output"
#       }
#     }
#   }
#
#   job_resources {
#     cluster_config {
#       instance_count    = 1
#       instance_type     = "ml.m5.large"
#       volume_size_in_gb = 20
#     }
#   }
#
#   stopping_condition {
#     max_runtime_in_seconds = 3600
#   }
#
#   tags = merge(
#     var.tags,
#     {
#       Name = "${var.project_name}-model-quality-${var.environment}"
#       Type = "ModelQualityMonitoring"
#     }
#   )
# }

# -----------------------------------------------------------------------------
# CloudWatch Alarms for Model Performance Degradation
# -----------------------------------------------------------------------------

# Alarm: Model Invocation Errors
resource "aws_cloudwatch_metric_alarm" "model_invocation_errors" {
  count = var.enable_monitoring ? 1 : 0

  alarm_name          = "${var.project_name}-model-errors-${var.environment}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "ModelInvocationErrors"
  namespace           = "AWS/SageMaker"
  period              = 300 # 5 minutes
  statistic           = "Sum"
  threshold           = 10
  alarm_description   = "Alert when model invocation errors exceed 10 in 5 minutes"
  treat_missing_data  = "notBreaching"

  dimensions = {
    EndpointName = var.endpoint_name
    VariantName  = "AllTraffic"
  }

  alarm_actions = var.sns_topic_arns

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-model-errors-${var.environment}"
    }
  )
}

# Alarm: Model Latency
resource "aws_cloudwatch_metric_alarm" "model_latency" {
  count = var.enable_monitoring ? 1 : 0

  alarm_name          = "${var.project_name}-model-latency-${var.environment}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "ModelLatency"
  namespace           = "AWS/SageMaker"
  period              = 300
  statistic           = "Average"
  threshold           = 1000 # 1 second
  alarm_description   = "Alert when model latency exceeds 1 second"
  treat_missing_data  = "notBreaching"

  dimensions = {
    EndpointName = var.endpoint_name
    VariantName  = "AllTraffic"
  }

  alarm_actions = var.sns_topic_arns

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-model-latency-${var.environment}"
    }
  )
}

# Alarm: Invocations per Instance
resource "aws_cloudwatch_metric_alarm" "invocations_high" {
  count = var.enable_monitoring ? 1 : 0

  alarm_name          = "${var.project_name}-invocations-high-${var.environment}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "InvocationsPerInstance"
  namespace           = "AWS/SageMaker"
  period              = 300
  statistic           = "Sum"
  threshold           = 1000
  alarm_description   = "Alert when invocations per instance exceed 1000 in 5 minutes"
  treat_missing_data  = "notBreaching"

  dimensions = {
    EndpointName = var.endpoint_name
    VariantName  = "AllTraffic"
  }

  alarm_actions = var.sns_topic_arns

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-invocations-high-${var.environment}"
    }
  )
}
