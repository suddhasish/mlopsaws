# MLOps AWS SageMaker - Complete Setup Guide

**Industry-grade MLOps infrastructure with automated CI/CD**

**Version:** 5.0 - Professional & Streamlined  
**Last Updated:** November 4, 2025  
**Setup Time:** 45-60 minutes (one-time)  
**Method:** GitHub Actions + Terraform + AWS OIDC

---

## 📖 Documentation Structure

This is the main setup guide. Specialized topics are covered in dedicated documents:

| Document | Purpose | When to Use |
|----------|---------|-------------|
| **This Guide** | End-to-end setup walkthrough | First-time setup, complete deployment |
| [IAM_SETUP.md](./IAM_SETUP.md) | Detailed IAM and OIDC configuration | IAM role creation, trust policies, permissions |
| [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) | All deployment issues and fixes | When you encounter errors |
| [DATA_INGESTION_GUIDE.md](./DATA_INGESTION_GUIDE.md) | Production data pipelines | Moving from sample to production data |
| [TRUST_POLICY_BEST_PRACTICES.md](./TRUST_POLICY_BEST_PRACTICES.md) | Organization-based trust patterns | Enterprise security hardening |
| [ACTUAL_SETUP_COMPLETED.md](./ACTUAL_SETUP_COMPLETED.md) | Current project status | Check what's already configured |
| [CHANGELOG_2025-11-04.md](./CHANGELOG_2025-11-04.md) | Recent changes and commits | Session history and progress |

---

## 🎯 What You'll Build

**Automated ML Pipeline on AWS:**
- ✅ Infrastructure as Code (Terraform)
- ✅ Secure OIDC authentication (no access keys!)
- ✅ Multi-environment support (dev/staging/prod)
- ✅ Automated model training and deployment
- ✅ Model monitoring and drift detection
- ✅ Cost controls and auto-shutdown
- ✅ Complete audit trail

**After setup, every code push automatically:**
1. Validates infrastructure changes
2. Deploys to AWS via Terraform
3. Trains ML model on SageMaker
4. Deploys model to endpoint
5. Configures monitoring

---

## 📋 Table of Contents

**Setup (45-60 minutes, one-time):**
1. [Prerequisites](#1-prerequisites)
2. [AWS OIDC & IAM Setup](#2-aws-oidc--iam-setup)
3. [GitHub Configuration](#3-github-configuration)
4. [Terraform Configuration](#4-terraform-configuration)
5. [First Deployment](#5-first-deployment)

**Operations:**
6. [Monitoring & Validation](#6-monitoring--validation)
7. [Cost Management](#7-cost-management)
8. [Production Deployment](#8-production-deployment)

**Reference:**
9. [Common Issues](#9-common-issues)
10. [Next Steps](#10-next-steps)

---

## 1. Prerequisites

### Required Tools

Install these before starting:

| Tool | Purpose | Download | Verify |
|------|---------|----------|--------|
| **AWS Account** | Cloud infrastructure | [aws.amazon.com](https://aws.amazon.com/) | — |
| **GitHub Account** | Code & CI/CD | [github.com](https://github.com/) | — |
| **AWS CLI v2** | AWS configuration | [Download](https://awscli.amazonaws.com/AWSCLIV2.msi) | `aws --version` |
| **Git** | Version control | [Download](https://git-scm.com/downloads) | `git --version` |
| **Text Editor** | Edit configs | VS Code recommended | — |

### AWS Account Setup

```powershell
# 1. Install AWS CLI (Windows)
# Download and run: https://awscli.amazonaws.com/AWSCLIV2.msi
# Restart PowerShell after installation

# 2. Verify installation
aws --version
# Expected: aws-cli/2.x.x

# 3. Configure AWS credentials
# Create IAM user in AWS Console with AdministratorAccess
# Then configure CLI:
aws configure --profile mlops-dev
# Enter Access Key ID, Secret Access Key, region (us-east-1), format (json)

# 4. Test credentials
aws sts get-caller-identity --profile mlops-dev

# 5. Get your AWS Account ID (save this!)
$accountId = aws sts get-caller-identity --query Account --output text --profile mlops-dev
Write-Host "AWS Account ID: $accountId"
```

**If AWS CLI not recognized:** See [TROUBLESHOOTING.md#1-aws-cli-not-recognized](./TROUBLESHOOTING.md#1-aws-cli-not-recognized)

### GitHub Repository

```powershell
# Fork or clone the repository
git clone https://github.com/suddhasish/mlopsaws.git
cd mlopsaws
```

✅ **Checkpoint:** AWS CLI configured, repository cloned, account ID saved

---

## 2. AWS OIDC & IAM Setup

**Why OIDC?** Secure authentication without storing AWS access keys. GitHub Actions gets temporary credentials (1-hour lifespan) that cannot leak.

**Detailed guide:** See [IAM_SETUP.md](./IAM_SETUP.md) for comprehensive documentation.

### Quick Setup (5 Commands)

```powershell
# Set your details
$accountId = aws sts get-caller-identity --query Account --output text --profile mlops-dev
$githubUsername = "YOUR_USERNAME"  # ⚠️ CHANGE THIS
$repoName = "mlopsaws"

# 1. Create OIDC Provider
aws iam create-open-id-connect-provider `
  --url https://token.actions.githubusercontent.com `
  --client-id-list sts.amazonaws.com `
  --thumbprint-list 6938fd4d98bab03faadb97b34396831e3780aea1 `
  --profile mlops-dev

# 2. Create IAM Role (inline JSON avoids encoding issues)
aws iam create-role `
  --role-name GitHubActions-MLOps-Dev `
  --assume-role-policy-document "{\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Principal\":{\"Federated\":\"arn:aws:iam::${accountId}:oidc-provider/token.actions.githubusercontent.com\"},\"Action\":\"sts:AssumeRoleWithWebIdentity\",\"Condition\":{\"StringEquals\":{\"token.actions.githubusercontent.com:aud\":\"sts.amazonaws.com\"},\"StringLike\":{\"token.actions.githubusercontent.com:sub\":\"repo:${githubUsername}/${repoName}:*\"}}}]}" `
  --description "GitHub Actions role for MLOps dev environment" `
  --profile mlops-dev

# 3. Attach all 8 required policies
$policies = @(
    "arn:aws:iam::aws:policy/AmazonSageMakerFullAccess",
    "arn:aws:iam::aws:policy/AmazonS3FullAccess",
    "arn:aws:iam::aws:policy/AmazonEC2FullAccess",
    "arn:aws:iam::aws:policy/IAMFullAccess",
    "arn:aws:iam::aws:policy/CloudWatchFullAccess",
    "arn:aws:iam::aws:policy/AWSCloudTrail_FullAccess",
    "arn:aws:iam::aws:policy/AmazonEventBridgeFullAccess",
    "arn:aws:iam::aws:policy/AWSLambda_FullAccess"
)
foreach ($policy in $policies) {
    aws iam attach-role-policy --role-name GitHubActions-MLOps-Dev --policy-arn $policy --profile mlops-dev
}

# 4. Get Role ARN (save this for GitHub Secrets!)
$roleArn = aws iam get-role --role-name GitHubActions-MLOps-Dev --query 'Role.Arn' --output text --profile mlops-dev
Write-Host "Role ARN: $roleArn"

# 5. Verify (should show 8 policies)
aws iam list-attached-role-policies --role-name GitHubActions-MLOps-Dev --profile mlops-dev
```

**Expected Role ARN:**
```
arn:aws:iam::891807086260:role/GitHubActions-MLOps-Dev
```

**If you encounter errors:** See [TROUBLESHOOTING.md#4-malformed-iam-policy-document](./TROUBLESHOOTING.md#4-malformed-iam-policy-document)

✅ **Checkpoint:** IAM role created with 8 policies, ARN saved

---

## 3. GitHub Configuration

### Add Repository Secrets

**Navigate to:**
```
https://github.com/YOUR_USERNAME/mlopsaws/settings/secrets/actions
```

**Add these secrets:**

| Secret Name | Value | Example |
|-------------|-------|---------|
| `AWS_ROLE_ARN` | Role ARN from Step 2 | `arn:aws:iam::891807086260:role/GitHubActions-MLOps-Dev` |
| `AWS_REGION` | AWS region | `us-east-1` |

**Steps:**
1. Click "New repository secret"
2. Name: `AWS_ROLE_ARN`
3. Value: Paste the ARN from Step 2
4. Click "Add secret"
5. Repeat for `AWS_REGION` with value `us-east-1`

✅ **Checkpoint:** 2 secrets configured (values hidden as •••••••)

---

## 4. Terraform Configuration

### Update Environment Variables

**Edit:** `infrastructure/terraform/environments/dev/terraform.tfvars`

**Required changes (4 values):**

```hcl
# 1. Your AWS Account ID (from Step 1)
aws_account_id = "891807086260"  # ⚠️ REPLACE with YOUR account ID

# 2. Your email (for cost alerts)
owner_email = "your.email@company.com"  # ⚠️ REPLACE

# 3. Your GitHub repository
repository_url = "https://github.com/YOUR_USERNAME/mlopsaws"  # ⚠️ REPLACE

# 4. Alert email
alert_email_endpoints = ["your.email@company.com"]  # ⚠️ REPLACE

# ========================================
# Optional settings (defaults recommended)
# ========================================

aws_region = "us-east-1"
project_name = "mlops-diabetes"
environment = "dev"

# Cost Optimization
budget_amount = 100  # USD per month
enable_auto_shutdown = false  # Lambda ZIPs not included (see note below)

# Free tier settings
enable_vpc = false  # Use default VPC
enable_kms_encryption = false  # Use AES256 (free)

# Instance types (smallest for cost)
sagemaker_processing_instance_type = "ml.t3.medium"
sagemaker_training_instance_type = "ml.m5.large"
sagemaker_endpoint_instance_type = "ml.t2.medium"
```

**Note on auto-shutdown:**
- Currently disabled because Lambda ZIP files are not included in repository
- Can be enabled after creating Lambda functions
- Saves ~60% of endpoint costs
- See [DEPLOYMENT_ISSUES_AND_FIXES.md](../infrastructure/DEPLOYMENT_ISSUES_AND_FIXES.md#issue-1-missing-lambda-zip-files) for details

### Commit Configuration

```powershell
git add infrastructure/terraform/environments/dev/terraform.tfvars
git commit -m "Configure dev environment with AWS account details"
```

✅ **Checkpoint:** Configuration updated with your details

---

## 5. First Deployment

### Push to GitHub

```powershell
git push origin main
```

**This triggers GitHub Actions automatically!**

### Monitor Deployment

**Go to:**
```
https://github.com/YOUR_USERNAME/mlopsaws/actions
```

**You'll see workflows running:**

#### Workflow 1: Terraform Infrastructure (10-15 minutes)

Jobs:
- ✅ `terraform-fmt`: Format validation
- ✅ `terraform-plan`: Generate deployment plan
- ✅ `terraform-apply`: Create AWS resources

**Resources created:**
- S3 bucket for data/models
- IAM roles for SageMaker
- SageMaker Model Registry
- CloudWatch log groups
- Budget alerts
- (Note: Auto-shutdown Lambda skipped if disabled)

#### Workflow 2: MLOps Pipeline (25-30 minutes)

Jobs:
- ✅ `code-quality`: Black, flake8, pytest
- ✅ `upload-data`: Download and upload diabetes dataset
- ✅ `sagemaker-pipeline`: Train model
- ✅ `deploy-model`: Deploy to endpoint
- ✅ `setup-monitoring`: Configure Model Monitor

### Verify Deployment

**Check AWS Console:**

```
S3 Buckets:
https://s3.console.aws.amazon.com/s3/buckets
→ Look for: mlops-diabetes-ACCOUNT_ID-dev

SageMaker Endpoints:
https://console.aws.amazon.com/sagemaker/home#/endpoints
→ Look for: diabetes-endpoint-dev
→ Status should be: InService

Model Registry:
https://console.aws.amazon.com/sagemaker/home#/model-packages
→ Look for: mlops-diabetes-model-group-dev
```

**Or via AWS CLI:**

```powershell
# Check S3 bucket
aws s3 ls | Select-String mlops-diabetes

# Check SageMaker endpoint
aws sagemaker list-endpoints --profile mlops-dev

# Check model registry
aws sagemaker list-model-package-groups --name-contains diabetes --profile mlops-dev
```

✅ **Checkpoint:** Workflows completed successfully, resources exist in AWS

---

## 6. Monitoring & Validation

### Test Model Endpoint

```powershell
# Create test data (diabetes prediction features)
$testData = "6,148,72,35,0,33.6,0.627,50"

# Get endpoint name
$endpointName = aws sagemaker list-endpoints --query 'Endpoints[0].EndpointName' --output text --profile mlops-dev

# Invoke endpoint
aws sagemaker-runtime invoke-endpoint `
  --endpoint-name $endpointName `
  --content-type text/csv `
  --body $testData `
  output.json `
  --profile mlops-dev

# View prediction
Get-Content output.json
# Expected: [0] or [1] (diabetes prediction)
```

### View Logs

```powershell
# Training job logs
aws logs tail /aws/sagemaker/TrainingJobs --since 1h --profile mlops-dev

# Endpoint logs
aws logs tail /aws/sagemaker/Endpoints/mlops-diabetes-endpoint-dev --since 1h --profile mlops-dev
```

### Check Costs

```powershell
# Today's costs
aws ce get-cost-and-usage `
  --time-period Start=$(Get-Date -Format yyyy-MM-dd),End=$(Get-Date -Format yyyy-MM-dd) `
  --granularity DAILY `
  --metrics BlendedCost `
  --profile mlops-dev
```

---

## 7. Cost Management

### Expected Costs

**Development Environment:**
- S3 storage: ~$1/month
- SageMaker training: ~$0.50/job
- SageMaker endpoint: ~$38/month (24/7) or ~$15/month (with auto-shutdown)
- CloudWatch logs: ~$1/month
- **Total: $20-40/month**

**Production Environment:**
- High availability: $1200-1500/month
- Multiple instances, auto-scaling

### Enable Auto-Shutdown (Optional)

**Currently disabled** because Lambda ZIP files are not included. To enable:

1. Create Lambda functions (see [DEPLOYMENT_ISSUES_AND_FIXES.md](../infrastructure/DEPLOYMENT_ISSUES_AND_FIXES.md#issue-1-missing-lambda-zip-files))
2. Update `terraform.tfvars`:
   ```hcl
   enable_auto_shutdown = true
   ```
3. Commit and push

**Savings:** ~60% reduction in endpoint costs

### Budget Alerts

Already configured! You'll receive email alerts at:
- 80% of budget ($80)
- 100% of budget ($100)

### Cost Optimization Tips

```powershell
# Delete unused endpoints
aws sagemaker delete-endpoint --endpoint-name OLD_ENDPOINT --profile mlops-dev

# Use spot instances for training
# Add to terraform.tfvars:
# use_spot_instances = true
# max_wait_time_in_seconds = 3600

# Reduce log retention (dev only)
# cloudwatch_log_retention_days = 1
```

---

## 8. Production Deployment

### Production Considerations

**Before deploying to production:**

1. ✅ Test thoroughly in dev environment
2. ✅ Review all Terraform changes
3. ✅ Enable VPC for network isolation
4. ✅ Enable KMS encryption
5. ✅ Enable CloudTrail for audit logging
6. ✅ Configure high availability (multi-AZ)
7. ✅ Set up approval gates for deployments
8. ✅ Use organization-based trust policies

### Production Configuration

**Edit:** `infrastructure/terraform/environments/production/terraform.tfvars`

```hcl
environment = "production"

# High Availability
sagemaker_endpoint_initial_instance_count = 2  # Multi-AZ
sagemaker_endpoint_instance_type = "ml.m5.xlarge"
enable_autoscaling = true
autoscaling_min_capacity = 2
autoscaling_max_capacity = 10

# Security
enable_vpc = true  # Network isolation
enable_kms_encryption = true  # Encrypt all data
enable_cloudtrail = true  # Audit logging

# Cost Control
budget_amount = 1500  # $1500/month
enable_auto_shutdown = false  # Production runs 24/7

# Model Approval
model_approval_status = "PendingManualApproval"  # Require approval

# Monitoring
cloudwatch_log_retention_days = 30
monitoring_schedule_expression = "cron(0 * * * ? *)"  # Hourly
```

### Deployment Process

1. Create pull request with production changes
2. Review Terraform plan in PR comments
3. Approve PR
4. Merge to main
5. Manually trigger production workflow (requires approval)
6. Monitor deployment
7. Smoke test endpoint

**Detailed production setup:** See [IAM_SETUP.md#multi-environment-setup](./IAM_SETUP.md#multi-environment-setup)

---

## 9. Common Issues

**Quick fixes for common problems. Full documentation:** [TROUBLESHOOTING.md](./TROUBLESHOOTING.md)

### Issue: AWS CLI Not Recognized

**Error:** `aws : The term 'aws' is not recognized`

**Fix:** Restart PowerShell after AWS CLI installation
```powershell
# Or use full path temporarily:
& "C:\Program Files\Amazon\AWSCLIV2\aws.exe" --version
```

**Details:** [TROUBLESHOOTING.md#1-aws-cli-not-recognized](./TROUBLESHOOTING.md#1-aws-cli-not-recognized)

---

### Issue: Terraform Format Check Failures

**Error:** `terraform fmt -check -recursive found formatting issues`

**Fix:** Terraform requires EXACTLY 2 spaces before `#` comments
```powershell
cd infrastructure/terraform
terraform fmt -recursive
```

**Details:** [TROUBLESHOOTING.md#5-terraform-format-check-failures](./TROUBLESHOOTING.md#5-terraform-format-check-failures)

---

### Issue: OIDC Authentication Failed

**Error:** `Not authorized to perform sts:AssumeRoleWithWebIdentity`

**Fix:** Verify repository name in trust policy matches exactly
```powershell
aws iam get-role --role-name GitHubActions-MLOps-Dev --query 'Role.AssumeRolePolicyDocument' --profile mlops-dev
```

**Details:** [TROUBLESHOOTING.md#3-oidc-authentication-failed](./TROUBLESHOOTING.md#3-oidc-authentication-failed)

---

### Issue: SageMaker Quota Exceeded

**Error:** `The account-level service limit 'Model package groups per account' is 0`

**Fix:** Request quota increase (approved in 24-48 hours)
```powershell
aws service-quotas request-service-quota-increase `
  --service-code sagemaker `
  --quota-code L-BC8DC54C `
  --desired-value 250 `
  --profile mlops-dev
```

**Details:** [TROUBLESHOOTING.md#13-sagemaker-quota-exceeded](./TROUBLESHOOTING.md#13-sagemaker-quota-exceeded)

---

### Issue: Permission Denied Errors

**Error:** `User is not authorized to perform: SERVICE:ACTION`

**Fix:** Verify all 8 IAM policies are attached
```powershell
aws iam list-attached-role-policies --role-name GitHubActions-MLOps-Dev --profile mlops-dev
# Should show 8 policies
```

**Add missing policies:**
```powershell
# Example: EventBridge
aws iam attach-role-policy `
  --role-name GitHubActions-MLOps-Dev `
  --policy-arn arn:aws:iam::aws:policy/AmazonEventBridgeFullAccess `
  --profile mlops-dev
```

**Details:** [TROUBLESHOOTING.md#permission-issues](./TROUBLESHOOTING.md#permission-issues)

---

### All Deployment Issues

**Complete fixes for Lambda ZIPs, quotas, permissions:**  
[infrastructure/DEPLOYMENT_ISSUES_AND_FIXES.md](../infrastructure/DEPLOYMENT_ISSUES_AND_FIXES.md)

---

## 10. Next Steps

### ✅ You've Successfully Deployed MLOps Infrastructure!

**What you have now:**
- ✅ Secure OIDC-based AWS authentication
- ✅ Infrastructure as Code with Terraform
- ✅ Automated CI/CD pipelines
- ✅ ML model training and deployment
- ✅ Model monitoring and drift detection
- ✅ Cost controls and budget alerts

### Enhance Your Setup

**1. Production Data Pipeline**

Move from sample data to production:
- [DATA_INGESTION_GUIDE.md](./DATA_INGESTION_GUIDE.md) - S3 events, scheduled ingestion, streaming

**2. Organization-Based Security**

Migrate to user-independent trust policies:
- [TRUST_POLICY_BEST_PRACTICES.md](./TRUST_POLICY_BEST_PRACTICES.md) - Enterprise patterns

**3. Advanced Monitoring**

- Custom CloudWatch dashboards
- PagerDuty/Slack alerts
- Anomaly detection

**4. Model Improvements**

- Experiment with hyperparameters
- Try different algorithms (Random Forest, Neural Networks)
- Add more features

**5. Multi-Environment Deployment**

- Deploy to staging
- Configure production with HA
- A/B testing for models

### Learning Resources

**Documentation:**
- This guide: Main setup walkthrough
- [IAM_SETUP.md](./IAM_SETUP.md): Detailed IAM configuration
- [TROUBLESHOOTING.md](./TROUBLESHOOTING.md): All issues and fixes
- [ACTUAL_SETUP_COMPLETED.md](./ACTUAL_SETUP_COMPLETED.md): Project status
- [CHANGELOG_2025-11-04.md](./CHANGELOG_2025-11-04.md): Recent changes

**External Resources:**
- [AWS SageMaker Documentation](https://docs.aws.amazon.com/sagemaker/)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)

### Getting Help

**Repository Issues:**
- Create issue in GitHub repository
- Include error messages and logs

**AWS Support:**
- [AWS Forums](https://forums.aws.amazon.com/)
- [AWS Support Center](https://console.aws.amazon.com/support/)

**Community:**
- [SageMaker Examples](https://github.com/aws/amazon-sagemaker-examples)
- [Terraform AWS Modules](https://github.com/terraform-aws-modules)

---

## 📊 Project Status

**Current Setup:**
- ✅ AWS Account: 891807086260
- ✅ Region: us-east-1
- ✅ IAM Role: GitHubActions-MLOps-Dev (8 policies)
- ✅ OIDC Provider: Configured
- ✅ GitHub Secrets: AWS_ROLE_ARN, AWS_REGION
- ✅ Terraform: Configured for dev environment
- ⏳ SageMaker Quota: Pending approval (Request ID: 3d8c1063060c49d69c68694f8155a1aeXRl7MRZT)
- ⚠️ Auto-Shutdown: Disabled (Lambda ZIPs not included)

**For detailed status:** [ACTUAL_SETUP_COMPLETED.md](./ACTUAL_SETUP_COMPLETED.md)

---

## 📝 Summary

**Time Investment:**
- Initial setup: 45-60 minutes (one-time)
- Deployments: Fully automated (45 minutes per run)

**Monthly Costs:**
- Dev: $20-40/month
- Prod: $1200-1500/month (high availability)

**Value Delivered:**
- Production-grade MLOps infrastructure
- Secure, automated CI/CD
- Complete observability
- Industry best practices

**You're ready to deploy production ML models on AWS! 🚀**

---

**Version:** 5.0 Professional  
**Last Updated:** November 4, 2025  
**Maintainer:** MLOps Team  
**Status:** ✅ Production Ready
