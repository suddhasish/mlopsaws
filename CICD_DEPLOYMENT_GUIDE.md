# 🚀 CI/CD Deployment Guide - GitHub Actions to AWS

## 📋 Complete End-to-End Guide for Automated Infrastructure & MLOps Pipeline Deployment

**Version:** 2.0 - GitHub Actions Deployment  
**Last Updated:** November 4, 2025  
**Prerequisites:** AWS Account, GitHub Repository  
**Deployment Method:** 100% Automated via GitHub Actions

---

## 🎯 What This Guide Covers

This guide replaces manual/local Terraform deployments with **fully automated CI/CD pipelines** using GitHub Actions. You'll set up:

1. **Automated Infrastructure Deployment** - Terraform via GitHub Actions
2. **Automated MLOps Pipeline** - SageMaker training/deployment via GitHub Actions
3. **Zero Manual Steps** - Everything triggered by Git commits
4. **Multi-Environment** - Separate dev/staging/production workflows
5. **Security Best Practices** - OIDC authentication, secret management

---

## 📊 Deployment Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     GITHUB REPOSITORY                        │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐│
│  │   develop      │  │     main       │  │   Manual       ││
│  │   branch       │  │    branch      │  │  Workflow      ││
│  └────────┬───────┘  └────────┬───────┘  └────────┬───────┘│
│           │                   │                    │         │
└───────────┼───────────────────┼────────────────────┼─────────┘
            │                   │                    │
            ▼                   ▼                    ▼
┌───────────────────┐ ┌────────────────┐ ┌────────────────────┐
│  DEV ENVIRONMENT  │ │  STAGING ENV   │ │  PRODUCTION ENV    │
│  ┌─────────────┐  │ │  ┌──────────┐  │ │  ┌──────────────┐ │
│  │ Terraform   │  │ │  │Terraform │  │ │  │  Terraform   │ │
│  │ Auto-Apply  │  │ │  │  Plan    │  │ │  │Manual Approve│ │
│  └─────────────┘  │ │  └──────────┘  │ │  └──────────────┘ │
│  ┌─────────────┐  │ │  ┌──────────┐  │ │  ┌──────────────┐ │
│  │  MLOps      │  │ │  │  MLOps   │  │ │  │    MLOps     │ │
│  │  Pipeline   │  │ │  │ Pipeline │  │ │  │   Pipeline   │ │
│  └─────────────┘  │ │  └──────────┘  │ │  └──────────────┘ │
└───────────────────┘ └────────────────┘ └────────────────────┘
         │                     │                      │
         └─────────────────────┴──────────────────────┘
                               │
                               ▼
                        ┌─────────────┐
                        │  AWS CLOUD  │
                        └─────────────┘
```

---

## 📋 TABLE OF CONTENTS

1. [Prerequisites](#1-prerequisites)
2. [AWS Account Setup for OIDC](#2-aws-account-setup-for-oidc)
3. [GitHub Repository Setup](#3-github-repository-setup)
4. [Configure GitHub Secrets](#4-configure-github-secrets)
5. [Understanding Workflows](#5-understanding-workflows)
6. [First Deployment](#6-first-deployment)
7. [MLOps Pipeline Automation](#7-mlops-pipeline-automation)
8. [Monitoring & Validation](#8-monitoring--validation)
9. [Production Deployment](#9-production-deployment)
10. [Troubleshooting](#10-troubleshooting)

---

## 1️⃣ Prerequisites

### ✅ Required Accounts & Tools

**AWS Account:**
- [ ] Active AWS account with billing enabled
- [ ] Admin access or IAM user with sufficient permissions
- [ ] Budget alerts configured ($50-100 for dev)
- [ ] MFA enabled on root account

**GitHub Account:**
- [ ] GitHub account (free or paid)
- [ ] Repository created for this project
- [ ] Admin access to repository settings

**Local Development:**
- [ ] Git installed and configured
- [ ] Text editor (VS Code recommended)
- [ ] AWS CLI v2 (for verification only)
- [ ] Basic understanding of YAML and GitHub Actions

**Knowledge:**
- [ ] Basic Git operations (commit, push, pull)
- [ ] Basic AWS concepts (IAM, S3, SageMaker)
- [ ] Understanding of CI/CD principles

---

## 2️⃣ AWS Account Setup for OIDC

### Why OIDC Instead of Access Keys?

**Traditional Method (NOT RECOMMENDED):**
```
AWS Access Keys → Stored in GitHub Secrets → Security Risk
- Keys can be leaked in logs
- Keys don't expire
- Hard to rotate
- Broad permissions
```

**OIDC Method (RECOMMENDED):**
```
GitHub Actions → AWS STS → Temporary Credentials
- No long-lived credentials
- Automatic expiration (1 hour)
- Scoped permissions per workflow
- Audit trail via CloudTrail
```

### Step 2.1: Create OIDC Identity Provider in AWS

**Duration:** 5 minutes

```powershell
# Login to AWS Console
# Navigate to: https://console.aws.amazon.com/iam/

# Step 1: Create Identity Provider
# IAM → Identity providers → Add provider
```

**Provider Configuration:**
- **Provider type:** OpenID Connect
- **Provider URL:** `https://token.actions.githubusercontent.com`
- **Audience:** `sts.amazonaws.com`

**AWS CLI Method:**
```powershell
aws iam create-open-id-connect-provider \
  --url https://token.actions.githubusercontent.com \
  --client-id-list sts.amazonaws.com \
  --thumbprint-list 6938fd4d98bab03faadb97b34396831e3780aea1
```

**✅ Checkpoint:** Identity provider appears in IAM console

### Step 2.2: Create IAM Role for GitHub Actions

**Duration:** 10 minutes

**Create Trust Policy File:**

```powershell
# Create trust-policy.json
@"
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::ACCOUNT_ID:oidc-provider/token.actions.githubusercontent.com"
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
"@ | Out-File -FilePath trust-policy.json -Encoding utf8

# Replace ACCOUNT_ID with your AWS account ID
# Replace YOUR_GITHUB_USERNAME with your GitHub username
```

**Create IAM Role:**
```powershell
# Get your AWS account ID
$accountId = aws sts get-caller-identity --query Account --output text

# Replace placeholders in trust policy
(Get-Content trust-policy.json) `
  -replace 'ACCOUNT_ID', $accountId `
  -replace 'YOUR_GITHUB_USERNAME', 'suddhasish' `
  -replace 'mlopsaws', 'mlopsaws' | Set-Content trust-policy.json

# Create role
aws iam create-role \
  --role-name GitHubActions-MLOps-Role \
  --assume-role-policy-document file://trust-policy.json \
  --description "Role for GitHub Actions to deploy MLOps infrastructure"

# Attach permissions policies
aws iam attach-role-policy \
  --role-name GitHubActions-MLOps-Role \
  --policy-arn arn:aws:iam::aws:policy/AdministratorAccess

# ⚠️ NOTE: AdministratorAccess is for initial setup
# For production, use least-privilege policies (see Step 2.3)
```

**✅ Checkpoint:** Role created with ARN like:
```
arn:aws:iam::123456789012:role/GitHubActions-MLOps-Role
```

### Step 2.3: Create Least-Privilege Policies (Production)

**Duration:** 15 minutes

Instead of `AdministratorAccess`, create specific policies:

**Terraform Deployment Policy:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "TerraformStateAccess",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:ListBucket",
        "s3:DeleteObject"
      ],
      "Resource": [
        "arn:aws:s3:::mlops-terraform-state-*",
        "arn:aws:s3:::mlops-terraform-state-*/*"
      ]
    },
    {
      "Sid": "TerraformStateLocking",
      "Effect": "Allow",
      "Action": [
        "dynamodb:GetItem",
        "dynamodb:PutItem",
        "dynamodb:DeleteItem"
      ],
      "Resource": "arn:aws:dynamodb:*:*:table/mlops-terraform-locks"
    },
    {
      "Sid": "InfrastructureDeployment",
      "Effect": "Allow",
      "Action": [
        "s3:CreateBucket",
        "s3:DeleteBucket",
        "s3:PutBucketPolicy",
        "s3:PutBucketEncryption",
        "s3:PutBucketVersioning",
        "s3:PutBucketPublicAccessBlock",
        "iam:CreateRole",
        "iam:DeleteRole",
        "iam:AttachRolePolicy",
        "iam:DetachRolePolicy",
        "iam:PutRolePolicy",
        "iam:DeleteRolePolicy",
        "iam:GetRole",
        "iam:PassRole",
        "sagemaker:*",
        "sns:*",
        "cloudwatch:*",
        "logs:*",
        "lambda:*",
        "events:*",
        "budgets:*",
        "kms:CreateKey",
        "kms:CreateAlias",
        "kms:DescribeKey",
        "kms:PutKeyPolicy",
        "ec2:CreateVpc",
        "ec2:DeleteVpc",
        "ec2:CreateSubnet",
        "ec2:DeleteSubnet",
        "ec2:CreateSecurityGroup",
        "ec2:DeleteSecurityGroup",
        "ec2:CreateVpcEndpoint",
        "ec2:DeleteVpcEndpoint",
        "ec2:Describe*"
      ],
      "Resource": "*"
    }
  ]
}
```

**Save as:** `github-actions-terraform-policy.json`

```powershell
aws iam create-policy \
  --policy-name GitHubActions-Terraform-Policy \
  --policy-document file://github-actions-terraform-policy.json

# Attach to role
aws iam attach-role-policy \
  --role-name GitHubActions-MLOps-Role \
  --policy-arn arn:aws:iam::ACCOUNT_ID:policy/GitHubActions-Terraform-Policy
```

**MLOps Pipeline Policy:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "SageMakerFullAccess",
      "Effect": "Allow",
      "Action": "sagemaker:*",
      "Resource": "*"
    },
    {
      "Sid": "S3DataAccess",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:ListBucket",
        "s3:DeleteObject"
      ],
      "Resource": [
        "arn:aws:s3:::mlops-diabetes-*",
        "arn:aws:s3:::mlops-diabetes-*/*"
      ]
    },
    {
      "Sid": "PassRoleToSageMaker",
      "Effect": "Allow",
      "Action": "iam:PassRole",
      "Resource": "arn:aws:iam::*:role/mlops-diabetes-sagemaker-execution-*",
      "Condition": {
        "StringEquals": {
          "iam:PassedToService": "sagemaker.amazonaws.com"
        }
      }
    },
    {
      "Sid": "CloudWatchLogs",
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents",
        "logs:DescribeLogStreams"
      ],
      "Resource": "arn:aws:logs:*:*:log-group:/aws/sagemaker/*"
    }
  ]
}
```

**Save as:** `github-actions-mlops-policy.json`

```powershell
aws iam create-policy \
  --policy-name GitHubActions-MLOps-Policy \
  --policy-document file://github-actions-mlops-policy.json

aws iam attach-role-policy \
  --role-name GitHubActions-MLOps-Role \
  --policy-arn arn:aws:iam::ACCOUNT_ID:policy/GitHubActions-MLOps-Policy
```

### Step 2.4: Create Separate Roles for Each Environment

**Best Practice:** One role per environment for isolation

```powershell
# Dev Environment Role
aws iam create-role \
  --role-name GitHubActions-MLOps-Dev \
  --assume-role-policy-document file://trust-policy-dev.json

# Staging Environment Role
aws iam create-role \
  --role-name GitHubActions-MLOps-Staging \
  --assume-role-policy-document file://trust-policy-staging.json

# Production Environment Role (most restrictive)
aws iam create-role \
  --role-name GitHubActions-MLOps-Prod \
  --assume-role-policy-document file://trust-policy-prod.json
```

**trust-policy-dev.json** (only triggers from `develop` branch):
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::ACCOUNT_ID:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
        },
        "StringLike": {
          "token.actions.githubusercontent.com:sub": "repo:suddhasish/mlopsaws:ref:refs/heads/develop"
        }
      }
    }
  ]
}
```

**trust-policy-prod.json** (only manual workflow dispatch):
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::ACCOUNT_ID:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com",
          "token.actions.githubusercontent.com:sub": "repo:suddhasish/mlopsaws:ref:refs/heads/main"
        }
      }
    }
  ]
}
```

**✅ Checkpoint:** Three IAM roles created (dev, staging, prod)

---

## 3️⃣ GitHub Repository Setup

### Step 3.1: Fork or Clone Repository

**Duration:** 5 minutes

```powershell
# Option 1: Clone existing repository
git clone https://github.com/suddhasish/mlopsaws.git
cd mlopsaws

# Option 2: Initialize new repository
git init
git remote add origin https://github.com/YOUR_USERNAME/mlopsaws.git
```

### Step 3.2: Create Branch Structure

```powershell
# Create develop branch
git checkout -b develop
git push -u origin develop

# Create staging branch (optional)
git checkout -b staging
git push -u origin staging

# Back to main
git checkout main
```

**Branch Strategy:**
```
develop  → Auto-deploys to DEV environment
main     → Auto-deploys to STAGING, manual approval for PROD
staging  → (Optional) Dedicated staging branch
```

### Step 3.3: Verify Workflow Files Exist

```powershell
# Check workflows exist
ls .github\workflows\

# You should see:
# - terraform.yml         (Infrastructure CI/CD)
# - mlops_pipeline.yaml   (MLOps pipeline CI/CD)
```

**✅ Checkpoint:** Workflows present in `.github/workflows/`

---

## 4️⃣ Configure GitHub Secrets

### Step 4.1: Add AWS Role ARN Secrets

**Duration:** 10 minutes

**Navigate to GitHub Repository:**
```
Settings → Secrets and variables → Actions → New repository secret
```

**Add These Secrets:**

| Secret Name | Value | Description |
|-------------|-------|-------------|
| `AWS_ROLE_ARN_DEV` | `arn:aws:iam::123456789012:role/GitHubActions-MLOps-Dev` | Dev environment role |
| `AWS_ROLE_ARN_STAGING` | `arn:aws:iam::123456789012:role/GitHubActions-MLOps-Staging` | Staging environment role |
| `AWS_ROLE_ARN_PROD` | `arn:aws:iam::123456789012:role/GitHubActions-MLOps-Prod` | Production environment role |

**⚠️ IMPORTANT:** Replace `123456789012` with your actual AWS account ID!

**Get your account ID:**
```powershell
aws sts get-caller-identity --query Account --output text
```

### Step 4.2: Add Additional Secrets (For MLOps Pipeline)

**After infrastructure is deployed, add these:**

| Secret Name | Value | Where to Find |
|-------------|-------|---------------|
| `SAGEMAKER_EXECUTION_ROLE` | Role ARN from Terraform output | `terraform output sagemaker_execution_role_arn` |
| `S3_BUCKET_NAME` | Bucket name from Terraform | `terraform output s3_bucket_name` |
| `AWS_ACCOUNT_ID` | Your AWS account ID | `aws sts get-caller-identity --query Account --output text` |
| `SNS_TOPIC_ARN_DEV` | SNS topic ARN | `terraform output sns_topic_arn` |
| `SLACK_WEBHOOK_URL` | (Optional) Slack webhook | Create in Slack workspace |
| `INFRACOST_API_KEY` | (Optional) For cost estimates | https://www.infracost.io/ |

### Step 4.3: Configure Environment Protection Rules

**Duration:** 5 minutes

**Production Environment (Manual Approval Required):**

```
Settings → Environments → New environment
Name: production

☑️ Required reviewers: [Your GitHub username]
☑️ Wait timer: 0 minutes (or set delay)
☑️ Deployment branches: main only
```

**Staging Environment (Optional approval):**
```
Settings → Environments → New environment
Name: staging

☑️ Required reviewers: [Team lead]
☑️ Deployment branches: main, staging
```

**Dev Environment (No approval):**
```
Settings → Environments → New environment
Name: dev

☐ Required reviewers: (none)
☑️ Deployment branches: develop, main
```

**✅ Checkpoint:** Environment protection rules configured

---

## 5️⃣ Understanding Workflows

### Workflow 1: Terraform Infrastructure CI/CD

**File:** `.github/workflows/terraform.yml`

**Triggers:**
```yaml
on:
  push:
    branches: [main, develop]
    paths: ['infrastructure/terraform/**', '.github/workflows/terraform.yml']
  pull_request:
    branches: [main, develop]
  workflow_dispatch:  # Manual trigger
```

**Jobs:**

1. **validate** - Checks Terraform syntax
   ```
   terraform fmt -check
   terraform validate
   ```

2. **security-scan** - Runs tfsec for security issues
   ```
   tfsec infrastructure/terraform/
   ```

3. **plan-dev** - Plans infrastructure changes (develop branch)
   ```
   terraform plan -var-file=terraform.tfvars -out=tfplan
   ```

4. **apply-dev** - Applies changes automatically (develop branch)
   ```
   terraform apply -auto-approve tfplan
   ```

5. **plan-staging** - Plans for staging (main branch)
6. **apply-staging** - Applies with manual approval
7. **plan-production** - Plans for production (workflow_dispatch only)
8. **apply-production** - Applies with manual approval
9. **cost-estimate** - Infracost report on PRs

### Workflow 2: MLOps Pipeline CI/CD

**File:** `.github/workflows/mlops_pipeline.yaml`

**Triggers:**
```yaml
on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]
  workflow_dispatch:  # Manual trigger
```

**Jobs:**

1. **code-quality** - Linting, formatting, unit tests
   ```
   black --check src/
   flake8 src/
   pytest tests/ --cov=src
   ```

2. **data-validation** - Validates dataset
   ```
   python src/processing/download_data.py
   ```

3. **build-docker** - (Optional) Builds custom containers
4. **upload-data** - Uploads data to S3
5. **sagemaker-pipeline** - Creates/executes SageMaker pipeline
6. **deploy-model** - Deploys model to endpoint (manual approval for prod)
7. **setup-monitoring** - Configures Model Monitor
8. **notify** - Sends success/failure notifications

---

## 6️⃣ First Deployment

### Step 6.1: Update Configuration Files

**Duration:** 10 minutes

**Edit:** `infrastructure/terraform/environments/dev/terraform.tfvars`

```hcl
# REQUIRED: Update these values
owner_email          = "your-email@company.com"  # Your email
repository_url       = "https://github.com/suddhasish/mlopsaws"  # Your repo
alert_email_endpoints = ["your-email@company.com"]

# AWS Configuration
aws_region          = "us-east-1"
aws_account_id      = "123456789012"  # Your AWS account ID

# Project Configuration
project_name        = "mlops-diabetes"
environment         = "dev"

# Cost Optimization
budget_amount       = 100
enable_auto_shutdown = true  # Shuts down endpoints 7 PM - 8 AM
```

**Commit changes:**
```powershell
git add infrastructure/terraform/environments/dev/terraform.tfvars
git commit -m "chore: Update dev environment configuration"
git push origin develop
```

### Step 6.2: Trigger First Deployment

**Duration:** 10-15 minutes

**Method 1: Push to Develop Branch (Automatic)**
```powershell
# Make a change to trigger workflow
git checkout develop
echo "# Infrastructure deployment" > infrastructure/terraform/README.md
git add infrastructure/terraform/README.md
git commit -m "docs: Add infrastructure README"
git push origin develop
```

**Method 2: Manual Workflow Dispatch**
```
GitHub → Actions → Terraform Infrastructure CI/CD → Run workflow
Branch: develop
Environment: dev
Action: apply
```

**Watch Progress:**
```
GitHub → Actions → [Your workflow run]

You'll see:
1. ✅ Validate Terraform
2. ✅ Security Scan (tfsec)
3. ✅ Plan (DEV) - Shows resources to create
4. ✅ Apply (DEV) - Creates infrastructure
```

**Expected Duration:** 8-12 minutes

**Expected Output:**
```
Apply complete! Resources: 15 added, 0 changed, 0 destroyed.

Outputs:
s3_bucket_name = "mlops-diabetes-123456789012-dev"
sagemaker_execution_role_arn = "arn:aws:iam::123456789012:role/mlops-diabetes-sagemaker-execution-dev"
model_package_group_name = "mlops-diabetes-model-group-dev"
...
```

### Step 6.3: Verify Infrastructure in AWS

```powershell
# Set AWS profile
$env:AWS_PROFILE = "default"

# Verify S3 bucket
aws s3 ls | Select-String "mlops-diabetes"

# Verify IAM role
aws iam get-role --role-name mlops-diabetes-sagemaker-execution-dev

# Verify SageMaker Model Registry
aws sagemaker list-model-package-groups --name-contains diabetes

# Verify Lambda functions
aws lambda list-functions --query 'Functions[?contains(FunctionName, `mlops-diabetes`)].FunctionName'
```

**✅ Checkpoint:** All infrastructure resources visible in AWS Console

### Step 6.4: Download Terraform Outputs

**Duration:** 2 minutes

```
GitHub → Actions → [Your workflow run] → apply-dev → Terraform Output

Copy outputs and save to local file for reference
```

**Or from AWS Console:**
```powershell
# If you need to run Terraform locally to get outputs
cd infrastructure/terraform/environments/dev
terraform init
terraform output
```

---

## 7️⃣ MLOps Pipeline Automation

### Step 7.1: Configure Application Secrets

**Duration:** 5 minutes

After infrastructure is deployed, add MLOps-specific secrets:

```
GitHub → Settings → Secrets → New repository secret
```

**Add from Terraform outputs:**
```powershell
# Get values from GitHub Actions artifacts or AWS Console
$bucketName = "mlops-diabetes-123456789012-dev"
$roleArn = "arn:aws:iam::123456789012:role/mlops-diabetes-sagemaker-execution-dev"
$accountId = "123456789012"
$snsTopic = "arn:aws:sns:us-east-1:123456789012:mlops-diabetes-alerts-dev"

# Add as GitHub secrets:
# - SAGEMAKER_EXECUTION_ROLE: $roleArn
# - S3_BUCKET_NAME: $bucketName
# - AWS_ACCOUNT_ID: $accountId
# - SNS_TOPIC_ARN_DEV: $snsTopic
```

### Step 7.2: Trigger MLOps Pipeline

**Method 1: Push to Develop (Automatic)**
```powershell
git checkout develop
git add src/
git commit -m "feat: Update training script"
git push origin develop
```

**Method 2: Manual Workflow Dispatch**
```
GitHub → Actions → MLOps Pipeline → Run workflow
Branch: develop
Execute pipeline: true
```

### Step 7.3: Monitor Pipeline Execution

**GitHub Actions Console:**
```
Actions → MLOps Pipeline → [Your run]

Jobs:
1. ✅ Code Quality & Unit Tests (3-5 mins)
2. ✅ Data Validation (2 mins)
3. ✅ Upload Data to S3 (1 min)
4. ✅ Execute SageMaker Pipeline (15-20 mins)
   - Data processing
   - Model training
   - Model evaluation
   - Model registration
5. ✅ Deploy Model to Endpoint (8-10 mins)
6. ✅ Setup Model Monitoring (2-3 mins)
```

**Total Duration:** ~30-40 minutes

**AWS SageMaker Console:**
```
https://console.aws.amazon.com/sagemaker/

Pipelines → diabetes-training-pipeline-dev → Executions
Training → Training jobs
Inference → Endpoints
Model Registry → diabetes-classification-models-dev
```

### Step 7.4: Verify Deployment

```powershell
# Check endpoint is running
aws sagemaker list-endpoints --name-contains diabetes

# Test inference
python -c "
import boto3
import json

client = boto3.client('sagemaker-runtime', region_name='us-east-1')

# Sample data (diabetes features)
payload = '0.038076,0.050680,0.061696,0.021872,-0.044223,-0.034821,-0.043401,-0.002592,0.019908,-0.017646'

response = client.invoke_endpoint(
    EndpointName='mlops-diabetes-endpoint-dev',
    ContentType='text/csv',
    Body=payload
)

result = json.loads(response['Body'].read().decode())
print(f'Prediction: {result}')
"
```

**Expected Output:**
```
Prediction: 0.7234
```

**✅ Checkpoint:** Model endpoint deployed and serving predictions

---

## 8️⃣ Monitoring & Validation

### Step 8.1: View GitHub Actions Logs

```
GitHub → Actions → [Workflow run] → [Job] → [Step]

Examples:
- Terraform Apply logs
- SageMaker pipeline execution logs
- Model deployment logs
```

### Step 8.2: CloudWatch Logs (AWS)

```powershell
# View SageMaker training logs
aws logs tail /aws/sagemaker/TrainingJobs --follow

# View endpoint logs
aws logs tail /aws/sagemaker/Endpoints/mlops-diabetes-dev --follow

# View Lambda logs (auto-shutdown)
aws logs tail /aws/lambda/mlops-diabetes-endpoint-shutdown-dev --since 1h
```

### Step 8.3: Cost Monitoring

**GitHub Actions Cost Estimate (Infracost):**
```
Actions → Terraform Infrastructure CI/CD → cost-estimate

View estimated monthly costs for infrastructure
```

**AWS Cost Explorer:**
```powershell
# Get last 7 days costs
aws ce get-cost-and-usage \
  --time-period Start=$(Get-Date -Format yyyy-MM-dd -Date (Get-Date).AddDays(-7)),End=$(Get-Date -Format yyyy-MM-dd) \
  --granularity DAILY \
  --metrics BlendedCost \
  --group-by Type=DIMENSION,Key=SERVICE
```

### Step 8.4: Set Up Notifications

**Slack Notifications (Optional):**

1. Create Slack App:
   ```
   https://api.slack.com/apps → Create New App
   Incoming Webhooks → Activate
   Copy Webhook URL
   ```

2. Add to GitHub Secrets:
   ```
   Secret name: SLACK_WEBHOOK_URL
   Value: https://hooks.slack.com/services/YOUR/WEBHOOK/URL
   ```

3. Workflow will automatically send notifications on success/failure

**Email Notifications (Via SNS):**

Already configured via Terraform! Check your email for:
- Training job completion
- Model registration
- Endpoint deployment
- Budget alerts

---

## 9️⃣ Production Deployment

### Step 9.1: Prepare Production Configuration

**Duration:** 20 minutes

**Edit:** `infrastructure/terraform/environments/production/terraform.tfvars`

```hcl
# Production Configuration
environment         = "production"
owner_email         = "mlops-team@company.com"
alert_email_endpoints = [
  "mlops-team@company.com",
  "oncall@company.com",
  "manager@company.com"
]

# High Availability
sagemaker_endpoint_initial_instance_count = 2
sagemaker_endpoint_instance_type = "ml.m5.xlarge"
enable_auto_scaling = true
enable_autoscaling_target_value = 70.0

# Security
enable_vpc = true
enable_kms_encryption = true
enable_cloudtrail = true
enable_guardduty = true

# Cost Control
budget_amount = 1500
enable_auto_shutdown = false  # Production runs 24/7

# Model Approval
model_approval_status = "PendingManualApproval"

# Monitoring
cloudwatch_log_retention_days = 30
enable_model_monitor = true
```

**Commit production config:**
```powershell
git checkout main
git add infrastructure/terraform/environments/production/terraform.tfvars
git commit -m "feat: Configure production environment"
git push origin main
```

### Step 9.2: Create Production Deployment PR

```powershell
# Create feature branch
git checkout -b feature/production-deployment

# Make necessary changes
# Update config, add documentation, etc.

# Commit and push
git add .
git commit -m "feat: Production deployment configuration"
git push -u origin feature/production-deployment

# Create Pull Request on GitHub
# Request review from team
```

### Step 9.3: Review Terraform Plan

**Pull Request will automatically trigger:**
```
GitHub → Pull Requests → [Your PR] → Checks

✅ Terraform Plan (Production)
  Shows all resources to be created
  Infracost estimate: $1,200-1,500/month
```

**Review Plan Carefully:**
- Number of resources (should be ~30-40 for production)
- Instance types (ml.m5.xlarge recommended)
- VPC configuration
- Encryption settings
- Backup retention

### Step 9.4: Manual Deployment Approval

**After PR is merged to main:**

```
GitHub → Actions → Terraform Infrastructure CI/CD → Run workflow

Environment: production
Action: apply
Confirm: Yes, I want to deploy to production
```

**Approval Required:**
```
GitHub → Actions → [Workflow run] → apply-production

⏸️ Waiting for approval

Reviewers can:
- Review Terraform plan
- Check cost estimates
- Approve deployment
```

**Production Deployment Steps:**
1. Review Terraform plan artifact
2. Approve deployment in GitHub
3. Workflow applies infrastructure
4. Wait for completion (~15-20 minutes)
5. Verify all resources in AWS Console

### Step 9.5: Deploy ML Model to Production

**Trigger MLOps Pipeline:**
```
GitHub → Actions → MLOps Pipeline → Run workflow

Branch: main
Execute pipeline: true
```

**Jobs with Manual Approval:**
```
1. ✅ Code Quality
2. ✅ Data Validation
3. ✅ Upload Data
4. ✅ SageMaker Pipeline
5. ⏸️ Deploy Model (Waiting for manual approval)
   - Review model metrics
   - Check evaluation reports
   - Approve deployment
6. ✅ Setup Monitoring
```

**Approval Process:**
1. Review model performance:
   ```
   SageMaker → Model Registry → diabetes-classification-models-prod
   → Select latest model → View evaluation report
   
   Required Metrics:
   - Accuracy: > 85%
   - Precision: > 0.80
   - Recall: > 0.75
   - F1-Score: > 0.77
   - ROC-AUC: > 0.85
   ```

2. Approve in GitHub Actions:
   ```
   Actions → MLOps Pipeline → deploy-model → Review deployments
   → Approve
   ```

3. Monitor deployment:
   ```
   SageMaker → Endpoints → mlops-diabetes-endpoint-prod
   Status: Creating → InService (~10 minutes)
   ```

### Step 9.6: Production Validation

**Smoke Tests:**
```powershell
# Test endpoint
python -c "
import boto3
import json

client = boto3.client('sagemaker-runtime', region_name='us-east-1')

# Test data
test_cases = [
    '0.038076,0.050680,0.061696,0.021872,-0.044223,-0.034821,-0.043401,-0.002592,0.019908,-0.017646',
    '-0.001882,-0.044642,-0.051474,-0.026328,-0.008449,-0.019163,0.074412,-0.039493,-0.068330,-0.092204',
    '0.085299,0.050680,0.044451,-0.005671,-0.045599,-0.034194,-0.032356,-0.002592,0.002864,-0.025930'
]

for i, payload in enumerate(test_cases):
    response = client.invoke_endpoint(
        EndpointName='mlops-diabetes-endpoint-prod',
        ContentType='text/csv',
        Body=payload
    )
    result = json.loads(response['Body'].read().decode())
    print(f'Test {i+1}: {result}')
"
```

**Load Test (Optional):**
```python
import boto3
import concurrent.futures
import time

def invoke_endpoint(payload):
    client = boto3.client('sagemaker-runtime', region_name='us-east-1')
    start = time.time()
    response = client.invoke_endpoint(
        EndpointName='mlops-diabetes-endpoint-prod',
        ContentType='text/csv',
        Body=payload
    )
    latency = time.time() - start
    return latency

# Send 100 concurrent requests
with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
    payloads = ['0.038076,0.050680,...'] * 100
    latencies = list(executor.map(invoke_endpoint, payloads))

print(f"Average latency: {sum(latencies)/len(latencies):.3f}s")
print(f"Max latency: {max(latencies):.3f}s")
```

**Expected Results:**
- Average latency: < 200ms
- Max latency: < 500ms
- No errors

**✅ Checkpoint:** Production endpoint serving predictions successfully

---

## 🔟 Troubleshooting

### Issue 1: OIDC Authentication Fails

**Error:**
```
Error: Could not assume role with OIDC: Not authorized to perform sts:AssumeRoleWithWebIdentity
```

**Solution:**
```powershell
# 1. Verify OIDC provider exists
aws iam list-open-id-connect-providers

# 2. Check trust policy
aws iam get-role --role-name GitHubActions-MLOps-Role --query 'Role.AssumeRolePolicyDocument'

# 3. Verify repository name matches
# Trust policy: repo:YOUR_USERNAME/mlopsaws:*
# GitHub Actions: YOUR_USERNAME/mlopsaws

# 4. Update trust policy if needed
aws iam update-assume-role-policy \
  --role-name GitHubActions-MLOps-Role \
  --policy-document file://trust-policy.json
```

### Issue 2: Terraform State Lock

**Error:**
```
Error: Error acquiring the state lock
```

**Solution:**
```powershell
# Option 1: Wait for concurrent workflow to finish

# Option 2: Force unlock (only if sure no other process is running)
cd infrastructure/terraform/environments/dev
terraform force-unlock LOCK_ID
```

### Issue 3: GitHub Secrets Not Found

**Error:**
```
Error: Secret SAGEMAKER_EXECUTION_ROLE not found
```

**Solution:**
```
1. Go to: Settings → Secrets → Actions
2. Verify secret name matches exactly (case-sensitive)
3. Re-add secret if missing
4. Re-run workflow
```

### Issue 4: Terraform Plan Shows Unexpected Changes

**Error:**
```
Plan: 0 to add, 5 to change, 0 to destroy
(Expected: 0 changes after initial deployment)
```

**Solution:**
```powershell
# Review what changed
terraform plan -var-file=terraform.tfvars

# Common causes:
# 1. Tags changed (update terraform.tfvars)
# 2. Provider version updated (lock version in main.tf)
# 3. Manual changes in AWS Console (import to Terraform)

# Import manually changed resource
terraform import aws_s3_bucket.data mlops-diabetes-123456789012-dev
```

### Issue 5: SageMaker Pipeline Fails

**Error:**
```
ClientError: Data not found in S3
```

**Solution:**
```powershell
# Verify data was uploaded
aws s3 ls s3://mlops-diabetes-123456789012-dev/data/raw/

# Re-upload data manually
aws s3 cp data/raw/diabetes.csv s3://mlops-diabetes-123456789012-dev/data/raw/

# Check SageMaker execution role has S3 access
aws iam get-role-policy \
  --role-name mlops-diabetes-sagemaker-execution-dev \
  --policy-name SageMakerS3Access
```

### Issue 6: Endpoint Deployment Timeout

**Error:**
```
Endpoint deployment timed out after 15 minutes
```

**Solution:**
```powershell
# Check endpoint status
aws sagemaker describe-endpoint --endpoint-name mlops-diabetes-endpoint-dev

# Possible causes:
# 1. Model size too large → Use smaller model or larger instance
# 2. VPC networking issues → Check VPC endpoints
# 3. Image pull failure → Verify ECR permissions

# View endpoint creation logs
aws logs tail /aws/sagemaker/Endpoints/mlops-diabetes-endpoint-dev --since 30m
```

### Issue 7: High Costs

**Unexpected bill: $200+**

**Solution:**
```powershell
# Identify cost drivers
aws ce get-cost-and-usage \
  --time-period Start=2024-11-01,End=2024-11-05 \
  --granularity DAILY \
  --metrics BlendedCost \
  --group-by Type=DIMENSION,Key=SERVICE

# Common causes:
# 1. Endpoint running 24/7 (dev should have auto-shutdown)
# 2. Multiple training jobs
# 3. Large data transfer

# Fix: Delete unused endpoints
aws sagemaker delete-endpoint --endpoint-name mlops-diabetes-endpoint-dev

# Fix: Enable auto-shutdown
# Update terraform.tfvars: enable_auto_shutdown = true
# Re-run Terraform workflow
```

---

## 📊 Workflow Comparison: Local vs CI/CD

| Aspect | Local Deployment | GitHub Actions CI/CD |
|--------|------------------|----------------------|
| **Setup Time** | 10 minutes | 30-60 minutes (one-time) |
| **Deployment Time** | 5-10 minutes | 10-15 minutes |
| **Security** | Access keys (high risk) | OIDC tokens (low risk) |
| **Audit Trail** | Local history only | Full GitHub Actions logs |
| **Team Collaboration** | Requires credentials sharing | No credential sharing |
| **Environment Consistency** | Varies by machine | Identical containers |
| **Approval Process** | Manual checks | Automated + manual gates |
| **Cost Visibility** | Manual tracking | Automated Infracost reports |
| **Rollback** | Manual | Git revert + re-deploy |
| **Documentation** | Separate docs | Embedded in workflow |

**Recommendation:** Always use CI/CD for production deployments!

---

## 📚 Additional Resources

### Official Documentation
- **GitHub Actions**: https://docs.github.com/en/actions
- **AWS OIDC**: https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-amazon-web-services
- **Terraform GitHub Actions**: https://developer.hashicorp.com/terraform/tutorials/automation/github-actions
- **SageMaker Pipelines**: https://docs.aws.amazon.com/sagemaker/latest/dg/pipelines.html

### Tools
- **tfsec**: https://github.com/aquasecurity/tfsec
- **Infracost**: https://www.infracost.io/
- **checkov**: https://www.checkov.io/

### Best Practices
- **GitOps**: https://www.gitops.tech/
- **Infrastructure as Code**: https://www.terraform-best-practices.com/
- **MLOps Maturity Model**: https://learn.microsoft.com/en-us/azure/architecture/example-scenario/mlops/mlops-maturity-model

---

## ✅ Final Checklist

Before going live with CI/CD:

### AWS Setup
- [ ] OIDC identity provider created
- [ ] IAM roles created (dev, staging, prod)
- [ ] Least-privilege policies attached
- [ ] Trust policies configured correctly
- [ ] Budget alerts configured

### GitHub Setup
- [ ] Repository created and cloned
- [ ] Branch protection rules configured
- [ ] Environment protection rules configured
- [ ] All secrets added (AWS roles, SageMaker config)
- [ ] Workflow files present and reviewed

### Testing
- [ ] Dev deployment successful
- [ ] Infrastructure verified in AWS
- [ ] MLOps pipeline executed successfully
- [ ] Model deployed and serving predictions
- [ ] Monitoring configured and working
- [ ] Cost tracking enabled

### Production Readiness
- [ ] Production configuration reviewed
- [ ] Security audit completed
- [ ] Team trained on approval process
- [ ] Runbook created for incidents
- [ ] Backup and disaster recovery plan
- [ ] Compliance requirements met

---

**🎉 Congratulations! You now have a fully automated CI/CD pipeline for MLOps on AWS!**

**Estimated Setup Time:** 2-3 hours (first time)  
**Estimated Deployment Time:** 10-15 minutes (subsequent deployments)  
**Security Level:** Production-grade with OIDC

**Last Updated:** November 4, 2025  
**Version:** 2.0 - GitHub Actions CI/CD  
**Maintainer:** MLOps Team

---

**Next Steps:**
1. Deploy to dev environment
2. Test MLOps pipeline
3. Configure monitoring dashboards
4. Plan staging deployment
5. Execute production deployment with team approval
