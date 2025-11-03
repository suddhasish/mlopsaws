# 🏗️ AWS Services Architecture - Detailed Explanation

## 📋 Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Core ML Services](#core-ml-services)
3. [Storage Services](#storage-services)
4. [Networking Services](#networking-services)
5. [Security Services](#security-services)
6. [Monitoring & Logging](#monitoring-logging)
7. [Cost Optimization](#cost-optimization)
8. [Service Interaction Flow](#service-interaction-flow)

---

## 🎯 Architecture Overview

### Why This Architecture?

This MLOps architecture follows the **AWS Well-Architected Framework** with five pillars:

1. **Operational Excellence**: Automated pipelines, IaC, monitoring
2. **Security**: Encryption, least-privilege, network isolation
3. **Reliability**: Multi-AZ deployment, auto-scaling, backups
4. **Performance Efficiency**: Right-sized instances, caching, optimization
5. **Cost Optimization**: Spot instances, auto-shutdown, tagging

### High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                          AWS CLOUD                                  │
│                                                                     │
│  ┌───────────────────┐         ┌──────────────────────┐            │
│  │   GitHub Actions  │────────▶│  S3 (Code/Data)      │            │
│  │   (CI/CD)         │         │  - Source code       │            │
│  └───────────────────┘         │  - Training data     │            │
│           │                    │  - Model artifacts   │            │
│           ▼                    └──────────────────────┘            │
│  ┌───────────────────┐                   │                         │
│  │ SageMaker Pipeline│◀──────────────────┘                         │
│  │  Orchestration    │                                              │
│  └────────┬──────────┘                                              │
│           │                                                          │
│     ┌─────┴────────┬──────────────┬────────────┐                   │
│     ▼              ▼              ▼            ▼                    │
│  ┌─────┐      ┌─────────┐    ┌────────┐   ┌─────────┐             │
│  │ Pre │      │ Training│    │ Eval   │   │ Deploy  │             │
│  │ Proc│      │ (XGBoost)   │ Metrics│   │ Endpoint│             │
│  └─────┘      └─────────┘    └────────┘   └────┬────┘             │
│     │              │              │              │                  │
│     └──────────────┴──────────────┴──────────────┘                  │
│                          │                                           │
│                          ▼                                           │
│              ┌──────────────────────┐                               │
│              │  Model Registry      │                               │
│              │  (Versioned Models)  │                               │
│              └──────────────────────┘                               │
│                          │                                           │
│                          ▼                                           │
│              ┌──────────────────────┐                               │
│              │  Real-time Endpoint  │◀───── User Applications       │
│              │  (ml.m5.xlarge)      │                               │
│              └──────────────────────┘                               │
│                          │                                           │
│                          ▼                                           │
│              ┌──────────────────────┐                               │
│              │  Model Monitor       │                               │
│              │  (Drift Detection)   │                               │
│              └──────────────────────┘                               │
│                          │                                           │
│                          ▼                                           │
│              ┌──────────────────────┐                               │
│              │  CloudWatch Alarms   │────▶ SNS Notifications        │
│              │  (Automated Actions) │                               │
│              └──────────────────────┘                               │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │              VPC (Private Network)                           │  │
│  │  ┌────────────────┐            ┌────────────────┐           │  │
│  │  │ Private Subnet │            │ Private Subnet │           │  │
│  │  │  (AZ-1)        │            │  (AZ-2)        │           │  │
│  │  │ - SageMaker    │            │ - SageMaker    │           │  │
│  │  │ - RDS (optional)│           │ - RDS (standby)│           │  │
│  │  └────────────────┘            └────────────────┘           │  │
│  │           │                              │                   │  │
│  │           └──────────┬───────────────────┘                   │  │
│  │                      ▼                                       │  │
│  │            ┌──────────────────┐                              │  │
│  │            │  VPC Endpoints   │                              │  │
│  │            │  - S3            │                              │  │
│  │            │  - SageMaker     │                              │  │
│  │            │  - CloudWatch    │                              │  │
│  │            └──────────────────┘                              │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🤖 Core ML Services

### 1. Amazon SageMaker

**What it is**: Fully managed machine learning platform for building, training, and deploying ML models.

**Why we use it**:
- ✅ **Managed Infrastructure**: No need to provision EC2 instances manually
- ✅ **Built-in Algorithms**: XGBoost, scikit-learn pre-installed
- ✅ **Auto-scaling**: Endpoints scale based on traffic
- ✅ **Integration**: Native integration with S3, CloudWatch, IAM
- ✅ **Cost Efficiency**: Pay only for compute time used (per-second billing)

**Components we use**:

#### a) SageMaker Processing Jobs
```
Purpose: Data preprocessing and feature engineering
Instance: ml.m5.xlarge (4 vCPUs, 16 GB RAM)
Duration: ~5-10 minutes per run
Cost: ~$0.23/hour = ~$0.04 per job
```

**Why this component**:
- Runs Python scripts (scikit-learn) at scale
- Auto-handles data loading from S3
- Parallel processing support
- Automatically cleans up resources after completion

**Code example**:
```python
from sagemaker.sklearn.processing import SKLearnProcessor

processor = SKLearnProcessor(
    framework_version='1.0-1',
    role=sagemaker_role,
    instance_type='ml.m5.xlarge',
    instance_count=1
)

processor.run(
    code='preprocessing.py',
    inputs=[ProcessingInput(source='s3://bucket/raw-data/', destination='/opt/ml/processing/input')],
    outputs=[ProcessingOutput(source='/opt/ml/processing/output', destination='s3://bucket/processed/')]
)
```

#### b) SageMaker Training Jobs
```
Purpose: Model training with hyperparameter tuning
Instance: ml.m5.xlarge (for our diabetes dataset)
Algorithm: XGBoost 1.5-1 (built-in container)
Duration: ~10-20 minutes per training run
Cost: ~$0.23/hour = ~$0.08 per training job
```

**Why XGBoost on SageMaker**:
- **Built-in Container**: AWS maintains optimized Docker image
- **Distributed Training**: Supports multi-instance training for large datasets
- **Hyperparameter Tuning**: Built-in Bayesian optimization
- **Checkpointing**: Saves intermediate models (good for spot instances)
- **Managed Spot Training**: Up to 90% cost savings

**Training configuration**:
```python
from sagemaker.xgboost import XGBoost

xgb = XGBoost(
    entry_point='train.py',
    framework_version='1.5-1',
    role=sagemaker_role,
    instance_type='ml.m5.xlarge',
    instance_count=1,
    hyperparameters={
        'max_depth': 6,
        'eta': 0.1,
        'objective': 'binary:logistic',
        'num_round': 100
    },
    use_spot_instances=True,  # 90% cost savings
    max_wait=3600,
    max_run=1800
)
```

#### c) SageMaker Model Registry
```
Purpose: Versioned model storage with approval workflow
Storage: Integrated with S3
Versioning: Automatic
Approval: Manual or automated
```

**Why we use it**:
- **Model Versioning**: Track all model versions automatically
- **Approval Workflow**: PendingManualApproval → Approved → Deployed
- **Lineage Tracking**: Links model to training data and code version
- **Audit Trail**: Who approved, when, why
- **A/B Testing**: Deploy multiple model versions simultaneously

**Model registration**:
```python
from sagemaker.workflow.step_collections import RegisterModel

step_register = RegisterModel(
    name="RegisterDiabetesModel",
    estimator=xgb,
    model_data=step_train.properties.ModelArtifacts.S3ModelArtifacts,
    content_types=["text/csv"],
    response_types=["text/csv"],
    inference_instances=["ml.t2.medium", "ml.m5.large"],
    transform_instances=["ml.m5.xlarge"],
    model_package_group_name="diabetes-classification-models",
    approval_status="PendingManualApproval",  # Requires human review
    model_metrics=model_metrics
)
```

#### d) SageMaker Endpoints
```
Purpose: Real-time inference API
Instance: ml.m5.xlarge (production), ml.t2.medium (dev)
Availability: 99.9% SLA with multi-AZ deployment
Latency: <100ms p99
Autoscaling: 1-10 instances based on invocations/minute
```

**Why real-time endpoints**:
- **Low Latency**: <100ms response time for predictions
- **Auto-scaling**: Handles traffic spikes automatically
- **Load Balancing**: Distributes requests across instances
- **Blue/Green Deployment**: Zero-downtime updates
- **Data Capture**: Logs requests for monitoring

**Endpoint configuration**:
```python
from sagemaker.model import Model

model = Model(
    image_uri=container,
    model_data=model_s3_path,
    role=sagemaker_role,
    predictor_cls=Predictor
)

predictor = model.deploy(
    initial_instance_count=2,  # High availability
    instance_type='ml.m5.xlarge',
    endpoint_name='diabetes-classifier-prod',
    data_capture_config=data_capture_config,  # For monitoring
    auto_scaling_config={
        'min_capacity': 2,
        'max_capacity': 10,
        'target_value': 1000.0,  # Invocations per minute
        'scale_in_cooldown': 300,
        'scale_out_cooldown': 60
    }
)
```

#### e) SageMaker Pipelines
```
Purpose: ML workflow orchestration (like Apache Airflow for ML)
Components: Directed Acyclic Graph (DAG) of steps
Execution: On-demand or scheduled
Cost: Free (only pay for compute resources used by steps)
```

**Why SageMaker Pipelines**:
- **Native Integration**: Works seamlessly with SageMaker components
- **Conditional Logic**: Skip model registration if metrics are poor
- **Parameter Store**: Share parameters between steps
- **Retry Logic**: Automatically retry failed steps
- **Version Control**: Pipeline definitions are JSON (can be versioned in Git)
- **No Server Management**: Unlike Airflow, no EC2 instances to maintain

**Pipeline structure**:
```python
from sagemaker.workflow.pipeline import Pipeline

pipeline = Pipeline(
    name="diabetes-training-pipeline",
    parameters=[
        training_instance_type,
        training_instance_count,
        model_approval_status
    ],
    steps=[
        step_preprocess,   # SKLearn processing job
        step_train,        # XGBoost training job
        step_evaluate,     # Model evaluation
        step_condition,    # Conditional: only register if metrics > threshold
        step_register      # Model registration (conditional)
    ],
    sagemaker_session=sagemaker_session
)

# Create/update pipeline
pipeline.upsert(role_arn=sagemaker_role)

# Execute pipeline
execution = pipeline.start()
```

#### f) SageMaker Model Monitor
```
Purpose: Detect data drift, model quality degradation
Monitoring: Data quality, model quality, bias, feature attribution
Schedule: Hourly (production), daily (staging)
Alerts: CloudWatch alarms → SNS notifications
```

**Why we use it**:
- **Data Drift Detection**: Detects when input data distribution changes
- **Quality Monitoring**: Tracks model performance over time
- **Automated Baselines**: Automatically generates statistical baselines
- **Violation Reports**: Detailed reports on constraint violations
- **Retraining Triggers**: Can trigger automated retraining

**Monitoring setup**:
```python
from sagemaker.model_monitor import DefaultModelMonitor

monitor = DefaultModelMonitor(
    role=sagemaker_role,
    instance_count=1,
    instance_type='ml.m5.xlarge',
    volume_size_in_gb=20,
    max_runtime_in_seconds=3600
)

# Create baseline from training data
monitor.suggest_baseline(
    baseline_dataset='s3://bucket/baseline/train.csv',
    dataset_format=DatasetFormat.csv(header=True),
    output_s3_uri='s3://bucket/baseline-results'
)

# Schedule hourly monitoring
monitor.create_monitoring_schedule(
    monitor_schedule_name='diabetes-hourly-monitor',
    endpoint_input=endpoint_name,
    output_s3_uri='s3://bucket/monitoring-results',
    statistics=baseline_statistics,
    constraints=baseline_constraints,
    schedule_cron_expression='cron(0 * * * ? *)',  # Every hour
    enable_cloudwatch_metrics=True
)
```

---

## 💾 Storage Services

### 2. Amazon S3 (Simple Storage Service)

**What it is**: Object storage service with 99.999999999% (11 9's) durability.

**Why we use it**:
- ✅ **Unlimited Storage**: No capacity planning needed
- ✅ **High Durability**: Automatic replication across 3+ facilities
- ✅ **Low Cost**: $0.023 per GB/month (Standard tier)
- ✅ **Native Integration**: SageMaker reads/writes directly to S3
- ✅ **Versioning**: Track changes to datasets and models
- ✅ **Lifecycle Policies**: Auto-archive old data to Glacier (cheaper)

**Bucket structure**:
```
mlops-diabetes-production/
├── data/
│   ├── raw/                    # Original datasets
│   │   └── diabetes.csv
│   ├── processed/              # After preprocessing
│   │   ├── train.csv
│   │   ├── validation.csv
│   │   └── test.csv
│   └── baseline/               # For model monitoring
│       └── baseline_stats.json
├── models/
│   ├── training-job-2024-11-01-12-00/
│   │   ├── model.tar.gz        # Trained XGBoost model
│   │   └── output/
│   │       └── evaluation.json
│   └── training-job-2024-11-02-15-30/
│       └── model.tar.gz
├── code/
│   ├── preprocessing.py
│   ├── train.py
│   └── inference.py
├── monitoring/
│   ├── data-quality/
│   │   └── 2024-11-04-10-00/
│   │       └── constraint_violations.json
│   └── model-quality/
│       └── 2024-11-04-10-00/
│           └── metrics.json
└── logs/
    └── processing-jobs/
        └── job-2024-11-04/
            └── processing.log
```

**Security configuration**:
```hcl
# Terraform: S3 bucket with security best practices

resource "aws_s3_bucket" "ml_data" {
  bucket = "mlops-diabetes-${var.environment}"
  
  tags = {
    Environment = var.environment
    Project     = "mlops-diabetes"
  }
}

# Enable versioning (track dataset changes)
resource "aws_s3_bucket_versioning" "ml_data" {
  bucket = aws_s3_bucket.ml_data.id
  
  versioning_configuration {
    status = "Enabled"
  }
}

# Enable encryption at rest (AES-256)
resource "aws_s3_bucket_server_side_encryption_configuration" "ml_data" {
  bucket = aws_s3_bucket.ml_data.id
  
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"  # Or use KMS for key rotation
    }
  }
}

# Block public access (CRITICAL for security)
resource "aws_s3_bucket_public_access_block" "ml_data" {
  bucket = aws_s3_bucket.ml_data.id
  
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Lifecycle policy (archive old training data to save costs)
resource "aws_s3_bucket_lifecycle_configuration" "ml_data" {
  bucket = aws_s3_bucket.ml_data.id
  
  rule {
    id     = "archive-old-training-data"
    status = "Enabled"
    
    filter {
      prefix = "models/"
    }
    
    transition {
      days          = 90
      storage_class = "GLACIER"  # 5x cheaper than Standard
    }
    
    expiration {
      days = 365  # Delete after 1 year
    }
  }
}
```

**Cost optimization**:
- **Standard**: $0.023/GB/month (frequent access)
- **Intelligent-Tiering**: Auto-moves between tiers based on access patterns
- **Glacier**: $0.004/GB/month (archive, 3-5 hour retrieval)
- **Glacier Deep Archive**: $0.00099/GB/month (long-term, 12-hour retrieval)

### 3. Amazon EBS (Elastic Block Store)

**What it is**: Block storage volumes for EC2 and SageMaker instances.

**Why we use it**:
- ✅ **Low Latency**: Attached directly to compute instances
- ✅ **High IOPS**: For fast data loading during training
- ✅ **Snapshots**: Backup training data volumes
- ✅ **Encryption**: Hardware-level encryption

**Usage in SageMaker**:
- Training jobs get 30 GB EBS by default
- Can increase to 10 TB for large datasets
- Data is downloaded from S3 to EBS before training starts

```python
# SageMaker training job with custom EBS volume
xgb = XGBoost(
    ...,
    volume_size=100,  # 100 GB EBS volume
    volume_kms_key='arn:aws:kms:...'  # Encrypted with KMS
)
```

---

## 🌐 Networking Services

### 4. Amazon VPC (Virtual Private Cloud)

**What it is**: Isolated virtual network in AWS cloud.

**Why we use it**:
- ✅ **Network Isolation**: SageMaker jobs run in private subnets (no internet access)
- ✅ **Security**: Control inbound/outbound traffic with security groups
- ✅ **Cost Savings**: VPC endpoints avoid data transfer charges
- ✅ **Compliance**: Meet regulatory requirements (HIPAA, PCI-DSS)

**Architecture**:
```
VPC: 10.0.0.0/16 (65,536 IP addresses)
├── Public Subnet (AZ-1): 10.0.1.0/24
│   └── NAT Gateway (for private subnet internet access)
├── Public Subnet (AZ-2): 10.0.2.0/24
│   └── NAT Gateway (high availability)
├── Private Subnet (AZ-1): 10.0.10.0/24
│   ├── SageMaker Training Jobs
│   ├── SageMaker Endpoints
│   └── RDS Database (if used)
└── Private Subnet (AZ-2): 10.0.11.0/24
    ├── SageMaker Training Jobs (HA)
    └── RDS Standby (HA)
```

**Why private subnets**:
- Training jobs cannot be accessed from internet
- Data never leaves AWS network
- Prevents data exfiltration attacks
- Compliance with data residency requirements

**Terraform configuration**:
```hcl
resource "aws_vpc" "mlops" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true
  
  tags = {
    Name = "mlops-vpc-${var.environment}"
  }
}

resource "aws_subnet" "private" {
  count             = 2
  vpc_id            = aws_vpc.mlops.id
  cidr_block        = "10.0.${10 + count.index}.0/24"
  availability_zone = data.aws_availability_zones.available.names[count.index]
  
  tags = {
    Name = "mlops-private-subnet-${count.index + 1}"
    Type = "Private"
  }
}

resource "aws_security_group" "sagemaker" {
  name        = "sagemaker-sg-${var.environment}"
  vpc_id      = aws_vpc.mlops.id
  description = "Security group for SageMaker resources"
  
  # Allow all outbound traffic to VPC endpoints
  egress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = [aws_vpc.mlops.cidr_block]
    description = "HTTPS to VPC endpoints"
  }
  
  # Block all inbound traffic (training jobs don't need inbound)
  # Endpoints will have separate security group
}
```

### 5. VPC Endpoints

**What they are**: Private connections to AWS services without internet gateway.

**Why we use them**:
- ✅ **Security**: Traffic never leaves AWS network
- ✅ **Cost Savings**: No data transfer charges ($0.01/GB savings)
- ✅ **Performance**: Lower latency (private AWS backbone)
- ✅ **Compliance**: Data residency requirements

**Required endpoints for SageMaker**:
```hcl
# S3 endpoint (Gateway type - FREE)
resource "aws_vpc_endpoint" "s3" {
  vpc_id       = aws_vpc.mlops.id
  service_name = "com.amazonaws.${var.region}.s3"
  
  route_table_ids = [aws_route_table.private.id]
  
  tags = {
    Name = "s3-endpoint"
  }
}

# SageMaker API endpoint (Interface type - $0.01/GB)
resource "aws_vpc_endpoint" "sagemaker_api" {
  vpc_id              = aws_vpc.mlops.id
  service_name        = "com.amazonaws.${var.region}.sagemaker.api"
  vpc_endpoint_type   = "Interface"
  subnet_ids          = aws_subnet.private[*].id
  security_group_ids  = [aws_security_group.vpc_endpoints.id]
  private_dns_enabled = true
}

# CloudWatch Logs endpoint
resource "aws_vpc_endpoint" "logs" {
  vpc_id              = aws_vpc.mlops.id
  service_name        = "com.amazonaws.${var.region}.logs"
  vpc_endpoint_type   = "Interface"
  subnet_ids          = aws_subnet.private[*].id
  security_group_ids  = [aws_security_group.vpc_endpoints.id]
  private_dns_enabled = true
}

# ECR endpoint (for pulling Docker images)
resource "aws_vpc_endpoint" "ecr" {
  vpc_id              = aws_vpc.mlops.id
  service_name        = "com.amazonaws.${var.region}.ecr.dkr"
  vpc_endpoint_type   = "Interface"
  subnet_ids          = aws_subnet.private[*].id
  security_group_ids  = [aws_security_group.vpc_endpoints.id]
  private_dns_enabled = true
}
```

**Cost comparison**:
```
Without VPC Endpoints (via Internet Gateway):
- Data transfer out: $0.09/GB (first 10 TB)
- 100 GB/day = $9/day = $270/month

With VPC Endpoints:
- S3 Gateway endpoint: $0 (free)
- Interface endpoints: $0.01/GB + $0.01/hour per AZ
- 100 GB/day = $1/day = $30/month
- Savings: $240/month (88% reduction)
```

---

## 🔒 Security Services

### 6. AWS IAM (Identity and Access Management)

**What it is**: Access control service for AWS resources.

**Why we use it**:
- ✅ **Least Privilege**: Grant minimum permissions required
- ✅ **Audit Trail**: CloudTrail logs all IAM actions
- ✅ **Temporary Credentials**: Roles instead of long-lived keys
- ✅ **MFA**: Multi-factor authentication for sensitive operations

**IAM Roles we create**:

#### a) SageMaker Execution Role
```hcl
resource "aws_iam_role" "sagemaker_execution" {
  name = "SageMakerExecutionRole-${var.environment}"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "sagemaker.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy" "sagemaker_s3_access" {
  name = "sagemaker-s3-access"
  role = aws_iam_role.sagemaker_execution.id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.ml_data.arn,
          "${aws_s3_bucket.ml_data.arn}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:log-group:/aws/sagemaker/*"
      },
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
```

#### b) Data Scientist Role
```hcl
resource "aws_iam_role" "data_scientist" {
  name = "DataScientistRole-${var.environment}"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        AWS = "arn:aws:iam::${var.account_id}:root"
      }
      Condition = {
        StringEquals = {
          "sts:ExternalId" = var.external_id
        }
      }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "data_scientist_sagemaker" {
  role       = aws_iam_role.data_scientist.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSageMakerFullAccess"
}

# Allow passing SageMaker execution role
resource "aws_iam_role_policy" "data_scientist_pass_role" {
  name = "pass-sagemaker-role"
  role = aws_iam_role.data_scientist.id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = "iam:PassRole"
      Resource = aws_iam_role.sagemaker_execution.arn
      Condition = {
        StringEquals = {
          "iam:PassedToService" = "sagemaker.amazonaws.com"
        }
      }
    }]
  })
}
```

### 7. AWS KMS (Key Management Service)

**What it is**: Managed encryption key service.

**Why we use it**:
- ✅ **Centralized Key Management**: Single place to manage encryption keys
- ✅ **Automatic Rotation**: Keys rotated every 365 days
- ✅ **Audit Trail**: All key usage logged in CloudTrail
- ✅ **Compliance**: Meets FIPS 140-2 Level 2 requirements

**Where we encrypt**:
- S3 buckets (datasets, models)
- EBS volumes (training job storage)
- SageMaker endpoints (data at rest)
- RDS database (if used for feature store)

```hcl
resource "aws_kms_key" "mlops" {
  description             = "KMS key for MLOps encryption"
  deletion_window_in_days = 30
  enable_key_rotation     = true
  
  tags = {
    Name = "mlops-key-${var.environment}"
  }
}

resource "aws_kms_alias" "mlops" {
  name          = "alias/mlops-${var.environment}"
  target_key_id = aws_kms_key.mlops.key_id
}

# Grant SageMaker access to use this key
resource "aws_kms_grant" "sagemaker" {
  name              = "sagemaker-grant"
  key_id            = aws_kms_key.mlops.key_id
  grantee_principal = aws_iam_role.sagemaker_execution.arn
  
  operations = [
    "Encrypt",
    "Decrypt",
    "GenerateDataKey"
  ]
}
```

### 8. AWS Secrets Manager

**What it is**: Secure storage for credentials and API keys.

**Why we use it**:
- ✅ **Rotation**: Automatically rotate database passwords
- ✅ **Encryption**: Secrets encrypted with KMS
- ✅ **Audit**: Track secret access in CloudTrail
- ✅ **Versioning**: Keep history of secret values

**Example**: Database credentials for feature store
```hcl
resource "aws_secretsmanager_secret" "db_credentials" {
  name = "mlops/database/credentials-${var.environment}"
  
  kms_key_id = aws_kms_key.mlops.id
  
  tags = {
    Environment = var.environment
  }
}

resource "aws_secretsmanager_secret_version" "db_credentials" {
  secret_id = aws_secretsmanager_secret.db_credentials.id
  
  secret_string = jsonencode({
    username = "mlops_admin"
    password = random_password.db_password.result
    engine   = "postgres"
    host     = aws_db_instance.feature_store[0].address
    port     = 5432
    dbname   = "features"
  })
}

# Automatic rotation every 30 days
resource "aws_secretsmanager_secret_rotation" "db_credentials" {
  secret_id           = aws_secretsmanager_secret.db_credentials.id
  rotation_lambda_arn = aws_lambda_function.rotate_db_password.arn
  
  rotation_rules {
    automatically_after_days = 30
  }
}
```

---

## 📊 Monitoring & Logging

### 9. Amazon CloudWatch

**What it is**: Monitoring and observability service.

**Why we use it**:
- ✅ **Metrics**: Track endpoint latency, invocations, errors
- ✅ **Logs**: Centralized logging from SageMaker jobs
- ✅ **Alarms**: Automated alerts for anomalies
- ✅ **Dashboards**: Visual monitoring of system health

**Metrics we track**:

#### a) SageMaker Endpoint Metrics
```
- ModelLatency: Time to generate prediction
- Invocations: Number of inference requests
- InvocationsPerInstance: Load per instance
- ModelSetupTime: Cold start time
- CPUUtilization: CPU usage percentage
- MemoryUtilization: Memory usage percentage
```

#### b) Training Job Metrics
```
- TrainingTime: Total training duration
- ValidationAccuracy: Model accuracy on validation set
- ObjectiveMetric: Custom metric (e.g., F1 score)
```

**CloudWatch alarms**:
```hcl
# Alert if endpoint latency exceeds 500ms
resource "aws_cloudwatch_metric_alarm" "high_latency" {
  alarm_name          = "sagemaker-high-latency-${var.environment}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "ModelLatency"
  namespace           = "AWS/SageMaker"
  period              = 60
  statistic           = "Average"
  threshold           = 500  # milliseconds
  alarm_description   = "Alert when endpoint latency > 500ms"
  alarm_actions       = [aws_sns_topic.alerts.arn]
  
  dimensions = {
    EndpointName = "diabetes-classifier-${var.environment}"
    VariantName  = "AllTraffic"
  }
}

# Alert if error rate exceeds 1%
resource "aws_cloudwatch_metric_alarm" "high_error_rate" {
  alarm_name          = "sagemaker-high-errors-${var.environment}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "ModelInvocationError"
  namespace           = "/aws/sagemaker/Endpoints"
  period              = 300
  statistic           = "Sum"
  threshold           = 10  # 10 errors in 5 minutes
  alarm_description   = "Alert when error rate is high"
  alarm_actions       = [aws_sns_topic.alerts.arn]
}
```

**CloudWatch Logs**:
```hcl
resource "aws_cloudwatch_log_group" "sagemaker_training" {
  name              = "/aws/sagemaker/TrainingJobs"
  retention_in_days = 30  # Production: 90, Dev: 7
  
  kms_key_id = aws_kms_key.mlops.arn
}

resource "aws_cloudwatch_log_group" "sagemaker_endpoints" {
  name              = "/aws/sagemaker/Endpoints/${var.environment}"
  retention_in_days = 90
  
  kms_key_id = aws_kms_key.mlops.arn
}
```

### 10. Amazon SNS (Simple Notification Service)

**What it is**: Pub/sub messaging service for alerts.

**Why we use it**:
- ✅ **Multi-Channel**: Email, SMS, Slack, PagerDuty
- ✅ **Fan-out**: One alert to multiple recipients
- ✅ **Filtering**: Subscribe to specific alert types
- ✅ **Reliable**: 99.9% SLA

**Alert topics**:
```hcl
# Critical alerts (PagerDuty + Email)
resource "aws_sns_topic" "critical_alerts" {
  name = "mlops-critical-alerts-${var.environment}"
  
  kms_master_key_id = aws_kms_key.mlops.id
}

resource "aws_sns_topic_subscription" "critical_pagerduty" {
  topic_arn = aws_sns_topic.critical_alerts.arn
  protocol  = "https"
  endpoint  = var.pagerduty_endpoint
}

resource "aws_sns_topic_subscription" "critical_email" {
  topic_arn = aws_sns_topic.critical_alerts.arn
  protocol  = "email"
  endpoint  = "ml-oncall@company.com"
}

# Warning alerts (Email + Slack)
resource "aws_sns_topic" "warning_alerts" {
  name = "mlops-warning-alerts-${var.environment}"
}

resource "aws_sns_topic_subscription" "warning_slack" {
  topic_arn = aws_sns_topic.warning_alerts.arn
  protocol  = "lambda"
  endpoint  = aws_lambda_function.slack_notifier.arn
}
```

### 11. AWS CloudTrail

**What it is**: API activity logging for governance and compliance.

**Why we use it**:
- ✅ **Audit Trail**: Who did what, when
- ✅ **Compliance**: Required for SOC 2, HIPAA, PCI-DSS
- ✅ **Security**: Detect unauthorized access attempts
- ✅ **Forensics**: Investigate security incidents

**What gets logged**:
- SageMaker: CreateTrainingJob, CreateEndpoint, UpdateModelPackage
- S3: GetObject, PutObject, DeleteObject
- IAM: CreateUser, AttachUserPolicy
- CloudWatch: PutMetricAlarm, DeleteAlarm

```hcl
resource "aws_cloudtrail" "mlops" {
  name                          = "mlops-trail-${var.environment}"
  s3_bucket_name                = aws_s3_bucket.cloudtrail_logs.id
  include_global_service_events = true
  is_multi_region_trail         = true
  enable_log_file_validation    = true
  
  kms_key_id = aws_kms_key.mlops.arn
  
  event_selector {
    read_write_type           = "All"
    include_management_events = true
    
    # Log S3 data events for ML buckets
    data_resource {
      type   = "AWS::S3::Object"
      values = ["${aws_s3_bucket.ml_data.arn}/*"]
    }
    
    # Log SageMaker events
    data_resource {
      type   = "AWS::SageMaker::TrainingJob"
      values = ["arn:aws:sagemaker:${var.region}:${var.account_id}:training-job/*"]
    }
  }
  
  insight_selector {
    insight_type = "ApiCallRateInsight"  # Detect anomalous API activity
  }
}
```

---

## 💰 Cost Optimization

### 12. Cost Allocation Tags

**Why**: Track costs by environment, team, project.

```hcl
# Enforce tagging on all resources
resource "aws_organizations_policy" "tag_policy" {
  name = "mlops-tag-policy"
  
  content = jsonencode({
    tags = {
      Environment = {
        tag_key = {
          "@@assign" = "Environment"
        }
        tag_value = {
          "@@assign" = ["dev", "staging", "production"]
        }
        enforced_for = {
          "@@assign" = ["sagemaker:*", "s3:*", "ec2:*"]
        }
      }
      CostCenter = {
        tag_key = {
          "@@assign" = "CostCenter"
        }
      }
    }
  })
}
```

### 13. Auto-Shutdown for Dev Resources

**Why**: Dev endpoints cost $0.23/hour = $165/month if left running 24/7.

```hcl
# Lambda function to shutdown dev endpoints after business hours
resource "aws_lambda_function" "auto_shutdown" {
  filename      = "auto_shutdown.zip"
  function_name = "sagemaker-auto-shutdown-${var.environment}"
  role          = aws_iam_role.lambda_exec.arn
  handler       = "index.handler"
  runtime       = "python3.9"
  
  environment {
    variables = {
      ENVIRONMENT = var.environment
    }
  }
}

# Schedule: Shutdown at 7 PM weekdays, startup at 8 AM
resource "aws_cloudwatch_event_rule" "shutdown_schedule" {
  name                = "shutdown-dev-endpoints"
  description         = "Shutdown dev SageMaker endpoints"
  schedule_expression = "cron(0 19 ? * MON-FRI *)"  # 7 PM Mon-Fri
}

resource "aws_cloudwatch_event_target" "shutdown_lambda" {
  rule      = aws_cloudwatch_event_rule.shutdown_schedule.name
  target_id = "lambda"
  arn       = aws_lambda_function.auto_shutdown.arn
  
  input = jsonencode({
    action = "shutdown"
  })
}
```

---

## 🔄 Service Interaction Flow

### End-to-End ML Workflow

```
1. CODE COMMIT (Developer)
   └─> GitHub → GitHub Actions (CI/CD)

2. CI/CD PIPELINE
   ├─> Linting (flake8, black)
   ├─> Unit tests (pytest)
   ├─> Upload code to S3
   └─> Trigger SageMaker Pipeline

3. DATA PREPROCESSING
   ├─> SageMaker Processing Job (SKLearn)
   ├─> Read raw data from S3
   ├─> Data validation & cleaning
   ├─> Feature engineering
   └─> Write processed data to S3

4. MODEL TRAINING
   ├─> SageMaker Training Job (XGBoost)
   ├─> Read processed data from S3
   ├─> Train model with hyperparameters
   ├─> Evaluate on validation set
   └─> Save model artifact to S3

5. MODEL EVALUATION
   ├─> SageMaker Processing Job
   ├─> Calculate metrics (accuracy, F1, ROC-AUC)
   ├─> Generate confusion matrix
   ├─> Check quality gates
   └─> Save evaluation results to S3

6. CONDITIONAL REGISTRATION
   ├─> IF (accuracy >= 0.78 AND f1 >= 0.73 AND roc_auc >= 0.82)
   │   └─> Register model to Model Registry
   └─> ELSE
       └─> Stop pipeline (no registration)

7. MANUAL APPROVAL (Production)
   ├─> Data scientist reviews metrics in console
   ├─> Approves or rejects model
   └─> IF approved → Proceed to deployment

8. MODEL DEPLOYMENT
   ├─> Create SageMaker Endpoint
   ├─> Deploy model from registry
   ├─> Enable data capture
   ├─> Configure auto-scaling (2-10 instances)
   └─> Blue/green or canary deployment

9. MONITORING
   ├─> CloudWatch metrics (latency, errors)
   ├─> Model Monitor (hourly drift detection)
   ├─> CloudWatch alarms
   └─> SNS notifications

10. DRIFT DETECTION & RETRAINING
    ├─> Model Monitor detects drift
    ├─> CloudWatch alarm triggers
    ├─> SNS notification to ML team
    ├─> Lambda triggers new pipeline execution
    └─> Loop back to step 3
```

**Data flow security**:
- All data in transit: TLS 1.2+ encryption
- All data at rest: AES-256 encryption (KMS)
- No data leaves VPC (VPC endpoints)
- All API calls logged (CloudTrail)

---

**Last Updated**: November 2025  
**Maintained By**: MLOps Team
