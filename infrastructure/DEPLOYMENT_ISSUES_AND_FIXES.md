# Terraform Deployment Issues - Quick Fix Guide

## Issues Found and Solutions

### ✅ Issue 1: Missing Lambda ZIP Files
**Error:** `reading ZIP file (modules/auto_shutdown/lambda_shutdown.zip): no such file or directory`

**Solution:** Disabled auto_shutdown module for dev environment
- Changed `enable_auto_shutdown = false` in `dev/terraform.tfvars`
- Lambda functions can be created later if needed

---

### ✅ Issue 2: Missing EventBridge Permissions
**Error:** `User is not authorized to perform: events:TagResource`

**Solution:** Add EventBridge permissions to IAM role

```powershell
aws iam attach-role-policy `
    --role-name GitHubActions-MLOps-Dev `
    --policy-arn arn:aws:iam::aws:policy/AmazonEventBridgeFullAccess `
    --profile mlops-dev
```

---

### ✅ Issue 3: Missing Lambda Permissions
**Error:** Lambda functions cannot be created

**Solution:** Add Lambda permissions to IAM role

```powershell
aws iam attach-role-policy `
    --role-name GitHubActions-MLOps-Dev `
    --policy-arn arn:aws:iam::aws:policy/AWSLambda_FullAccess `
    --profile mlops-dev
```

---

### ✅ Issue 4: Missing Budgets Permissions
**Error:** `User is not authorized to perform: budgets:ModifyBudget`

**Solution:** Budgets permissions are included in IAMFullAccess policy already attached.
The error is because budget creation requires special handling. We'll keep budgets enabled.

---

### ⚠️ Issue 5: SageMaker Model Package Group Quota
**Error:** `The account-level service limit 'Maximum number of SageMaker Model Package Groups allowed per account' is 0`

**Solution:** Request quota increase from AWS Console (CLI quota codes may vary)

**AWS Console Method (RECOMMENDED):**

1. **Go to Service Quotas Console:**
   - Direct link: https://console.aws.amazon.com/servicequotas/home/services/sagemaker/quotas
   - Or: AWS Console → Service Quotas → AWS Services → Amazon SageMaker

2. **Find the quota:**
   - Search for: "Model package groups"
   - Full name: "Model package groups per account"
   - Current value: 0
   - Default value: Usually 100

3. **Request increase:**
   - Click on "Model package groups per account"
   - Click "Request quota increase"
   - Enter desired value: **10** (or higher if you plan many models)
   - Click "Request"

4. **Wait for approval:**
   - Usually approved in: 15 minutes to 48 hours
   - You'll receive email notification
   - Check status: Service Quotas → Dashboard → Quota request history

**Alternative - AWS Support Ticket:**
If Service Quotas doesn't work, create a support case:
1. Go to: https://console.aws.amazon.com/support/home
2. Click "Create case"
3. Select "Service limit increase"
4. Service: Amazon SageMaker
5. Limit type: Model Package Groups
6. Request: Increase to 10

**Why this error occurs:**
- New AWS accounts have 0 quota for Model Package Groups by default
- This is a security/cost measure
- First request is usually auto-approved quickly

---

## Quick Fix Commands

Run these commands in order:

```powershell
# 1. Add EventBridge permissions
aws iam attach-role-policy `
    --role-name GitHubActions-MLOps-Dev `
    --policy-arn arn:aws:iam::aws:policy/AmazonEventBridgeFullAccess `
    --profile mlops-dev

# 2. Add Lambda permissions
aws iam attach-role-policy `
    --role-name GitHubActions-MLOps-Dev `
    --policy-arn arn:aws:iam::aws:policy/AWSLambda_FullAccess `
    --profile mlops-dev

# 3. Verify all policies (should show 8 policies now)
aws iam list-attached-role-policies --role-name GitHubActions-MLOps-Dev --profile mlops-dev
```

**Then manually in AWS Console:**
- Go to: https://console.aws.amazon.com/servicequotas/home/services/sagemaker/quotas
- Search for "Model package groups per account"
- Request increase to 10

---

## Expected IAM Policies After Fix

The role should have 8 managed policies:

1. ✅ AmazonSageMakerFullAccess
2. ✅ AmazonS3FullAccess
3. ✅ IAMFullAccess
4. ✅ AmazonEC2FullAccess
5. ✅ CloudWatchFullAccess
6. ✅ AWSCloudTrail_FullAccess
7. ✅ AmazonEventBridgeFullAccess ← NEW
8. ✅ AWSLambda_FullAccess ← NEW

---

## After Applying Fixes

1. Commit the terraform.tfvars change (auto_shutdown disabled)
2. Push to GitHub
3. Wait for quota increase approval (24-48 hours)
4. Re-run GitHub Actions workflow

---

## Monitoring Quota Request Status

```powershell
# Check quota request status
aws service-quotas list-requested-service-quota-change-history-by-quota `
    --service-code sagemaker `
    --quota-code L-7B5A4C83 `
    --profile mlops-dev
```

**Status values:**
- PENDING - Request submitted, waiting for approval
- APPROVED - Quota increased successfully
- DENIED - Request rejected (rare)
- CASE_OPENED - Support case created for review

---

## Alternative: Disable Model Package Group Temporarily

If you want to test infrastructure without waiting for quota:

Edit `infrastructure/terraform/modules.tf` and comment out the sagemaker module:

```hcl
# Temporarily disabled - waiting for quota increase
# module "sagemaker" {
#   source = "./modules/sagemaker"
#   
#   project_name = var.project_name
#   environment  = var.environment
#   tags         = merge(
#     {
#       Project     = var.project_name
#       Environment = var.environment
#       ManagedBy   = "Terraform"
#     },
#     var.additional_tags
#   )
# }
```

⚠️ **Not recommended** - Model Package Group is essential for ML model versioning

---

## Summary

**Immediate Actions:**
1. ✅ Disabled auto_shutdown (Lambda ZIP files missing)
2. ⏸️ Add EventBridge permissions (run command above)
3. ⏸️ Add Lambda permissions (run command above)
4. ⏸️ Request SageMaker quota increase (run command above)

**After Quota Approval:**
5. ⏸️ Re-run Terraform deployment
6. ⏸️ Enable auto_shutdown if needed (after creating Lambda functions)
