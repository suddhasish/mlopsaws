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
12. [Budgets Permission Denied](#12-budgets-permission-denied)
13. [DynamoDB Permission Denied](#13-dynamodb-permission-denied)

**Deployment Issues:**
14. [Lambda ZIP Files Missing](#14-lambda-zip-files-missing)
15. [SageMaker Quota Exceeded](#15-sagemaker-quota-exceeded)
16. [GitHub Actions Artifact Deprecation](#16-github-actions-artifact-deprecation)
17. [GitHub Actions S3 Backend Authentication Error](#17-github-actions-s3-backend-authentication-error)
18. [Resource Already Exists](#18-resource-already-exists)

**Runtime Issues:**
19. [Endpoint Deployment Timeout](#19-endpoint-deployment-timeout)
20. [Training Job Failed](#20-training-job-failed)
21. [High AWS Costs](#21-high-aws-costs)

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

### 12. Budgets Permission Denied

**Error:**
```
Error: UnauthorizedOperation: User: arn:aws:sts::891807086260:assumed-role/GitHubActions-MLOps-Dev/GitHubActions-Terraform-Dev
is not authorized to perform: budgets:ModifyBudget
```

**Root Cause:** IAM role lacks AWS Budgets permissions.

**Solution:**
```powershell
aws iam attach-role-policy `
  --role-name GitHubActions-MLOps-Dev `
  --policy-arn arn:aws:iam::aws:policy/AWSBudgetsActionsWithAWSResourceControlAccess `
  --profile mlops-dev
```

**Verify:**
```powershell
aws iam list-attached-role-policies --role-name GitHubActions-MLOps-Dev --profile mlops-dev
# Should show AWSBudgetsActionsWithAWSResourceControlAccess
```

**What This Policy Provides:**
- `budgets:ModifyBudget` - Create and update budgets
- `budgets:ViewBudget` - Read budget configurations
- `budgets:DeleteBudget` - Remove budgets
- `budgets:*Action*` - Manage budget actions (alerts, SNS)

---

### 13. DynamoDB Permission Denied

**Error:**
```
Error: AccessDeniedException: User: arn:aws:sts::891807086260:assumed-role/GitHubActions-MLOps-Dev/GitHubActions-Terraform-Dev
is not authorized to perform: dynamodb:PutItem on resource: arn:aws:dynamodb:***:891807086260:table/mlops-terraform-locks
is not authorized to perform: dynamodb:GetItem on resource: arn:aws:dynamodb:***:891807086260:table/mlops-terraform-locks
```

**Root Cause:** IAM role lacks DynamoDB permissions for Terraform state locking.

**Solution:**
```powershell
aws iam attach-role-policy `
  --role-name GitHubActions-MLOps-Dev `
  --policy-arn arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess `
  --profile mlops-dev
```

**Verify:**
```powershell
aws iam list-attached-role-policies --role-name GitHubActions-MLOps-Dev --profile mlops-dev
# Should show AmazonDynamoDBFullAccess
```

**What This Policy Provides:**
- `dynamodb:PutItem` - Acquire state lock
- `dynamodb:GetItem` - Check lock status
- `dynamodb:DeleteItem` - Release state lock
- Required for Terraform remote backend with S3 + DynamoDB

**Why DynamoDB Locking?**
- Prevents concurrent Terraform runs from corrupting state
- Essential for GitHub Actions (multiple workflows can run simultaneously)
- Low cost: ~$0.01/month for state locking operations

---

## Deployment Issues

### 14. Lambda ZIP Files Missing

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

### 15. SageMaker Quota Exceeded

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

### 16. GitHub Actions Artifact Deprecation

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

### 17. GitHub Actions S3 Backend Authentication Error

**Error:**
```
Error: error configuring S3 Backend: no valid credential sources for S3 Backend found.
Error: NoCredentialProviders: no valid providers in chain.
```

**Cause:**
There are two scenarios where this error occurs:

1. **Validate Job Issue**: Even with `terraform init -backend=false`, Terraform still tries to **parse** the backend configuration syntax and requires AWS credentials to be present (even if not used).

2. **Plan/Apply Job Issue**: Terraform tries to initialize the S3 backend **before** AWS credentials are configured in the workflow. The step order matters.

**Solution 1: Fix Validate Job (Add Dummy Credentials)**

For the `validate` job that uses `-backend=false`, provide dummy AWS credentials to satisfy the backend config parser:

```yaml
- name: Terraform Init
  run: terraform init -backend=false
  working-directory: infrastructure/terraform
  env:
    AWS_ACCESS_KEY_ID: dummy
    AWS_SECRET_ACCESS_KEY: dummy
    AWS_DEFAULT_REGION: us-east-1
```

**Solution 2: Fix Plan/Apply Jobs (Reorder Steps)**

For `plan` and `apply` jobs, configure AWS credentials **before** running `terraform init`:

```yaml
steps:
  - name: Checkout code
    uses: actions/checkout@v4
  
  # Step 1: Setup Terraform CLI first
  - name: Setup Terraform
    uses: hashicorp/setup-terraform@v3
    with:
      terraform_version: 1.5.0
  
  # Step 2: Configure AWS credentials BEFORE init
  - name: Configure AWS Credentials (OIDC)
    uses: aws-actions/configure-aws-credentials@v4
    with:
      role-to-assume: ${{ secrets.AWS_ROLE_ARN }}
      aws-region: ${{ secrets.AWS_REGION }}
      role-session-name: GitHubActions-Terraform-Dev
  
  # Step 3: Now init can access S3 backend
  - name: Terraform Init
    run: terraform init
    working-directory: infrastructure/terraform
```

**Key Points:**
- The `validate` job needs dummy credentials even with `-backend=false` (Terraform parses backend config)
- The `plan` and `apply` jobs **must** configure AWS credentials before `terraform init`
- OIDC authentication (role-to-assume) is preferred over access keys
- For staging/production using access keys, same rule applies: credentials first, then init

---

### 18. Resource Already Exists

**Error:**
```
Error: S3BucketAlreadyOwnedByYou: Your previous request to create the named bucket succeeded
Error: EntityAlreadyExists: Role with name mlops-diabetes-sagemaker-execution-dev already exists
Error: ResourceAlreadyExistsException: Log group /aws/sagemaker/TrainingJobs already exists
Error: Budget already exists
```

**Root Cause:** Resources were created by GitHub Actions, but Terraform state was lost (ephemeral runners).

**Solution 1: Configure Remote Backend (Recommended)**

This prevents state loss in the future:

```powershell
# Run the backend setup script
.\infrastructure\scripts\setup-terraform-backend.ps1

# This creates:
# - S3 bucket: mlops-terraform-state-891807086260
# - DynamoDB table: mlops-terraform-locks
# - backend.tf configuration
```

**Solution 2: Import Existing Resources**

Add existing resources to Terraform state:

```powershell
cd infrastructure/terraform

# Import S3 bucket
terraform import -var-file="environments/dev/terraform.tfvars" `
  module.s3.aws_s3_bucket.ml_data `
  mlops-diabetes-dev-891807086260

# Import IAM roles
terraform import -var-file="environments/dev/terraform.tfvars" `
  module.iam.aws_iam_role.sagemaker_execution `
  mlops-diabetes-sagemaker-execution-dev

terraform import -var-file="environments/dev/terraform.tfvars" `
  module.iam.aws_iam_role.data_scientist `
  mlops-diabetes-data-scientist-dev

# Import CloudWatch log groups
terraform import -var-file="environments/dev/terraform.tfvars" `
  module.monitoring.aws_cloudwatch_log_group.training_jobs `
  /aws/sagemaker/TrainingJobs

terraform import -var-file="environments/dev/terraform.tfvars" `
  module.monitoring.aws_cloudwatch_log_group.endpoints `
  /aws/sagemaker/Endpoints/mlops-diabetes-dev

# Import Budget
terraform import -var-file="environments/dev/terraform.tfvars" `
  module.budgets.aws_budgets_budget.monthly `
  mlops-diabetes-dev-budget
```

**Solution 3: Delete and Recreate (Last Resort)**

⚠️ **WARNING:** This deletes production resources. Only use in development.

```powershell
# Delete existing resources manually
aws s3 rb s3://mlops-diabetes-dev-891807086260 --force --profile mlops-dev
aws iam delete-role --role-name mlops-diabetes-sagemaker-execution-dev --profile mlops-dev
# ... etc
```

**Prevent Future Issues:**
- ✅ Use remote backend (S3 + DynamoDB)
- ✅ Never run `terraform destroy` without backup
- ✅ Import resources before re-applying

---

## Runtime Issues

---

### 19. Endpoint Deployment Timeout

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

### 20. Training Job Failed

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

### 21. High AWS Costs

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
