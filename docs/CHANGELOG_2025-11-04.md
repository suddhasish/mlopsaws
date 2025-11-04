# Changelog - November 4, 2025

## Session Summary: Infrastructure Setup & Terraform Configuration

**Repository:** suddhasish/mlopsaws  
**Branch:** main  
**AWS Account:** 891807086260  
**Region:** us-east-1

---

## 🎯 Major Accomplishments

### ✅ Completed Setup Tasks

1. **AWS OIDC Authentication** - Configured GitHub Actions to use OIDC instead of access keys
2. **IAM Role Configuration** - Created and configured `GitHubActions-MLOps-Dev` role with all necessary permissions
3. **Terraform Structure** - Validated and fixed multi-environment Terraform configuration
4. **GitHub Actions Workflow** - Updated CI/CD pipeline with proper authentication and artifact handling
5. **Documentation** - Updated all setup guides with actual configurations

---

## 📝 Detailed Changes

### 1. Documentation Updates

#### `docs/COMPLETE_SETUP_GUIDE.md`
**Changes:**
- Updated Step 2.3 to include 6 AWS managed policies (was 3)
- Added EC2, CloudWatch, and CloudTrail permissions
- Added `--profile mlops-dev` to all AWS CLI commands
- Updated verification section to show expected 6 policies

**Why:** Terraform needs additional AWS service permissions beyond SageMaker, S3, and IAM to manage VPC, logging, and audit trails.

#### `docs/ACTUAL_SETUP_COMPLETED.md`
**Changes:**
- Updated attached policies list from 3 to 6
- Added detailed permission explanations
- Updated current status section with all completed tasks
- Added commit hashes and progress tracking

**Why:** Track actual implementation vs. documentation for future reference.

---

### 2. IAM Role Permissions

#### Added Managed Policies to `GitHubActions-MLOps-Dev`

**Original 3 Policies:**
1. ✅ AmazonSageMakerFullAccess
2. ✅ AmazonS3FullAccess
3. ✅ IAMFullAccess

**Added 3 New Policies:**
4. ✅ AmazonEC2FullAccess - *For VPC, subnets, security groups, availability zones*
5. ✅ CloudWatchFullAccess - *For logs, alarms, and metrics*
6. ✅ AWSCloudTrail_FullAccess - *For audit logging and compliance*

**Commands Used:**
```powershell
aws iam attach-role-policy --role-name GitHubActions-MLOps-Dev --policy-arn arn:aws:iam::aws:policy/AmazonEC2FullAccess --profile mlops-dev
aws iam attach-role-policy --role-name GitHubActions-MLOps-Dev --policy-arn arn:aws:iam::aws:policy/CloudWatchFullAccess --profile mlops-dev
aws iam attach-role-policy --role-name GitHubActions-MLOps-Dev --policy-arn arn:aws:iam::aws:policy/AWSCloudTrail_FullAccess --profile mlops-dev
```

**Verification:**
```powershell
aws iam list-attached-role-policies --role-name GitHubActions-MLOps-Dev --profile mlops-dev
```

**Why:** Original error: `UnauthorizedOperation: User: arn:aws:sts::891807086260:assumed-role/GitHubActions-MLOps-Dev/GitHubActions-Terraform-Dev is not authorized to perform: ec2:DescribeAvailabilityZones`

---

### 3. GitHub Actions Workflow Updates

#### `.github/workflows/terraform.yml`

**Change 1: Artifact Actions Updated**
- **Before:** `actions/upload-artifact@v3` and `actions/download-artifact@v3`
- **After:** `actions/upload-artifact@v4` and `actions/download-artifact@v4`
- **Why:** v3 deprecated as of April 2024, GitHub Actions was failing with deprecation warnings

**Change 2: Working Directory Structure**
- **Before:** Running terraform from `infrastructure/terraform/environments/dev/`
- **After:** Running terraform from `infrastructure/terraform/` with `-var-file="environments/dev/terraform.tfvars"`
- **Why:** The `.tf` files are in root terraform directory, only `.tfvars` files are in environment subdirectories

**Change 3: Terraform Commands Updated**
```yaml
# Before
working-directory: infrastructure/terraform/environments/dev
terraform plan -var-file="terraform.tfvars" -out=tfplan

# After
working-directory: infrastructure/terraform
terraform plan -var-file="environments/dev/terraform.tfvars" -out=tfplan-dev
```

**Commits:**
- `50d6dfc` - fix: Update artifact actions from v3 to v4 to resolve deprecation warning
- `3ab8cb1` - fix: Correct Terraform workflow to run from root directory with env-specific tfvars
- `29d266d` - fix: Change additional_tags to tags for networking module

---

### 4. Terraform Configuration Fixes

#### Formatting Fixes (All `.tfvars` files)

**Files Modified:**
- `infrastructure/terraform/environments/dev/terraform.tfvars`
- `infrastructure/terraform/environments/staging/terraform.tfvars`
- `infrastructure/terraform/environments/production/terraform.tfvars`

**Changes:**
- Fixed inline comment spacing: Changed varying spaces to exactly **2 spaces** before `#`
- Example: `enable_vpc = true  # Comment` (2 spaces)
- **Why:** `terraform fmt -check` requires exactly 2 spaces before inline comments

**Commits:**
- `e30a5e2` - fix: Standardize inline comment spacing to 2 spaces for terraform fmt compliance
- `bf2ee4e` - fix: Format staging and production terraform.tfvars for fmt compliance
- `240d859` - fix: Run terraform fmt on all files to resolve formatting issues

#### Module Configuration Fix

**File:** `infrastructure/terraform/modules.tf`

**Change:**
```hcl
# Before
module "networking" {
  additional_tags = var.additional_tags
}

# After
module "networking" {
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

**Why:** Networking module's `variables.tf` expects `tags` parameter, not `additional_tags`

**Error Fixed:** `Error: Unsupported argument - An argument named "additional_tags" is not expected here.`

**Commit:** `29d266d` - fix: Change additional_tags to tags for networking module

---

### 5. Python Dependencies Fix

#### `requirements.txt`

**Change:**
- **Removed:** `sagemaker-model-monitor==2.0.0`
- **Why:** Package doesn't exist separately; model monitor functionality is included in `sagemaker` SDK

**Error Fixed:** `ERROR: Could not find a version that satisfies the requirement sagemaker-model-monitor==2.0.0`

**Commit:** `524088e` - fix: Remove non-existent sagemaker-model-monitor package from requirements.txt

---

### 6. Terraform Variables Configuration

#### `infrastructure/terraform/environments/dev/terraform.tfvars`

**Changes:**
```hcl
owner_email    = "suddhasiishkar@gmail.com"  # Updated
repository_url = "https://github.com/suddhasish/mlopsaws"  # Updated
alert_email_endpoints = ["suddhasiishkar@gmail.com"]  # Updated
```

**Note:** `aws_account_id` is NOT in tfvars because Terraform auto-detects it using:
```hcl
data "aws_caller_identity" "current" {}
# Then reference: data.aws_caller_identity.current.account_id
```

---

### 7. Infrastructure Scripts Organization

**New Scripts Created & Moved to `infrastructure/scripts/`:**

1. **`attach-terraform-permissions.ps1`**
   - Attaches EC2, CloudWatch, CloudTrail policies to GitHub Actions role
   - Includes verification and colorful output

2. **`add-ec2-permissions.ps1`**
   - Simplified script to add EC2 permissions only
   - Includes verification of attached policies

3. **`update-github-actions-policy.ps1`**
   - Alternative approach using custom inline policy (not used)
   - Kept for reference

4. **`github-actions-policy-updated.json`**
   - Comprehensive custom policy JSON (not used)
   - Kept for reference

**Why Managed Policies Were Chosen:**
- Simpler to maintain
- AWS-managed, kept up-to-date
- Easier to understand permissions
- Standard industry practice

---

## 🔍 Validation Results

### Terraform Format Check
```bash
terraform fmt -check -recursive
# Result: No output = All files formatted correctly ✅
```

### IAM Role Verification
```json
{
    "AttachedPolicies": [
        {"PolicyName": "AmazonEC2FullAccess"},
        {"PolicyName": "IAMFullAccess"},
        {"PolicyName": "CloudWatchFullAccess"},
        {"PolicyName": "AmazonSageMakerFullAccess"},
        {"PolicyName": "AmazonS3FullAccess"},
        {"PolicyName": "AWSCloudTrail_FullAccess"}
    ]
}
```
✅ All 6 policies attached successfully

### GitHub Actions Workflow
- ✅ Artifact actions updated to v4
- ✅ Terraform commands use correct directory structure
- ✅ OIDC authentication configured
- ✅ Workflow triggers on push to main

---

## 🐛 Issues Resolved

### Issue 1: Terraform fmt Failures
**Error:** Multiple files flagged with formatting violations
**Root Cause:** Inconsistent spacing before inline comments (some had 1 space, some 4+ spaces)
**Solution:** Standardized all inline comments to exactly 2 spaces before `#`
**Files Fixed:** All `.tfvars` files in dev, staging, production environments

### Issue 2: EC2 Permission Denied
**Error:** `ec2:DescribeAvailabilityZones` not authorized
**Root Cause:** GitHub Actions role only had SageMaker, S3, and IAM permissions
**Solution:** Attached `AmazonEC2FullAccess` managed policy
**Impact:** Terraform can now query availability zones and manage VPC resources

### Issue 3: Terraform Configuration Not Found
**Error:** `No configuration files - Plan requires configuration to be present`
**Root Cause:** Workflow running terraform commands from `environments/dev/` directory where `.tf` files don't exist
**Solution:** Updated workflow to run from `infrastructure/terraform/` root and pass environment-specific `.tfvars` via `-var-file` flag
**Validation:** Terraform structure is correct - root module pattern with environment-specific variable files

### Issue 4: Artifact Actions Deprecated
**Error:** `This request has been automatically failed because it uses a deprecated version of actions/upload-artifact: v3`
**Root Cause:** GitHub deprecated v3 of artifact actions in April 2024
**Solution:** Updated all `upload-artifact` and `download-artifact` actions from v3 to v4
**Impact:** Workflow no longer shows deprecation warnings

### Issue 5: Networking Module Parameter Mismatch
**Error:** `An argument named "additional_tags" is not expected here`
**Root Cause:** Networking module expects `tags` parameter but was receiving `additional_tags`
**Solution:** Updated `modules.tf` to merge tags and pass as `tags` parameter
**Impact:** Networking module can now be instantiated correctly

### Issue 6: Python Package Not Found
**Error:** `Could not find a version that satisfies the requirement sagemaker-model-monitor==2.0.0`
**Root Cause:** `sagemaker-model-monitor` doesn't exist as a separate package
**Solution:** Removed from `requirements.txt` - functionality included in `sagemaker` SDK
**Impact:** Dependencies install successfully

---

## 📊 Terraform Structure Validation

**Confirmed Correct Structure:**
```
infrastructure/terraform/
├── main.tf                    # Provider, backend, data sources
├── modules.tf                 # Module instantiations
├── outputs.tf                 # Root outputs
├── variables.tf               # Root variable declarations
├── modules/                   # Reusable infrastructure modules
│   ├── iam/
│   ├── s3/
│   ├── networking/
│   └── ...
└── environments/              # Environment-specific values only
    ├── dev/terraform.tfvars
    ├── staging/terraform.tfvars
    └── production/terraform.tfvars
```

**Why This Structure:**
- ✅ DRY (Don't Repeat Yourself) - Single codebase for all environments
- ✅ Standard Terraform best practice for multi-environment deployments
- ✅ Easier to maintain - Changes to modules affect all environments
- ✅ Environment-specific customization via `.tfvars` files

---

## 🚀 Next Steps

### Immediate
1. ✅ **IAM Permissions** - All 6 policies attached
2. ✅ **Terraform Formatting** - All files compliant
3. ✅ **GitHub Actions** - Workflow updated and running
4. ⏸️ **Infrastructure Deployment** - Waiting for GitHub Actions to complete

### Pending
1. Monitor GitHub Actions workflow execution at: https://github.com/suddhasish/mlopsaws/actions
2. Verify Terraform plan output shows expected resources
3. Review and approve Terraform apply (if manual approval required)
4. Validate deployed infrastructure in AWS Console
5. Test SageMaker pipeline execution

---

## 📚 Files Modified Summary

### Configuration Files
- `.github/workflows/terraform.yml` - Workflow updates
- `infrastructure/terraform/environments/dev/terraform.tfvars` - Formatting + values
- `infrastructure/terraform/environments/staging/terraform.tfvars` - Formatting
- `infrastructure/terraform/environments/production/terraform.tfvars` - Formatting
- `infrastructure/terraform/modules.tf` - Networking module fix
- `requirements.txt` - Removed non-existent package

### Documentation
- `docs/COMPLETE_SETUP_GUIDE.md` - Updated IAM permissions section
- `docs/ACTUAL_SETUP_COMPLETED.md` - Updated status and policies
- `docs/CHANGELOG_2025-11-04.md` - This file

### Scripts (New/Moved to `infrastructure/scripts/`)
- `attach-terraform-permissions.ps1` - Main script to add all permissions
- `add-ec2-permissions.ps1` - Simplified EC2-only script
- `update-github-actions-policy.ps1` - Alternative inline policy approach
- `github-actions-policy-updated.json` - Custom policy definition

---

## 🔑 Key Learnings

1. **Terraform fmt is strict** - Requires exactly 2 spaces before inline comments
2. **AWS Managed Policies** - Prefer over custom inline policies for standard permissions
3. **Terraform Structure** - Root module with environment-specific tfvars is best practice
4. **GitHub Actions** - OIDC authentication more secure than access keys
5. **Module Parameters** - Always check module's `variables.tf` for expected parameter names
6. **AWS Account ID** - Terraform can auto-detect via `data.aws_caller_identity`, no need to hardcode

---

## ✅ Verification Checklist

- [x] OIDC provider created in AWS
- [x] IAM role created with trust policy
- [x] 6 managed policies attached to role
- [x] GitHub secrets configured (AWS_ROLE_ARN, AWS_REGION)
- [x] Terraform variables updated
- [x] All Terraform files properly formatted
- [x] GitHub Actions workflow updated
- [x] Python dependencies fixed
- [x] All commits pushed to main branch
- [ ] GitHub Actions workflow completed successfully
- [ ] Infrastructure deployed in AWS
- [ ] SageMaker resources created

---

**Last Updated:** November 4, 2025  
**Session Duration:** ~2 hours  
**Total Commits:** 8 commits  
**Files Modified:** 15+ files  
**Scripts Created:** 4 scripts
