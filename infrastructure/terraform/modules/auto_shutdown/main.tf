# =============================================================================
# Auto Shutdown Module - Lambda Function for DEV Environment
# =============================================================================

# -----------------------------------------------------------------------------
# Lambda IAM Role
# -----------------------------------------------------------------------------
resource "aws_iam_role" "lambda" {
  name = "${var.project_name}-auto-shutdown-lambda-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-auto-shutdown-lambda-${var.environment}"
    }
  )
}

# -----------------------------------------------------------------------------
# Lambda Policy for SageMaker and CloudWatch
# -----------------------------------------------------------------------------
resource "aws_iam_role_policy" "lambda" {
  name = "sagemaker-endpoint-management"
  role = aws_iam_role.lambda.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "sagemaker:ListEndpoints",
          "sagemaker:DescribeEndpoint",
          "sagemaker:UpdateEndpoint",
          "sagemaker:DeleteEndpoint"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:*"
      }
    ]
  })
}

# -----------------------------------------------------------------------------
# Lambda Function for Shutdown
# -----------------------------------------------------------------------------
resource "aws_lambda_function" "shutdown" {
  filename         = data.archive_file.lambda_shutdown.output_path
  function_name    = "${var.project_name}-endpoint-shutdown-${var.environment}"
  role             = aws_iam_role.lambda.arn
  handler          = "shutdown.lambda_handler"
  source_code_hash = data.archive_file.lambda_shutdown.output_base64sha256
  runtime          = "python3.11"
  timeout          = 60

  environment {
    variables = {
      PROJECT_NAME = var.project_name
      ENVIRONMENT  = var.environment
    }
  }

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-shutdown-lambda-${var.environment}"
    }
  )
}

# -----------------------------------------------------------------------------
# Lambda Function for Startup
# -----------------------------------------------------------------------------
resource "aws_lambda_function" "startup" {
  filename         = data.archive_file.lambda_startup.output_path
  function_name    = "${var.project_name}-endpoint-startup-${var.environment}"
  role             = aws_iam_role.lambda.arn
  handler          = "startup.lambda_handler"
  source_code_hash = data.archive_file.lambda_startup.output_base64sha256
  runtime          = "python3.11"
  timeout          = 60

  environment {
    variables = {
      PROJECT_NAME = var.project_name
      ENVIRONMENT  = var.environment
    }
  }

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-startup-lambda-${var.environment}"
    }
  )
}

# -----------------------------------------------------------------------------
# EventBridge Rule for Shutdown Schedule
# -----------------------------------------------------------------------------
resource "aws_cloudwatch_event_rule" "shutdown" {
  name                = "${var.project_name}-shutdown-schedule-${var.environment}"
  description         = "Shutdown SageMaker endpoints at ${var.shutdown_schedule}"
  schedule_expression = var.shutdown_schedule

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-shutdown-schedule-${var.environment}"
    }
  )
}

# -----------------------------------------------------------------------------
# EventBridge Target for Shutdown
# -----------------------------------------------------------------------------
resource "aws_cloudwatch_event_target" "shutdown" {
  rule      = aws_cloudwatch_event_rule.shutdown.name
  target_id = "ShutdownLambda"
  arn       = aws_lambda_function.shutdown.arn
}

# -----------------------------------------------------------------------------
# Lambda Permission for Shutdown EventBridge
# -----------------------------------------------------------------------------
resource "aws_lambda_permission" "shutdown" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.shutdown.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.shutdown.arn
}

# -----------------------------------------------------------------------------
# EventBridge Rule for Startup Schedule
# -----------------------------------------------------------------------------
resource "aws_cloudwatch_event_rule" "startup" {
  name                = "${var.project_name}-startup-schedule-${var.environment}"
  description         = "Start SageMaker endpoints at ${var.startup_schedule}"
  schedule_expression = var.startup_schedule

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-startup-schedule-${var.environment}"
    }
  )
}

# -----------------------------------------------------------------------------
# EventBridge Target for Startup
# -----------------------------------------------------------------------------
resource "aws_cloudwatch_event_target" "startup" {
  rule      = aws_cloudwatch_event_rule.startup.name
  target_id = "StartupLambda"
  arn       = aws_lambda_function.startup.arn
}

# -----------------------------------------------------------------------------
# Lambda Permission for Startup EventBridge
# -----------------------------------------------------------------------------
resource "aws_lambda_permission" "startup" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.startup.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.startup.arn
}

# -----------------------------------------------------------------------------
# Lambda Source Code - Shutdown
# -----------------------------------------------------------------------------
data "archive_file" "lambda_shutdown" {
  type        = "zip"
  output_path = "${path.module}/lambda_shutdown.zip"

  source {
    content  = <<-EOT
      import boto3
      import os
      import json
      
      def lambda_handler(event, context):
          sagemaker = boto3.client('sagemaker')
          project_name = os.environ['PROJECT_NAME']
          environment = os.environ['ENVIRONMENT']
          
          # List all endpoints
          response = sagemaker.list_endpoints(
              NameContains=f"{project_name}-",
              StatusEquals='InService'
          )
          
          shutdown_count = 0
          for endpoint in response['Endpoints']:
              endpoint_name = endpoint['EndpointName']
              
              # Only shutdown endpoints in this environment with AutoShutdown tag
              endpoint_desc = sagemaker.describe_endpoint(EndpointName=endpoint_name)
              tags_response = sagemaker.list_tags(ResourceArn=endpoint_desc['EndpointArn'])
              
              auto_shutdown = False
              for tag in tags_response.get('Tags', []):
                  if tag['Key'] == 'AutoShutdown' and tag['Value'] == 'true':
                      auto_shutdown = True
                      break
              
              if auto_shutdown and environment in endpoint_name:
                  print(f"Shutting down endpoint: {endpoint_name}")
                  sagemaker.delete_endpoint(EndpointName=endpoint_name)
                  shutdown_count += 1
          
          return {
              'statusCode': 200,
              'body': json.dumps(f'Shutdown {shutdown_count} endpoints')
          }
    EOT
    filename = "shutdown.py"
  }
}

# -----------------------------------------------------------------------------
# Lambda Source Code - Startup
# -----------------------------------------------------------------------------
data "archive_file" "lambda_startup" {
  type        = "zip"
  output_path = "${path.module}/lambda_startup.zip"

  source {
    content  = <<-EOT
      import boto3
      import os
      import json
      
      def lambda_handler(event, context):
          sagemaker = boto3.client('sagemaker')
          project_name = os.environ['PROJECT_NAME']
          environment = os.environ['ENVIRONMENT']
          
          # Note: This is a placeholder. In production, you would:
          # 1. Store endpoint configuration in DynamoDB or Parameter Store before shutdown
          # 2. Recreate endpoints from stored configuration
          # 3. Update DNS/load balancer if needed
          
          print(f"Startup triggered for {project_name}-{environment}")
          
          # For now, just log that startup was triggered
          # Implementation would require storing endpoint configs before shutdown
          
          return {
              'statusCode': 200,
              'body': json.dumps('Startup triggered - manual endpoint recreation required')
          }
    EOT
    filename = "startup.py"
  }
}
