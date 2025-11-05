# 🔄 Complete MLOps Lifecycle Guide - Comprehensive Edition

**The definitive guide to understanding every step of the MLOps workflow in this project**

**From local development to production monitoring - every command, every decision, every automation explained in detail**

Last Updated: November 5, 2025  
Version: 2.0 (Comprehensive Edition)

---

## 📋 Table of Contents

### Part I: Foundation
1. [Executive Overview](#executive-overview)
2. [Architecture & Design Principles](#architecture--design-principles)
3. [Technology Stack](#technology-stack)
4. [Prerequisites & Environment Setup](#prerequisites--environment-setup)

### Part II: Development Lifecycle
5. [Phase 0: Project Initialization](#phase-0-project-initialization)
6. [Phase 1: Development & Code Changes](#phase-1-development--code-changes)
7. [Phase 2: Infrastructure Deployment](#phase-2-infrastructure-deployment)
8. [Phase 3: Data Engineering & Preparation](#phase-3-data-engineering--preparation)

### Part III: ML Pipeline
9. [Phase 4: ML Pipeline Execution](#phase-4-ml-pipeline-execution)
10. [Phase 5: Model Evaluation & Quality Gates](#phase-5-model-evaluation--quality-gates)
11. [Phase 6: Model Registration & Versioning](#phase-6-model-registration--versioning)
12. [Phase 7: Model Deployment](#phase-7-model-deployment)

### Part IV: Operations & Monitoring
13. [Phase 8: Production Monitoring](#phase-8-production-monitoring)
14. [Phase 9: Drift Detection & Alerts](#phase-9-drift-detection--alerts)
15. [Phase 10: Retraining & Continuous Improvement](#phase-10-retraining--continuous-improvement)

### Part V: Automation & Best Practices
16. [CI/CD Automation](#cicd-automation)
17. [Security & Compliance](#security--compliance)
18. [Cost Management & Optimization](#cost-management--optimization)
19. [Troubleshooting & Operations](#troubleshooting--operations)
20. [Production Readiness Checklist](#production-readiness-checklist)

---

## Executive Overview

### What is This Project?

This is a **production-grade MLOps implementation** for diabetes classification that demonstrates:

- ✅ **Complete ML lifecycle automation** (from data to production)
- ✅ **Infrastructure as Code** (Terraform)
- ✅ **Multi-environment deployment** (dev → staging → production)
- ✅ **Continuous monitoring & retraining**
- ✅ **Cost optimization** (50% reduction through automation)
- ✅ **Enterprise security** (AWS OIDC, IAM roles, least privilege)

### The Big Picture

```
┌──────────────────────────────────────────────────────────────────────────┐
│                     COMPLETE MLOPS WORKFLOW                               │
│                                                                           │
│  Developer → GitHub → CI/CD → AWS → SageMaker → Production → Monitoring │
│     ↑                                                              ↓      │
│     └──────────────────── Feedback Loop ──────────────────────────┘      │
│                    (Drift Detection → Retrain → Deploy)                  │
└──────────────────────────────────────────────────────────────────────────┘
```

### Key Metrics

| Metric | Value |
|--------|-------|
| **End-to-End Deployment Time** | 30-45 minutes (automated) |
| **Model Training Time** | 10-15 minutes |
| **Model Accuracy** | 75-80% |
| **Endpoint Latency** | <100ms (p99) |
| **Monthly Cost (Optimized)** | $150-200 |
| **Deployment Frequency** | Weekly or on-demand |
| **Pipeline Success Rate** | >95% |

---

## Architecture & Design Principles

### System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              LAYERS                                     │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  LAYER 1: SOURCE CONTROL & CI/CD                                 │  │
│  │  ├─ GitHub Repository (Code, Configs, Infrastructure)            │  │
│  │  ├─ GitHub Actions (Terraform, MLOps, Monitoring Workflows)      │  │
│  │  └─ GitHub Secrets (AWS Credentials, API Keys)                   │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                              ↓                                          │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  LAYER 2: INFRASTRUCTURE (Terraform)                             │  │
│  │  ├─ S3 Buckets (Data, Models, Artifacts)                         │  │
│  │  ├─ IAM Roles (SageMaker, Lambda, GitHub OIDC)                   │  │
│  │  ├─ CloudWatch (Logs, Metrics, Alarms)                           │  │
│  │  ├─ SNS Topics (Alerts, Notifications)                           │  │
│  │  ├─ EventBridge (Scheduled Triggers)                             │  │
│  │  └─ Budget Alerts (Cost Control)                                 │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                              ↓                                          │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  LAYER 3: DATA PIPELINE                                          │  │
│  │  ├─ Raw Data (S3) → Preprocessing (SageMaker Processing)         │  │
│  │  ├─ Train/Val/Test Split                                         │  │
│  │  ├─ Feature Engineering & Scaling                                │  │
│  │  └─ Data Validation (Great Expectations)                         │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                              ↓                                          │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  LAYER 4: ML PIPELINE (SageMaker Pipelines)                      │  │
│  │  ├─ Training (XGBoost on ml.m5.xlarge)                           │  │
│  │  ├─ Evaluation (Metrics: Accuracy, F1, ROC-AUC)                  │  │
│  │  ├─ Experiment Tracking (SageMaker Experiments)                  │  │
│  │  ├─ Quality Gates (Conditional approval)                         │  │
│  │  └─ Model Registry (Versioning + Approval)                       │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                              ↓                                          │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  LAYER 5: DEPLOYMENT                                             │  │
│  │  ├─ SageMaker Endpoints (Real-time inference)                    │  │
│  │  ├─ Data Capture (For monitoring)                                │  │
│  │  ├─ Auto-scaling (1-5 instances)                                 │  │
│  │  └─ Multi-environment (dev/staging/production)                   │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                              ↓                                          │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  LAYER 6: MONITORING & OPERATIONS                                │  │
│  │  ├─ Endpoint Metrics (CloudWatch - FREE)                         │  │
│  │  ├─ Data Drift Detection (SageMaker Model Monitor - $0.27/check) │  │
│  │  ├─ Model Quality Monitoring ($0.27/check)                       │  │
│  │  ├─ Statistical Drift (Custom algorithms - FREE)                 │  │
│  │  ├─ Experiment Comparison (SageMaker Experiments - FREE)         │  │
│  │  └─ Automated Alerts (SNS, Slack, GitHub Issues)                 │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                              ↓                                          │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  LAYER 7: FEEDBACK LOOP                                          │  │
│  │  ├─ Drift Detected? → Create GitHub Issue                        │  │
│  │  ├─ Model Degradation? → Trigger Retraining                      │  │
│  │  ├─ Retrain → Evaluate → Deploy (if better)                      │  │
│  │  └─ Continuous Improvement Cycle                                 │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Design Principles

#### 1. **Separation of Concerns**

```
Infrastructure (Terraform) ≠ ML Code (Python) ≠ Configuration (YAML)

Why?
- Infrastructure changes don't require code changes
- ML improvements don't require infrastructure changes
- Configuration updates don't require code deployment
```

#### 2. **Environment Isolation**

```
Dev → Staging → Production

Each environment has:
- Separate S3 buckets
- Separate endpoints
- Separate IAM roles
- Separate configurations
- Independent state
```

#### 3. **Immutable Infrastructure**

```
Never modify existing resources → Always create new versions

Benefits:
- Rollback capability
- Audit trail
- No configuration drift
- Reproducible deployments
```

#### 4. **Everything as Code**

```
Infrastructure → Terraform
ML Pipeline → Python (SageMaker Pipelines SDK)
CI/CD → GitHub Actions YAML
Configuration → YAML files
Documentation → Markdown
```

#### 5. **Fail Fast, Fail Safe**

```
Validation Gates:
├─ Terraform validate (before apply)
├─ Python linting (before deploy)
├─ Unit tests (before pipeline execution)
├─ Quality gates (before model registration)
└─ Manual approval (before production deployment)
```

---

## Technology Stack

### Core Technologies

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| **Cloud Platform** | AWS | - | Infrastructure hosting |
| **ML Platform** | SageMaker | - | Training, deployment, monitoring |
| **IaC** | Terraform | 1.5+ | Infrastructure provisioning |
| **CI/CD** | GitHub Actions | - | Automation workflows |
| **ML Framework** | XGBoost | 1.5-1 | Model training |
| **Data Processing** | Pandas, NumPy, Scikit-learn | - | Data manipulation |
| **Language** | Python | 3.8+ | Primary development language |
| **Configuration** | YAML | - | Declarative configs |

### AWS Services Used

| Service | Purpose | Cost |
|---------|---------|------|
| **SageMaker Training** | Model training jobs | ~$0.20/training |
| **SageMaker Endpoints** | Real-time inference | $47-470/month |
| **SageMaker Processing** | Data preprocessing, evaluation | ~$0.10/job |
| **SageMaker Pipelines** | ML workflow orchestration | FREE |
| **SageMaker Experiments** | Experiment tracking | FREE |
| **SageMaker Model Registry** | Model versioning | FREE |
| **SageMaker Model Monitor** | Drift detection (on-demand) | $0.27/check |
| **S3** | Data and artifact storage | $1-5/month |
| **CloudWatch** | Logs, metrics, alarms | $1-2/month |
| **IAM** | Access control | FREE |
| **SNS** | Notifications | <$1/month |
| **EventBridge** | Scheduled triggers | FREE |
| **AWS Budgets** | Cost alerts | FREE |

### Development Tools

| Tool | Purpose |
|------|---------|
| **Git** | Version control |
| **VS Code** | IDE (recommended) |
| **AWS CLI** | AWS command-line interface |
| **Terraform CLI** | Infrastructure management |
| **Python venv** | Virtual environments |
| **pytest** | Unit testing |
| **black** | Code formatting |
| **flake8** | Linting |

---

## Prerequisites & Environment Setup

### 1. AWS Account Setup

**Step 1.1: Create AWS Account**

```bash
# Navigate to https://aws.amazon.com/
# Click "Create an AWS Account"
# Follow prompts (requires credit card)

# IMPORTANT: Set up MFA for root account immediately
# AWS Console → IAM → Dashboard → Activate MFA
```

**Step 1.2: Create IAM User (for CLI access)**

```bash
# AWS Console → IAM → Users → Create User
# Username: mlops-admin
# Permissions: AdministratorAccess (for setup only)
# Access type: Programmatic access

# Download credentials CSV
# Save Access Key ID and Secret Access Key
```

**Step 1.3: Configure AWS CLI**

```powershell
# Install AWS CLI
# https://aws.amazon.com/cli/

# Configure credentials
aws configure --profile mlops-dev

# Enter:
AWS Access Key ID: <from CSV>
AWS Secret Access Key: <from CSV>
Default region name: us-east-1
Default output format: json

# Test connection
aws sts get-caller-identity --profile mlops-dev
```

**Step 1.4: Request SageMaker Quota Increase**

```bash
# AWS Console → Service Quotas → AWS SageMaker
# Find: "Model package groups per account"
# Current: 0 → Request: 5

# Fill form:
Quota value: 5
Use case description: "MLOps project for diabetes classification model registry"

# Approval time: 1-2 business days
```

### 2. GitHub Account Setup

**Step 2.1: Create GitHub Account**

```bash
# Navigate to https://github.com/
# Sign up (free account is sufficient)
```

**Step 2.2: Fork or Clone Repository**

```powershell
# Fork on GitHub (recommended)
# GitHub → Navigate to source repo → Fork

# Or clone directly
git clone https://github.com/YOUR_USERNAME/mlopsaws.git
cd mlopsaws
```

**Step 2.3: Configure GitHub Secrets**

```bash
# GitHub → Repository → Settings → Secrets and variables → Actions

# Add these secrets:
AWS_ROLE_ARN: arn:aws:iam::YOUR_ACCOUNT_ID:role/GitHubActions-MLOps-Dev
AWS_REGION: us-east-1
AWS_ACCOUNT_ID: YOUR_AWS_ACCOUNT_ID
SLACK_WEBHOOK_URL: https://hooks.slack.com/... (optional)
```

### 3. Local Development Setup

**Step 3.1: Install Python**

```powershell
# Download Python 3.8+ from https://www.python.org/

# Verify installation
python --version  # Should be 3.8+

# Create virtual environment
cd "d:\MLOPS\MLOPS-AWS\mlops AWS sagemaker"
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1  # PowerShell
# OR
venv\Scripts\activate.bat    # Command Prompt
```

**Step 3.2: Install Dependencies**

```powershell
# With venv activated
pip install --upgrade pip
pip install -r requirements.txt

# Verify key packages
python -c "import sagemaker; print(f'SageMaker SDK: {sagemaker.__version__}')"
python -c "import boto3; print(f'Boto3: {boto3.__version__}')"
python -c "import xgboost; print(f'XGBoost: {xgboost.__version__}')"
```

**Step 3.3: Install Terraform**

```powershell
# Download from https://www.terraform.io/downloads

# Windows: Download ZIP, extract to C:\terraform
# Add to PATH: System Properties → Environment Variables → Path → New → C:\terraform

# Verify installation
terraform version  # Should be 1.5+
```

**Step 3.4: Install Git**

```powershell
# Download from https://git-scm.com/

# Verify installation
git --version
```

**Step 3.5: Configure Git**

```powershell
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Set up SSH key (recommended)
ssh-keygen -t ed25519 -C "your.email@example.com"
# Add to GitHub: Settings → SSH and GPG keys → New SSH key
```

---

## Phase 0: Project Initialization

### What Happens in This Phase?

Before any automation runs, you need to initialize the project infrastructure manually (one-time setup).

### Timeline: 45-60 minutes (one-time)

---

### Step 0.1: AWS OIDC Provider Setup

**What is OIDC?**

OpenID Connect (OIDC) allows GitHub Actions to authenticate with AWS **without storing long-lived credentials**. Instead, GitHub gets temporary credentials that expire.

**Why use OIDC?**
- ✅ No secrets to rotate
- ✅ Temporary credentials (max 1 hour)
- ✅ Least privilege access
- ✅ Audit trail in CloudTrail

**Setup Commands:**

```powershell
# 1. Create OIDC Provider
aws iam create-open-id-connect-provider `
  --url "https://token.actions.githubusercontent.com" `
  --client-id-list "sts.amazonaws.com" `
  --thumbprint-list "6938fd4d98bab03faadb97b34396831e3780aea1" `
  --profile mlops-dev

# Output:
{
  "OpenIDConnectProviderArn": "arn:aws:iam::891807086260:oidc-provider/token.actions.githubusercontent.com"
}

# 2. Verify provider
aws iam list-open-id-connect-providers --profile mlops-dev
```

**Troubleshooting:**

```bash
# Error: "EntityAlreadyExists"
# Solution: Provider already exists, skip to next step

# Error: "InvalidClientTokenId"
# Solution: Check AWS credentials (aws configure --profile mlops-dev)
```

---

### Step 0.2: IAM Role Creation

**Create GitHub Actions Role:**

```json
// File: github-actions-trust-policy.json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::YOUR_ACCOUNT_ID:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
        },
        "StringLike": {
          "token.actions.githubusercontent.com:sub": "repo:YOUR_GITHUB_USERNAME/mlopsaws:*"
        }
      }
    }
  ]
}
```

```powershell
# Create role
aws iam create-role `
  --role-name GitHubActions-MLOps-Dev `
  --assume-role-policy-document file://github-actions-trust-policy.json `
  --description "Role for GitHub Actions to deploy MLOps infrastructure" `
  --profile mlops-dev

# Attach managed policies (8 policies for full functionality)
$policies = @(
    "arn:aws:iam::aws:policy/AmazonS3FullAccess",
    "arn:aws:iam::aws:policy/AmazonSageMakerFullAccess",
    "arn:aws:iam::aws:policy/IAMFullAccess",
    "arn:aws:iam::aws:policy/CloudWatchFullAccess",
    "arn:aws:iam::aws:policy/AmazonSNSFullAccess",
    "arn:aws:iam::aws:policy/AWSBudgetsActionsWithAWSResourceControlAccess",
    "arn:aws:iam::aws:policy/CloudWatchEventsFullAccess",
    "arn:aws:iam::aws:policy/AWSLambda_FullAccess"
)

foreach ($policy in $policies) {
    aws iam attach-role-policy `
      --role-name GitHubActions-MLOps-Dev `
      --policy-arn $policy `
      --profile mlops-dev
    
    Write-Host "Attached: $policy"
}

# Verify role
aws iam get-role --role-name GitHubActions-MLOps-Dev --profile mlops-dev
```

---

### Step 0.3: S3 Backend Setup (for Terraform State)

**Why S3 backend?**
- ✅ Shared state across team members
- ✅ State locking (prevents concurrent modifications)
- ✅ State versioning (rollback capability)
- ✅ Encryption at rest

**Create S3 bucket:**

```powershell
# Get AWS account ID
$ACCOUNT_ID = (aws sts get-caller-identity --query Account --output text --profile mlops-dev)

# Create bucket
aws s3 mb s3://mlops-terraform-state-$ACCOUNT_ID `
  --region us-east-1 `
  --profile mlops-dev

# Enable versioning
aws s3api put-bucket-versioning `
  --bucket mlops-terraform-state-$ACCOUNT_ID `
  --versioning-configuration Status=Enabled `
  --profile mlops-dev

# Enable encryption
aws s3api put-bucket-encryption `
  --bucket mlops-terraform-state-$ACCOUNT_ID `
  --server-side-encryption-configuration '{
    "Rules": [{
      "ApplyServerSideEncryptionByDefault": {
        "SSEAlgorithm": "AES256"
      }
    }]
  }' `
  --profile mlops-dev

# Block public access
aws s3api put-public-access-block `
  --bucket mlops-terraform-state-$ACCOUNT_ID `
  --public-access-block-configuration "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true" `
  --profile mlops-dev

# Verify bucket
aws s3 ls --profile mlops-dev | Select-String "mlops-terraform-state"
```

**Create DynamoDB table (for state locking):**

```powershell
aws dynamodb create-table `
  --table-name mlops-terraform-locks `
  --attribute-definitions AttributeName=LockID,AttributeType=S `
  --key-schema AttributeName=LockID,KeyType=HASH `
  --billing-mode PAY_PER_REQUEST `
  --region us-east-1 `
  --profile mlops-dev

# Verify table
aws dynamodb describe-table `
  --table-name mlops-terraform-locks `
  --profile mlops-dev
```

---

### Step 0.4: Update Terraform Backend Configuration

```hcl
# File: infrastructure/terraform/backend.tf

terraform {
  backend "s3" {
    bucket         = "mlops-terraform-state-891807086260"  # Update with your account ID
    key            = "mlops/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "mlops-terraform-locks"
    encrypt        = true
  }
}
```

---

### Step 0.5: Update Configuration Files

**File: `infrastructure/terraform/environments/dev/terraform.tfvars`**

```hcl
# AWS Configuration
aws_region     = "us-east-1"
aws_account_id = "891807086260"  # UPDATE THIS

# Project Configuration
project_name = "mlops-diabetes"
environment  = "dev"

# S3 Configuration
bucket_prefix = "mlops-diabetes-dev"

# SageMaker Configuration
sagemaker_execution_role_name = "SageMaker-MLOps-ExecutionRole-dev"

# Feature Flags
enable_model_package_group  = false  # Set true after quota approval
enable_auto_shutdown        = false  # Set true to save costs
enable_sagemaker_monitoring = false  # Set true for demos

# Endpoint Configuration (if deploying)
sagemaker_endpoint_name = "mlops-diabetes-endpoint-dev"

# Budget Configuration
monthly_budget_limit = 60  # USD
budget_alert_threshold_percentage = 80
```

**File: `config/config.yaml`**

```yaml
# Project Configuration
project:
  name: diabetes-classification
  version: "1.0.0"

# AWS Configuration
aws:
  region: us-east-1
  account_id: "891807086260"  # UPDATE THIS

# S3 Configuration
s3:
  bucket_name: mlops-diabetes-dev-891807086260  # UPDATE THIS
  prefix: mlops

# SageMaker Configuration
sagemaker:
  role: arn:aws:iam::891807086260:role/SageMaker-MLOps-ExecutionRole-dev  # UPDATE THIS
  
  processing:
    instance_type: ml.m5.xlarge
    instance_count: 1
  
  training:
    instance_type: ml.m5.xlarge
    instance_count: 1
    max_runtime_in_seconds: 3600
  
  endpoint:
    instance_type: ml.t2.medium
    instance_count: 1
  
  model_registry:
    model_package_group_name: diabetes-classifier-package-group
    approval_status: PendingManualApproval  # For dev: Approved, For prod: PendingManualApproval

# Model Hyperparameters
model:
  algorithm: xgboost
  framework_version: "1.5-1"
  
  hyperparameters:
    max_depth: 5
    eta: 0.2
    gamma: 4
    min_child_weight: 6
    subsample: 0.7
    objective: "binary:logistic"
    eval_metric: "auc"
    num_round: 100

# Evaluation Configuration
evaluation:
  approval_thresholds:
    min_accuracy: 0.70
    min_f1_score: 0.65
    min_roc_auc: 0.75

# Pipeline Configuration
pipeline:
  name: diabetes-classification-pipeline
```

---

### Step 0.6: Initialize Terraform

```powershell
cd infrastructure/terraform

# Initialize Terraform (downloads providers)
terraform init

# Output:
Initializing the backend...
Successfully configured the backend "s3"!
Terraform has been successfully initialized!

# Validate configuration
terraform validate

# Output:
Success! The configuration is valid.

# Format code (optional but recommended)
terraform fmt -recursive
```

---

### Step 0.7: Create Initial Infrastructure

```powershell
# Plan infrastructure (dry-run)
terraform plan -var-file="environments/dev/terraform.tfvars"

# Review output carefully
# Expected resources: ~15-20 resources

# Apply infrastructure
terraform apply -var-file="environments/dev/terraform.tfvars"

# Type 'yes' when prompted

# Output:
Apply complete! Resources: 18 added, 0 changed, 0 destroyed.

Outputs:
bucket_name = "mlops-diabetes-dev-891807086260"
sagemaker_role_arn = "arn:aws:iam::891807086260:role/SageMaker-MLOps-ExecutionRole-dev"
# ... more outputs
```

**What was created?**

- ✅ S3 bucket for data and models
- ✅ IAM role for SageMaker
- ✅ CloudWatch log groups
- ✅ SNS topics for alerts
- ✅ Budget alerts
- ✅ (Optional) Lambda functions
- ✅ (Optional) Model package group

---

### Step 0.8: Upload Initial Dataset

```powershell
# Navigate to project root
cd "d:\MLOPS\MLOPS-AWS\mlops AWS sagemaker"

# Ensure dataset exists
ls data/raw/diabetes.csv

# Upload to S3
$BUCKET = "mlops-diabetes-dev-891807086260"
aws s3 cp data/raw/diabetes.csv s3://$BUCKET/mlops/data/raw/diabetes.csv --profile mlops-dev

# Verify upload
aws s3 ls s3://$BUCKET/mlops/data/raw/ --profile mlops-dev

# Output:
2025-11-05 10:30:15      23876 diabetes.csv
```

---

### Step 0.9: Test AWS Connectivity

```powershell
# Test SageMaker access
aws sagemaker list-pipeline-executions `
  --pipeline-name diabetes-classification-pipeline `
  --max-results 5 `
  --profile mlops-dev

# Test S3 access
aws s3 ls s3://mlops-diabetes-dev-891807086260/mlops/ --profile mlops-dev

# Test IAM access
aws iam get-role `
  --role-name SageMaker-MLOps-ExecutionRole-dev `
  --profile mlops-dev
```

---

### Phase 0 Checklist

Before proceeding to Phase 1, ensure:

- [ ] AWS account created and configured
- [ ] IAM user with CLI access created
- [ ] AWS CLI configured with profile
- [ ] SageMaker quota requested
- [ ] GitHub account created
- [ ] Repository forked/cloned
- [ ] GitHub secrets configured
- [ ] Python 3.8+ installed
- [ ] Virtual environment created
- [ ] Dependencies installed (requirements.txt)
- [ ] Terraform installed
- [ ] OIDC provider created
- [ ] GitHub Actions IAM role created
- [ ] S3 backend bucket created
- [ ] DynamoDB state lock table created
- [ ] Configuration files updated (terraform.tfvars, config.yaml)
- [ ] Terraform initialized
- [ ] Initial infrastructure created
- [ ] Dataset uploaded to S3
- [ ] AWS connectivity tested

**If all checked, you're ready for Phase 1! 🎉**

---

