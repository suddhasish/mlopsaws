# 🚀 END-TO-END SETUP GUIDE
## Complete MLOps AWS SageMaker Project - From Zero to Production

**Version:** 1.0  
**Last Updated:** November 4, 2025  
**Estimated Time:** 4-6 hours for complete setup  
**Difficulty:** Intermediate

---

## ⚡ QUICK START (For Experienced Users)

If you already have AWS account, CLI configured, and Terraform installed:

```powershell
# 1. Deploy infrastructure (auto-updates config.yaml)
cd infrastructure\scripts
.\deploy-infrastructure.ps1 -Environment dev -Action all

# 2. Validate setup
cd ..\..
.\scripts\validate-setup.ps1

# 3. Setup Python & download data
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python src\processing\download_data.py

# 4. Run ML pipeline
python pipelines\training_pipeline.py --environment dev --execute
```

**For detailed step-by-step instructions, continue reading below.**

---

## 📋 TABLE OF CONTENTS

1. [Prerequisites](#prerequisites)
2. [AWS Account Setup](#aws-account-setup)
3. [Local Development Environment](#local-development-environment)
4. [Infrastructure Deployment](#infrastructure-deployment)
5. [Python Project Configuration](#python-project-configuration)
6. [First Pipeline Execution](#first-pipeline-execution)
7. [Monitoring & Validation](#monitoring--validation)
8. [Production Deployment](#production-deployment)
9. [Troubleshooting](#troubleshooting)
10. [Cost Management](#cost-management)

---

## ✅ PREREQUISITES

### Required Knowledge
- [ ] Basic AWS concepts (S3, IAM, EC2)
- [ ] Terraform fundamentals
- [ ] Python programming
- [ ] Git/GitHub basics
- [ ] Command line proficiency

### Required Tools
- [ ] Windows 10/11 OR Linux/Mac
- [ ] PowerShell 5.1+ (Windows) or Bash (Linux/Mac)
- [ ] Git 2.30+
- [ ] Python 3.8+
- [ ] Terraform 1.5+
- [ ] AWS CLI v2
- [ ] VS Code (recommended)

### AWS Account Requirements
- [ ] Active AWS account
- [ ] Credit card on file
- [ ] Email access for verification
- [ ] Phone number for MFA

**⚠️ COST WARNING:** 
- AWS Free Tier does **NOT** include SageMaker
- Minimum expected cost: **$30-50/month**
- Set up billing alerts immediately!

---

## 1️⃣ AWS ACCOUNT SETUP

### Step 1.1: Create AWS Account (if new)

**Duration:** 15 minutes

1. Go to https://aws.amazon.com/
2. Click **"Create an AWS Account"**
3. Enter email address and account name
4. Verify email
5. Set root password (strong: 20+ chars, mixed case, numbers, symbols)
6. Enter contact information
7. Add credit/debit card
8. Verify phone number
9. Select **Free** support plan

**✅ Checkpoint:** You can log into AWS Console

### Step 1.2: Secure Root Account

**Duration:** 10 minutes

```powershell
# 1. Enable MFA on root account
# Go to: https://console.aws.amazon.com/iam/home#/security_credentials
# - Click "Assign MFA device"
# - Choose "Virtual MFA device"
# - Use Google Authenticator or Authy
# - Scan QR code and enter two consecutive codes

# 2. Create strong password policy
# IAM Console → Account settings → Password policy
# - Minimum 14 characters
# - Require uppercase, lowercase, numbers, symbols
# - Enable password expiration (90 days)
# - Prevent password reuse (5 passwords)
```

**✅ Checkpoint:** Root account has MFA enabled (green checkmark)

### Step 1.3: Create IAM Admin User

**Duration:** 15 minutes

```powershell
# 1. Go to IAM Console
https://console.aws.amazon.com/iam/

# 2. Create user
- Click "Users" → "Create user"
- Username: "mlops-admin"
- Select "Provide user access to AWS Management Console"
- Console password: Custom password (save in password manager)
- Uncheck "User must create new password at next sign-in"

# 3. Attach Administrator policy
- Next → "Attach policies directly"
- Search and select: "AdministratorAccess"
- Next → Create user

# 4. Save credentials
- Download CSV with username and password
- Store securely in password manager

# 5. Enable MFA for admin user
- IAM → Users → mlops-admin → Security credentials
- Assign MFA device (same as root)
```

**✅ Checkpoint:** Can log in as `mlops-admin` with MFA

### Step 1.4: Install and Configure AWS CLI

**Duration:** 10 minutes

**Windows (PowerShell):**
```powershell
# Download AWS CLI v2
$url = "https://awscli.amazonaws.com/AWSCLIV2.msi"
$output = "$env:TEMP\AWSCLIV2.msi"
Invoke-WebRequest -Uri $url -OutFile $output
Start-Process msiexec.exe -Wait -ArgumentList "/i $output /quiet"

# Verify installation
aws --version  # Should show: aws-cli/2.x.x

# Configure AWS CLI
aws configure --profile mlops-dev

# Enter when prompted:
# AWS Access Key ID: (Go to IAM → Users → mlops-admin → Security credentials → Create access key)
# AWS Secret Access Key: (shown only once - save it!)
# Default region name: us-east-1
# Default output format: json

# Test connection
aws sts get-caller-identity --profile mlops-dev
# Should show your account ID and user ARN
```

**Linux/Mac:**
```bash
# Download and install
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Verify
aws --version

# Configure
aws configure --profile mlops-dev

# Test
aws sts get-caller-identity --profile mlops-dev
```

**✅ Checkpoint:** `aws sts get-caller-identity` returns your account info

### Step 1.5: Request SageMaker Service Quota Increases

**Duration:** 5 minutes (approval: 1-2 business days)

```powershell
# Check current quotas
aws service-quotas get-service-quota `
  --service-code sagemaker `
  --quota-code L-D9090DE7 `  # ml.m5.xlarge for training
  --profile mlops-dev

# Request increases (if needed)
# Go to: https://console.aws.amazon.com/servicequotas/home/services/sagemaker/quotas

# Request these quotas:
# 1. "ml.t3.medium for processing job usage" → 2 instances
# 2. "ml.m5.large for training job usage" → 2 instances
# 3. "ml.t2.medium for endpoint usage" → 2 instances
```

**✅ Checkpoint:** Quota requests submitted (check email for approval)

### Step 1.6: Enable Cost and Billing Alerts

**Duration:** 10 minutes

```powershell
# 1. Enable Billing Alerts
# Go to: https://console.aws.amazon.com/billing/home#/preferences
# - Check "Receive Billing Alerts"
# - Check "Receive Free Tier Usage Alerts"
# - Enter email address
# - Save preferences

# 2. Create Budget (via CLI)
aws budgets create-budget `
  --account-id $(aws sts get-caller-identity --query Account --output text --profile mlops-dev) `
  --budget file://budget.json `
  --notifications-with-subscribers file://notifications.json `
  --profile mlops-dev
```

**budget.json:**
```json
{
  "BudgetName": "MLOps-Monthly-Budget",
  "BudgetLimit": {
    "Amount": "50",
    "Unit": "USD"
  },
  "TimeUnit": "MONTHLY",
  "BudgetType": "COST"
}
```

**notifications.json:**
```json
[
  {
    "Notification": {
      "NotificationType": "ACTUAL",
      "ComparisonOperator": "GREATER_THAN",
      "Threshold": 80
    },
    "Subscribers": [
      {
        "SubscriptionType": "EMAIL",
        "Address": "your-email@example.com"
      }
    ]
  }
]
```

**✅ Checkpoint:** You receive a budget confirmation email

---

## 2️⃣ LOCAL DEVELOPMENT ENVIRONMENT

### Step 2.1: Install Git

**Duration:** 5 minutes

**Windows:**
```powershell
# Download from https://git-scm.com/download/win
# Or use winget:
winget install Git.Git

# Verify
git --version
```

**Linux:**
```bash
sudo apt-get update
sudo apt-get install git

# Verify
git --version
```

**✅ Checkpoint:** Git version 2.30+

### Step 2.2: Install Terraform

**Duration:** 5 minutes

**Windows (PowerShell):**
```powershell
# Using Chocolatey
choco install terraform

# Or manual:
$terraformUrl = "https://releases.hashicorp.com/terraform/1.6.0/terraform_1.6.0_windows_amd64.zip"
$output = "$env:TEMP\terraform.zip"
Invoke-WebRequest -Uri $terraformUrl -OutFile $output
Expand-Archive -Path $output -DestinationPath "C:\terraform"
$env:PATH += ";C:\terraform"

# Verify
terraform --version  # Should show 1.5.0+
```

**Linux:**
```bash
wget https://releases.hashicorp.com/terraform/1.6.0/terraform_1.6.0_linux_amd64.zip
unzip terraform_1.6.0_linux_amd64.zip
sudo mv terraform /usr/local/bin/
terraform --version
```

**✅ Checkpoint:** `terraform --version` shows 1.5.0+

### Step 2.3: Install Python and Dependencies

**Duration:** 10 minutes

```powershell
# Windows: Download from python.org or use:
winget install Python.Python.3.11

# Linux:
sudo apt-get install python3.11 python3.11-venv python3-pip

# Verify
python --version  # Should be 3.8+

# Create virtual environment
cd "D:\MLOPS\MLOPS-AWS\mlops AWS sagemaker"
python -m venv venv

# Activate
# Windows:
.\venv\Scripts\Activate.ps1

# Linux:
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

**✅ Checkpoint:** Virtual environment activated, packages installed

### Step 2.4: Clone or Verify Repository

**Duration:** 5 minutes

```powershell
# If starting fresh:
git clone https://github.com/your-org/mlops-diabetes.git
cd mlops-diabetes

# If already cloned:
cd "D:\MLOPS\MLOPS-AWS\mlops AWS sagemaker"
git status  # Verify you're in the right repo
```

**✅ Checkpoint:** Repository structure visible, all files present

---

## 3️⃣ INFRASTRUCTURE DEPLOYMENT

### Step 3.1: Configure Environment Variables

**Duration:** 5 minutes

```powershell
# Edit environment config
code infrastructure\terraform\environments\dev\terraform.tfvars

# CRITICAL: Update these values:
owner_email  = "your-actual-email@example.com"  # CHANGE THIS
repository_url = "https://github.com/YOUR-USERNAME/mlops-diabetes"  # CHANGE THIS

# Free Tier Optimized Settings (already configured):
enable_vpc = false                    # Use default VPC (free)
enable_kms_encryption = false         # Use AES256 (free)
enable_cloudtrail = false             # Save costs
cloudwatch_log_retention_days = 1     # Minimal retention
enable_auto_shutdown = true           # CRITICAL for cost savings
budget_amount = 50                    # Set your budget
```

**⚠️ IMPORTANT:** Review the entire `terraform.tfvars` file and understand each setting.

**✅ Checkpoint:** `terraform.tfvars` updated with your email

### Step 3.2: Initialize Terraform

**Duration:** 2 minutes

```powershell
cd infrastructure\terraform\environments\dev

# Create symbolic links to main Terraform files
# Windows (PowerShell as Administrator):
New-Item -ItemType SymbolicLink -Path main.tf -Target ..\..\main.tf
New-Item -ItemType SymbolicLink -Path variables.tf -Target ..\..\variables.tf
New-Item -ItemType SymbolicLink -Path outputs.tf -Target ..\..\outputs.tf
New-Item -ItemType SymbolicLink -Path modules.tf -Target ..\..\modules.tf
New-Item -ItemType Junction -Path modules -Target ..\..\modules

# Linux/Mac:
ln -s ../../main.tf main.tf
ln -s ../../variables.tf variables.tf
ln -s ../../outputs.tf outputs.tf
ln -s ../../modules.tf modules.tf
ln -s ../../modules modules

# Initialize Terraform
terraform init

# Expected output:
# Terraform has been successfully initialized!
```

**✅ Checkpoint:** Terraform initialized without errors

### Step 3.3: Review Infrastructure Plan

**Duration:** 5 minutes

```powershell
# Generate execution plan
terraform plan -var-file="terraform.tfvars" -out=tfplan

# Review carefully:
# - How many resources will be created?
# - Any unexpected changes?
# - Estimated costs?

# Example output:
# Plan: 15 to add, 0 to change, 0 to destroy.
#
# Resources to be created:
# - S3 bucket
# - 2 IAM roles
# - 2 CloudWatch log groups
# - 2 SNS topics
# - 1 SageMaker Model Registry
# - 1 Budget
# - 2 Lambda functions
# - 2 EventBridge rules
```

**⚠️ CRITICAL REVIEW POINTS:**
- No resources marked for deletion (-)
- No sensitive data in plan output
- Resource names follow expected pattern

**✅ Checkpoint:** Plan shows ~15 resources to be created

### Step 3.4: Deploy Infrastructure

**Duration:** 5-10 minutes

```powershell
# Apply the plan
terraform apply tfplan

# Monitor progress:
# - S3 bucket creation
# - IAM roles creation
# - Lambda deployment
# - SNS topic setup

# Expected final output:
# Apply complete! Resources: 15 added, 0 changed, 0 destroyed.
#
# Outputs:
# s3_bucket_name = "mlops-diabetes-123456789012-dev"
# sagemaker_execution_role_arn = "arn:aws:iam::123456789012:role/mlops-diabetes-sagemaker-execution-dev"
# ...
```

**✅ Checkpoint:** "Apply complete!" message appears

### Step 3.5: Save Terraform Outputs

**Duration:** 2 minutes

```powershell
# Save outputs to JSON file
terraform output -json > outputs.json

# Display formatted outputs
terraform output

# Save the quick reference guide
terraform output -raw quick_reference > deployment_info.txt
type deployment_info.txt
```

**✅ Checkpoint:** `outputs.json` created with all infrastructure details

### Step 3.6: Verify AWS Resources

**Duration:** 5 minutes

```powershell
# Set AWS profile
$env:AWS_PROFILE = "mlops-dev"

# 1. Verify S3 bucket
$bucketName = terraform output -raw s3_bucket_name
aws s3 ls s3://$bucketName

# 2. Verify IAM role
$roleArn = terraform output -raw sagemaker_execution_role_arn
aws iam get-role --role-name (Split-Path $roleArn -Leaf)

# 3. Verify Model Registry
$modelGroup = terraform output -raw model_package_group_name
aws sagemaker list-model-package-groups --name-contains diabetes

# 4. Verify Lambda functions
aws lambda list-functions --query 'Functions[?contains(FunctionName, `mlops-diabetes`)].FunctionName'

# 5. Verify Budget
aws budgets describe-budgets --account-id $(aws sts get-caller-identity --query Account --output text)
```

**✅ Checkpoint:** All resources verified in AWS Console

---

## 4️⃣ PYTHON PROJECT CONFIGURATION

### Step 4.1: Auto-Update Configuration from Terraform

**Duration:** 2 minutes

The `deploy-infrastructure.ps1` script automatically updates `config/config.yaml` with Terraform outputs. If you need to update it manually or verify the configuration:

```powershell
# Navigate to project root
cd ..\..\..\

# Option 1: Auto-update (already done by deploy script)
.\infrastructure\scripts\update-config.ps1 -Environment dev

# Option 2: Verify configuration was updated correctly
Get-Content config\config.yaml | Select-String -Pattern "mlops-diabetes-.*-dev"
# Should show your actual bucket name, not placeholder values
```

**✅ Checkpoint:** Config file has real AWS values (no "YOUR_AWS_ACCOUNT_ID" placeholders)

### Step 4.2: Validate Complete Setup

**Duration:** 2 minutes

Run the validation script to ensure everything is ready:

```powershell
# Validate all setup steps
.\scripts\validate-setup.ps1 -Environment dev

# Expected output:
# ✅ All Checks Passed!
# 
# Next steps:
#   1. Download dataset
#   2. Run ML pipeline
```

**✅ Checkpoint:** Validation script shows "All Checks Passed"

# Model Configuration
model:
  algorithm: "xgboost"
  framework_version: "1.7-1"
  max_depth: 5
  eta: 0.2
  gamma: 4
  min_child_weight: 6
  subsample: 0.8
  num_round: 100
  objective: "binary:logistic"
  eval_metric: "auc"

# Training Configuration
training:
  train_test_split: 0.2
  validation_split: 0.1
  random_state: 42

# Monitoring Configuration
monitoring:
  log_group_training: "/aws/sagemaker/TrainingJobs"
  log_group_endpoints: "/aws/sagemaker/Endpoints/mlops-diabetes-dev"
  sns_topic_arn: "arn:aws:sns:us-east-1:123456789012:mlops-diabetes-alerts-dev"  # From Terraform output
  enable_data_quality: false  # Disabled in dev
  enable_model_quality: false
  enable_model_bias: false
  enable_model_explainability: false

# Encryption (if KMS enabled)
encryption:
  kms_key_id: null  # null for dev (AES256)

# Pipeline Configuration
pipeline:
  environment: dev
  auto_approve: true
  enable_caching: true
```

### Step 4.3: Test AWS Connectivity

**Duration:** 3 minutes

```powershell
# Create test script
code test_aws_connection.py
```

**test_aws_connection.py:**
```python
import boto3
import yaml
from pathlib import Path

# Load config
with open('config/config.yaml') as f:
    config = yaml.safe_load(f)

# Test S3
s3 = boto3.client('s3', region_name=config['aws']['region'])
bucket_name = config['s3']['bucket_name']

try:
    s3.head_bucket(Bucket=bucket_name)
    print(f"✅ S3 bucket '{bucket_name}' accessible")
except Exception as e:
    print(f"❌ S3 error: {e}")

# Test IAM role
iam = boto3.client('iam', region_name=config['aws']['region'])
role_name = config['sagemaker']['role'].split('/')[-1]

try:
    role = iam.get_role(RoleName=role_name)
    print(f"✅ IAM role '{role_name}' exists")
except Exception as e:
    print(f"❌ IAM error: {e}")

# Test SageMaker
sagemaker = boto3.client('sagemaker', region_name=config['aws']['region'])

try:
    model_groups = sagemaker.list_model_package_groups(
        NameContains=config['sagemaker']['model_package_group']
    )
    if model_groups['ModelPackageGroupSummaryList']:
        print(f"✅ Model Registry '{config['sagemaker']['model_package_group']}' exists")
    else:
        print(f"⚠️ Model Registry not found")
except Exception as e:
    print(f"❌ SageMaker error: {e}")

print("\n🎉 All AWS connections successful!")
```

```powershell
# Run test
python test_aws_connection.py

# Expected output:
# ✅ S3 bucket 'mlops-diabetes-123456789012-dev' accessible
# ✅ IAM role 'mlops-diabetes-sagemaker-execution-dev' exists
# ✅ Model Registry 'mlops-diabetes-model-group-dev' exists
# 🎉 All AWS connections successful!
```

**✅ Checkpoint:** All AWS services accessible from Python

---

## 5️⃣ FIRST PIPELINE EXECUTION

### Step 5.1: Prepare Sample Data

**Duration:** 5 minutes

```powershell
# Download diabetes dataset
mkdir -p data\raw
cd data\raw

# Using Python to download
python -c "
from sklearn.datasets import load_diabetes
import pandas as pd

# Load diabetes dataset
diabetes = load_diabetes(as_frame=True)
df = diabetes.frame

# Add binary target (diabetes present/absent)
df['target_binary'] = (df['target'] > df['target'].median()).astype(int)

# Save to CSV
df.to_csv('diabetes.csv', index=False)
print('✅ Dataset saved to data/raw/diabetes.csv')
print(f'Shape: {df.shape}')
print(f'Columns: {list(df.columns)}')
"

# Verify file
dir diabetes.csv
```

**✅ Checkpoint:** `diabetes.csv` created with 442 rows

### Step 5.2: Upload Data to S3

**Duration:** 2 minutes

```powershell
# Upload to S3
$bucketName = terraform -chdir="infrastructure\terraform\environments\dev" output -raw s3_bucket_name
aws s3 cp data\raw\diabetes.csv s3://$bucketName/data/raw/diabetes.csv --profile mlops-dev

# Verify upload
aws s3 ls s3://$bucketName/data/raw/ --profile mlops-dev

# Expected output:
# 2024-11-04 10:00:00      12345 diabetes.csv
```

**✅ Checkpoint:** Dataset visible in S3 bucket

### Step 5.3: Run Data Processing Pipeline

**Duration:** 10-15 minutes

```powershell
# Run processing job
python pipelines\data_processing_pipeline.py --environment dev --execute

# Monitor progress:
# - Processing job starts
# - Data validation
# - Feature engineering
# - Train/test split
# - Upload to S3

# Check S3 for processed data
aws s3 ls s3://$bucketName/data/processed/ --recursive --profile mlops-dev

# Expected files:
# data/processed/train.csv
# data/processed/validation.csv
# data/processed/test.csv
```

**⚠️ COST WARNING:** SageMaker Processing charges: ~$0.05/hour

**✅ Checkpoint:** Processed data files in S3

### Step 5.4: Run Training Pipeline

**Duration:** 15-20 minutes

```powershell
# Run training job
python pipelines\training_pipeline.py --environment dev --execute

# Monitor in terminal:
# - Training job submitted
# - Model training progress
# - Model evaluation
# - Model registration

# Check CloudWatch Logs
aws logs tail /aws/sagemaker/TrainingJobs --follow --profile mlops-dev

# Check Model Registry
aws sagemaker list-model-packages `
  --model-package-group-name $(terraform -chdir="infrastructure\terraform\environments\dev" output -raw model_package_group_name) `
  --profile mlops-dev
```

**⚠️ COST WARNING:** SageMaker Training charges: ~$0.115/hour (with spot instances: ~$0.03/hour)

**✅ Checkpoint:** Model registered in Model Registry with "Approved" status

### Step 5.5: Deploy Model to Endpoint

**Duration:** 10-15 minutes

```powershell
# Run deployment pipeline
python pipelines\deployment_pipeline.py --environment dev --execute

# Monitor deployment:
# - Endpoint configuration created
# - Endpoint creating
# - Endpoint in service

# Check endpoint status
aws sagemaker list-endpoints --name-contains mlops-diabetes --profile mlops-dev

# Wait for endpoint (can take 5-10 minutes)
aws sagemaker wait endpoint-in-service `
  --endpoint-name mlops-diabetes-endpoint-dev `
  --profile mlops-dev

echo "✅ Endpoint deployed successfully!"
```

**⚠️ COST WARNING:** Endpoint charges continuously: ~$0.065/hour (~$47/month if always on)  
**💡 SOLUTION:** Auto-shutdown enabled 7 PM-8 AM = $18/month

**✅ Checkpoint:** Endpoint status shows "InService"

### Step 5.6: Test Model Predictions

**Duration:** 5 minutes

```powershell
# Create test script
code test_inference.py
```

**test_inference.py:**
```python
import boto3
import json
import numpy as np

# Sample data point (features from diabetes dataset)
sample_data = [
    0.038076,  # age
    0.050680,  # sex
    0.061696,  # bmi
    0.021872,  # bp
    -0.044223, # s1
    -0.034821, # s2
    -0.043401, # s3
    -0.002592, # s4
    0.019908,  # s5
    -0.017646  # s6
]

# Convert to CSV format (XGBoost expects CSV)
csv_data = ','.join([str(x) for x in sample_data])

# Invoke endpoint
sagemaker_runtime = boto3.client('sagemaker-runtime', region_name='us-east-1')

response = sagemaker_runtime.invoke_endpoint(
    EndpointName='mlops-diabetes-endpoint-dev',
    ContentType='text/csv',
    Body=csv_data
)

# Parse prediction
prediction = float(response['Body'].read().decode('utf-8'))
print(f"📊 Prediction: {prediction:.4f}")
print(f"🏥 Diabetes Risk: {'HIGH' if prediction > 0.5 else 'LOW'}")
```

```powershell
python test_inference.py

# Expected output:
# 📊 Prediction: 0.7234
# 🏥 Diabetes Risk: HIGH
```

**✅ Checkpoint:** Model inference working correctly

---

## 6️⃣ MONITORING & VALIDATION

### Step 6.1: Check CloudWatch Logs

**Duration:** 5 minutes

```powershell
# View training logs
aws logs tail /aws/sagemaker/TrainingJobs --since 1h --profile mlops-dev

# View endpoint logs
aws logs tail /aws/sagemaker/Endpoints/mlops-diabetes-dev --since 1h --follow --profile mlops-dev
```

**✅ Checkpoint:** Logs visible and showing inference requests

### Step 6.2: Monitor Costs

**Duration:** 10 minutes

```powershell
# Check current month costs
aws ce get-cost-and-usage `
  --time-period Start=2024-11-01,End=2024-11-05 `
  --granularity DAILY `
  --metrics BlendedCost `
  --profile mlops-dev

# Check by service
aws ce get-cost-and-usage `
  --time-period Start=2024-11-01,End=2024-11-05 `
  --granularity DAILY `
  --metrics BlendedCost `
  --group-by Type=DIMENSION,Key=SERVICE `
  --profile mlops-dev

# Expected services with costs:
# - Amazon SageMaker
# - Amazon Simple Storage Service (S3)
# - AWS Lambda
# - Amazon Simple Notification Service (SNS)
```

**✅ Checkpoint:** Costs are within expected range ($2-5 for first few days)

### Step 6.3: Verify Auto-Shutdown

**Duration:** Variable (wait until 7 PM UTC)

```powershell
# Check Lambda function logs
aws logs tail /aws/lambda/mlops-diabetes-endpoint-shutdown-dev --since 24h --profile mlops-dev

# Verify endpoint status after 7 PM
aws sagemaker describe-endpoint --endpoint-name mlops-diabetes-endpoint-dev --profile mlops-dev

# Expected: Endpoint should be deleted or updating
# Check again at 8 AM - endpoint should be recreated (if startup configured)
```

**✅ Checkpoint:** Auto-shutdown working (endpoint deleted after 7 PM)

---

## 7️⃣ PRODUCTION DEPLOYMENT

### Step 7.1: Review Production Configuration

**Duration:** 15 minutes

```powershell
# Review production tfvars
code infrastructure\terraform\environments\production\terraform.tfvars

# Key differences from dev:
# - enable_vpc = true (network isolation)
# - enable_kms_encryption = true (enhanced security)
# - enable_cloudtrail = true (audit logging)
# - larger instance types (ml.m5.2xlarge)
# - multi-instance endpoints (HA)
# - model_approval_status = "PendingManualApproval"
# - enable_auto_shutdown = false (24/7 availability)
# - budget_amount = 1500
```

**⚠️ PRODUCTION CHECKLIST:**
- [ ] Separate AWS account for production
- [ ] VPC and subnets configured
- [ ] KMS key rotation enabled
- [ ] CloudTrail logging to S3
- [ ] Budget alerts to multiple emails
- [ ] PagerDuty integration for critical alerts
- [ ] Backup and disaster recovery plan
- [ ] Security audit completed
- [ ] Penetration testing (if required)
- [ ] Compliance review (GDPR/HIPAA if applicable)

### Step 7.2: Deploy to Production (when ready)

**Duration:** 20-30 minutes

```powershell
# Navigate to production environment
cd infrastructure\terraform\environments\production

# Create symbolic links
New-Item -ItemType SymbolicLink -Path main.tf -Target ..\..\main.tf
New-Item -ItemType SymbolicLink -Path variables.tf -Target ..\..\variables.tf
New-Item -ItemType SymbolicLink -Path outputs.tf -Target ..\..\outputs.tf
New-Item -ItemType SymbolicLink -Path modules.tf -Target ..\..\modules.tf
New-Item -ItemType Junction -Path modules -Target ..\..\modules

# Initialize
terraform init

# Plan (review carefully!)
terraform plan -var-file="terraform.tfvars" -out=tfplan-prod

# CRITICAL: Review plan with team before applying
# - Expected resources: ~30
# - No data loss warnings
# - Costs within budget

# Apply (only after team approval)
terraform apply tfplan-prod
```

**✅ Checkpoint:** Production infrastructure deployed and verified

---

## 8️⃣ TROUBLESHOOTING

### Common Issues and Solutions

#### Issue 1: Terraform Init Fails
```
Error: Failed to query available provider packages
```

**Solution:**
```powershell
# Clear Terraform cache
Remove-Item -Recurse -Force .terraform
Remove-Item -Force .terraform.lock.hcl

# Re-initialize
terraform init
```

#### Issue 2: AWS Credentials Not Found
```
Error: No valid credential sources found
```

**Solution:**
```powershell
# Re-configure AWS CLI
aws configure --profile mlops-dev

# Set environment variable
$env:AWS_PROFILE = "mlops-dev"

# Or use explicit credentials
$env:AWS_ACCESS_KEY_ID = "YOUR_ACCESS_KEY"
$env:AWS_SECRET_ACCESS_KEY = "YOUR_SECRET_KEY"
```

#### Issue 3: S3 Bucket Already Exists
```
Error: S3 bucket already exists
```

**Solution:**
```terraform
# Change project name in terraform.tfvars
project_name = "mlops-diabetes-yourname"  # Make it unique
```

#### Issue 4: SageMaker Quota Exceeded
```
Error: ResourceLimitExceeded: You've reached your quota for ml.m5.large instances
```

**Solution:**
```powershell
# Request quota increase
aws service-quotas request-service-quota-increase `
  --service-code sagemaker `
  --quota-code L-D9090DE7 `
  --desired-value 5 `
  --profile mlops-dev

# Or use smaller instance
# Edit terraform.tfvars:
sagemaker_training_instance_type = "ml.t3.medium"
```

#### Issue 5: Training Job Fails
```
ClientError: Algorithm error: Missing required file
```

**Solution:**
```powershell
# Check S3 data upload
aws s3 ls s3://your-bucket/data/raw/ --profile mlops-dev

# Verify data format
aws s3 cp s3://your-bucket/data/raw/diabetes.csv - --profile mlops-dev | head -5

# Check CloudWatch Logs
aws logs tail /aws/sagemaker/TrainingJobs --since 1h --profile mlops-dev
```

#### Issue 6: Endpoint Takes Too Long
```
Waiting for endpoint... (10+ minutes)
```

**Solution:**
```powershell
# Normal for first deployment (5-10 minutes)
# Monitor status
aws sagemaker describe-endpoint --endpoint-name mlops-diabetes-endpoint-dev --profile mlops-dev

# If still Creating after 15 minutes, check logs
aws logs tail /aws/sagemaker/Endpoints --since 30m --profile mlops-dev
```

---

## 9️⃣ COST MANAGEMENT

### Daily Cost Monitoring

```powershell
# Create daily cost check script
code check_costs.ps1
```

**check_costs.ps1:**
```powershell
$today = Get-Date -Format "yyyy-MM-dd"
$yesterday = (Get-Date).AddDays(-1).ToString("yyyy-MM-dd")

Write-Host "💰 AWS Cost Report" -ForegroundColor Cyan
Write-Host "Period: $yesterday to $today`n" -ForegroundColor Gray

# Get costs by service
$costs = aws ce get-cost-and-usage `
  --time-period Start=$yesterday,End=$today `
  --granularity DAILY `
  --metrics BlendedCost `
  --group-by Type=DIMENSION,Key=SERVICE `
  --profile mlops-dev | ConvertFrom-Json

foreach ($group in $costs.ResultsByTime[0].Groups) {
    $service = $group.Keys[0]
    $cost = [math]::Round([decimal]$group.Metrics.BlendedCost.Amount, 2)
    if ($cost -gt 0) {
        Write-Host "  $service : $$$cost" -ForegroundColor Yellow
    }
}

# Get total
$total = [math]::Round([decimal]$costs.ResultsByTime[0].Total.BlendedCost.Amount, 2)
Write-Host "`n📊 Total: $$$total" -ForegroundColor Green

# Budget alert
$budget = 50
$percentage = ($total / $budget) * 100
Write-Host "🎯 Budget: $$$budget (${percentage:N1}% used)`n" -ForegroundColor $(if($percentage -gt 80){"Red"}else{"Green"})
```

```powershell
# Run daily
.\check_costs.ps1
```

### Cost Optimization Checklist

- [ ] Auto-shutdown enabled for dev (saves 60%)
- [ ] Spot instances for training (saves 70%)
- [ ] Minimal CloudWatch log retention (saves storage)
- [ ] No VPC in dev (saves $43/month on endpoints)
- [ ] Delete unused endpoints
- [ ] Archive old S3 data to Glacier
- [ ] Delete old model artifacts
- [ ] Monitor budget alerts

---

## 🎉 SUCCESS CRITERIA

### You've successfully completed setup when:

✅ **Infrastructure**
- [ ] All Terraform modules deployed without errors
- [ ] AWS resources visible in Console
- [ ] Budget alerts configured and tested

✅ **Application**
- [ ] Data successfully uploaded to S3
- [ ] Processing pipeline completes
- [ ] Training job runs and registers model
- [ ] Endpoint deployed and serving predictions

✅ **Monitoring**
- [ ] CloudWatch logs showing activity
- [ ] SNS alerts delivered to email
- [ ] Cost tracking under budget
- [ ] Auto-shutdown working (for dev)

✅ **Security**
- [ ] MFA enabled on AWS accounts
- [ ] IAM roles using least privilege
- [ ] S3 buckets have public access blocked
- [ ] Encryption enabled (AES256 or KMS)

---

## 📚 NEXT STEPS

1. **Learn the Codebase**
   - Read through Python pipeline files
   - Understand data processing logic
   - Review model training parameters

2. **Experiment in Dev**
   - Try different model hyperparameters
   - Add new features to dataset
   - Test different instance types

3. **Setup CI/CD**
   - Configure GitHub Actions
   - Automate testing
   - Implement blue/green deployments

4. **Enhance Monitoring**
   - Add SageMaker Model Monitor
   - Create CloudWatch dashboards
   - Setup anomaly detection

5. **Prepare for Production**
   - Complete security audit
   - Setup separate AWS account
   - Implement disaster recovery
   - Create runbooks

---

## 📞 SUPPORT

### Documentation
- AWS Documentation: https://docs.aws.amazon.com/
- Terraform AWS Provider: https://registry.terraform.io/providers/hashicorp/aws/
- SageMaker Developer Guide: https://docs.aws.amazon.com/sagemaker/

### Community
- AWS Forums: https://forums.aws.amazon.com/
- Stack Overflow: Tag `amazon-sagemaker`
- Terraform Community: https://discuss.hashicorp.com/

### Internal
- Project README: `README.md`
- Security Audit: `infrastructure/SECURITY_AUDIT_REPORT.md`
- Infrastructure Docs: `infrastructure/docs/`

---

**🎊 Congratulations! You've completed the MLOps AWS SageMaker setup!**

*Last Updated: November 4, 2025*  
*Version: 1.0*  
*Maintainer: MLOps Team*
