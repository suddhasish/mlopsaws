# 🚀 Infrastructure Deployment Guide

## 📋 Table of Contents
1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [Quick Start (5 Minutes)](#quick-start)
3. [Detailed Deployment Steps](#detailed-deployment-steps)
4. [Post-Deployment Verification](#post-deployment-verification)
5. [Updating Infrastructure](#updating-infrastructure)
6. [Destroying Infrastructure](#destroying-infrastructure)
7. [Troubleshooting](#troubleshooting)

---

## ✅ Pre-Deployment Checklist

Before deploying, ensure you've completed the [AWS Account Setup Guide](./AWS_ACCOUNT_SETUP_GUIDE.md):

### Required
- [ ] AWS account created and active
- [ ] AWS CLI v2 installed and configured
- [ ] Terraform 1.5+ installed
- [ ] IAM user with AdministratorAccess created
- [ ] AWS credentials configured (`aws configure`)
- [ ] MFA enabled on IAM user (recommended)
- [ ] Billing alerts configured

### Recommended
- [ ] CloudTrail enabled
- [ ] Service quotas checked (SageMaker instances)
- [ ] Budget configured
- [ ] Email for alerts configured
- [ ] GitHub repository created (for CI/CD)

### Configuration Files to Update
- [ ] `infrastructure/terraform/environments/dev/terraform.tfvars`
  - Change `owner_email`
  - Change `repository_url`
  - Verify instance types match your quotas
  
- [ ] `infrastructure/terraform/environments/staging/terraform.tfvars`
  - Change `owner_email`
  - Change `alert_email_endpoints`
  
- [ ] `infrastructure/terraform/environments/production/terraform.tfvars`
  - Change `owner_email`
  - Change `alert_email_endpoints`
  - Configure `pagerduty_endpoint` (if using PagerDuty)

---

## 🚀 Quick Start (5 Minutes)

### Windows PowerShell

```powershell
# Navigate to infrastructure directory
cd infrastructure\scripts

# Deploy DEV environment (one command)
.\deploy-infrastructure.ps1 -Environment dev -Action all

# Wait 5-10 minutes for AWS resources to be created
# Review outputs and confirm deployment
```

### What Gets Created

The script will create:
- **S3 Bucket**: For data, models, and artifacts
- **IAM Roles**: SageMaker execution role, data scientist role
- **SageMaker Model Registry**: For model versioning
- **CloudWatch Log Groups**: For training jobs and endpoints
- **SNS Topics**: For alerts and notifications
- **Budgets**: Cost control alarms
- **KMS Keys**: (if enabled) For encryption
- **VPC**: (if enabled) Private network for SageMaker

**Estimated deployment time**: 5-10 minutes  
**Estimated cost**: $0 initially (charges start when using resources)

---

## 📚 Detailed Deployment Steps

### Step 1: Prepare Your Environment

```powershell
# Clone repository (if not already done)
git clone https://github.com/your-org/mlops-diabetes
cd mlops-diabetes\infrastructure

# Verify tools are installed
terraform version  # Should show 1.5.0 or higher
aws --version      # Should show AWS CLI v2

# Verify AWS credentials
aws sts get-caller-identity
# Should show your Account ID and User ARN
```

### Step 2: Review Configuration

```powershell
# Open configuration file
notepad terraform\environments\dev\terraform.tfvars

# REQUIRED CHANGES:
# 1. owner_email = "your-email@company.com"
# 2. repository_url = "https://github.com/your-org/mlops-diabetes"
# 3. alert_email_endpoints = ["your-email@company.com"]

# OPTIONAL CHANGES:
# 4. budget_amount (default: $100 for dev)
# 5. Instance types (if you have different quotas)
```

### Step 3: Initialize Terraform (First Time Only)

```powershell
cd terraform\environments\dev

# Initialize Terraform (downloads providers)
terraform init

# Expected output:
# Terraform has been successfully initialized!
```

**What this does:**
- Downloads AWS provider plugin (~100 MB)
- Initializes backend (local state file for now)
- Prepares modules for use

### Step 4: Plan Infrastructure

```powershell
# Generate execution plan
terraform plan -var-file="terraform.tfvars" -out="tfplan"

# Review the plan carefully
# You should see:
#   Plan: XX to add, 0 to change, 0 to destroy
```

**What to look for:**
- ✅ S3 bucket with encryption enabled
- ✅ IAM roles with correct permissions
- ✅ CloudWatch log groups
- ✅ Budget with your specified amount
- ❌ No resources being destroyed (first deployment)

**Common resources created (dev environment):**
- 1 S3 bucket
- 2-3 IAM roles
- 1 IAM policy (SageMaker execution permissions)
- 1 SageMaker Model Registry group
- 2-3 CloudWatch log groups
- 2 SNS topics
- 1 Budget
- (Optional) VPC, subnets, security groups, KMS keys

**Total resources**: ~15-25 depending on configuration

### Step 5: Apply Infrastructure

```powershell
# Apply the planned changes
terraform apply tfplan

# Wait for completion (5-10 minutes)
```

**What happens during apply:**
1. Creates S3 bucket with encryption
2. Creates IAM roles (SageMaker can now access S3)
3. Creates Model Registry (for model versioning)
4. Creates CloudWatch log groups (for logging)
5. Creates SNS topics (for alerts)
6. Creates Budget (cost control)
7. (If enabled) Creates VPC, KMS keys, etc.

**Expected output:**
```
Apply complete! Resources: 18 added, 0 changed, 0 destroyed.

Outputs:

s3_bucket_name = "mlops-diabetes-dev-123456789012"
sagemaker_execution_role_arn = "arn:aws:iam::123456789012:role/SageMakerExecutionRole-dev"
model_package_group_name = "diabetes-classification-models-dev"
...
```

### Step 6: Verify Deployment

```powershell
# Check S3 bucket was created
aws s3 ls | Select-String "mlops-diabetes-dev"

# Check IAM role was created
aws iam get-role --role-name SageMakerExecutionRole-dev

# Check Model Registry was created
aws sagemaker describe-model-package-group --model-package-group-name diabetes-classification-models-dev
```

**Expected results:**
- ✅ S3 bucket exists
- ✅ IAM role exists with SageMakerFullAccess
- ✅ Model Registry group exists

### Step 7: Save Outputs

```powershell
# Get all outputs in JSON format
terraform output -json > outputs.json

# Get specific outputs
$bucketName = terraform output -raw s3_bucket_name
$roleArn = terraform output -raw sagemaker_execution_role_arn

Write-Host "S3 Bucket: $bucketName"
Write-Host "IAM Role: $roleArn"
```

### Step 8: Update Application Configuration

```powershell
# Navigate back to project root
cd ..\..\..\

# Update config/config.yaml with Terraform outputs
notepad config\config.yaml

# Update these values:
# aws:
#   region: us-east-1
#   account_id: <your-account-id>
# s3:
#   bucket_name: <from terraform output s3_bucket_name>
# sagemaker:
#   role: <from terraform output sagemaker_execution_role_arn>
#   model_registry:
#     model_package_group_name: <from terraform output model_package_group_name>
```

---

## 🔍 Post-Deployment Verification

### Test 1: Upload Data to S3

```powershell
# Create test file
"test data" | Out-File test.txt

# Upload to S3 (using output from Terraform)
aws s3 cp test.txt s3://mlops-diabetes-dev-123456789012/data/test.txt

# Verify upload
aws s3 ls s3://mlops-diabetes-dev-123456789012/data/

# Clean up
aws s3 rm s3://mlops-diabetes-dev-123456789012/data/test.txt
Remove-Item test.txt
```

**Expected**: File uploads successfully (proves S3 bucket works)

### Test 2: Verify IAM Role Permissions

```powershell
# Assume the SageMaker execution role (requires permissions)
aws sts assume-role `
  --role-arn arn:aws:iam::123456789012:role/SageMakerExecutionRole-dev `
  --role-session-name test-session

# If successful, you'll see temporary credentials
```

**Expected**: Role can be assumed (proves IAM setup works)

### Test 3: Run a Simple SageMaker Processing Job

```powershell
# Navigate to project root
cd ..\..\..

# Run preprocessing script (this will use the infrastructure)
python src/processing/preprocessing.py

# Or run the full pipeline
python pipelines/training_pipeline.py --environment dev --execute
```

**Expected**: Processing job starts successfully in SageMaker

### Test 4: Check CloudWatch Logs

```powershell
# List log streams
aws logs describe-log-streams `
  --log-group-name /aws/sagemaker/TrainingJobs `
  --max-items 5

# Get recent log events
aws logs tail /aws/sagemaker/TrainingJobs --follow
```

**Expected**: Log group exists and receives logs

### Test 5: Verify Budget Alert

```powershell
# Check budget was created
aws budgets describe-budget `
  --account-id (aws sts get-caller-identity --query Account --output text) `
  --budget-name "MLOps-Dev-Monthly"
```

**Expected**: Budget exists with configured amount

---

## 🔄 Updating Infrastructure

When you need to change infrastructure (e.g., increase instance counts, add VPC):

### Step 1: Update Configuration

```powershell
# Edit terraform.tfvars
notepad terraform\environments\dev\terraform.tfvars

# Example: Change endpoint instance count
# sagemaker_endpoint_initial_instance_count = 2  # Changed from 1
```

### Step 2: Plan Changes

```powershell
cd terraform\environments\dev
terraform plan -var-file="terraform.tfvars" -out="tfplan"

# Review changes
# Look for:
#   Plan: X to add, Y to change, Z to destroy
```

### Step 3: Apply Changes

```powershell
terraform apply tfplan
```

**Important**: Some changes require resource recreation (e.g., S3 bucket name changes will destroy and recreate the bucket, losing data!)

### Safe Changes (No Downtime)
- Increasing instance counts
- Adding new resources (VPC, KMS)
- Changing log retention days
- Updating tags

### Risky Changes (Potential Data Loss)
- Changing S3 bucket names (destroys bucket)
- Changing KMS key IDs
- Changing VPC CIDR blocks

---

## 💥 Destroying Infrastructure

**⚠️ WARNING**: This will permanently delete all resources and data!

### Option 1: PowerShell Script

```powershell
cd infrastructure\scripts
.\deploy-infrastructure.ps1 -Environment dev -Action destroy
```

The script will ask for confirmation twice.

### Option 2: Terraform Command

```powershell
cd terraform\environments\dev
terraform destroy -var-file="terraform.tfvars"
```

### What Gets Deleted

- ✅ S3 buckets (and all data inside)
- ✅ IAM roles
- ✅ Model Registry (and all model versions)
- ✅ CloudWatch log groups (and all logs)
- ✅ SNS topics
- ✅ Budgets
- ✅ VPC, subnets, security groups (if created)
- ✅ KMS keys (after 30-day waiting period)

### Before Destroying

1. **Backup important data**:
   ```powershell
   # Sync S3 bucket to local folder
   aws s3 sync s3://mlops-diabetes-dev-123456789012/ ./backup/
   ```

2. **Export Model Registry**:
   ```powershell
   # List all model packages
   aws sagemaker list-model-packages `
     --model-package-group-name diabetes-classification-models-dev
   
   # Download model artifacts
   aws s3 cp s3://mlops-diabetes-dev-123456789012/models/ ./backup/models/ --recursive
   ```

3. **Stop running endpoints**:
   ```powershell
   # List endpoints
   aws sagemaker list-endpoints
   
   # Delete each endpoint
   aws sagemaker delete-endpoint --endpoint-name <endpoint-name>
   ```

4. **Wait for endpoints to delete** (Terraform destroy will fail if endpoints exist)

---

## 🐛 Troubleshooting

### Error: "Bucket already exists"

**Cause**: S3 bucket names are globally unique. Someone else may have used that name.

**Solution**:
```powershell
# Edit terraform.tfvars and change project_name
project_name = "mlops-diabetes-yourname"  # Make it unique
```

### Error: "Access Denied" when creating resources

**Cause**: IAM user doesn't have sufficient permissions.

**Solution**:
```powershell
# Verify IAM user has AdministratorAccess policy
aws iam list-attached-user-policies --user-name your-username

# If not attached, attach it (requires admin rights)
aws iam attach-user-policy `
  --user-name your-username `
  --policy-arn arn:aws:iam::aws:policy/AdministratorAccess
```

### Error: "Quota exceeded for ml.m5.xlarge"

**Cause**: AWS limits how many SageMaker instances you can run.

**Solution**:
1. Request quota increase:
   ```
   https://console.aws.amazon.com/servicequotas/
   → SageMaker
   → ml.m5.xlarge for training job usage
   → Request quota increase
   ```

2. Or change instance type in terraform.tfvars:
   ```powershell
   sagemaker_training_instance_type = "ml.t3.medium"  # Use smaller instance
   ```

### Error: "State lock failed"

**Cause**: Another Terraform process is running, or previous run crashed.

**Solution**:
```powershell
# Force unlock (only if you're sure no other process is running)
terraform force-unlock <LOCK_ID>
```

### Error: "Module not found"

**Cause**: Terraform modules not initialized.

**Solution**:
```powershell
terraform init -upgrade
```

### Error: Deployment works but Python code fails

**Cause**: Configuration file not updated with Terraform outputs.

**Solution**:
```powershell
# Get outputs
cd infrastructure\terraform\environments\dev
terraform output

# Update config/config.yaml with the values
```

---

## 📊 Cost Monitoring

### Check Current Spending

```powershell
# Get month-to-date costs
aws ce get-cost-and-usage `
  --time-period Start=2024-11-01,End=2024-11-05 `
  --granularity MONTHLY `
  --metrics UnblendedCost `
  --group-by Type=TAG,Key=Environment
```

### Set Up Cost Alerts

Already configured via Terraform! Check your email for budget alerts.

### Cost Breakdown by Environment

```powershell
# Tag all resources during deployment
# Terraform automatically tags with Environment = dev|staging|production

# View costs by environment in AWS Console:
# Cost Explorer → Filters → Tags → Environment
```

---

## 🎓 Best Practices

### 1. Use Separate AWS Accounts for Environments

**Why**: Maximum isolation, separate billing, different security policies

**How**:
```powershell
# Configure profiles for each account
aws configure --profile mlops-dev
aws configure --profile mlops-staging
aws configure --profile mlops-prod

# Deploy to each account
.\deploy-infrastructure.ps1 -Environment dev -AWSProfile mlops-dev
.\deploy-infrastructure.ps1 -Environment staging -AWSProfile mlops-staging
.\deploy-infrastructure.ps1 -Environment production -AWSProfile mlops-prod
```

### 2. Use Terraform Remote State (S3 Backend)

**Why**: Enable team collaboration, state locking, versioning

**How**:
1. Create S3 bucket for state:
   ```powershell
   aws s3 mb s3://mlops-terraform-state-123456789012
   aws s3api put-bucket-versioning `
     --bucket mlops-terraform-state-123456789012 `
     --versioning-configuration Status=Enabled
   ```

2. Create DynamoDB table for locking:
   ```powershell
   aws dynamodb create-table `
     --table-name mlops-terraform-locks `
     --attribute-definitions AttributeName=LockID,AttributeType=S `
     --key-schema AttributeName=LockID,KeyType=HASH `
     --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5
   ```

3. Uncomment backend configuration in `main.tf`

4. Re-initialize:
   ```powershell
   terraform init -migrate-state
   ```

### 3. Always Review Plans Before Applying

```powershell
# ALWAYS run plan first
terraform plan -var-file="terraform.tfvars" -out="tfplan"

# Review carefully:
# - What will be created?
# - What will be modified?
# - What will be destroyed?

# Only then apply
terraform apply tfplan
```

### 4. Use Version Control for Terraform Code

```powershell
# Add all infrastructure code to Git
git add infrastructure/
git commit -m "Add Terraform infrastructure"
git push
```

### 5. Document Changes

Update `CHANGELOG.md` when making infrastructure changes:
```
## [1.1.0] - 2024-11-05
### Added
- VPC endpoints for cost savings
- KMS encryption for production

### Changed
- Increased endpoint instance count from 1 to 2

### Removed
- Auto-shutdown (keeping dev running 24/7 for testing)
```

---

## 📞 Getting Help

### Official Documentation
- **AWS**: https://docs.aws.amazon.com/
- **Terraform**: https://www.terraform.io/docs
- **SageMaker**: https://docs.aws.amazon.com/sagemaker/

### Common Issues
- Check [Troubleshooting](#troubleshooting) section
- Search AWS forums: https://forums.aws.amazon.com/
- Terraform community: https://discuss.hashicorp.com/

### Contact
- **Email**: ml-ops@company.com
- **Slack**: #mlops-infrastructure
- **On-call**: PagerDuty rotation

---

**Last Updated**: November 2025  
**Maintained By**: MLOps Team

