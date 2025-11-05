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
16. [Phase 11: Model Inference (Real-World Usage)](#phase-11-model-inference-real-world-usage)

### Part V: Automation & Best Practices
17. [CI/CD Automation](#cicd-automation)
18. [Security & Compliance](#security--compliance)
19. [Cost Management & Optimization](#cost-management--optimization)
20. [Troubleshooting & Operations](#troubleshooting--operations)
21. [Production Readiness Checklist](#production-readiness-checklist)
22. [What Else Are We Missing?](#what-else-are-we-missing)

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


# Phase 1: Development & Code Changes

**Duration:** 15-30 minutes per feature  
**Frequency:** Multiple times per week  
**Cost:** $0 (development is local)

## 1.1 Overview

Phase 1 is where data scientists and ML engineers make code changes to improve model accuracy, add new features, fix bugs, update configurations, and optimize performance. This phase follows Git best practices with feature branches and pull requests.

---

## 1.2 Git Workflow

### Step 1.1: Create Feature Branch

```bash
# Ensure you're on main and up to date
git checkout main
git pull origin main

# Create and checkout new feature branch
git checkout -b feature/improve-model-accuracy
```

**Expected Output:**
```
Switched to a new branch 'feature/improve-model-accuracy'
```

---

### Step 1.2: Make Code Changes

**Example A) Update Hyperparameters** (`src/training/train.py`):

```python
# After (tuning for better performance)
parser.add_argument('--max-depth', type=int, default=7)
parser.add_argument('--eta', type=float, default=0.1)
```

**Example B) Add Feature Engineering** (`src/preprocessing/preprocess.py`):

```python
def add_bmi_categories(df):
    '''Categorize BMI into risk groups'''
    df['BMI_Category'] = pd.cut(
        df['BMI'], 
        bins=[0, 18.5, 25, 30, 100],
        labels=['Underweight', 'Normal', 'Overweight', 'Obese']
    )
    return df
```

---

### Step 1.3: Test Locally

```powershell
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Run unit tests
python -m pytest tests/ -v

# Run linting
flake8 src/ --max-line-length=100

# Format code automatically
black src/
```

**Expected Output:**
```
===== 15 passed, 0 failed in 2.34s =====
All done!   
10 files reformatted.
```

---

### Step 1.4: Commit Changes

```bash
git add .
git commit -m "feat: Improve model accuracy with hyperparameter tuning

- Increase max_depth from 5 to 7
- Decrease learning rate (eta) from 0.2 to 0.1
- Expected impact: +2-3% accuracy improvement"
```

### Step 1.5: Push to GitHub

```bash
git push -u origin feature/improve-model-accuracy
```

### Step 1.6: Create Pull Request

1. Go to GitHub repository
2. Click "Compare & pull request"
3. Fill PR description with changes, testing notes, expected impact
4. Assign reviewers and add labels
5. Click "Create pull request"

### Step 1.7: Code Review & Merge

After approval and CI checks pass, merge to main branch using "Squash and merge" option.

---

## 1.3 What Happens After Merge?

Automated CI/CD pipelines trigger:
- Terraform workflow (if infrastructure changed)
- ML pipeline workflow (if ML code changed)
- Monitoring workflow (always runs)

---

# Phase 2: Infrastructure Deployment

**Duration:** 5-15 minutes (automated)  
**Frequency:** As needed  
**Cost:** Depends on resources (~$50-300/month)

## 2.1 Terraform Workflow (Automated)

### Step 2.1: Validation Phase

```bash
terraform fmt -check -recursive
terraform validate
tfsec infrastructure/terraform/
```

### Step 2.2: Terraform Plan (DEV)

```bash
terraform plan -var-file="environments/dev/terraform.tfvars" -out=tfplan-dev
```

**Expected Output:**
```
Plan: 12 to add, 0 to change, 0 to destroy.
```

### Step 2.3: Terraform Apply (DEV)

```bash
terraform apply -auto-approve tfplan-dev
```

**Deployment creates:**
- S3 buckets (data, models, artifacts)
- SageMaker resources (pipelines, model registry)
- IAM roles and policies
- CloudWatch dashboards and alarms
- SNS topics for notifications

**Deployment Time:** 5-10 minutes

---

## 2.2 Multi-Environment Deployment

| Environment | Trigger | Approval | Cost/Month |
|------------|---------|----------|------------|
| **DEV** | Auto on push | None | $50-100 |
| **STAGING** | Manual/Auto | Required | $100-150 |
| **PRODUCTION** | Manual only | 2 approvers | $150-300 |

---

# Phase 3: Data Engineering & Preparation

**Duration:** 10-20 minutes (automated)  
**Frequency:** Every pipeline run  
**Cost:** $2-5 per job

## 3.1 Data Validation

```python
def validate_data(df):
    # Check: No empty dataset
    assert len(df) > 0
    
    # Check: Expected columns present
    # Check: Data types correct
    # Check: Value ranges valid
    # Check: Class distribution reasonable
    # Check: Missing values < 50%
    
    return validation_results
```

## 3.2 Preprocessing Steps

1. **Load data from S3**
2. **Validate data quality**
3. **Handle missing values** (median imputation, forward fill)
4. **Engineer features** (BMI categories, age groups, risk scores)
5. **Train/val/test split** (60/20/20, stratified)
6. **Scale features** (StandardScaler)
7. **Save to S3** (XGBoost CSV format)

**Output:**
```
s3://bucket/processed/train.csv
s3://bucket/processed/validation.csv  
s3://bucket/processed/test.csv
s3://bucket/processed/scaler.pkl
s3://bucket/processed/metadata.json
```

---

# Phase 4: ML Pipeline Execution

**Duration:** 15-25 minutes (automated)  
**Frequency:** On code changes or manual trigger  
**Cost:** $3-8 per pipeline run

## 4.1 SageMaker Pipeline Steps

### Step 4.1: Preprocessing Step
- Instance: ml.m5.xlarge
- Duration: 5-10 minutes
- Cost: ~$0.24
- Output: Processed train/val/test data

### Step 4.2: Training Step
- Instance: ml.m5.xlarge
- Algorithm: XGBoost 1.5-1
- Duration: 10-15 minutes
- Cost: ~$0.48
- Output: Trained model artifacts

### Step 4.3: Evaluation Step
- Instance: ml.m5.xlarge
- Duration: 2-3 minutes
- Cost: ~$0.10
- Output: Metrics (accuracy, precision, recall, F1, AUC)

### Step 4.4: Model Registration Step
- Registers model in SageMaker Model Registry
- Attaches metadata and metrics
- Sets approval status
- Duration: 1 minute
- Cost: FREE

---

## 4.2 Training Execution

```python
# XGBoost training with hyperparameters
params = {
    'max_depth': 7,
    'eta': 0.1,
    'gamma': 4,
    'min_child_weight': 6,
    'subsample': 0.8,
    'objective': 'binary:logistic',
    'eval_metric': 'auc'
}

bst = xgb.train(
    params=params,
    dtrain=dtrain,
    num_boost_round=150,
    evals=[(dtrain, 'train'), (dval, 'validation')],
    early_stopping_rounds=10
)
```

**Expected Training Output:**
```
[0] train-auc:0.7234  validation-auc:0.7123
[10] train-auc:0.8456  validation-auc:0.8234
...
[95] train-auc:0.9234  validation-auc:0.8567
Best iteration: 85
```

---

## 4.3 Model Evaluation

```python
# Calculate metrics
accuracy = 0.76
precision = 0.74
recall = 0.72
f1_score = 0.73
roc_auc = 0.85

# Quality gate thresholds
MIN_ACCURACY = 0.70
MIN_AUC = 0.75

if accuracy >= MIN_ACCURACY and roc_auc >= MIN_AUC:
    # Register model
    register_model_in_registry()
else:
    # Skip registration
    logger.warning("Model quality below threshold")
```

---

# Phase 5: Model Evaluation & Quality Gates

**Duration:** 2-5 minutes  
**Frequency:** Every successful training run  
**Cost:** Included in training cost

## 5.1 Metrics Calculated

| Metric | Threshold | Current | Status |
|--------|-----------|---------|--------|
| Accuracy |  0.70 | 0.76 |  PASS |
| Precision |  0.65 | 0.74 |  PASS |
| Recall |  0.60 | 0.72 |  PASS |
| F1-Score |  0.65 | 0.73 |  PASS |
| ROC-AUC |  0.75 | 0.85 |  PASS |

**Decision:**  Register model

---

# Phase 6: Model Registration & Versioning

**Duration:** 1-2 minutes  
**Frequency:** After quality gates pass  
**Cost:** FREE

## 6.1 Registration Process

```python
model_package = sagemaker_client.create_model_package(
    ModelPackageGroupName='diabetes-classifier-package-group',
    ModelPackageDescription='XGBoost diabetes classifier v1.2',
    ModelApprovalStatus='PendingManualApproval',  # or 'Approved'
    InferenceSpecification={
        'Containers': [{
            'Image': training_image,
            'ModelDataUrl': model_s3_uri
        }],
        'SupportedContentTypes': ['text/csv'],
        'SupportedResponseMIMETypes': ['application/json']
    },
    ModelMetrics={
        'ModelQuality': {
            'Statistics': {
                'S3Uri': metrics_s3_uri
            }
        }
    }
)
```

**Model Version:** Automatically incremented (v1, v2, v3...)

---

# Phase 7: Model Deployment

**Duration:** 10-15 minutes  
**Frequency:** After model approval  
**Cost:** $30-150/month (endpoint hosting)

## 7.1 Deployment Steps

### Step 7.1: Get Approved Model

```python
response = sagemaker_client.list_model_packages(
    ModelPackageGroupName='diabetes-classifier-package-group',
    ModelApprovalStatus='Approved',
    SortBy='CreationTime',
    SortOrder='Descending',
    MaxResults=1
)

model_package_arn = response['ModelPackageSummaryList'][0]['ModelPackageArn']
```

### Step 7.2: Create Endpoint

```python
predictor = model.deploy(
    initial_instance_count=1,
    instance_type='ml.t2.medium',
    endpoint_name='diabetes-classifier-dev',
    serializer=CSVSerializer(),
    deserializer=JSONDeserializer()
)
```

**Deployment time:** 10-15 minutes

### Step 7.3: Test Endpoint

```python
test_data = [[6, 148, 72, 35, 0, 33.6, 0.627, 50]]
response = predictor.predict(test_data)

# Output: {'predictions': [0.78]}  # 78% probability of diabetes
```

---

## 7.2 Auto-Scaling Configuration

```python
autoscaling_client.put_scaling_policy(
    PolicyName='diabetes-endpoint-scaling-policy',
    ServiceNamespace='sagemaker',
    ResourceId='endpoint/diabetes-classifier/variant/AllTraffic',
    ScalableDimension='sagemaker:variant:DesiredInstanceCount',
    PolicyType='TargetTrackingScaling',
    TargetTrackingScalingPolicyConfiguration={
        'TargetValue': 1000.0,  # Target invocations per instance
        'PredefinedMetricSpecification': {
            'PredefinedMetricType': 'SageMakerVariantInvocationsPerInstance'
        },
        'ScaleInCooldown': 300,
        'ScaleOutCooldown': 60
    }
)
```

---

# Phase 8: Production Monitoring

**Duration:** Continuous  
**Frequency:** 24/7  
**Cost:** $10-30/month

## 8.1 Monitoring Components

### Component 1: CloudWatch Metrics (FREE)
- Endpoint invocations
- Model latency (p50, p90, p99)
- Error rate
- Instance CPU/memory

### Component 2: Model Quality Monitoring ($0.27/check)
- Ground truth labeling
- Performance degradation detection
- Accuracy tracking over time

### Component 3: Data Drift Detection ($0.27/check)
- Statistical drift (KS test, PSI, Chi-Square)
- Feature distribution changes
- Baseline comparison

### Component 4: Custom Metrics (FREE)
- Prediction distribution
- Business KPIs
- Custom alerts

---

## 8.2 CloudWatch Dashboards

Pre-configured dashboard includes:
- Endpoint invocations (requests/minute)
- Model latency (milliseconds)
- Error rate (4xx, 5xx)
- Drift score (0-1)
- CPU/memory utilization

**Access:**
```
https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#dashboards:name=MLOps-Diabetes-Dev
```

---

# Phase 9: Drift Detection & Alerts

**Duration:** 5-10 minutes per check  
**Frequency:** Hourly or daily  
**Cost:** $0.27 per monitoring job

## 9.1 Drift Types Monitored

1. **Data Drift:** Input feature distributions change
2. **Prediction Drift:** Model output distribution changes
3. **Concept Drift:** Relationship between features and target changes
4. **Model Quality Drift:** Performance degrades over time

## 9.2 Alert Configuration

```python
# SNS notification when drift detected
cloudwatch.put_metric_alarm(
    AlarmName='diabetes-model-drift-alarm',
    MetricName='FeatureDrift',
    Namespace='MLOps/Diabetes',
    Statistic='Average',
    Period=3600,
    EvaluationPeriods=1,
    Threshold=0.3,  # Drift score threshold
    ComparisonOperator='GreaterThanThreshold',
    AlarmActions=[sns_topic_arn]
)
```

**Alert destinations:**
- Email (SNS)
- Slack webhook
- PagerDuty (production)
- GitHub Issues (auto-created)

---

# Phase 10: Retraining & Continuous Improvement

**Duration:** 20-30 minutes (automated)  
**Frequency:** Weekly or triggered by drift  
**Cost:** Same as Phase 4 ($3-8)

## 10.1 Retraining Triggers

1. **Scheduled:** Weekly/monthly retraining
2. **Drift-based:** When drift score > 0.3
3. **Performance-based:** When accuracy drops > 5%
4. **Data-based:** When new training data available

## 10.2 Retraining Workflow

```python
def trigger_retraining(reason):
    # 1. Fetch latest data from S3
    # 2. Run preprocessing pipeline
    # 3. Train new model
    # 4. Evaluate against current production model
    # 5. If better, register new model
    # 6. Update endpoint with new model
    # 7. Monitor for 24 hours
    # 8. If stable, mark as production
    
    logger.info(f"Retraining triggered: {reason}")
    pipeline.start()
```

---

# CI/CD Automation

## GitHub Actions Workflows

### Workflow 1: Terraform CI/CD

**File:** `.github/workflows/terraform.yml`

**Triggers:**
- Push to main/develop (Terraform files changed)
- Manual dispatch

**Jobs:**
1. Validate  Format check, validation, security scan
2. Plan (DEV)  Calculate infrastructure changes
3. Apply (DEV)  Deploy to dev environment
4. Plan (Staging)  Calculate staging changes
5. Apply (Staging)  Deploy to staging (manual approval)
6. Plan (Production)  Calculate prod changes
7. Apply (Production)  Deploy to prod (manual approval, 2 reviewers)

**Estimated runtime:** 5-15 minutes per environment

---

### Workflow 2: ML Pipeline CI/CD

**File:** `.github/workflows/ml_pipeline.yml` (if exists)

**Triggers:**
- Push to main (ML code changed)
- Manual dispatch

**Jobs:**
1. Lint & Test  Run pytest, flake8, black
2. Trigger Pipeline  Start SageMaker Pipeline
3. Wait for Completion  Poll pipeline status
4. Evaluate Results  Check quality gates
5. Deploy Model  If approved, deploy to endpoint
6. Smoke Test  Verify endpoint health

---

### Workflow 3: Monitoring & Drift Detection

**File:** `.github/workflows/monitoring_pipeline.yml`

**Triggers:**
- Schedule (cron: daily at 6 AM UTC)
- Manual dispatch

**Jobs:**
1. Check Model Metrics  Query CloudWatch
2. Run Drift Detection  SageMaker Model Monitor
3. Analyze Results  Calculate drift scores
4. Send Alerts  If drift detected, notify team
5. Trigger Retraining  If drift > threshold

---

# Security & Compliance

## Security Best Practices

 **IAM Least Privilege:**
- Separate roles for each component
- No root account usage
- MFA enforced
- Temporary credentials (OIDC)

 **Encryption:**
- S3 server-side encryption (SSE-S3)
- SageMaker encryption at rest
- TLS 1.2+ for data in transit

 **Access Control:**
- S3 bucket policies
- VPC endpoints (optional)
- CloudTrail audit logging
- IAM Access Analyzer

 **Secrets Management:**
- GitHub Secrets for credentials
- AWS Secrets Manager for API keys
- No hardcoded credentials in code
- Regular secret rotation

---

# Cost Management & Optimization

## Cost Optimization Strategies

1. **Use Spot Instances for Training** (-70% cost)
```python
train_args = TrainingStep(
    estimator=xgboost_estimator,
    use_spot_instances=True,
    max_wait=7200
)
```

2. **Stop Dev Endpoints When Not in Use**
```powershell
aws sagemaker delete-endpoint --endpoint-name diabetes-classifier-dev
```

3. **Use Smaller Instances for Dev**
- Dev: ml.t2.medium ($0.065/hour)
- Prod: ml.m5.large ($0.134/hour)

4. **Enable S3 Lifecycle Policies**
```
Move old data to Glacier after 90 days
Delete temporary files after 30 days
```

5. **Use Reserved Instances for Production** (-40% cost)

6. **Monitor with AWS Cost Explorer**
- Set budget alerts at 80% threshold
- Tag resources by environment
- Review monthly cost reports

---

# Troubleshooting & Operations

## Common Issues

### Issue: Pipeline Fails with "Resource Limit Exceeded"

**Error:**
```
ResourceLimitExceeded: The account-level service limit 'ml.m5.xlarge for training job usage' is 0
```

**Solution:**
Request quota increase in AWS Service Quotas console.

---

### Issue: Endpoint Returns 500 Errors

**Symptoms:**
- Endpoint invocations fail
- CloudWatch shows ModelInvocationError

**Diagnosis:**
```powershell
aws logs tail /aws/sagemaker/Endpoints/diabetes-classifier --follow
```

**Common Causes:**
- Input data format mismatch
- Model serialization issue
- Insufficient memory

**Solution:**
Check input format matches model expectations (CSV, JSON, etc.)

---

### Issue: Drift Detection Always Triggers

**Symptoms:**
- Drift score always > threshold
- Constant retraining alerts

**Diagnosis:**
Check baseline data distribution vs current data.

**Solution:**
- Update baseline with recent data
- Adjust drift threshold (0.3  0.5)
- Use different statistical test

---

# Production Readiness Checklist

Before deploying to production:

## Infrastructure
- [ ] Multi-AZ deployment configured
- [ ] Auto-scaling enabled and tested
- [ ] Backup and disaster recovery plan
- [ ] Monitoring dashboards configured
- [ ] All alarms tested and validated
- [ ] Cost budgets and alerts set

## Security
- [ ] Least privilege IAM policies
- [ ] Encryption enabled (at rest and in transit)
- [ ] Secrets rotated
- [ ] CloudTrail logging enabled
- [ ] Compliance requirements met
- [ ] Security scan passed (no critical issues)

## Model Quality
- [ ] Model accuracy meets requirements (70%)
- [ ] Quality gates configured and tested
- [ ] A/B testing plan (if applicable)
- [ ] Rollback procedure documented
- [ ] Model registry approval workflow

## Monitoring
- [ ] All metrics being collected
- [ ] Drift detection configured
- [ ] Alert routing tested
- [ ] On-call rotation established
- [ ] Incident response runbook created

## Documentation
- [ ] Architecture diagrams updated
- [ ] API documentation complete
- [ ] Runbooks for common operations
- [ ] Troubleshooting guides
- [ ] Team training completed

## Testing
- [ ] Unit tests passing (100%)
- [ ] Integration tests passing
- [ ] Load testing completed
- [ ] Endpoint smoke tests passing
- [ ] Rollback tested

## Compliance
- [ ] Data privacy requirements met
- [ ] Model explainability documented
- [ ] Bias testing completed
- [ ] Regulatory approvals obtained

---

# Phase 11: Model Inference (Real-World Usage)

**Duration:** <100ms per request (real-time)  
**Frequency:** Continuous (production traffic)  
**Cost:** Included in endpoint hosting cost

## 11.1 Overview

Once the model is deployed (Phase 7), **inference** is how you actually use it to make predictions. There are multiple ways to invoke the endpoint depending on your use case.

### Inference Flow

```
Client Application
    │
    ├─ Prepare input data (patient features)
    │
    ▼
HTTP/HTTPS Request → SageMaker Endpoint
    │
    ├─ Input validation
    ├─ Data preprocessing (scaling)
    ├─ Model prediction
    ├─ Output formatting
    │
    ▼
JSON/CSV Response ← Client receives prediction
```

---

## 11.2 Inference Methods

### Method 1: Direct API Call (Python SDK) ⭐ RECOMMENDED

**Use Case:** Python applications, Jupyter notebooks, backend services

**Example:**

```python
import boto3
import json

# Initialize SageMaker runtime client
sagemaker_runtime = boto3.client('sagemaker-runtime', region_name='us-east-1')

# Prepare input data (8 diabetes features)
# [Pregnancies, Glucose, BloodPressure, SkinThickness, Insulin, BMI, DiabetesPedigreeFunction, Age]
payload = {
    "instances": [
        [6, 148, 72, 35, 0, 33.6, 0.627, 50]  # Patient 1
    ]
}

# Invoke endpoint
response = sagemaker_runtime.invoke_endpoint(
    EndpointName='diabetes-classifier-dev',
    ContentType='application/json',
    Accept='application/json',
    Body=json.dumps(payload)
)

# Parse response
result = json.loads(response['Body'].read().decode())
print(json.dumps(result, indent=2))
```

**Expected Response:**

```json
{
  "predictions": [
    {
      "prediction": 1,
      "label": "Diabetes",
      "probability": 0.78,
      "confidence": 0.78
    }
  ],
  "model_version": "1.0",
  "timestamp": "2025-11-05 14:23:45"
}
```

**Interpretation:**
- **Prediction:** 1 (patient HAS diabetes)
- **Probability:** 0.78 (78% confidence)
- **Label:** "Diabetes" (human-readable)

---

### Method 2: AWS CLI (Command Line)

**Use Case:** Quick testing, shell scripts, automation

```powershell
# Prepare data (CSV format)
$payload = "6,148,72,35,0,33.6,0.627,50"

# Invoke endpoint
aws sagemaker-runtime invoke-endpoint `
  --endpoint-name diabetes-classifier-dev `
  --content-type text/csv `
  --accept application/json `
  --body $payload `
  --region us-east-1 `
  output.json

# View result
Get-Content output.json
```

**Expected Output (output.json):**
```json
{
  "predictions": [{"prediction": 1, "label": "Diabetes", "probability": 0.78}]
}
```

---

### Method 3: Batch Transform (Large-Scale Processing)

**Use Case:** Process thousands of records at once (batch predictions)

**When to use:**
- ✅ Millions of records to score
- ✅ Non-real-time predictions (e.g., nightly batch job)
- ✅ Cost optimization (no persistent endpoint needed)

**Example:**

```python
from sagemaker.transformer import Transformer

# Initialize transformer
transformer = Transformer(
    model_name='diabetes-model-v1',
    instance_count=1,
    instance_type='ml.m5.xlarge',
    output_path='s3://bucket/batch-predictions/',
    accept='text/csv'
)

# Run batch transform job
transformer.transform(
    data='s3://bucket/input-data/patients.csv',
    content_type='text/csv',
    split_type='Line'
)

# Wait for completion
transformer.wait()

# Results written to S3
# s3://bucket/batch-predictions/patients.csv.out
```

**Cost Comparison:**

| Method | Cost | Best For |
|--------|------|----------|
| **Real-time Endpoint** | $0.065/hour (24/7) | <1000 predictions/day |
| **Batch Transform** | $0.269/hour (on-demand) | >10,000 predictions/batch |

---

### Method 4: Lambda Function (Serverless)

**Use Case:** Triggered predictions, event-driven, API Gateway integration

**Architecture:**

```
API Gateway → Lambda → SageMaker Endpoint → Response
```

**Lambda Function:**

```python
import json
import boto3
import os

def lambda_handler(event, context):
    """
    Lambda function to invoke SageMaker endpoint
    Triggered by API Gateway or other AWS services
    """
    # Parse input from API Gateway
    body = json.loads(event['body'])
    features = body['features']
    
    # Invoke SageMaker endpoint
    sagemaker_runtime = boto3.client('sagemaker-runtime')
    
    response = sagemaker_runtime.invoke_endpoint(
        EndpointName=os.environ['ENDPOINT_NAME'],
        ContentType='application/json',
        Body=json.dumps({"instances": [features]})
    )
    
    # Parse prediction
    result = json.loads(response['Body'].read().decode())
    
    # Return to API Gateway
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'  # CORS
        },
        'body': json.dumps(result)
    }
```

**API Gateway Request:**

```bash
curl -X POST https://api-id.execute-api.us-east-1.amazonaws.com/prod/predict \
  -H "Content-Type: application/json" \
  -d '{
    "features": [6, 148, 72, 35, 0, 33.6, 0.627, 50]
  }'
```

**Response:**
```json
{
  "predictions": [{"prediction": 1, "label": "Diabetes", "probability": 0.78}]
}
```

**Benefits:**
- ✅ No server management
- ✅ Auto-scaling
- ✅ Pay per request ($0.20 per 1M requests)
- ✅ Easy API integration

---

## 11.3 Input Data Formats

### Format 1: JSON (Recommended)

**Single prediction:**

```json
{
  "instances": [
    [6, 148, 72, 35, 0, 33.6, 0.627, 50]
  ]
}
```

**Multiple predictions:**

```json
{
  "instances": [
    [6, 148, 72, 35, 0, 33.6, 0.627, 50],
    [1, 85, 66, 29, 0, 26.6, 0.351, 31],
    [8, 183, 64, 0, 0, 23.3, 0.672, 32]
  ]
}
```

**Named features:**

```json
{
  "features": {
    "Pregnancies": 6,
    "Glucose": 148,
    "BloodPressure": 72,
    "SkinThickness": 35,
    "Insulin": 0,
    "BMI": 33.6,
    "DiabetesPedigreeFunction": 0.627,
    "Age": 50
  }
}
```

---

### Format 2: CSV

**Single prediction:**
```
6,148,72,35,0,33.6,0.627,50
```

**Multiple predictions:**
```
6,148,72,35,0,33.6,0.627,50
1,85,66,29,0,26.6,0.351,31
8,183,64,0,0,23.3,0.672,32
```

---

## 11.4 Custom Inference Code

The project uses a **custom inference handler** (`src/deployment/inference.py`) that provides:

### Feature 1: Automatic Scaling

The handler includes a scaler that was saved during training:

```python
def predict_fn(input_data, model_dict):
    model = model_dict['model']
    scaler = model_dict.get('scaler')
    
    # Apply scaling (same as training)
    if scaler is not None:
        input_data = scaler.transform(input_data)
    
    # Make prediction
    predictions = model.predict(xgb.DMatrix(input_data))
    
    return predictions
```

**Why this matters:**
- Input data must be scaled exactly as during training
- Scaler is automatically loaded and applied
- No manual preprocessing needed by caller

---

### Feature 2: Multiple Output Formats

```python
def output_fn(predictions, response_content_type):
    if response_content_type == 'application/json':
        return json.dumps({
            'prediction': int(pred),
            'label': 'Diabetes' if pred == 1 else 'No Diabetes',
            'probability': float(prob),
            'confidence': float(prob) if pred == 1 else float(1 - prob)
        })
    elif response_content_type == 'text/csv':
        return f"{pred},{prob}"
```

**Supported outputs:**
- JSON (detailed response with labels)
- CSV (simple prediction + probability)

---

### Feature 3: Error Handling

```python
try:
    predictions = model.predict(input_data)
except Exception as e:
    logger.error(f"Prediction failed: {str(e)}")
    return {
        'error': str(e),
        'status': 'failed'
    }
```

---

## 11.5 Production Inference Patterns

### Pattern 1: Synchronous API (Real-Time)

**Use Case:** User-facing applications, dashboards, mobile apps

```python
# Web app backend
@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    
    # Invoke SageMaker
    response = sagemaker_runtime.invoke_endpoint(
        EndpointName='diabetes-classifier-prod',
        ContentType='application/json',
        Body=json.dumps({"instances": [data['features']]})
    )
    
    result = json.loads(response['Body'].read().decode())
    
    return jsonify(result)
```

**Latency:** <100ms  
**Throughput:** 1000+ requests/second (with auto-scaling)

---

### Pattern 2: Asynchronous Queue (High Volume)

**Use Case:** Background processing, high-volume predictions

```
SQS Queue → Lambda → SageMaker → DynamoDB/S3
```

```python
import boto3

sqs = boto3.client('sqs')
sagemaker_runtime = boto3.client('sagemaker-runtime')

# Process messages from queue
while True:
    messages = sqs.receive_message(QueueUrl=queue_url, MaxNumberOfMessages=10)
    
    for msg in messages.get('Messages', []):
        # Parse patient data
        data = json.loads(msg['Body'])
        
        # Predict
        response = sagemaker_runtime.invoke_endpoint(
            EndpointName='diabetes-classifier-prod',
            Body=json.dumps({"instances": [data['features']]})
        )
        
        # Store result
        result = json.loads(response['Body'].read())
        dynamodb.put_item(TableName='predictions', Item=result)
        
        # Delete message
        sqs.delete_message(QueueUrl=queue_url, ReceiptHandle=msg['ReceiptHandle'])
```

---

### Pattern 3: Streaming (Real-Time Events)

**Use Case:** IoT devices, continuous monitoring

```
Kinesis Stream → Lambda → SageMaker → CloudWatch
```

---

## 11.6 Performance & Monitoring

### Endpoint Metrics (CloudWatch)

**Automatically tracked:**

| Metric | Description | Threshold |
|--------|-------------|-----------|
| **Invocations** | Total requests | Monitor for traffic patterns |
| **ModelLatency** | Prediction time | Alert if >100ms (p99) |
| **Overhead Latency** | Infrastructure time | Alert if >50ms |
| **Invocation4XXErrors** | Client errors | Alert if >1% |
| **Invocation5XXErrors** | Server errors | Alert if >0.1% |
| **CPUUtilization** | Compute usage | Scale up if >80% |
| **MemoryUtilization** | Memory usage | Scale up if >80% |

---

### Logging & Debugging

**View endpoint logs:**

```powershell
# Stream logs
aws logs tail /aws/sagemaker/Endpoints/diabetes-classifier-dev --follow

# Search for errors
aws logs filter-log-events `
  --log-group-name /aws/sagemaker/Endpoints/diabetes-classifier-dev `
  --filter-pattern "ERROR"
```

**Example log output:**

```
2025-11-05 14:23:45 INFO Loading model from /opt/ml/model
2025-11-05 14:23:46 INFO Model loaded successfully
2025-11-05 14:23:50 INFO Processing input with content type: application/json
2025-11-05 14:23:50 INFO Input data shape: (1, 8)
2025-11-05 14:23:50 INFO Input data scaled
2025-11-05 14:23:50 INFO Predictions made for 1 samples
2025-11-05 14:23:50 INFO Response: {"prediction": 1, "probability": 0.78}
```

---

## 11.7 Security & Authentication

### IAM-Based Authentication

**Required permissions for caller:**

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "sagemaker:InvokeEndpoint"
      ],
      "Resource": [
        "arn:aws:sagemaker:us-east-1:*:endpoint/diabetes-classifier-*"
      ]
    }
  ]
}
```

---

### VPC Endpoints (Private Access)

**For enhanced security:**

```hcl
# Terraform configuration
resource "aws_vpc_endpoint" "sagemaker_runtime" {
  vpc_id              = aws_vpc.main.id
  service_name        = "com.amazonaws.us-east-1.sagemaker.runtime"
  vpc_endpoint_type   = "Interface"
  subnet_ids          = aws_subnet.private[*].id
  security_group_ids  = [aws_security_group.sagemaker_endpoint.id]
}
```

**Benefits:**
- Traffic stays within VPC (no internet)
- Reduced latency
- Enhanced security
- Compliance with regulations

---

## 11.8 Cost Optimization for Inference

### Strategy 1: Auto-Scaling

**Scale based on traffic:**

```python
# Only scale up during business hours
autoscaling_client.put_scaling_policy(
    PolicyName='business-hours-scaling',
    TargetTrackingScalingPolicyConfiguration={
        'TargetValue': 100.0,  # Target invocations per instance
        'ScaleInCooldown': 300,  # 5 min cooldown before scale down
        'ScaleOutCooldown': 60   # 1 min cooldown before scale up
    }
)
```

**Cost Savings:** 50-70% during off-peak hours

---

### Strategy 2: Serverless Inference

**For sporadic traffic:**

```python
from sagemaker.serverless import ServerlessInferenceConfig

serverless_config = ServerlessInferenceConfig(
    memory_size_in_mb=2048,  # 2GB
    max_concurrency=10       # Max concurrent invocations
)

model.deploy(
    serverless_inference_config=serverless_config,
    endpoint_name='diabetes-serverless'
)
```

**Cost:**
- $0 when idle (no requests)
- $0.20 per 1M requests + compute time
- Best for <100 requests/hour

---

### Strategy 3: Multi-Model Endpoints

**Host multiple models on same endpoint:**

```python
# Cost savings when hosting 5+ models
# Share same compute instances
# Pay only for instances, not per model
```

**Savings:** Up to 90% for multiple model scenarios

---

## 11.9 Testing Inference Locally

### Local Testing (Before Deployment)

```python
# Test inference handler locally
from src.deployment.inference import model_fn, predict_fn, input_fn, output_fn

# Load model
model_dict = model_fn('models/')

# Prepare input
sample_data = json.dumps({
    "instances": [[6, 148, 72, 35, 0, 33.6, 0.627, 50]]
})

# Test prediction pipeline
input_data = input_fn(sample_data, 'application/json')
predictions = predict_fn(input_data, model_dict)
response = output_fn(predictions, 'application/json')

print(response)
```

**Expected Output:**
```json
{
  "predictions": [
    {
      "prediction": 1,
      "label": "Diabetes",
      "probability": 0.78,
      "confidence": 0.78
    }
  ]
}
```

---

## 11.10 Inference Troubleshooting

### Issue: 4xx Errors (Client Error)

**Error:**
```json
{
  "message": "Could not parse request body into json: Expecting value: line 1 column 1 (char 0)"
}
```

**Cause:** Invalid JSON format

**Solution:**
```python
# Ensure valid JSON
import json
payload = json.dumps({"instances": [[...]]})  # Always use json.dumps
```

---

### Issue: 5xx Errors (Server Error)

**Error:**
```
ModelError: An error occurred (ModelError) when calling the InvokeEndpoint operation
```

**Cause:** Model inference failed (e.g., wrong input shape)

**Diagnosis:**

```powershell
# Check CloudWatch logs
aws logs tail /aws/sagemaker/Endpoints/diabetes-classifier-dev --follow
```

**Common causes:**
- Wrong number of features (expected 8, got 10)
- Missing scaling
- Model file corrupted

**Solution:**
```python
# Verify input shape matches training
# Expected: (n_samples, 8)
assert input_data.shape[1] == 8, f"Expected 8 features, got {input_data.shape[1]}"
```

---

### Issue: High Latency (>500ms)

**Symptoms:**
- Slow predictions
- CloudWatch shows high ModelLatency

**Diagnosis:**

```powershell
# Check endpoint utilization
aws cloudwatch get-metric-statistics `
  --namespace AWS/SageMaker `
  --metric-name CPUUtilization `
  --dimensions Name=EndpointName,Value=diabetes-classifier-dev `
  --start-time 2025-11-05T00:00:00Z `
  --end-time 2025-11-05T23:59:59Z `
  --period 300 `
  --statistics Average
```

**Solutions:**
1. **Scale up:** Add more instances
2. **Upgrade instance:** ml.t2.medium → ml.m5.large
3. **Optimize model:** Reduce model size, quantization
4. **Enable caching:** Cache frequent predictions

---

## 11.11 Phase 11 Checklist

- [ ] Endpoint deployed and InService
- [ ] Test prediction successful (Python SDK)
- [ ] Test prediction successful (AWS CLI)
- [ ] Input validation working
- [ ] Output format correct
- [ ] Scaling configured (if production)
- [ ] CloudWatch metrics tracking
- [ ] Logging enabled and accessible
- [ ] Error handling tested
- [ ] Latency within SLA (<100ms)
- [ ] Security/IAM permissions configured
- [ ] Cost monitoring active
- [ ] Documentation for API consumers
- [ ] Integration tests passing

---

# What Else Are We Missing?

## ✅ Currently Covered (Phases 0-11)

1. ✅ **Project Initialization** - AWS setup, Terraform, GitHub
2. ✅ **Development Workflow** - Git, PRs, code review
3. ✅ **Infrastructure Deployment** - Terraform, multi-env
4. ✅ **Data Engineering** - Validation, preprocessing, feature engineering
5. ✅ **ML Pipeline** - Training, evaluation, registration
6. ✅ **Model Deployment** - Endpoints, auto-scaling
7. ✅ **Monitoring** - CloudWatch, drift detection
8. ✅ **Retraining** - Automated triggers
9. ✅ **CI/CD** - GitHub Actions workflows
10. ✅ **Security** - IAM, OIDC, encryption
11. ✅ **Cost Management** - Optimization strategies
12. ✅ **Inference** - Real-world predictions (NEW!)

---

## 🔶 Potentially Missing (Advanced Topics)

### 1. Model Explainability (SHAP, LIME)

**Purpose:** Understand why model made specific prediction

**Implementation:**

```python
import shap

# Create explainer
explainer = shap.TreeExplainer(model)

# Explain prediction
shap_values = explainer.shap_values(X_test)

# Visualize
shap.summary_plot(shap_values, X_test, feature_names=feature_names)
```

**When to add:** For healthcare/finance compliance

---

### 2. A/B Testing (Canary Deployment)

**Purpose:** Test new model against production model

**Implementation:**

```python
# Deploy with traffic splitting
endpoint_config = {
    'ProductionVariants': [
        {
            'VariantName': 'ModelA',
            'ModelName': 'diabetes-v1',
            'InitialInstanceCount': 2,
            'InitialVariantWeight': 0.9  # 90% traffic
        },
        {
            'VariantName': 'ModelB',
            'ModelName': 'diabetes-v2',
            'InitialInstanceCount': 1,
            'InitialVariantWeight': 0.1  # 10% traffic
        }
    ]
}
```

**When to add:** Before full production deployment of new model

---

### 3. Model Versioning & Rollback

**Purpose:** Quick rollback to previous model version

**Implementation:**

```python
# List model versions
versions = sagemaker_client.list_model_packages(
    ModelPackageGroupName='diabetes-classifier',
    SortBy='CreationTime'
)

# Rollback to previous version
previous_model_arn = versions['ModelPackageSummaryList'][1]['ModelPackageArn']

# Update endpoint with previous model
update_endpoint(endpoint_name='diabetes-prod', model_package_arn=previous_model_arn)
```

**When to add:** Production deployments

---

### 4. Data Quality Monitoring

**Purpose:** Detect bad input data before prediction

**Implementation:**

```python
def validate_input(features):
    """Validate input before prediction"""
    assert len(features) == 8, "Expected 8 features"
    assert all(isinstance(f, (int, float)) for f in features), "All features must be numeric"
    assert features[1] >= 0, "Glucose must be positive"
    assert features[5] > 0, "BMI must be positive"
    
    return True
```

**When to add:** If receiving poor-quality user input

---

### 5. Shadow Mode Testing

**Purpose:** Test new model without affecting production

**Implementation:**

```python
# Production endpoint serves users
prod_response = invoke_endpoint('diabetes-prod', data)

# Shadow endpoint logs predictions but doesn't serve
shadow_response = invoke_endpoint('diabetes-shadow', data)

# Compare predictions
log_comparison(prod_response, shadow_response)
```

**When to add:** Before switching to new model

---

### 6. Feature Store Integration

**Purpose:** Centralized feature management

**Implementation:**

```python
from sagemaker.feature_store.feature_group import FeatureGroup

# Create feature group
feature_group = FeatureGroup(
    name='diabetes-features',
    sagemaker_session=sagemaker_session
)

# Store features
feature_group.ingest(data_frame, max_workers=3)

# Retrieve for training
features = feature_group.athena_query().run(
    query_string='SELECT * FROM "diabetes-features" WHERE age > 30'
)
```

**When to add:** Multiple models using same features

---

### 7. Model Performance SLAs

**Purpose:** Define and monitor service level agreements

**SLA Example:**

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Availability** | 99.9% | Endpoint uptime |
| **Latency (p99)** | <100ms | CloudWatch metrics |
| **Error Rate** | <0.1% | 5xx errors |
| **Accuracy** | ≥75% | Model quality monitoring |

**Implementation:**

```python
# CloudWatch alarm for SLA breach
cloudwatch.put_metric_alarm(
    AlarmName='SLA-Breach-Latency',
    MetricName='ModelLatency',
    Threshold=100,  # ms
    EvaluationPeriods=3,
    ComparisonOperator='GreaterThanThreshold',
    AlarmActions=[sns_topic_arn]
)
```

**When to add:** Production deployments with customer commitments

---

### 8. Disaster Recovery & Backup

**Purpose:** Recover from outages, data loss

**Implementation:**

```bash
# Backup strategy
1. S3 versioning: Enabled ✅
2. Model artifacts: Replicated to us-west-2
3. Terraform state: Backed up to separate bucket
4. DynamoDB point-in-time recovery: Enabled
5. Multi-region endpoint: Optional (cost: +100%)
```

**When to add:** Mission-critical production systems

---

### 9. Bias Detection & Fairness

**Purpose:** Ensure model doesn't discriminate

**Implementation:**

```python
from sagemaker import clarify

# Bias detection
clarify_processor = clarify.SageMakerClarifyProcessor(...)

clarify_processor.run_bias(
    data_config=data_config,
    bias_config=bias_config,
    model_config=model_config
)
```

**When to add:** Healthcare, finance, hiring ML applications

---

### 10. Model Cards (Documentation)

**Purpose:** Document model details for stakeholders

**Example Model Card:**

```markdown
# Diabetes Classification Model Card

**Model Version:** 1.0  
**Training Date:** 2025-11-05  
**Training Data:** 768 patients, 8 features  
**Performance:** 76% accuracy, 0.85 AUC  
**Use Case:** Predict diabetes risk  
**Limitations:** Not for clinical diagnosis  
**Ethical Considerations:** Balanced dataset, no demographic bias detected  
```

**When to add:** Regulated industries, compliance requirements

---

## 📋 Recommendation: What to Add Next

**For Learning/Demo Projects:**
✅ Current setup is comprehensive  
🟡 Optional: Model explainability (SHAP)

**For Production Systems:**
🔴 **Must add:** A/B testing, rollback procedures, SLA monitoring  
🟡 **Should add:** Feature store, bias detection, disaster recovery  
🟢 **Nice to have:** Shadow mode, model cards

---

# Conclusion

**You now have a complete, production-ready MLOps pipeline!**

This guide covered all 10 phases plus CI/CD, security, cost management, and troubleshooting. 

**Total setup time:** 2-4 hours  
**Monthly cost (dev):** $50-100  
**Monthly cost (production):** $150-300

**Next steps:**
1. Execute Phase 0 (setup)
2. Deploy infrastructure (Phase 2)
3. Run your first pipeline (Phases 3-4)
4. Monitor and improve (Phases 8-10)

**Questions?** Check TROUBLESHOOTING.md or create a GitHub issue.

** Happy MLOps Engineering! **
