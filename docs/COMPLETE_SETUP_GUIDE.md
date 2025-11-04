# 🚀 COMPLETE MLOps SETUP GUIDE - GitHub Actions Automation

**THE ONLY GUIDE YOU NEED - End-to-End Automated Deployment**

**Version:** 3.0 - Consolidated Single Guide  
**Last Updated:** November 4, 2025  
**Total Time:** 2-3 hours (one-time setup) + monitoring  
**Method:** 100% GitHub Actions Automation

---

## 📋 TABLE OF CONTENTS

1. [Overview & Architecture](#1-overview--architecture)
2. [Prerequisites](#2-prerequisites)
3. [Manual Steps - AWS OIDC Setup](#3-manual-steps---aws-oidc-setup)
4. [Manual Steps - GitHub Configuration](#4-manual-steps---github-configuration)
5. [Automated - Infrastructure Deployment](#5-automated---infrastructure-deployment)
6. [Automated - MLOps Pipeline](#6-automated---mlops-pipeline)
7. [Manual Steps - Production Deployment](#7-manual-steps---production-deployment)
8. [Monitoring & Validation](#8-monitoring--validation)
9. [PowerShell Scripts Reference](#9-powershell-scripts-reference)
10. [Troubleshooting](#10-troubleshooting)

**Additional Guides:**
- 📊 [Data Ingestion Guide](./DATA_INGESTION_GUIDE.md) - How data flows through the pipeline
- 🔐 [Trust Policy Best Practices](./TRUST_POLICY_BEST_PRACTICES.md) - Production security setup

---

## 🎯 STEP-BY-STEP EXECUTION SUMMARY

### Quick Reference: What's Manual vs Automated

| Step | Action | Type | Time | Where |
|------|--------|------|------|-------|
| 1 | AWS Account Setup | 🔴 **MANUAL** | 30 min | AWS Console |
| 2 | Create OIDC Provider | 🔴 **MANUAL** | 10 min | AWS Console / CLI |
| 3 | Create IAM Roles | 🔴 **MANUAL** | 15 min | AWS Console / CLI |
| 4 | Configure GitHub Secrets | 🔴 **MANUAL** | 10 min | GitHub Settings |
| 5 | Setup Environment Protection | 🔴 **MANUAL** | 5 min | GitHub Settings |
| 6 | Update terraform.tfvars | 🔴 **MANUAL** | 5 min | Code Editor |
| 7 | Push to develop branch | 🔴 **MANUAL** | 1 min | Git |
| 8 | **Infrastructure Deployment** | 🟢 **AUTOMATED** | 10-15 min | GitHub Actions |
| 9 | **Config Auto-Update** | 🟢 **AUTOMATED** | 1 min | GitHub Actions |
| 10 | **MLOps Pipeline Execution** | 🟢 **AUTOMATED** | 25-30 min | GitHub Actions |
| 11 | **Model Training** | 🟢 **AUTOMATED** | 15-20 min | SageMaker |
| 12 | **Model Deployment** | 🟢 **AUTOMATED** | 8-10 min | SageMaker |
| 13 | **Monitoring Setup** | 🟢 **AUTOMATED** | 2-3 min | SageMaker |
| 14 | Production Approval | 🔴 **MANUAL** | 5 min | GitHub Actions |
| 15 | Cost Monitoring | 🟡 **SEMI-AUTO** | Daily | AWS Console |

**Legend:**
- 🔴 **MANUAL** = You must do this step yourself (AWS Console, GitHub UI, or CLI)
- 🟢 **AUTOMATED** = GitHub Actions does this automatically after setup
- 🟡 **SEMI-AUTO** = Automated alerts, manual review

---

## 1️⃣ Overview & Architecture

### What Gets Deployed Automatically

```
┌────────────────────────────────────────────────────────────────┐
│                    YOUR GITHUB REPOSITORY                       │
│                                                                 │
│  When you push to 'develop' or 'main' branch:                  │
└──────────────────────┬─────────────────────────────────────────┘
                       │
                       ▼
┌────────────────────────────────────────────────────────────────┐
│              GITHUB ACTIONS WORKFLOWS (Automated)               │
│                                                                 │
│  Workflow 1: terraform.yml                                      │
│  ├─ Validates Terraform syntax                                 │
│  ├─ Runs security scan (tfsec)                                 │
│  ├─ Generates Terraform plan                                   │
│  ├─ Applies infrastructure (auto for dev, manual for prod)     │
│  └─ Outputs: S3 bucket, IAM roles, SageMaker registry          │
│                                                                 │
│  Workflow 2: mlops_pipeline.yaml                               │
│  ├─ Runs code quality checks (black, flake8)                   │
│  ├─ Executes unit tests (pytest)                               │
│  ├─ Uploads data to S3                                         │
│  ├─ Creates SageMaker pipeline                                 │
│  ├─ Trains XGBoost model                                       │
│  ├─ Evaluates model performance                                │
│  ├─ Deploys to SageMaker endpoint                              │
│  └─ Sets up Model Monitor                                      │
└──────────────────────┬─────────────────────────────────────────┘
                       │
                       ▼
┌────────────────────────────────────────────────────────────────┐
│                        AWS CLOUD                                │
│                                                                 │
│  ✅ S3 Bucket (data, models, artifacts)                        │
│  ✅ IAM Roles (SageMaker execution, data scientist)            │
│  ✅ SageMaker Model Registry                                   │
│  ✅ CloudWatch Log Groups                                      │
│  ✅ SNS Topics (alerts)                                        │
│  ✅ Lambda Functions (auto-shutdown)                           │
│  ✅ Budgets (cost control)                                     │
│  ✅ SageMaker Training Jobs                                    │
│  ✅ SageMaker Endpoints (real-time inference)                  │
│  ✅ Model Monitor (drift detection)                            │
└────────────────────────────────────────────────────────────────┘
```

### PowerShell Scripts (Used Locally - Optional)

These scripts are **alternatives** to GitHub Actions for **local development only**:

1. **deploy-infrastructure.ps1** 
   - Purpose: Local Terraform deployment
   - When to use: Learning Terraform, offline dev, quick testing
   - GitHub Actions equivalent: `terraform.yml` workflow

2. **update-config.ps1**
   - Purpose: Auto-updates config.yaml from Terraform outputs
   - When to use: After local Terraform apply
   - GitHub Actions equivalent: Built into `terraform.yml` workflow

3. **validate-setup.ps1**
   - Purpose: Validates infrastructure is ready
   - When to use: Before running ML pipeline locally
   - GitHub Actions equivalent: Built into `mlops_pipeline.yaml` workflow

**For GitHub Actions deployment (recommended), you DON'T need to run these scripts!**

---

## 2️⃣ Prerequisites

### 🔴 MANUAL SETUP - Required Before Automation

#### AWS Account (30 minutes)

**Status:** 🔴 **MANUAL** - Must create via AWS website

1. **Create AWS Account** (if you don't have one)
   ```
   URL: https://aws.amazon.com/
   Click: "Create an AWS Account"
   
   Provide:
   - Email address (use company email for production)
   - Account name: mlops-production or yourname-ml
   - Credit card (required, won't be charged unless you exceed free tier)
   - Phone verification
   ```

2. **Enable MFA on Root Account** ⚠️ **CRITICAL SECURITY STEP**
   ```
   AWS Console → Security Credentials → Multi-factor authentication
   
   Steps:
   1. Click "Activate MFA"
   2. Choose "Virtual MFA device"
   3. Use Google Authenticator or Authy app
   4. Scan QR code
   5. Enter two consecutive MFA codes
   6. Save recovery codes in password manager
   ```
   
   **✅ Checkpoint:** Root account shows MFA enabled (green checkmark)

3. **Create Admin IAM User** (don't use root for daily tasks)
   ```
   IAM Console → Users → Create user
   
   Username: mlops-admin
   Access type: ✅ Programmatic access + ✅ Console access
   Attach policy: AdministratorAccess
   
   SAVE CREDENTIALS:
   - Access Key ID
   - Secret Access Key
   - Console password
   ```
   
   **✅ Checkpoint:** Can log in as mlops-admin with MFA

4. **Install AWS CLI v2** (for verification only)
   
   **Windows:**
   ```powershell
   # Download and install
   msiexec.exe /i https://awscli.amazonaws.com/AWSCLIV2.msi /quiet
   
   # Verify
   aws --version  # Should show: aws-cli/2.x.x
   ```
   
   **Linux/Mac:**
   ```bash
   curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
   unzip awscliv2.zip
   sudo ./aws/install
   
   # Verify
   aws --version
   ```

5. **Configure AWS CLI** (optional, for verification)
   ```powershell
   aws configure --profile mlops-dev
   
   # Enter when prompted:
   AWS Access Key ID: [from step 3]
   AWS Secret Access Key: [from step 3]
   Default region: us-east-1
   Default output format: json
   
   # Test connection
   aws sts get-caller-identity --profile mlops-dev
   ```

#### GitHub Account (5 minutes)

**Status:** 🔴 **MANUAL** - GitHub.com

1. **Create GitHub account** (if needed): https://github.com/signup
2. **Fork or create repository**: https://github.com/new
   ```
   Repository name: mlopsaws
   Visibility: Private (recommended) or Public
   Initialize: With README
   ```

3. **Clone repository locally**
   ```powershell
   git clone https://github.com/YOUR_USERNAME/mlopsaws.git
   cd mlopsaws
   
   # Copy all project files to this directory
   ```

#### Local Tools (10 minutes)

**Status:** 🔴 **MANUAL** - Install on your computer

1. **Git** (for code management)
   ```powershell
   # Windows
   winget install Git.Git
   
   # Linux
   sudo apt-get install git
   
   # Verify
   git --version  # Should be 2.30+
   ```

2. **Python 3.8+** (for running scripts locally - optional)
   ```powershell
   # Windows
   winget install Python.Python.3.11
   
   # Linux
   sudo apt-get install python3.11 python3-pip
   
   # Verify
   python --version  # Should be 3.8+
   ```

3. **Text Editor** (VS Code recommended)
   ```powershell
   # Windows
   winget install Microsoft.VisualStudioCode
   
   # Linux
   sudo snap install code --classic
   ```

**✅ Checkpoint:** All tools installed and working

---

## 3️⃣ Manual Steps - AWS OIDC Setup

### Why OIDC Instead of Access Keys?

**🔴 OLD WAY (Insecure):**
```
AWS Access Keys → Stored in GitHub Secrets → Can leak in logs
- Keys never expire
- Hard to rotate
- Security risk if exposed
```

**🟢 NEW WAY (Secure - OIDC):**
```
GitHub Actions → AWS STS → Temporary tokens (1 hour)
- No long-lived credentials
- Automatic expiration
- Scoped permissions
- Complete audit trail
```

### Step 3.1: Create OIDC Identity Provider

**Status:** 🔴 **MANUAL** - One-time AWS Console/CLI setup

**Duration:** 10 minutes

**Method 1: AWS Console (Easiest)**

```
1. Open: https://console.aws.amazon.com/iam/
2. Click: Identity providers → Add provider
3. Configure:
   - Provider type: OpenID Connect
   - Provider URL: https://token.actions.githubusercontent.com
   - Audience: sts.amazonaws.com
4. Click: Add provider
```

**Method 2: AWS CLI (Faster if familiar)**

```powershell
aws iam create-open-id-connect-provider \
  --url https://token.actions.githubusercontent.com \
  --client-id-list sts.amazonaws.com \
  --thumbprint-list 6938fd4d98bab03faadb97b34396831e3780aea1
```

**✅ Checkpoint:** Identity provider appears in IAM → Identity providers

### Step 3.2: Create IAM Roles for GitHub Actions

**Status:** 🔴 **MANUAL** - Create 3 roles (dev, staging, prod)

**Duration:** 15 minutes

> **⚠️ PRODUCTION WARNING:** The example below uses a **personal GitHub username**, which creates maintenance issues when users leave. For production use, see **[Trust Policy Best Practices](./TRUST_POLICY_BEST_PRACTICES.md)** for organization-based setup.

**Create trust policy file:**

```powershell
# Get your AWS account ID
$accountId = aws sts get-caller-identity --query Account --output text
Write-Host "Your AWS Account ID: $accountId"

# OPTION 1: Personal Repository (Learning/Development Only)
# ⚠️ Issue: Requires trust policy update when user leaves

# Create trust-policy-dev.json
@"
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::${accountId}:oidc-provider/token.actions.githubusercontent.com"
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
"@ | Out-File -FilePath trust-policy-dev.json -Encoding utf8

# ⚠️ REPLACE: YOUR_GITHUB_USERNAME with your actual GitHub username
# Example: "repo:suddhasish/mlopsaws:*"

# OPTION 2: GitHub Organization (Production-Ready) ✅ RECOMMENDED
# ✅ Benefit: No changes needed when users leave
# See: docs/TRUST_POLICY_BEST_PRACTICES.md for complete setup

# Uncomment this block for organization-based trust:
<#
$orgName = "YOUR_ORG_NAME"  # e.g., "acme-corp"
@"
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::${accountId}:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
        },
        "StringLike": {
          "token.actions.githubusercontent.com:sub": "repo:${orgName}/mlopsaws:*"
        }
      }
    }
  ]
}
"@ | Out-File -FilePath trust-policy-dev.json -Encoding utf8
#>
```

**Create the IAM roles:**

```powershell
# Dev Environment Role
aws iam create-role \
  --role-name GitHubActions-MLOps-Dev \
  --assume-role-policy-document file://trust-policy-dev.json \
  --description "GitHub Actions role for MLOps dev environment"

# Attach AdministratorAccess (for initial setup - will narrow later)
aws iam attach-role-policy \
  --role-name GitHubActions-MLOps-Dev \
  --policy-arn arn:aws:iam::aws:policy/AdministratorAccess

# Get Role ARN (save this!)
aws iam get-role --role-name GitHubActions-MLOps-Dev --query 'Role.Arn' --output text
```

**Expected output:**
```
arn:aws:iam::123456789012:role/GitHubActions-MLOps-Dev
```

**Repeat for Staging and Production:**

```powershell
# Staging Role
aws iam create-role \
  --role-name GitHubActions-MLOps-Staging \
  --assume-role-policy-document file://trust-policy-staging.json

aws iam attach-role-policy \
  --role-name GitHubActions-MLOps-Staging \
  --policy-arn arn:aws:iam::aws:policy/AdministratorAccess

# Production Role
aws iam create-role \
  --role-name GitHubActions-MLOps-Prod \
  --assume-role-policy-document file://trust-policy-prod.json

aws iam attach-role-policy \
  --role-name GitHubActions-MLOps-Prod \
  --policy-arn arn:aws:iam::aws:policy/AdministratorAccess
```

**✅ Checkpoint:** Three IAM roles created with ARNs saved

---

## 4️⃣ Manual Steps - GitHub Configuration

### Step 4.1: Add GitHub Secrets

**Status:** 🔴 **MANUAL** - GitHub repository settings

**Duration:** 10 minutes

**Navigate to:**
```
Your GitHub Repository → Settings → Secrets and variables → Actions
```

**Click:** "New repository secret"

**Add these secrets one by one:**

| Secret Name | Value | Where to Get |
|-------------|-------|--------------|
| `AWS_ROLE_ARN_DEV` | `arn:aws:iam::123456789012:role/GitHubActions-MLOps-Dev` | From Step 3.2 |
| `AWS_ROLE_ARN_STAGING` | `arn:aws:iam::123456789012:role/GitHubActions-MLOps-Staging` | From Step 3.2 |
| `AWS_ROLE_ARN_PROD` | `arn:aws:iam::123456789012:role/GitHubActions-MLOps-Prod` | From Step 3.2 |

**⚠️ IMPORTANT:** Replace `123456789012` with your actual AWS account ID!

**Screenshots/Steps:**
```
1. Click "New repository secret"
2. Name: AWS_ROLE_ARN_DEV
3. Secret: arn:aws:iam::YOUR_ACCOUNT_ID:role/GitHubActions-MLOps-Dev
4. Click "Add secret"
5. Repeat for STAGING and PROD
```

**✅ Checkpoint:** All 3 secrets visible in repository settings

### Step 4.2: Configure Environment Protection Rules

**Status:** 🔴 **MANUAL** - GitHub repository settings

**Duration:** 5 minutes

**Navigate to:**
```
Your GitHub Repository → Settings → Environments
```

**Create Dev Environment (No approval required):**
```
1. Click "New environment"
2. Name: dev
3. ☐ Required reviewers: (leave empty)
4. ☐ Wait timer: 0 minutes
5. Deployment branches:
   ☑️ Selected branches
   Add: develop
6. Click "Save protection rules"
```

**Create Staging Environment (Optional approval):**
```
1. Click "New environment"
2. Name: staging
3. ☑️ Required reviewers: [Add yourself or team lead]
4. ☐ Wait timer: 0 minutes
5. Deployment branches:
   ☑️ Selected branches
   Add: main
6. Click "Save protection rules"
```

**Create Production Environment (Manual approval REQUIRED):**
```
1. Click "New environment"
2. Name: production
3. ☑️ Required reviewers: [Add yourself + manager]
4. ☐ Wait timer: 0 minutes (or set to 30 minutes for safety)
5. Deployment branches:
   ☑️ Selected branches
   Add: main only
6. Click "Save protection rules"
```

**✅ Checkpoint:** Three environments configured with appropriate protections

### Step 4.3: Create Branch Structure

**Status:** 🔴 **MANUAL** - Local Git commands

**Duration:** 2 minutes

```powershell
# Ensure you're in the repository
cd mlopsaws

# Create develop branch
git checkout -b develop
git push -u origin develop

# Back to main
git checkout main
```

**Branch Strategy:**
```
develop → Auto-deploys to DEV environment
main    → Auto-deploys to STAGING, manual approval for PROD
```

**✅ Checkpoint:** Both branches visible on GitHub

---

## 5️⃣ Automated - Infrastructure Deployment

### Step 5.1: Update Terraform Configuration

**Status:** 🔴 **MANUAL** - Edit configuration file

**Duration:** 5 minutes

**Edit this file:**
```
infrastructure/terraform/environments/dev/terraform.tfvars
```

**Required changes:**

```hcl
# ==========================================
# REQUIRED: UPDATE THESE VALUES
# ==========================================

# Your email (for budget alerts)
owner_email = "YOUR_EMAIL@company.com"  # ⚠️ CHANGE THIS

# Your GitHub repository
repository_url = "https://github.com/YOUR_USERNAME/mlopsaws"  # ⚠️ CHANGE THIS

# Alert email endpoints
alert_email_endpoints = ["YOUR_EMAIL@company.com"]  # ⚠️ CHANGE THIS

# AWS Configuration
aws_region     = "us-east-1"
aws_account_id = "123456789012"  # ⚠️ Get from: aws sts get-caller-identity

# Project Configuration
project_name = "mlops-diabetes"
environment  = "dev"

# Cost Optimization
budget_amount        = 100
enable_auto_shutdown = true  # Saves 60% cost (shuts down 7PM-8AM UTC)

# Free Tier Optimized Settings
enable_vpc              = false  # Use default VPC (free)
enable_kms_encryption   = false  # Use AES256 (free)
enable_cloudtrail       = false  # Save costs in dev
cloudwatch_log_retention_days = 1

# Instance Types (smallest for cost savings)
sagemaker_processing_instance_type = "ml.t3.medium"
sagemaker_training_instance_type   = "ml.m5.large"
sagemaker_endpoint_instance_type   = "ml.t2.medium"
```

**Save the file.**

**Commit and push:**

```powershell
git add infrastructure/terraform/environments/dev/terraform.tfvars
git commit -m "chore: Update dev environment configuration"
git push origin develop
```

### Step 5.2: Trigger Infrastructure Deployment

**Status:** 🟢 **AUTOMATED** - GitHub Actions takes over

**Duration:** 10-15 minutes (automated)

**Method 1: Automatic (Recommended)**

Simply push to develop branch (already done in Step 5.1):

```powershell
# Already pushed above, but if you make more changes:
git add .
git commit -m "feat: Your changes"
git push origin develop
```

**GitHub Actions will automatically:**
1. ✅ Validate Terraform syntax
2. ✅ Run security scan (tfsec)
3. ✅ Generate Terraform plan
4. ✅ Apply infrastructure to AWS
5. ✅ Output infrastructure details

**Method 2: Manual Workflow Dispatch**

```
1. Go to: https://github.com/YOUR_USERNAME/mlopsaws/actions
2. Select: "Terraform Infrastructure CI/CD"
3. Click: "Run workflow"
4. Choose:
   - Branch: develop
   - Environment: dev
   - Action: apply
5. Click: "Run workflow"
```

### Step 5.3: Monitor Deployment

**Status:** 🔴 **MANUAL** - Watch GitHub Actions

**Duration:** 10-15 minutes (watch automated process)

**Watch progress in GitHub:**

```
GitHub → Actions → [Your workflow run]

You'll see these jobs running:

1. ✅ validate (1-2 min)
   - Terraform format check
   - Terraform validate

2. ✅ security-scan (2-3 min)
   - tfsec security analysis
   - Identifies security issues

3. ✅ plan-dev (2-3 min)
   - Terraform plan
   - Shows resources to create (~15 resources)

4. ✅ apply-dev (5-8 min)
   - Creates S3 bucket
   - Creates IAM roles
   - Creates SageMaker Model Registry
   - Creates CloudWatch log groups
   - Creates SNS topics
   - Creates Lambda functions
   - Creates Budget
```

**Expected output (in workflow logs):**

```
Apply complete! Resources: 15 added, 0 changed, 0 destroyed.

Outputs:

cloudwatch_log_group_endpoints = "/aws/sagemaker/Endpoints/mlops-diabetes-dev"
cloudwatch_log_group_training = "/aws/sagemaker/TrainingJobs"
data_scientist_role_arn = "arn:aws:iam::123456789012:role/mlops-diabetes-data-scientist-dev"
model_package_group_name = "mlops-diabetes-model-group-dev"
s3_bucket_name = "mlops-diabetes-123456789012-dev"
sagemaker_execution_role_arn = "arn:aws:iam::123456789012:role/mlops-diabetes-sagemaker-execution-dev"
sns_topic_arn = "arn:aws:sns:us-east-1:123456789012:mlops-diabetes-alerts-dev"
```

**✅ Checkpoint:** Workflow shows "✅ apply-dev completed successfully"

### Step 5.4: Verify Infrastructure in AWS

**Status:** 🔴 **MANUAL** - AWS Console verification

**Duration:** 5 minutes

**Option 1: AWS Console (Visual)**

```
1. S3 Bucket:
   https://s3.console.aws.amazon.com/s3/buckets
   Look for: mlops-diabetes-123456789012-dev

2. IAM Roles:
   https://console.aws.amazon.com/iam/home#/roles
   Look for:
   - mlops-diabetes-sagemaker-execution-dev
   - mlops-diabetes-data-scientist-dev

3. SageMaker Model Registry:
   https://console.aws.amazon.com/sagemaker/home#/model-packages
   Look for: mlops-diabetes-model-group-dev

4. CloudWatch Log Groups:
   https://console.aws.amazon.com/cloudwatch/home#logsV2:log-groups
   Look for:
   - /aws/sagemaker/TrainingJobs
   - /aws/sagemaker/Endpoints/mlops-diabetes-dev

5. SNS Topics:
   https://console.aws.amazon.com/sns/home#/topics
   Look for: mlops-diabetes-alerts-dev

6. Lambda Functions:
   https://console.aws.amazon.com/lambda/home#/functions
   Look for: mlops-diabetes-endpoint-shutdown-dev

7. Budgets:
   https://console.aws.amazon.com/billing/home#/budgets
   Look for: MLOps-Dev-Monthly
```

**Option 2: AWS CLI (Faster)**

```powershell
# Set AWS profile
$env:AWS_PROFILE = "mlops-dev"

# Get bucket name from GitHub Actions output
$bucketName = "mlops-diabetes-YOUR_ACCOUNT_ID-dev"  # Replace with actual

# Verify S3 bucket
aws s3 ls | Select-String "mlops-diabetes"

# Verify IAM role
aws iam get-role --role-name mlops-diabetes-sagemaker-execution-dev

# Verify Model Registry
aws sagemaker list-model-package-groups --name-contains diabetes

# Verify Lambda
aws lambda list-functions --query 'Functions[?contains(FunctionName, `mlops-diabetes`)].FunctionName'

# Verify Budget
aws budgets describe-budgets --account-id $(aws sts get-caller-identity --query Account --output text)
```

**✅ Checkpoint:** All resources visible in AWS

### Step 5.5: Add Additional GitHub Secrets (From Terraform Outputs)

**Status:** 🔴 **MANUAL** - Update GitHub Secrets

**Duration:** 5 minutes

**Get values from GitHub Actions artifacts:**

```
GitHub → Actions → [Your workflow run] → apply-dev → Scroll to "Terraform Output"

Copy these values:
- sagemaker_execution_role_arn
- s3_bucket_name
- sns_topic_arn
```

**Add to GitHub Secrets:**

```
Settings → Secrets → Actions → New repository secret
```

| Secret Name | Value | From Terraform Output |
|-------------|-------|----------------------|
| `SAGEMAKER_EXECUTION_ROLE` | `arn:aws:iam::123456789012:role/mlops-diabetes-sagemaker-execution-dev` | sagemaker_execution_role_arn |
| `S3_BUCKET_NAME` | `mlops-diabetes-123456789012-dev` | s3_bucket_name |
| `AWS_ACCOUNT_ID` | `123456789012` | Your AWS account ID |
| `SNS_TOPIC_ARN_DEV` | `arn:aws:sns:us-east-1:123456789012:mlops-diabetes-alerts-dev` | sns_topic_arn |

**✅ Checkpoint:** 7 total secrets in GitHub (3 role ARNs + 4 infrastructure values)

---

## 6️⃣ Automated - MLOps Pipeline

> **📊 Data Flow Note:** Wondering how data gets into the pipeline? See **[Data Ingestion Guide](./DATA_INGESTION_GUIDE.md)** for complete details on:
> - Current implementation (GitHub download)
> - Production options (S3 events, scheduled ingestion, streaming)
> - Migration paths from learning to production

### Step 6.1: Trigger MLOps Pipeline

**Status:** 🟢 **AUTOMATED** - GitHub Actions

**Duration:** 25-30 minutes (fully automated)

**Method 1: Automatic Trigger (Push to develop)**

```powershell
# Make any change to code
git checkout develop
echo "# Pipeline test" >> README.md
git add README.md
git commit -m "feat: Trigger MLOps pipeline"
git push origin develop
```

**Method 2: Manual Workflow Dispatch**

```
GitHub → Actions → "MLOps Pipeline - Diabetes Classification"
Click: "Run workflow"
Branch: develop
Execute pipeline: ✅ true
Click: "Run workflow"
```

### Step 6.2: Monitor MLOps Pipeline Execution

**Status:** 🔴 **MANUAL** - Watch automated jobs

**Duration:** 25-30 minutes (watch automated process)

**GitHub Actions will run these jobs automatically:**

```
GitHub → Actions → "MLOps Pipeline" → [Your run]

Jobs (all automatic):

1. ✅ code-quality (3-5 min)
   - Black code formatting check
   - Flake8 linting
   - Pytest unit tests
   - Code coverage report

2. ✅ data-validation (2 min)
   - Download diabetes dataset
   - Validate data schema
   - Check for missing values

3. ✅ build-docker (Optional, skipped by default)
   - Build custom Docker images
   - Push to Amazon ECR

4. ✅ upload-data (1 min)
   - Upload dataset to S3
   - Path: s3://bucket/diabetes-project/data/raw/

5. ✅ sagemaker-pipeline (15-20 min) ⏰ LONGEST STEP
   - Create SageMaker Pipeline
   - Execute pipeline steps:
     a. Data Processing (5-7 min)
        - Feature scaling
        - Train/test split
        - Save to S3: data/processed/
     
     b. Model Training (8-10 min)
        - XGBoost classifier
        - Hyperparameter tuning (if enabled)
        - Save model to S3: models/
     
     c. Model Evaluation (2-3 min)
        - Calculate metrics (Accuracy, F1, ROC-AUC)
        - Generate evaluation report
        - Save to S3: evaluation/
     
     d. Model Registration (1 min)
        - Register in Model Registry
        - Status: PendingApproval or Approved (dev)

6. ✅ deploy-model (8-10 min)
   - Create endpoint configuration
   - Deploy model to endpoint
   - Endpoint name: mlops-diabetes-endpoint-dev
   - Instance: ml.t2.medium
   - Initial instance count: 1
   - Auto-scaling: Enabled (if configured)

7. ✅ setup-monitoring (2-3 min)
   - Enable data capture
   - Create baseline for monitoring
   - Schedule monitoring job (hourly)

8. ✅ notify (1 min)
   - Send success/failure notification
   - Email via SNS
   - Slack (if configured)
```

**Total Duration:** ~25-30 minutes (all automated!)

**✅ Checkpoint:** All jobs show green checkmarks

### Step 6.3: Verify in AWS SageMaker Console

**Status:** 🔴 **MANUAL** - Verification in AWS Console

**Duration:** 5 minutes

**Check SageMaker Pipeline:**

```
1. SageMaker Console → Pipelines
   https://console.aws.amazon.com/sagemaker/home#/pipelines
   
   Look for: diabetes-training-pipeline-dev
   Status: Succeeded
   Click on it to see execution graph
```

**Check Training Job:**

```
2. SageMaker Console → Training → Training jobs
   https://console.aws.amazon.com/sagemaker/home#/jobs
   
   Look for: diabetes-training-YYYY-MM-DD-HH-MM-SS
   Status: Completed
   Billable time: ~2-3 minutes
   Metrics: View accuracy, F1-score
```

**Check Model Registry:**

```
3. SageMaker Console → Model Registry
   https://console.aws.amazon.com/sagemaker/home#/model-packages
   
   Look for: mlops-diabetes-model-group-dev
   Model versions: 1 (or more if retrained)
   Status: Approved (for dev)
```

**Check Endpoint:**

```
4. SageMaker Console → Inference → Endpoints
   https://console.aws.amazon.com/sagemaker/home#/endpoints
   
   Look for: mlops-diabetes-endpoint-dev
   Status: InService ✅
   Instance type: ml.t2.medium
   Instance count: 1
   
   Click on endpoint → Monitor tab:
   - Invocations: 0 (initially)
   - Model latency: N/A (no requests yet)
```

**Check Model Monitor:**

```
5. SageMaker Console → Governance → Model Monitor
   https://console.aws.amazon.com/sagemaker/home#/model-monitor
   
   Look for monitoring schedule:
   - Endpoint: mlops-diabetes-endpoint-dev
   - Schedule: Hourly
   - Status: Scheduled
```

**✅ Checkpoint:** All SageMaker resources visible and operational

### Step 6.4: Test Model Inference

**Status:** 🔴 **MANUAL** - Test endpoint

**Duration:** 3 minutes

**Create test script:**

```powershell
# Create test-inference.py
@"
import boto3
import json

# Sample data (diabetes features)
sample_data = '0.038076,0.050680,0.061696,0.021872,-0.044223,-0.034821,-0.043401,-0.002592,0.019908,-0.017646'

# Invoke endpoint
client = boto3.client('sagemaker-runtime', region_name='us-east-1')

response = client.invoke_endpoint(
    EndpointName='mlops-diabetes-endpoint-dev',
    ContentType='text/csv',
    Body=sample_data
)

# Parse result
prediction = float(response['Body'].read().decode('utf-8'))
print(f'Prediction: {prediction:.4f}')
print(f'Diabetes Risk: {"HIGH" if prediction > 0.5 else "LOW"}')
"@ | Out-File -FilePath test-inference.py -Encoding utf8

# Run test
python test-inference.py
```

**Expected output:**

```
Prediction: 0.7234
Diabetes Risk: HIGH
```

**✅ Checkpoint:** Model successfully serving predictions

---

## 7️⃣ Manual Steps - Production Deployment

### Step 7.1: Prepare Production Configuration

**Status:** 🔴 **MANUAL** - Edit production config

**Duration:** 10 minutes

**Edit:**
```
infrastructure/terraform/environments/production/terraform.tfvars
```

**Production Settings:**

```hcl
# Production Environment Configuration
environment = "production"

# ⚠️ UPDATE THESE
owner_email = "mlops-team@company.com"
alert_email_endpoints = [
  "mlops-team@company.com",
  "oncall@company.com",
  "manager@company.com"
]

# High Availability
sagemaker_endpoint_initial_instance_count = 2  # HA across 2 AZs
sagemaker_endpoint_instance_type = "ml.m5.xlarge"  # Production-grade
enable_autoscaling = true
autoscaling_min_capacity = 2
autoscaling_max_capacity = 10
autoscaling_target_value = 70.0  # CPU target

# Security (Production-grade)
enable_vpc = true  # Network isolation
enable_kms_encryption = true  # Encrypt all data
enable_cloudtrail = true  # Audit logging
enable_guardduty = true  # Threat detection

# Cost Control
budget_amount = 1500  # $1500/month
enable_auto_shutdown = false  # Production runs 24/7

# Model Approval
model_approval_status = "PendingManualApproval"  # Require manual approval

# Monitoring
cloudwatch_log_retention_days = 30  # 30-day retention
enable_model_monitor = true
monitoring_schedule_expression = "cron(0 * * * ? *)"  # Hourly
```

**Commit to main branch:**

```powershell
git checkout main
git pull origin main
git add infrastructure/terraform/environments/production/terraform.tfvars
git commit -m "feat: Configure production environment"
git push origin main
```

### Step 7.2: Create Production Deployment PR

**Status:** 🔴 **MANUAL** - GitHub PR process

**Duration:** 5 minutes

```powershell
# Create feature branch
git checkout -b feature/production-deployment

# Make any additional changes needed
# Review security, cost estimates, etc.

# Commit
git add .
git commit -m "feat: Production deployment ready"
git push -u origin feature/production-deployment
```

**On GitHub:**

```
1. Go to: https://github.com/YOUR_USERNAME/mlopsaws/pulls
2. Click: "New pull request"
3. Base: main
4. Compare: feature/production-deployment
5. Title: "Production Deployment - Diabetes Classifier"
6. Description:
   - Infrastructure changes
   - Security enhancements
   - Cost estimate: $1200-1500/month
   - Approval required before merge
7. Create pull request
8. Request review from team
```

**GitHub Actions will automatically:**

- ✅ Run Terraform plan for production
- ✅ Generate cost estimate (Infracost)
- ✅ Run security scan
- ✅ Comment results on PR

**Review the plan carefully before merging!**

### Step 7.3: Approve and Deploy to Production

**Status:** 🔴 **MANUAL** - Requires approval

**Duration:** 15-20 minutes

**After PR is approved and merged:**

```
1. GitHub → Actions
2. Select: "Terraform Infrastructure CI/CD"
3. Click: "Run workflow"
4. Configure:
   - Branch: main
   - Environment: production
   - Action: apply
5. Click: "Run workflow"
```

**Approval gate will pause deployment:**

```
Workflow status: ⏸️ Waiting for approval

Review:
- Terraform plan (resources to create)
- Cost estimate ($1200-1500/month)
- Security scan results

Approvers:
- You (repository owner)
- Team lead (if configured)

Click: "Review deployments" → "Approve and deploy"
```

**GitHub Actions will then:**

1. ✅ Apply Terraform to production AWS account
2. ✅ Create production infrastructure
3. ✅ Output production credentials

**Duration:** 15-20 minutes

### Step 7.4: Deploy Model to Production

**Status:** 🟢 **AUTOMATED** with 🔴 **MANUAL** approval

**Trigger:**

```
GitHub → Actions → "MLOps Pipeline"
Run workflow:
- Branch: main
- Execute pipeline: true
```

**Pipeline runs automatically until deployment:**

```
1. ✅ Code quality checks (automated)
2. ✅ Data validation (automated)
3. ✅ SageMaker pipeline (automated)
4. ⏸️ Deploy model (WAITING FOR APPROVAL)
```

**Manual approval required:**

```
1. Review model metrics:
   - Accuracy > 85%
   - Precision > 0.80
   - Recall > 0.75
   - F1-Score > 0.77
   - ROC-AUC > 0.85

2. Check evaluation reports in S3

3. Approve deployment:
   GitHub Actions → Review deployments → Approve
```

**After approval:**

```
5. ✅ Deploy to production endpoint (automated)
6. ✅ Setup monitoring (automated)
7. ✅ Send notifications (automated)
```

**✅ Checkpoint:** Production endpoint serving traffic

---

## 8️⃣ Monitoring & Validation

### Automated Monitoring (Already Setup)

**Status:** 🟢 **AUTOMATED** - No action needed

The following monitoring is **automatic** after deployment:

1. **CloudWatch Logs**
   - All training jobs logged automatically
   - All endpoint invocations logged
   - Lambda function executions logged

2. **SageMaker Model Monitor**
   - Hourly data quality checks
   - Automatic drift detection
   - Alerts sent to SNS if drift detected

3. **Budget Alerts**
   - Email alert at 80% of budget
   - Email alert at 100% of budget
   - Daily cost tracking

4. **Auto-Shutdown (Dev only)**
   - Endpoint automatically deleted at 7 PM UTC
   - Saves 60% of endpoint costs
   - Can be disabled if needed

### Manual Monitoring Tasks

**Status:** 🔴 **MANUAL** - Daily/weekly checks

#### Daily Monitoring (5 minutes)

```powershell
# Check costs
aws ce get-cost-and-usage \
  --time-period Start=$(Get-Date -Format yyyy-MM-dd),End=$(Get-Date -Format yyyy-MM-dd) \
  --granularity DAILY \
  --metrics BlendedCost

# Check endpoint status
aws sagemaker describe-endpoint --endpoint-name mlops-diabetes-endpoint-dev

# Check recent invocations (CloudWatch)
aws logs tail /aws/sagemaker/Endpoints/mlops-diabetes-endpoint-dev --since 1h
```

#### Weekly Monitoring (15 minutes)

```
1. Review GitHub Actions history
   - Any failed workflows?
   - Cost estimate trends

2. Review SageMaker Model Monitor
   - Any drift detected?
   - Data quality issues?

3. Review AWS Cost Explorer
   - Unexpected cost increases?
   - Optimize instance usage

4. Review model performance
   - Accuracy degradation?
   - Need retraining?
```

**✅ Checkpoint:** All monitoring systems operational

---

## 9️⃣ PowerShell Scripts Reference

### When to Use PowerShell Scripts vs GitHub Actions

**PowerShell Scripts = Local Development Only**

Use PowerShell scripts ONLY if:
- Learning Terraform hands-on
- No internet/GitHub access
- Quick local testing
- Debugging infrastructure issues

**GitHub Actions = Production Method** ⭐ **RECOMMENDED**

Use GitHub Actions for:
- All production deployments
- Team collaboration
- Automated testing and validation
- Complete audit trail

### Script 1: deploy-infrastructure.ps1

**Purpose:** Deploy infrastructure locally (alternative to GitHub Actions)

**Location:** `infrastructure/scripts/deploy-infrastructure.ps1`

**When to use:** Learning Terraform, local testing only

**Usage:**

```powershell
cd infrastructure/scripts

# Deploy to dev
.\deploy-infrastructure.ps1 -Environment dev -Action all

# Options:
# -Environment: dev, staging, production
# -Action: init, plan, apply, destroy, output, all
# -AutoApprove: Skip confirmation prompts
# -AWSProfile: AWS CLI profile to use
```

**What it does:**

1. Validates prerequisites (Terraform, AWS CLI)
2. Navigates to environment directory
3. Runs `terraform init`
4. Runs `terraform plan`
5. Runs `terraform apply`
6. Calls `update-config.ps1` automatically
7. Displays Terraform outputs

**Example:**

```powershell
# Full deployment
.\deploy-infrastructure.ps1 -Environment dev -Action all

# Plan only (no changes)
.\deploy-infrastructure.ps1 -Environment dev -Action plan

# Destroy infrastructure
.\deploy-infrastructure.ps1 -Environment dev -Action destroy -AutoApprove
```

**GitHub Actions Equivalent:**

```yaml
# In .github/workflows/terraform.yml
- name: Terraform Apply
  run: terraform apply -auto-approve tfplan
  working-directory: infrastructure/terraform/environments/dev
```

### Script 2: update-config.ps1

**Purpose:** Auto-update config.yaml from Terraform outputs

**Location:** `infrastructure/scripts/update-config.ps1`

**When to use:** After local `terraform apply` (not needed with GitHub Actions)

**Usage:**

```powershell
cd infrastructure/scripts

# Update config for dev environment
.\update-config.ps1 -Environment dev
```

**What it does:**

1. Reads Terraform outputs from `environments/dev/`
2. Updates `config/config.yaml` with:
   - S3 bucket name
   - SageMaker execution role ARN
   - Model Registry group name
   - CloudWatch log groups
   - SNS topic ARN
3. Preserves other settings (model hyperparameters, etc.)

**Before running:**
```yaml
# config/config.yaml (before)
s3:
  bucket_name: "YOUR_S3_BUCKET_NAME"  # Placeholder
sagemaker:
  role: "YOUR_SAGEMAKER_ROLE_ARN"  # Placeholder
```

**After running:**
```yaml
# config/config.yaml (after)
s3:
  bucket_name: "mlops-diabetes-123456789012-dev"  # Real value
sagemaker:
  role: "arn:aws:iam::123456789012:role/mlops-diabetes-sagemaker-execution-dev"  # Real value
```

**GitHub Actions Equivalent:**

This is **built into the Terraform workflow** - config is updated automatically as part of deployment.

### Script 3: validate-setup.ps1

**Purpose:** Validate infrastructure before running ML pipeline

**Location:** `scripts/validate-setup.ps1`

**When to use:** Before running ML pipeline locally

**Usage:**

```powershell
# Validate dev environment
.\scripts\validate-setup.ps1 -Environment dev
```

**What it validates:**

1. **AWS Connection**
   - AWS CLI configured
   - Valid credentials
   - Can access AWS account

2. **Infrastructure Existence**
   - S3 bucket exists
   - IAM roles exist
   - Model Registry created
   - CloudWatch log groups exist
   - SNS topics configured

3. **Configuration File**
   - config.yaml exists
   - Contains real values (not placeholders)
   - All required fields present

4. **Python Environment**
   - Python 3.8+ installed
   - Required packages installed (boto3, sagemaker, etc.)

5. **Permissions**
   - SageMaker execution role has S3 access
   - Can create training jobs
   - Can deploy endpoints

**Example output:**

```
╔══════════════════════════════════════════════════════════════════╗
║              🔍 MLOps Setup Validation Check                    ║
╚══════════════════════════════════════════════════════════════════╝

Environment: dev

Checking AWS Connection...
✅ AWS CLI configured
✅ AWS credentials valid
✅ Account ID: 123456789012

Checking Infrastructure...
✅ S3 bucket exists: mlops-diabetes-123456789012-dev
✅ SageMaker execution role exists
✅ Model Registry created: mlops-diabetes-model-group-dev
✅ CloudWatch log groups configured
✅ SNS topic exists

Checking Configuration...
✅ config.yaml found
✅ All values updated (no placeholders)

Checking Python Environment...
✅ Python 3.11.5 installed
✅ All required packages installed

Checking Permissions...
✅ SageMaker role has S3 access
✅ Can create training jobs
✅ Can deploy endpoints

╔══════════════════════════════════════════════════════════════════╗
║                  ✅ All Checks Passed!                          ║
╚══════════════════════════════════════════════════════════════════╝

Next steps:
  1. Run ML pipeline: python pipelines/training_pipeline.py --environment dev --execute
  2. Monitor in AWS Console: https://console.aws.amazon.com/sagemaker/
```

**GitHub Actions Equivalent:**

These checks are **built into the MLOps pipeline workflow** - validation happens automatically before training.

---

## 🔟 Troubleshooting

### Issue 1: OIDC Authentication Failed

**Error:**
```
Error: Could not assume role with OIDC
Not authorized to perform sts:AssumeRoleWithWebIdentity
```

**Status:** 🔴 **MANUAL FIX**

**Solution:**

```powershell
# 1. Verify OIDC provider exists
aws iam list-open-id-connect-providers

# Expected output:
# arn:aws:iam::123456789012:oidc-provider/token.actions.githubusercontent.com

# 2. Check trust policy
aws iam get-role --role-name GitHubActions-MLOps-Dev --query 'Role.AssumeRolePolicyDocument'

# 3. Verify repository name in trust policy matches
# Trust policy: "repo:YOUR_USERNAME/mlopsaws:*"
# GitHub repo: https://github.com/YOUR_USERNAME/mlopsaws

# 4. Fix trust policy if needed
aws iam update-assume-role-policy \
  --role-name GitHubActions-MLOps-Dev \
  --policy-document file://trust-policy-dev.json
```

### Issue 2: Terraform State Lock

**Error:**
```
Error: Error acquiring the state lock
Lock Info:
  ID: abc123-def456-ghi789
```

**Status:** 🔴 **MANUAL FIX**

**Solution:**

```powershell
# Option 1: Wait (another workflow is running)
# Check: GitHub → Actions (is another workflow running?)

# Option 2: Force unlock (ONLY if sure no other process running)
cd infrastructure/terraform/environments/dev
terraform force-unlock abc123-def456-ghi789

# Option 3: Delete lock from DynamoDB (if using remote state)
aws dynamodb delete-item \
  --table-name mlops-terraform-locks \
  --key '{"LockID":{"S":"mlops-diabetes-dev"}}'
```

### Issue 3: GitHub Secrets Not Found

**Error:**
```
Error: Secret SAGEMAKER_EXECUTION_ROLE not found
```

**Status:** 🔴 **MANUAL FIX**

**Solution:**

```
1. Go to: GitHub → Settings → Secrets → Actions
2. Verify secret exists (case-sensitive!)
3. If missing, add it:
   Name: SAGEMAKER_EXECUTION_ROLE
   Value: arn:aws:iam::123456789012:role/mlops-diabetes-sagemaker-execution-dev
4. Re-run workflow
```

### Issue 4: SageMaker Training Job Failed

**Error:**
```
ClientError: AlgorithmError: Framework error:
Traceback (most recent call last):
  File "/opt/ml/code/train.py", line 45
```

**Status:** 🔴 **MANUAL DEBUG**

**Solution:**

```powershell
# 1. Check CloudWatch logs
aws logs tail /aws/sagemaker/TrainingJobs --follow --since 1h

# 2. Common issues:
# - Data not in S3
# - Wrong data format
# - Missing dependencies

# 3. Verify data exists
aws s3 ls s3://mlops-diabetes-123456789012-dev/data/raw/

# 4. Check data format
aws s3 cp s3://mlops-diabetes-123456789012-dev/data/raw/diabetes.csv - | head -5

# 5. Re-upload data if needed
python src/processing/download_data.py
aws s3 cp data/raw/diabetes.csv s3://mlops-diabetes-123456789012-dev/data/raw/
```

### Issue 5: Endpoint Deployment Timeout

**Error:**
```
Endpoint deployment timed out after 15 minutes
```

**Status:** 🔴 **MANUAL DEBUG**

**Solution:**

```powershell
# 1. Check endpoint status
aws sagemaker describe-endpoint --endpoint-name mlops-diabetes-endpoint-dev

# Possible statuses:
# - Creating: Still deploying (wait longer)
# - Failed: Check logs
# - InService: Success!

# 2. Check endpoint logs
aws logs tail /aws/sagemaker/Endpoints/mlops-diabetes-endpoint-dev --since 30m

# 3. Common causes:
# - Model too large
# - Instance type too small
# - VPC networking issues

# 4. Delete and retry with smaller instance
aws sagemaker delete-endpoint --endpoint-name mlops-diabetes-endpoint-dev
# Then re-run deployment workflow
```

### Issue 6: High AWS Costs

**Problem:** Monthly bill is higher than expected

**Status:** 🔴 **MANUAL COST OPTIMIZATION**

**Solution:**

```powershell
# 1. Identify cost drivers
aws ce get-cost-and-usage \
  --time-period Start=2024-11-01,End=2024-11-05 \
  --granularity DAILY \
  --metrics BlendedCost \
  --group-by Type=DIMENSION,Key=SERVICE

# Common culprits:
# - SageMaker endpoints running 24/7
# - Large data storage in S3
# - CloudWatch log retention

# 2. Delete unused endpoints
aws sagemaker list-endpoints
aws sagemaker delete-endpoint --endpoint-name mlops-diabetes-endpoint-dev

# 3. Enable auto-shutdown (dev only)
# Edit: infrastructure/terraform/environments/dev/terraform.tfvars
enable_auto_shutdown = true

# 4. Reduce log retention
cloudwatch_log_retention_days = 1  # Dev only

# 5. Use spot instances for training
use_spot_instances = true
max_wait_time_in_seconds = 3600

# 6. Clean up old data
aws s3 ls s3://mlops-diabetes-123456789012-dev/
aws s3 rm s3://mlops-diabetes-123456789012-dev/old-data/ --recursive
```

### Issue 7: User Left Organization - Need to Update Trust Policy

**Problem:** Team member who set up OIDC left, workflows failing with access denied.

**Symptoms:**
```
Error: Not authorized to perform sts:AssumeRoleWithWebIdentity
Trust policy references: repo:old-user/mlopsaws:*
Current repo: repo:new-user/mlopsaws:*
```

**Solution 1: Quick Fix - Update Trust Policy (If Personal Repo)**

```powershell
# Get new username and account details
$newUsername = "new-user"  # Replace with actual username
$accountId = aws sts get-caller-identity --query Account --output text

# Create updated trust policy
@"
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::${accountId}:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
        },
        "StringLike": {
          "token.actions.githubusercontent.com:sub": "repo:${newUsername}/mlopsaws:*"
        }
      }
    }
  ]
}
"@ | Out-File -FilePath trust-policy-updated.json -Encoding utf8

# Update each role
aws iam update-assume-role-policy `
  --role-name GitHubActions-MLOps-Dev `
  --policy-document file://trust-policy-updated.json

aws iam update-assume-role-policy `
  --role-name GitHubActions-MLOps-Staging `
  --policy-document file://trust-policy-updated.json

aws iam update-assume-role-policy `
  --role-name GitHubActions-MLOps-Prod `
  --policy-document file://trust-policy-updated.json

Write-Host "✅ Trust policies updated for new user: $newUsername"
```

**Solution 2: Long-Term Fix - Migrate to Organization (RECOMMENDED)**

This prevents future issues when users change:

```powershell
# See: docs/TRUST_POLICY_BEST_PRACTICES.md for complete guide

# Quick summary:
# 1. Create GitHub organization (free)
# 2. Transfer repository to organization
# 3. Update trust policy to use org name instead of username
# 4. Manage access via teams (user-independent)

# Result: When users leave, just remove from team - no AWS changes needed!
```

**Prevention:**
- **For Learning/Development:** Username-based trust is acceptable
- **For Production:** Always use organization-based trust policies
- **See:** `docs/TRUST_POLICY_BEST_PRACTICES.md` for migration guide

---

## ✅ FINAL CHECKLIST

### One-Time Setup (You Do Once)

- [ ] 🔴 **MANUAL** - AWS account created with MFA
- [ ] 🔴 **MANUAL** - IAM admin user created
- [ ] 🔴 **MANUAL** - AWS CLI installed and configured
- [ ] 🔴 **MANUAL** - GitHub repository created
- [ ] 🔴 **MANUAL** - Local tools installed (Git, Python, VS Code)
- [ ] 🔴 **MANUAL** - OIDC identity provider created in AWS
- [ ] 🔴 **MANUAL** - IAM roles created (dev, staging, prod)
- [ ] 🔴 **MANUAL** - GitHub Secrets configured (7 secrets)
- [ ] 🔴 **MANUAL** - Environment protection rules configured
- [ ] 🔴 **MANUAL** - terraform.tfvars updated with your details

### First Deployment (Automated After Setup)

- [ ] 🔴 **MANUAL** - Push code to develop branch
- [ ] 🟢 **AUTOMATED** - GitHub Actions validates Terraform
- [ ] 🟢 **AUTOMATED** - Security scan passes
- [ ] 🟢 **AUTOMATED** - Infrastructure deployed to AWS
- [ ] 🔴 **MANUAL** - Verify resources in AWS Console
- [ ] 🔴 **MANUAL** - Add additional GitHub Secrets from Terraform outputs
- [ ] 🔴 **MANUAL** - Trigger MLOps pipeline
- [ ] 🟢 **AUTOMATED** - Model training completes
- [ ] 🟢 **AUTOMATED** - Model deployed to endpoint
- [ ] 🟢 **AUTOMATED** - Monitoring configured
- [ ] 🔴 **MANUAL** - Test endpoint with sample data

### Production Deployment (When Ready)

- [ ] 🔴 **MANUAL** - Update production terraform.tfvars
- [ ] 🔴 **MANUAL** - Create deployment PR
- [ ] 🟢 **AUTOMATED** - Terraform plan generated
- [ ] 🟢 **AUTOMATED** - Cost estimate created
- [ ] 🔴 **MANUAL** - Review and approve PR
- [ ] 🔴 **MANUAL** - Trigger production workflow
- [ ] 🔴 **MANUAL** - Approve infrastructure deployment
- [ ] 🟢 **AUTOMATED** - Production infrastructure deployed
- [ ] 🔴 **MANUAL** - Trigger production MLOps pipeline
- [ ] 🔴 **MANUAL** - Review model metrics
- [ ] 🔴 **MANUAL** - Approve model deployment
- [ ] 🟢 **AUTOMATED** - Production endpoint deployed
- [ ] 🔴 **MANUAL** - Smoke test production endpoint
- [ ] 🟡 **SEMI-AUTO** - Monitor costs and performance

---

## 📞 Support & Next Steps

### You Did It! 🎉

If you've reached this point, you now have:

✅ Production-grade MLOps infrastructure  
✅ Automated CI/CD pipelines  
✅ Secure OIDC authentication  
✅ Cost monitoring and controls  
✅ Model training and deployment automation  
✅ Complete audit trail via GitHub Actions  

### Next Steps

1. **Learn More:**
   - Experiment with different hyperparameters
   - Try different algorithms (Random Forest, Neural Networks)
   - Add more features to the dataset

2. **Scale Up:**
   - Deploy to staging environment
   - Configure production with high availability
   - Add A/B testing for models

3. **Enhance Monitoring:**
   - Add custom CloudWatch dashboards
   - Configure PagerDuty alerts
   - Implement anomaly detection

4. **Optimize Costs:**
   - Use Spot instances for training
   - Implement endpoint auto-scaling
   - Archive old data to S3 Glacier

### Documentation

- **This guide:** `docs/COMPLETE_SETUP_GUIDE.md`
- **Quick reference:** `README.md`
- **2-day learning:** `QUICKSTART.md`
- **Project summary:** `PROJECT_SUMMARY.md`

### Getting Help

- **GitHub Issues:** Create issue in repository
- **AWS Forums:** https://forums.aws.amazon.com/
- **SageMaker Docs:** https://docs.aws.amazon.com/sagemaker/

---

**Last Updated:** November 4, 2025  
**Version:** 3.0 - Complete Consolidated Guide  
**Maintainer:** MLOps Team  
**Status:** ✅ Production Ready

---

**Total Manual Time:** ~2-3 hours (one-time setup)  
**Total Automated Time:** ~40-50 minutes per deployment  
**Monthly Cost (Dev):** $20-30 with auto-shutdown  
**Monthly Cost (Prod):** $1200-1500 (high availability)  

**You now have everything you need to deploy production-grade MLOps on AWS! 🚀**
