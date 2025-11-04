# MLOps AWS SageMaker - Troubleshooting Guide

**Complete reference for all deployment issues and solutions**

Last Updated: November 4, 2025

---

## 📋 Table of Contents

**Setup Issues:**
1. [AWS CLI Not Recognized](#1-aws-cli-not-recognized)
2. [Invalid AWS Credentials](#2-invalid-aws-credentials)
3. [OIDC Authentication Failed](#3-oidc-authentication-failed)
4. [Malformed IAM Policy Document](#4-malformed-iam-policy-document)

**Terraform Issues:**
5. [Terraform Format Check Failures](#5-terraform-format-check-failures)
6. [Directory Structure Error](#6-terraform-directory-structure-error)
7. [Module Parameter Mismatch](#7-networking-module-parameter-mismatch)
8. [State Lock Error](#8-terraform-state-lock)

**Permission Issues:**
9. [EC2 Permission Denied](#9-ec2-permission-denied)
10. [EventBridge Permission Denied](#10-eventbridge-permission-denied)
11. [Lambda Permission Denied](#11-lambda-permission-denied)

**Deployment Issues:**
12. [Lambda ZIP Files Missing](#12-lambda-zip-files-missing)
13. [SageMaker Quota Exceeded](#13-sagemaker-quota-exceeded)
14. [GitHub Actions Artifact Deprecation](#14-github-actions-artifact-deprecation)

**Runtime Issues:**
15. [Endpoint Deployment Timeout](#15-endpoint-deployment-timeout)
16. [Training Job Failed](#16-training-job-failed)
17. [High AWS Costs](#17-high-aws-costs)

---

## Setup Issues

### 1. AWS CLI Not Recognized

**Error:**
```powershell
aws : The term 'aws' is not recognized as the name of a cmdlet, function, script file, or operable program.
```

**Root Cause:** PowerShell hasn't loaded the updated PATH after AWS CLI installation.

**Solutions:**

**Quick Fix:** Restart PowerShell (recommended)
```powershell
# Close and reopen PowerShell window
# PATH will include AWS CLI automatically
```

**Temporary Fix:** Use full path
```powershell
& "C:\Program Files\Amazon\AWSCLIV2\aws.exe" --version
& "C:\Program Files\Amazon\AWSCLIV2\aws.exe" configure --profile mlops-dev
```

**Session Fix:** Reload PATH
```powershell
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
aws --version
```

**Verify:**
```powershell
aws --version
# Expected: aws-cli/2.x.x Python/3.x.x Windows/...
```

---

### 2. Invalid AWS Credentials

**Error:**
```
Unable to locate credentials. You can configure credentials by running "aws configure".
```
OR
```
An error occurred (InvalidClientTokenId): The security token included in the request is invalid
```

**Root Cause:** Credentials not configured or profile not specified.

**Solutions:**

**Set Default Profile:**
```powershell
$env:AWS_PROFILE = "mlops-dev"
aws sts get-caller-identity
```

**Always Specify Profile:**
```powershell
aws iam create-role --role-name GitHubActions-MLOps-Dev --profile mlops-dev
```

**Configure Credentials:**
```powershell
aws configure --profile mlops-dev
# Enter:
# - AWS Access Key ID: AKIA...
# - AWS Secret Access Key: ...
# - Default region: us-east-1
# - Default output format: json
```

**Verify Credentials:**
```powershell
aws sts get-caller-identity --profile mlops-dev
# Should return UserId, Account, and Arn
```

---

### 3. OIDC Authentication Failed

**Error:**
```
Error: Could not assume role with OIDC
Not authorized to perform sts:AssumeRoleWithWebIdentity
```

**Root Cause:** Trust policy doesn't match GitHub repository.

**Solutions:**

**Verify OIDC Provider Exists:**
```powershell
aws iam list-open-id-connect-providers --profile mlops-dev
# Expected: arn:aws:iam::ACCOUNT:oidc-provider/token.actions.githubusercontent.com
```

**Check Trust Policy:**
```powershell
aws iam get-role --role-name GitHubActions-MLOps-Dev --query 'Role.AssumeRolePolicyDocument' --profile mlops-dev
```

**Verify Repository Match:**
- Trust policy: `"repo:YOUR_USERNAME/mlopsaws:*"`
- GitHub repo: `https://github.com/YOUR_USERNAME/mlopsaws`
- **Must match exactly!**

**Fix Trust Policy:**
```powershell
# See docs/IAM_SETUP.md for detailed trust policy configuration
```

---

### 4. Malformed IAM Policy Document

**Error:**
```
An error occurred (MalformedPolicyDocument): This policy contains invalid Json
```

**Root Cause:** Windows file encoding issues (UTF-8 BOM) or JSON syntax errors.

**Solution 1: Use Inline JSON (Recommended for Windows)**
```powershell
$accountId = aws sts get-caller-identity --query Account --output text
$githubUsername = "YOUR_USERNAME"
$repoName = "mlopsaws"

aws iam create-role `
  --role-name GitHubActions-MLOps-Dev `
  --assume-role-policy-document "{\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Principal\":{\"Federated\":\"arn:aws:iam::${accountId}:oidc-provider/token.actions.githubusercontent.com\"},\"Action\":\"sts:AssumeRoleWithWebIdentity\",\"Condition\":{\"StringEquals\":{\"token.actions.githubusercontent.com:aud\":\"sts.amazonaws.com\"},\"StringLike\":{\"token.actions.githubusercontent.com:sub\":\"repo:${githubUsername}/${repoName}:*\"}}}]}" `
  --description "GitHub Actions role for MLOps dev environment" `
  --profile mlops-dev
```

**Solution 2: Recreate File with ASCII Encoding**
```powershell
@'
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
          "token.actions.githubusercontent.com:sub": "repo:USERNAME/mlopsaws:*"
        }
      }
    }
  ]
}
'@ | Out-File -FilePath trust-policy.json -Encoding ascii

aws iam create-role `
  --role-name GitHubActions-MLOps-Dev `
  --assume-role-policy-document file://trust-policy.json `
  --profile mlops-dev
```

---

## Terraform Issues

### 5. Terraform Format Check Failures

**Error:**
```
Error: Terraform exited with code 3
terraform fmt -check -recursive found formatting issues
```

**Root Cause:** Inconsistent spacing before inline comments. Terraform requires EXACTLY 2 spaces before `#`.

**Incorrect Formatting:**
```hcl
enable_auto_shutdown = true    # 4 spaces - WRONG
budget_amount = 100 # 1 space - WRONG
aws_region = "us-east-1"   # 3 spaces - WRONG
```

**Correct Formatting:**
```hcl
enable_auto_shutdown = true  # Exactly 2 spaces
budget_amount = 100  # Exactly 2 spaces
aws_region = "us-east-1"  # Exactly 2 spaces
```

**Auto-Fix:**
```powershell
cd infrastructure/terraform
terraform fmt -recursive
terraform fmt -check -recursive
# Exit code 0 = success
```

**Files to Check:**
- `environments/dev/terraform.tfvars`
- `environments/staging/terraform.tfvars`
- `environments/production/terraform.tfvars`

---

### 6. Terraform Directory Structure Error

**Error:**
```
Error: No configuration files found in directory
Terraform could not load any files in infrastructure/terraform/environments/dev
```

**Root Cause:** Running Terraform from environment directory instead of root.

**Correct Directory Structure:**
```
infrastructure/terraform/
├── main.tf              ← Root module (all .tf files here)
├── modules.tf
├── variables.tf
└── environments/
    └── dev/
        └── terraform.tfvars  ← Only variable values
```

**Solution:**

Run from root with `-var-file`:

```powershell
# Wrong:
cd infrastructure/terraform/environments/dev
terraform init  # ❌ Fails - no .tf files

# Correct:
cd infrastructure/terraform
terraform init
terraform plan -var-file="environments/dev/terraform.tfvars"
terraform apply -var-file="environments/dev/terraform.tfvars"
```

**GitHub Actions Fix:**
```yaml
# Update .github/workflows/terraform.yml
- name: Terraform Plan
  working-directory: infrastructure/terraform  # Root directory
  run: terraform plan -var-file="environments/dev/terraform.tfvars" -out=tfplan
```

---

### 7. Networking Module Parameter Mismatch

**Error:**
```
Error: Unsupported argument
An argument named "additional_tags" is not expected here.
```

**Root Cause:** Module expects `tags` parameter, not `additional_tags`.

**Solution:**

Edit `infrastructure/terraform/modules.tf`:

```hcl
# Before (incorrect):
module "networking" {
  source = "./modules/networking"
  additional_tags = var.additional_tags  # ❌ Wrong parameter
}

# After (correct):
module "networking" {
  source = "./modules/networking"
  tags = merge(
    {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "Terraform"
    },
    var.additional_tags
  )
}
```

**Verify:**
```powershell
cd infrastructure/terraform
terraform validate
# Should show: Success! The configuration is valid.
```

---

### 8. Terraform State Lock

**Error:**
```
Error: Error acquiring the state lock
Lock Info: ID: abc123-def456-ghi789
```

**Root Cause:** Another Terraform process is running or didn't release lock.

**Solutions:**

**Check for Running Workflows:**
```
GitHub → Actions → Check if another workflow is running
```

**Force Unlock (ONLY if sure no other process):**
```powershell
cd infrastructure/terraform
terraform force-unlock abc123-def456-ghi789
```

**Delete DynamoDB Lock (if using remote state):**
```powershell
aws dynamodb delete-item `
  --table-name mlops-terraform-locks `
  --key '{"LockID":{"S":"mlops-diabetes-dev"}}' `
  --profile mlops-dev
```

---

## Permission Issues

### 9. EC2 Permission Denied

**Error:**
```
Error: AccessDenied: User is not authorized to perform: ec2:DescribeAvailabilityZones
```

**Root Cause:** IAM role missing EC2 permissions.

**Solution:**
```powershell
aws iam attach-role-policy `
  --role-name GitHubActions-MLOps-Dev `
  --policy-arn arn:aws:iam::aws:policy/AmazonEC2FullAccess `
  --profile mlops-dev
```

**Why Needed:**
- Query availability zones
- Create subnets
- Configure VPC and security groups

**Verify:**
```powershell
aws ec2 describe-availability-zones --profile mlops-dev
```

---

### 10. EventBridge Permission Denied

**Error:**
```
Error: AccessDeniedException: User is not authorized to perform: events:TagResource
```

**Root Cause:** IAM role missing EventBridge permissions.

**Solution:**
```powershell
aws iam attach-role-policy `
  --role-name GitHubActions-MLOps-Dev `
  --policy-arn arn:aws:iam::aws:policy/AmazonEventBridgeFullAccess `
  --profile mlops-dev
```

**Why Needed:**
- Create scheduled rules for auto-shutdown
- Event-driven ML pipeline triggers
- Monitoring alerts

---

### 11. Lambda Permission Denied

**Error:**
```
Error: AccessDeniedException: User is not authorized to perform: lambda:CreateFunction
```

**Root Cause:** IAM role missing Lambda permissions.

**Solution:**
```powershell
aws iam attach-role-policy `
  --role-name GitHubActions-MLOps-Dev `
  --policy-arn arn:aws:iam::aws:policy/AWSLambda_FullAccess `
  --profile mlops-dev
```

**Why Needed:**
- Deploy auto-shutdown functions
- Event handlers
- Custom ML pipeline triggers

**Verify All 8 Policies:**
```powershell
aws iam list-attached-role-policies --role-name GitHubActions-MLOps-Dev --profile mlops-dev

# Expected:
# 1. AmazonSageMakerFullAccess
# 2. AmazonS3FullAccess
# 3. AmazonEC2FullAccess
# 4. IAMFullAccess
# 5. CloudWatchFullAccess
# 6. AWSCloudTrail_FullAccess
# 7. AmazonEventBridgeFullAccess
# 8. AWSLambda_FullAccess
```

---

## Deployment Issues

### 12. Lambda ZIP Files Missing

**Error:**
```
Error: InvalidParameterValueException: Could not find file: ./modules/auto_shutdown/shutdown_endpoint.zip
```

**Root Cause:** Lambda deployment packages don't exist in repository.

**Temporary Solution (Disable Auto-Shutdown):**

Edit `infrastructure/terraform/environments/dev/terraform.tfvars`:
```hcl
enable_auto_shutdown = false  # Disabled until Lambda ZIPs created
```

**Cost Impact:**
- With auto-shutdown: ~$15/month (endpoint runs ~8 hours/day)
- Without auto-shutdown: ~$38/month (endpoint runs 24/7)

**Permanent Solution (Create Lambda Functions):**

See `infrastructure/DEPLOYMENT_ISSUES_AND_FIXES.md` for Lambda function creation guide.

---

### 13. SageMaker Quota Exceeded

**Error:**
```
Error: ResourceLimitExceeded: The account-level service limit 'Model package groups per account' is 0
```

**Root Cause:** SageMaker Model Package Groups quota set to 0 (disabled by default).

**Check Current Quota:**
```powershell
aws service-quotas list-service-quotas `
  --service-code sagemaker `
  --query "Quotas[?contains(QuotaName, 'Model') && contains(QuotaName, 'Package')]" `
  --profile mlops-dev
```

**Solution 1: Request via CLI**
```powershell
aws service-quotas request-service-quota-increase `
  --service-code sagemaker `
  --quota-code L-BC8DC54C `
  --desired-value 250 `
  --profile mlops-dev

# Note: Cannot request value less than default (250)
```

**Solution 2: Request via AWS Console (Recommended)**
```
1. Go to: https://console.aws.amazon.com/servicequotas/
2. Search: "SageMaker"
3. Find: "Model package groups per account" (L-BC8DC54C)
4. Click: "Request quota increase"
5. Enter: 250 (or desired value ≥ 250)
6. Submit request
```

**Monitor Request:**
```powershell
aws service-quotas get-requested-service-quota-change `
  --request-id REQUEST_ID `
  --profile mlops-dev

# Status:
# - PENDING: Waiting (24-48 hours typical)
# - APPROVED: Ready to use
# - DENIED: Contact support
```

**Timeline:**
- Simple increases: 24-48 hours
- Large increases (0 → 250): May need review
- Can expedite via support ticket

---

### 14. GitHub Actions Artifact Deprecation

**Error:**
```
Warning: actions/upload-artifact@v3 is deprecated
Warning: actions/download-artifact@v3 is deprecated
```

**Root Cause:** GitHub deprecated artifact actions v3.

**Solution:**

Update `.github/workflows/terraform.yml`:

```yaml
# Before:
- uses: actions/upload-artifact@v3
- uses: actions/download-artifact@v3

# After:
- uses: actions/upload-artifact@v4
- uses: actions/download-artifact@v4
```

**Verify:**
```powershell
Select-String -Path ".github/workflows/terraform.yml" -Pattern "artifact@v3"
# Should find no matches
```

---

## Runtime Issues

### 15. Endpoint Deployment Timeout

**Error:**
```
Endpoint deployment timed out after 15 minutes
```

**Solutions:**

**Check Status:**
```powershell
aws sagemaker describe-endpoint --endpoint-name mlops-diabetes-endpoint-dev --profile mlops-dev

# Possible statuses:
# - Creating: Wait longer (can take 10-15 min)
# - Failed: Check logs
# - InService: Success!
```

**Check Logs:**
```powershell
aws logs tail /aws/sagemaker/Endpoints/mlops-diabetes-endpoint-dev --since 30m --profile mlops-dev
```

**Common Causes:**
- Model too large
- Instance type too small
- VPC networking issues

**Retry with Smaller Instance:**
```powershell
aws sagemaker delete-endpoint --endpoint-name mlops-diabetes-endpoint-dev --profile mlops-dev
# Then re-run deployment with ml.t2.medium instead of ml.m5.large
```

---

### 16. Training Job Failed

**Error:**
```
ClientError: AlgorithmError: Framework error
```

**Solutions:**

**Check Logs:**
```powershell
aws logs tail /aws/sagemaker/TrainingJobs --follow --since 1h --profile mlops-dev
```

**Common Issues:**
- Data not in S3
- Wrong data format
- Missing dependencies

**Verify Data:**
```powershell
aws s3 ls s3://mlops-diabetes-ACCOUNT-dev/data/raw/ --profile mlops-dev
```

**Re-upload Data:**
```powershell
python src/processing/download_data.py
aws s3 cp data/raw/diabetes.csv s3://mlops-diabetes-ACCOUNT-dev/data/raw/ --profile mlops-dev
```

---

### 17. High AWS Costs

**Problem:** Monthly bill higher than expected.

**Solutions:**

**Identify Cost Drivers:**
```powershell
aws ce get-cost-and-usage `
  --time-period Start=2025-11-01,End=2025-11-05 `
  --granularity DAILY `
  --metrics BlendedCost `
  --group-by Type=DIMENSION,Key=SERVICE `
  --profile mlops-dev
```

**Common Culprits:**
- SageMaker endpoints running 24/7
- Large S3 storage
- Long CloudWatch log retention

**Cost Optimization:**

1. **Delete Unused Endpoints:**
```powershell
aws sagemaker list-endpoints --profile mlops-dev
aws sagemaker delete-endpoint --endpoint-name ENDPOINT_NAME --profile mlops-dev
```

2. **Enable Auto-Shutdown (Dev):**
```hcl
# In dev/terraform.tfvars
enable_auto_shutdown = true  # Saves 60%
```

3. **Reduce Log Retention:**
```hcl
cloudwatch_log_retention_days = 1  # Dev only
```

4. **Use Spot Instances:**
```hcl
use_spot_instances = true
max_wait_time_in_seconds = 3600
```

5. **Clean Old Data:**
```powershell
aws s3 rm s3://mlops-diabetes-ACCOUNT-dev/old-data/ --recursive --profile mlops-dev
```

---

## Quick Reference: All Commands

**Add All 8 IAM Policies:**
```powershell
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
    aws iam attach-role-policy `
        --role-name GitHubActions-MLOps-Dev `
        --policy-arn $policy `
        --profile mlops-dev
}
```

**Verify Setup:**
```powershell
# Check AWS credentials
aws sts get-caller-identity --profile mlops-dev

# Check IAM role
aws iam get-role --role-name GitHubActions-MLOps-Dev --profile mlops-dev

# Check policies (should show 8)
aws iam list-attached-role-policies --role-name GitHubActions-MLOps-Dev --profile mlops-dev

# Check Terraform
cd infrastructure/terraform
terraform validate
terraform fmt -check -recursive
```

---

## Getting Help

**Documentation:**
- Setup Guide: `docs/COMPLETE_SETUP_GUIDE.md`
- IAM Configuration: `docs/IAM_SETUP.md`
- Deployment Issues: `infrastructure/DEPLOYMENT_ISSUES_AND_FIXES.md`
- Changelog: `docs/CHANGELOG_2025-11-04.md`

**Support:**
- GitHub Issues: Create issue in repository
- AWS Forums: https://forums.aws.amazon.com/
- SageMaker Docs: https://docs.aws.amazon.com/sagemaker/

---

**Last Updated:** November 4, 2025  
**Maintainer:** MLOps Team
