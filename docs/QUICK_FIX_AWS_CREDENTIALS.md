# Quick Fix: GitHub Actions AWS Credentials Error

## Problem
```
Error: Credentials could not be loaded, please check your action inputs
```

## Root Cause
GitHub Secrets are not configured in your repository.

## Solution (3 Minutes)

### Step 1: Create AWS Access Key

Run in PowerShell:
```powershell
# Create IAM user
aws iam create-user --user-name github-actions-mlops

# Attach permissions
aws iam attach-user-policy --user-name github-actions-mlops --policy-arn arn:aws:iam::aws:policy/AmazonSageMakerFullAccess
aws iam attach-user-policy --user-name github-actions-mlops --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess

# Create access key
aws iam create-access-key --user-name github-actions-mlops
```

**Save the output immediately!** You'll see:
```json
{
  "AccessKeyId": "AKIAXXXXXXXXXXXXXXXX",
  "SecretAccessKey": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
}
```

### Step 2: Add Secrets to GitHub

1. **Open GitHub Secrets page:**
   ```
   https://github.com/suddhasish/mlopsaws/settings/secrets/actions
   ```

2. **Click "New repository secret"** and add these 5 secrets:

   | Secret Name | Value (Your Actual Values) |
   |------------|---------------------------|
   | `AWS_ACCESS_KEY_ID` | `AKIAXXXXXXXXXXXXXXXX` (from above) |
   | `AWS_SECRET_ACCESS_KEY` | `wJalrXUtnFEMI/K7MDENG...` (from above) |
   | `AWS_ACCOUNT_ID` | `891807086260` |
   | `S3_BUCKET_NAME` | `mlops-diabetes-dev-891807086260` |
   | `SAGEMAKER_EXECUTION_ROLE` | `arn:aws:iam::891807086260:role/service-role/AmazonSageMaker-ExecutionRole-20251026T145759` |

3. **Verify:** You should see 5 secrets listed (values are hidden)

### Step 3: Test

```bash
git commit --allow-empty -m "Test: Fix AWS credentials"
git push origin main
```

Check: `https://github.com/suddhasish/mlopsaws/actions`

## Automated Setup (Alternative)

Run the PowerShell script:
```powershell
.\scripts\setup-github-secrets.ps1
```

This will:
- ✅ Create IAM user
- ✅ Generate access keys
- ✅ Display secrets to copy to GitHub
- ✅ Save to local file (delete after use!)

## Troubleshooting

**Q: I don't have AWS CLI configured**
```bash
aws configure
# Enter your AWS access key, secret key, region (us-east-1)
```

**Q: User already exists**
```bash
# Create new access key for existing user
aws iam create-access-key --user-name github-actions-mlops
```

**Q: Still getting authentication errors**
- Verify all 5 secrets are added to GitHub
- Check secret names match exactly (case-sensitive)
- Ensure no extra spaces in secret values
- Wait 1-2 minutes for GitHub to sync secrets

## Security Notes

⚠️ **Never commit access keys to Git**
✅ Use OIDC authentication (more secure, no keys) - See full docs
✅ Rotate access keys every 90 days
✅ Delete `github-secrets-DO-NOT-COMMIT.txt` after use
