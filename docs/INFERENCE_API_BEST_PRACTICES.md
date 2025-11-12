# SageMaker Inference Endpoint - API Exposure Best Practices

**Generated:** November 12, 2025  
**Use Case:** Exposing diabetes classification model endpoint to applications

---

## 🎯 Overview

This guide covers best practices for exposing your SageMaker inference endpoint (`diabetes-classifier-prod-*`) to external applications, users, and services.

---

## 📊 Architecture Comparison

| Approach | Latency | Security | Cost | Complexity | Best For |
|----------|---------|----------|------|------------|----------|
| **API Gateway + Lambda** | ~100-200ms | ⭐⭐⭐⭐⭐ | $ | Medium | Production APIs |
| **ALB + ECS/Fargate** | ~50-100ms | ⭐⭐⭐⭐ | $$ | High | High throughput |
| **Direct Boto3** | ~20-50ms | ⭐⭐⭐ | $ | Low | Internal apps |
| **SageMaker Async** | Minutes | ⭐⭐⭐⭐ | $ | Medium | Batch processing |

---

# 🏆 RECOMMENDED: API Gateway + Lambda Architecture

## Architecture Diagram

```text
┌──────────────┐
│   Client     │
│ (Web/Mobile) │
└──────┬───────┘
       │ HTTPS
       │ POST /predict
       │ { "features": [6, 148, 72, ...] }
       ▼
┌──────────────────────────────────────────────┐
│           AWS API Gateway                    │
│  • Custom domain: api.yourdomain.com         │
│  • Authentication: API Key / Cognito / IAM   │
│  • Rate limiting: 1000 req/min per user      │
│  • Request validation                        │
│  • CORS enabled                              │
└──────────────┬───────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────┐
│          AWS Lambda Function                 │
│  • Runtime: Python 3.8                       │
│  • Memory: 512 MB                            │
│  • Timeout: 30 seconds                       │
│  • Responsibilities:                         │
│    1. Validate input features                │
│    2. Transform to CSV format                │
│    3. Invoke SageMaker endpoint              │
│    4. Parse response                         │
│    5. Return formatted JSON                  │
└──────────────┬───────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────┐
│      SageMaker Inference Endpoint            │
│  • Endpoint: diabetes-classifier-prod-...    │
│  • Instance: ml.m5.large                     │
│  • Auto-scaling: 1-5 instances               │
│  • Data capture enabled                      │
└──────────────────────────────────────────────┘
```

---

## 🔧 Implementation

### Step 1: Lambda Function Code

**File:** `lambda/inference_handler.py`

```python
import json
import boto3
import os
from typing import Dict, List, Any

# Configuration
ENDPOINT_NAME = os.environ['SAGEMAKER_ENDPOINT_NAME']
REGION = os.environ.get('AWS_REGION', 'us-east-1')

# Initialize SageMaker runtime client
sagemaker_runtime = boto3.client('sagemaker-runtime', region_name=REGION)


def validate_features(features: List[float]) -> tuple[bool, str]:
    """
    Validate input features
    
    Expected: 8 features [Pregnancies, Glucose, BloodPressure, SkinThickness,
                         Insulin, BMI, DiabetesPedigreeFunction, Age]
    """
    if not isinstance(features, list):
        return False, "Features must be a list"
    
    if len(features) != 8:
        return False, f"Expected 8 features, got {len(features)}"
    
    # Validate ranges (domain knowledge)
    validations = [
        (features[0] >= 0 and features[0] <= 20, "Pregnancies must be 0-20"),
        (features[1] >= 0 and features[1] <= 300, "Glucose must be 0-300 mg/dL"),
        (features[2] >= 0 and features[2] <= 200, "Blood pressure must be 0-200 mmHg"),
        (features[3] >= 0 and features[3] <= 100, "Skin thickness must be 0-100 mm"),
        (features[4] >= 0 and features[4] <= 900, "Insulin must be 0-900 mu U/ml"),
        (features[5] >= 0 and features[5] <= 70, "BMI must be 0-70"),
        (features[6] >= 0 and features[6] <= 3, "Pedigree function must be 0-3"),
        (features[7] >= 18 and features[7] <= 120, "Age must be 18-120"),
    ]
    
    for is_valid, error_msg in validations:
        if not is_valid:
            return False, error_msg
    
    return True, ""


def invoke_endpoint(features: List[float]) -> Dict[str, Any]:
    """
    Invoke SageMaker endpoint with features
    """
    # Convert to CSV format (expected by XGBoost)
    csv_data = ','.join(map(str, features))
    
    # Invoke endpoint
    response = sagemaker_runtime.invoke_endpoint(
        EndpointName=ENDPOINT_NAME,
        ContentType='text/csv',
        Accept='application/json',
        Body=csv_data
    )
    
    # Parse response
    result = json.loads(response['Body'].read().decode())
    
    return result


def lambda_handler(event, context):
    """
    Main Lambda handler
    
    Expected input:
    {
        "features": [6, 148, 72, 35, 0, 33.6, 0.627, 50]
    }
    
    Response:
    {
        "prediction": 1,
        "probability": 0.85,
        "risk_level": "high",
        "message": "High risk of diabetes detected"
    }
    """
    try:
        # Parse request body
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event
        
        # Extract features
        features = body.get('features')
        if not features:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'Missing required field: features',
                    'example': {
                        'features': [6, 148, 72, 35, 0, 33.6, 0.627, 50]
                    }
                })
            }
        
        # Validate features
        is_valid, error_msg = validate_features(features)
        if not is_valid:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': error_msg})
            }
        
        # Invoke endpoint
        result = invoke_endpoint(features)
        
        # Parse prediction (XGBoost returns probability)
        probability = float(result)
        prediction = 1 if probability >= 0.5 else 0
        
        # Determine risk level
        if probability >= 0.75:
            risk_level = "high"
            message = "High risk of diabetes detected. Please consult a healthcare provider."
        elif probability >= 0.5:
            risk_level = "moderate"
            message = "Moderate risk of diabetes. Consider lifestyle modifications."
        elif probability >= 0.25:
            risk_level = "low"
            message = "Low risk of diabetes. Maintain healthy habits."
        else:
            risk_level = "very_low"
            message = "Very low risk of diabetes."
        
        # Format response
        response_body = {
            'prediction': prediction,
            'probability': round(probability, 4),
            'risk_level': risk_level,
            'message': message,
            'model_version': ENDPOINT_NAME,
            'features_received': features
        }
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(response_body)
        }
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Internal server error',
                'message': str(e)
            })
        }
```

---

### Step 2: Lambda IAM Policy

**Required permissions:**

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "sagemaker:InvokeEndpoint"
      ],
      "Resource": "arn:aws:sagemaker:us-east-1:*:endpoint/diabetes-classifier-prod-*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*"
    }
  ]
}
```

---

### Step 3: API Gateway Configuration

**Create REST API:**

```bash
# Using AWS CLI
aws apigateway create-rest-api \
  --name "DiabetesPredictionAPI" \
  --description "Diabetes classification inference API" \
  --endpoint-configuration types=REGIONAL \
  --region us-east-1
```

**Resource structure:**
```
/
└── /predict (POST)
    ├── Method Request: Requires API Key
    ├── Integration: Lambda proxy
    └── Method Response: 200, 400, 500
```

**Add API Key & Usage Plan:**

```bash
# Create API key
aws apigateway create-api-key \
  --name "WebAppAPIKey" \
  --enabled \
  --region us-east-1

# Create usage plan
aws apigateway create-usage-plan \
  --name "StandardPlan" \
  --throttle rateLimit=100,burstLimit=200 \
  --quota limit=100000,period=MONTH \
  --region us-east-1
```

---

### Step 4: Terraform Deployment (Recommended)

**File:** `infrastructure/terraform/modules/api_gateway/main.tf`

```hcl
# Lambda Function
resource "aws_lambda_function" "inference_handler" {
  filename         = "lambda/inference_handler.zip"
  function_name    = "diabetes-inference-handler"
  role            = aws_iam_role.lambda_role.arn
  handler         = "inference_handler.lambda_handler"
  runtime         = "python3.8"
  timeout         = 30
  memory_size     = 512

  environment {
    variables = {
      SAGEMAKER_ENDPOINT_NAME = var.endpoint_name
      AWS_REGION             = var.region
    }
  }

  tags = {
    Project = "mlops-diabetes"
  }
}

# API Gateway REST API
resource "aws_api_gateway_rest_api" "diabetes_api" {
  name        = "diabetes-prediction-api"
  description = "Diabetes classification inference API"

  endpoint_configuration {
    types = ["REGIONAL"]
  }
}

# API Gateway Resource: /predict
resource "aws_api_gateway_resource" "predict" {
  rest_api_id = aws_api_gateway_rest_api.diabetes_api.id
  parent_id   = aws_api_gateway_rest_api.diabetes_api.root_resource_id
  path_part   = "predict"
}

# API Gateway Method: POST /predict
resource "aws_api_gateway_method" "predict_post" {
  rest_api_id   = aws_api_gateway_rest_api.diabetes_api.id
  resource_id   = aws_api_gateway_resource.predict.id
  http_method   = "POST"
  authorization = "API_KEY"
  api_key_required = true
}

# Lambda Integration
resource "aws_api_gateway_integration" "lambda_integration" {
  rest_api_id             = aws_api_gateway_rest_api.diabetes_api.id
  resource_id             = aws_api_gateway_resource.predict.id
  http_method             = aws_api_gateway_method.predict_post.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.inference_handler.invoke_arn
}

# Lambda permission for API Gateway
resource "aws_lambda_permission" "apigw_lambda" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.inference_handler.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.diabetes_api.execution_arn}/*/*"
}

# API Gateway Deployment
resource "aws_api_gateway_deployment" "api_deployment" {
  depends_on = [
    aws_api_gateway_integration.lambda_integration
  ]

  rest_api_id = aws_api_gateway_rest_api.diabetes_api.id
  stage_name  = var.environment

  lifecycle {
    create_before_destroy = true
  }
}

# Usage Plan
resource "aws_api_gateway_usage_plan" "standard_plan" {
  name        = "standard-usage-plan"
  description = "Standard usage plan for diabetes API"

  api_stages {
    api_id = aws_api_gateway_rest_api.diabetes_api.id
    stage  = aws_api_gateway_deployment.api_deployment.stage_name
  }

  throttle_settings {
    rate_limit  = 100  # requests per second
    burst_limit = 200  # max concurrent requests
  }

  quota_settings {
    limit  = 100000  # requests per month
    period = "MONTH"
  }
}

# API Key
resource "aws_api_gateway_api_key" "webapp_key" {
  name    = "webapp-api-key"
  enabled = true
}

# Link API Key to Usage Plan
resource "aws_api_gateway_usage_plan_key" "webapp_key_association" {
  key_id        = aws_api_gateway_api_key.webapp_key.id
  key_type      = "API_KEY"
  usage_plan_id = aws_api_gateway_usage_plan.standard_plan.id
}

# Outputs
output "api_endpoint" {
  value       = "${aws_api_gateway_deployment.api_deployment.invoke_url}/predict"
  description = "API Gateway endpoint URL"
}

output "api_key" {
  value       = aws_api_gateway_api_key.webapp_key.value
  sensitive   = true
  description = "API key for authentication"
}
```

---

## 🔒 Security Best Practices

### 1. **Authentication Methods**

| Method | Security Level | Use Case |
|--------|----------------|----------|
| **API Key** | ⭐⭐⭐ | Simple apps, rate limiting |
| **AWS IAM** | ⭐⭐⭐⭐⭐ | AWS-native apps, highest security |
| **Cognito User Pools** | ⭐⭐⭐⭐ | User-based apps, OAuth2 |
| **Lambda Authorizer** | ⭐⭐⭐⭐ | Custom auth logic, JWT validation |

**Recommended:** Cognito for user-facing apps, IAM for service-to-service

### 2. **Rate Limiting Configuration**

```yaml
# Recommended limits by tier
Free Tier:
  requests_per_second: 10
  burst: 20
  monthly_quota: 10000

Standard Tier:
  requests_per_second: 100
  burst: 200
  monthly_quota: 100000

Premium Tier:
  requests_per_second: 1000
  burst: 2000
  monthly_quota: 1000000
```

### 3. **Input Validation**

```python
# Always validate:
✅ Feature count (exactly 8)
✅ Feature ranges (domain-specific)
✅ Data types (all numeric)
✅ Missing values (no nulls)
✅ Request size (< 1 MB)
✅ Content-Type header

# Example validation schema
FEATURE_SCHEMA = {
    "Pregnancies": {"min": 0, "max": 20, "type": "int"},
    "Glucose": {"min": 0, "max": 300, "type": "float"},
    "BloodPressure": {"min": 0, "max": 200, "type": "float"},
    "SkinThickness": {"min": 0, "max": 100, "type": "float"},
    "Insulin": {"min": 0, "max": 900, "type": "float"},
    "BMI": {"min": 0, "max": 70, "type": "float"},
    "DiabetesPedigreeFunction": {"min": 0, "max": 3, "type": "float"},
    "Age": {"min": 18, "max": 120, "type": "int"}
}
```

### 4. **Encryption**

```text
✅ HTTPS only (TLS 1.2+)
✅ API keys in AWS Secrets Manager
✅ Endpoint data capture encrypted (KMS)
✅ CloudWatch logs encrypted
✅ No sensitive data in URLs
```

---

## 📈 Monitoring & Observability

### CloudWatch Metrics to Track

```python
# API Gateway Metrics
- Count (total requests)
- Latency (p50, p95, p99)
- 4XXError (client errors)
- 5XXError (server errors)
- CacheHitCount / CacheMissCount

# Lambda Metrics
- Invocations
- Duration
- Errors
- Throttles
- ConcurrentExecutions

# SageMaker Endpoint Metrics
- ModelLatency
- Invocations
- InvocationErrors (4xx, 5xx)
- CPUUtilization
- MemoryUtilization
```

### CloudWatch Alarms

```yaml
alarms:
  - name: HighErrorRate
    metric: 5XXError
    threshold: 10 per minute
    action: SNS notification
  
  - name: HighLatency
    metric: Latency
    threshold: p99 > 2000ms
    action: Scale endpoint
  
  - name: LowModelAccuracy
    metric: Custom (from monitoring)
    threshold: < 0.70
    action: Trigger retraining
```

---

## 🧪 Testing

### Unit Test (Lambda)

```python
# tests/test_inference_handler.py
import pytest
from lambda.inference_handler import lambda_handler, validate_features

def test_valid_prediction():
    event = {
        'body': json.dumps({
            'features': [6, 148, 72, 35, 0, 33.6, 0.627, 50]
        })
    }
    
    response = lambda_handler(event, {})
    
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert 'prediction' in body
    assert 'probability' in body
    assert body['prediction'] in [0, 1]

def test_invalid_feature_count():
    event = {
        'body': json.dumps({
            'features': [6, 148, 72]  # Only 3 features
        })
    }
    
    response = lambda_handler(event, {})
    assert response['statusCode'] == 400

def test_feature_range_validation():
    is_valid, msg = validate_features([6, 500, 72, 35, 0, 33.6, 0.627, 50])
    assert not is_valid  # Glucose 500 is out of range
```

### Integration Test

```bash
# Test API endpoint
curl -X POST https://api.yourdomain.com/predict \
  -H "x-api-key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "features": [6, 148, 72, 35, 0, 33.6, 0.627, 50]
  }'

# Expected response:
{
  "prediction": 1,
  "probability": 0.8532,
  "risk_level": "high",
  "message": "High risk of diabetes detected. Please consult a healthcare provider.",
  "model_version": "diabetes-classifier-prod-2025-11-11-15-15-49",
  "features_received": [6, 148, 72, 35, 0, 33.6, 0.627, 50]
}
```

---

## 💰 Cost Optimization

### Estimated Monthly Costs

**Scenario: 1 million requests/month**

```
API Gateway:
  1,000,000 requests × $3.50/million = $3.50

Lambda:
  1,000,000 invocations × $0.20/million = $0.20
  Compute: 512 MB × 100ms × $0.0000166667/GB-sec = $8.33

SageMaker Endpoint (ml.m5.large):
  730 hours × $0.115/hour = $83.95

CloudWatch Logs:
  5 GB ingestion × $0.50/GB = $2.50
  Storage: 5 GB × $0.03/GB = $0.15

TOTAL: ~$98.63/month
```

### Cost Reduction Tips

```text
1. Use SageMaker Serverless Inference for low traffic (<100 req/min)
   💰 Save ~80% on endpoint costs

2. Enable API Gateway caching (300 seconds TTL)
   💰 Reduce Lambda invocations by 50-70%

3. Use Lambda SnapStart for faster cold starts
   💰 Reduce Lambda duration charges

4. Batch predictions when possible
   💰 Process 100 predictions in 1 Lambda call

5. Use CloudWatch Logs Insights instead of storing all logs
   💰 Reduce storage costs by 90%
```

---

## 🚀 Client Examples

### Python Client

```python
import requests
import json

API_ENDPOINT = "https://api.yourdomain.com/predict"
API_KEY = "your-api-key-here"

def predict_diabetes(features):
    """
    Make prediction request
    
    Args:
        features: List of 8 numerical features
    
    Returns:
        dict: Prediction response
    """
    headers = {
        "x-api-key": API_KEY,
        "Content-Type": "application/json"
    }
    
    payload = {
        "features": features
    }
    
    response = requests.post(API_ENDPOINT, headers=headers, json=payload)
    response.raise_for_status()
    
    return response.json()

# Example usage
patient_data = [6, 148, 72, 35, 0, 33.6, 0.627, 50]
result = predict_diabetes(patient_data)

print(f"Prediction: {result['prediction']}")
print(f"Probability: {result['probability']}")
print(f"Risk Level: {result['risk_level']}")
print(f"Message: {result['message']}")
```

### JavaScript (React/Node.js)

```javascript
const API_ENDPOINT = "https://api.yourdomain.com/predict";
const API_KEY = "your-api-key-here";

async function predictDiabetes(features) {
    const response = await fetch(API_ENDPOINT, {
        method: 'POST',
        headers: {
            'x-api-key': API_KEY,
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ features })
    });

    if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
    }

    return await response.json();
}

// Example usage
const patientData = [6, 148, 72, 35, 0, 33.6, 0.627, 50];
predictDiabetes(patientData)
    .then(result => {
        console.log(`Prediction: ${result.prediction}`);
        console.log(`Probability: ${result.probability}`);
        console.log(`Risk Level: ${result.risk_level}`);
    })
    .catch(error => console.error('Error:', error));
```

### cURL (Testing)

```bash
curl -X POST https://api.yourdomain.com/predict \
  -H "x-api-key: your-api-key-here" \
  -H "Content-Type: application/json" \
  -d '{
    "features": [6, 148, 72, 35, 0, 33.6, 0.627, 50]
  }'
```

---

## 🎯 Deployment Checklist

Before going to production:

```text
✅ Lambda function deployed with correct IAM role
✅ API Gateway configured with authentication
✅ Rate limiting enabled (per usage plan)
✅ CloudWatch alarms configured
✅ CORS enabled for web clients
✅ Custom domain configured (optional but recommended)
✅ SSL certificate configured
✅ API documentation published (Swagger/OpenAPI)
✅ Client SDKs generated
✅ Load testing completed (1000+ concurrent requests)
✅ Error handling tested (4xx, 5xx responses)
✅ Monitoring dashboard created
✅ On-call rotation established
✅ Incident response plan documented
```

---

## 📚 Additional Resources

- [AWS API Gateway Best Practices](https://docs.aws.amazon.com/apigateway/latest/developerguide/best-practices.html)
- [SageMaker Endpoint Security](https://docs.aws.amazon.com/sagemaker/latest/dg/endpoint-security.html)
- [Lambda Performance Optimization](https://docs.aws.amazon.com/lambda/latest/dg/best-practices.html)
- [API Design Guidelines](https://restfulapi.net/)

---

## 🔄 Next Steps

1. **Create Lambda function** with provided code
2. **Deploy API Gateway** using Terraform module
3. **Test with Postman/cURL** to verify functionality
4. **Set up monitoring** with CloudWatch dashboards
5. **Document API** with Swagger/OpenAPI spec
6. **Create client SDKs** for your applications
7. **Perform load testing** to validate auto-scaling
8. **Implement CI/CD** for API updates

---

**Questions or issues?** Check the troubleshooting section in the main README or create a GitHub issue.
