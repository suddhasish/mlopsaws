# GitHub Actions AWS Authentication Troubleshooting

**Error:** `Credentials could not be loaded, please check your action inputs: Could not load credentials from any providers`

## Problem

Your GitHub Actions workflow cannot authenticate with AWS. This happens when GitHub Secrets are not properly configured.

## Required GitHub Secrets

Go to your GitHub repository: **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

Add these 4 secrets:

| Secret Name | Description | How to Get Value |
|------------|-------------|------------------|
| `AWS_ACCESS_KEY_ID` | AWS access key | AWS Console → IAM → Users → Security credentials → Create access key |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key | (Shown only once when creating access key - save it!) |
| `AWS_ACCOUNT_ID` | Your AWS account ID | AWS Console → Account menu (top-right) → Copy account ID |
| `S3_BUCKET_NAME` | S3 bucket name | `mlops-diabetes-dev-891807086260` |
| `SAGEMAKER_EXECUTION_ROLE` | SageMaker role ARN | `arn:aws:iam::891807086260:role/service-role/AmazonSageMaker-ExecutionRole-20251026T145759` |

## Step-by-Step: Create AWS Access Keys

### Option 1: Create IAM User for GitHub Actions (Recommended)

```bash
# 1. Create IAM user
aws iam create-user --user-name github-actions-mlops

# 2. Attach policies
aws iam attach-user-policy \
  --user-name github-actions-mlops \
  --policy-arn arn:aws:iam::aws:policy/AmazonSageMakerFullAccess

aws iam attach-user-policy \
  --user-name github-actions-mlops \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess

aws iam attach-user-policy \
  --user-name github-actions-mlops \
  --policy-arn arn:aws:iam::aws:policy/IAMReadOnlyAccess

# 3. Create access key
aws iam create-access-key --user-name github-actions-mlops
```

Output will look like:
```json
{
    "AccessKey": {
        "UserName": "github-actions-mlops",
        "AccessKeyId": "AKIAIOSFODNN7EXAMPLE",
        "Status": "Active",
        "SecretAccessKey": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
        "CreateDate": "2025-11-06T12:00:00Z"
    }
}
```

⚠️ **SAVE THE `SecretAccessKey` IMMEDIATELY** - You can't retrieve it later!

### Option 2: Use Existing IAM User

If you already have an IAM user:

```bash
# List existing access keys
aws iam list-access-keys --user-name YOUR_USERNAME

# Create new access key
aws iam create-access-key --user-name YOUR_USERNAME
```

## Add Secrets to GitHub

1. Go to: `https://github.com/suddhasish/mlopsaws/settings/secrets/actions`

2. Click **"New repository secret"**

3. Add each secret:
   - **Name:** `AWS_ACCESS_KEY_ID`
   - **Value:** `AKIAIOSFODNN7EXAMPLE` (from above)
   
   - **Name:** `AWS_SECRET_ACCESS_KEY`
   - **Value:** `wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY` (from above)
   
   - **Name:** `AWS_ACCOUNT_ID`
   - **Value:** `891807086260`
   
   - **Name:** `S3_BUCKET_NAME`
   - **Value:** `mlops-diabetes-dev-891807086260`
   
   - **Name:** `SAGEMAKER_EXECUTION_ROLE`
   - **Value:** `arn:aws:iam::891807086260:role/service-role/AmazonSageMaker-ExecutionRole-20251026T145759`

4. Click **"Add secret"** for each

## Verify Secrets

After adding all secrets, you should see 5 secrets listed (names only, values are hidden):
- ✅ AWS_ACCESS_KEY_ID
- ✅ AWS_SECRET_ACCESS_KEY
- ✅ AWS_ACCOUNT_ID
- ✅ S3_BUCKET_NAME
- ✅ SAGEMAKER_EXECUTION_ROLE

## Test the Fix

Push a commit to trigger the workflow:

```bash
git commit --allow-empty -m "Test: Verify AWS credentials configured"
git push origin main
```

Check workflow: `https://github.com/suddhasish/mlopsaws/actions`

## Alternative: Use OIDC (No Access Keys Needed)

If you prefer not to use access keys, you can use OIDC authentication instead. This is more secure as it uses temporary credentials.

### OIDC Setup

1. **Create OIDC Provider in AWS IAM:**

```bash
aws iam create-open-id-connect-provider \
  --url https://token.actions.githubusercontent.com \
  --client-id-list sts.amazonaws.com \
  --thumbprint-list 6938fd4d98bab03faadb97b34396831e3780aea1
```

2. **Create IAM Role for GitHub Actions:**

Create file `github-oidc-trust-policy.json`:
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

```bash
# Create role
aws iam create-role \
  --role-name GitHubActionsOIDC \
  --assume-role-policy-document file://github-oidc-trust-policy.json

# Attach policies
aws iam attach-role-policy \
  --role-name GitHubActionsOIDC \
  --policy-arn arn:aws:iam::aws:policy/AmazonSageMakerFullAccess

aws iam attach-role-policy \
  --role-name GitHubActionsOIDC \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess
```

3. **Update GitHub Actions workflow:**

```yaml
- name: Configure AWS credentials
  uses: aws-actions/configure-aws-credentials@v4
  with:
    role-to-assume: arn:aws:iam::891807086260:role/GitHubActionsOIDC
    aws-region: us-east-1
    audience: sts.amazonaws.com
```

4. **Add GitHub Secret:**
   - Name: `AWS_ROLE_ARN`
   - Value: `arn:aws:iam::891807086260:role/GitHubActionsOIDC`

## Troubleshooting Commands

```bash
# Check if access keys work locally
aws sts get-caller-identity

# Test S3 access
aws s3 ls s3://mlops-diabetes-dev-891807086260/

# Test SageMaker access
aws sagemaker list-model-packages --model-package-group-name mlops-diabetes-model-group-dev
```

## Security Best Practices

1. ✅ Use OIDC instead of access keys (if possible)
2. ✅ Use least-privilege IAM policies
3. ✅ Rotate access keys every 90 days
4. ✅ Enable MFA for IAM users
5. ✅ Monitor access with CloudTrail
6. ✅ Never commit secrets to Git

## Next Steps

After secrets are configured:
1. ✅ Push code to GitHub
2. ✅ GitHub Actions will run automatically
3. ✅ Monitor workflow: `https://github.com/suddhasish/mlopsaws/actions`
4. ✅ Check SageMaker Pipeline execution in AWS Console
