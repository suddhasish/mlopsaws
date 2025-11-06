# OIDC Authentication Setup for GitHub Actions

## Current Status

✅ **Workflow Updated** - All jobs now use OIDC authentication with `AWS_ROLE_ARN`
❌ **IAM Setup Required** - Need to configure AWS IAM for OIDC trust

## What You Need to Do

Since you already have `AWS_ROLE_ARN` secret in GitHub, you need to ensure your IAM role has the correct trust policy to allow GitHub Actions to assume it.

## Step 1: Verify OIDC Provider Exists

Run in PowerShell:
```powershell
aws iam list-open-id-connect-providers
```

**If you see `token.actions.githubusercontent.com`:** ✅ Already configured, skip to Step 2

**If empty:** Create OIDC provider:
```powershell
aws iam create-open-id-connect-provider `
  --url https://token.actions.githubusercontent.com `
  --client-id-list sts.amazonaws.com `
  --thumbprint-list 6938fd4d98bab03faadb97b34396831e3780aea1
```

## Step 2: Update IAM Role Trust Policy

Get your current role name from `AWS_ROLE_ARN` secret. It should look like:
```
arn:aws:iam::891807086260:role/YOUR_ROLE_NAME
```

Extract the role name (e.g., `GitHubActionsRole`) and update its trust policy:

### Create Trust Policy File

Create `github-trust-policy.json`:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::891807086260:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
        },
        "StringLike": {
          "token.actions.githubusercontent.com:sub": "repo:suddhasish/mlopsaws:*"
        }
      }
    }
  ]
}
```

### Update Role

```powershell
# Replace YOUR_ROLE_NAME with actual role name
aws iam update-assume-role-policy `
  --role-name YOUR_ROLE_NAME `
  --policy-document file://github-trust-policy.json
```

## Step 3: Verify Role Permissions

Ensure the role has these policies attached:
```powershell
aws iam list-attached-role-policies --role-name YOUR_ROLE_NAME
```

**Required policies:**
- ✅ `AmazonSageMakerFullAccess`
- ✅ `AmazonS3FullAccess`
- ✅ `IAMReadOnlyAccess` (for SageMaker execution role)

**If missing, attach them:**
```powershell
aws iam attach-role-policy `
  --role-name YOUR_ROLE_NAME `
  --policy-arn arn:aws:iam::aws:policy/AmazonSageMakerFullAccess

aws iam attach-role-policy `
  --role-name YOUR_ROLE_NAME `
  --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess
```

## Step 4: Verify GitHub Secrets

Ensure these secrets are set in GitHub:
- ✅ `AWS_ROLE_ARN` (you already have this)
- ✅ `SAGEMAKER_EXECUTION_ROLE` 
- ✅ `S3_BUCKET_NAME`
- ✅ `AWS_ACCOUNT_ID`

You can add the missing ones at:
```
https://github.com/suddhasish/mlopsaws/settings/secrets/actions
```

Values:
- **SAGEMAKER_EXECUTION_ROLE**: `arn:aws:iam::891807086260:role/service-role/AmazonSageMaker-ExecutionRole-20251026T145759`
- **S3_BUCKET_NAME**: `mlops-diabetes-dev-891807086260`
- **AWS_ACCOUNT_ID**: `891807086260`

## Step 5: Test

Commit and push these workflow changes:
```bash
git add .github/workflows/mlops_pipeline.yaml
git commit -m "chore: Switch to OIDC authentication"
git push origin main
```

Monitor at: `https://github.com/suddhasish/mlopsaws/actions`

## Quick Check: What's Your Role ARN?

Run this to see what your `AWS_ROLE_ARN` secret should be:
```powershell
# List all roles with "GitHub" or "Actions" in the name
aws iam list-roles --query "Roles[?contains(RoleName, 'GitHub') || contains(RoleName, 'Actions')].{Name:RoleName, ARN:Arn}" --output table
```

## Alternative: If You Don't Have the Role Yet

If you need to create a new role from scratch:

```powershell
# 1. Create OIDC provider (if not exists)
aws iam create-open-id-connect-provider `
  --url https://token.actions.githubusercontent.com `
  --client-id-list sts.amazonaws.com `
  --thumbprint-list 6938fd4d98bab03faadb97b34396831e3780aea1

# 2. Create role with trust policy
aws iam create-role `
  --role-name GitHubActionsMLOpsRole `
  --assume-role-policy-document file://github-trust-policy.json

# 3. Attach permissions
aws iam attach-role-policy `
  --role-name GitHubActionsMLOpsRole `
  --policy-arn arn:aws:iam::aws:policy/AmazonSageMakerFullAccess

aws iam attach-role-policy `
  --role-name GitHubActionsMLOpsRole `
  --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess

# 4. Get the ARN
aws iam get-role --role-name GitHubActionsMLOpsRole --query 'Role.Arn' --output text
```

Copy the ARN output and set it as `AWS_ROLE_ARN` in GitHub secrets.

## Benefits of OIDC vs Access Keys

✅ **More Secure** - No long-term credentials stored
✅ **Temporary Credentials** - Automatically rotated
✅ **Better Audit Trail** - CloudTrail shows GitHub repo/workflow
✅ **No Key Rotation** - No need to rotate every 90 days
✅ **Compliance** - Meets security best practices

## Troubleshooting

**Error: "AssumeRoleWithWebIdentity is not authorized"**
- Trust policy is incorrect
- OIDC provider not created
- Repository name doesn't match in trust policy

**Error: "Access Denied" when accessing SageMaker/S3**
- Role missing required IAM policies
- Attach `AmazonSageMakerFullAccess` and `AmazonS3FullAccess`

**Error: "Role ARN not found"**
- Check `AWS_ROLE_ARN` secret value in GitHub
- Verify role exists: `aws iam get-role --role-name YOUR_ROLE_NAME`
