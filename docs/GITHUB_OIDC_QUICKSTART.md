# Quick Setup: GitHub Actions OIDC Authentication

**Time to complete:** 10 minutes  
**Current branch:** feature/production-grade-deployment

---

## ✅ What Changed

Your workflow now uses **OIDC (OpenID Connect)** instead of access keys:

**Before:**
```yaml
- uses: aws-actions/configure-aws-credentials@v2
  with:
    aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}      # ❌ Long-lived credentials
    aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
```

**After:**
```yaml
- uses: aws-actions/configure-aws-credentials@v4
  with:
    role-to-assume: ${{ secrets.AWS_ROLE_ARN }}  # ✅ Short-lived tokens
    aws-region: us-east-1
    audience: sts.amazonaws.com
```

---

## 🚀 Setup Steps (PowerShell)

### Step 1: Create OIDC Identity Provider

```powershell
# Create OIDC provider in AWS (one-time setup)
aws iam create-open-id-connect-provider `
  --url https://token.actions.githubusercontent.com `
  --client-id-list sts.amazonaws.com `
  --thumbprint-list 6938fd4d98bab03faadb97b34396831e3780aea1
```

**Expected output:**
```json
{
    "OpenIDConnectProviderArn": "arn:aws:iam::891807086260:oidc-provider/token.actions.githubusercontent.com"
}
```

### Step 2: Create IAM Role for GitHub Actions

```powershell
# Create trust policy file
@"
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
"@ | Out-File -FilePath trust-policy.json -Encoding utf8

# Create the role
aws iam create-role `
  --role-name GitHubActionsMLOpsRole `
  --assume-role-policy-document file://trust-policy.json `
  --description "Role for GitHub Actions to deploy ML models"
```

**Expected output:**
```json
{
    "Role": {
        "RoleName": "GitHubActionsMLOpsRole",
        "Arn": "arn:aws:iam::891807086260:role/GitHubActionsMLOpsRole"
    }
}
```

**⚠️ SAVE THIS ARN - You'll need it for GitHub Secrets!**

### Step 3: Attach Policies to Role

```powershell
# Attach SageMaker permissions
aws iam attach-role-policy `
  --role-name GitHubActionsMLOpsRole `
  --policy-arn arn:aws:iam::aws:policy/AmazonSageMakerFullAccess

# Attach S3 permissions
aws iam attach-role-policy `
  --role-name GitHubActionsMLOpsRole `
  --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess

# Attach CloudWatch permissions
aws iam attach-role-policy `
  --role-name GitHubActionsMLOpsRole `
  --policy-arn arn:aws:iam::aws:policy/CloudWatchFullAccess
```

### Step 4: Add Role ARN to GitHub Secrets

1. **Go to:** https://github.com/suddhasish/mlopsaws/settings/secrets/actions

2. **Click:** "New repository secret"

3. **Add secret:**
   - **Name:** `AWS_ROLE_ARN`
   - **Value:** `arn:aws:iam::891807086260:role/GitHubActionsMLOpsRole`
   - Click "Add secret"

### Step 5: Verify Setup

```powershell
# Verify OIDC provider exists
aws iam get-open-id-connect-provider `
  --open-id-connect-provider-arn "arn:aws:iam::891807086260:oidc-provider/token.actions.githubusercontent.com"

# Verify role exists
aws iam get-role --role-name GitHubActionsMLOpsRole

# Verify attached policies
aws iam list-attached-role-policies --role-name GitHubActionsMLOpsRole
```

---

## ✅ Test the Workflow

1. **Go to:** https://github.com/suddhasish/mlopsaws/actions

2. **Click:** "Multi-Stage Model Deployment (Dev → Staging → Prod)"

3. **Click:** "Run workflow"

4. **Select:**
   - Branch: `feature/production-grade-deployment`
   - Deploy to environment: `dev`
   - Model package ARN: (leave empty)

5. **Click:** "Run workflow"

6. **Watch it run!** It should now authenticate using OIDC ✅

---

## 🔍 Troubleshooting

### Error: "No OpenIDConnect provider found"

**Solution:**
```powershell
# Create the OIDC provider
aws iam create-open-id-connect-provider `
  --url https://token.actions.githubusercontent.com `
  --client-id-list sts.amazonaws.com `
  --thumbprint-list 6938fd4d98bab03faadb97b34396831e3780aea1
```

### Error: "User is not authorized to perform: sts:AssumeRoleWithWebIdentity"

**Solution:** Check the trust policy allows your repository:
```powershell
aws iam get-role --role-name GitHubActionsMLOpsRole --query 'Role.AssumeRolePolicyDocument'

# Should show: "repo:suddhasish/mlopsaws:*"
```

### Error: "Context access might be invalid: AWS_ROLE_ARN"

**Solution:** Add the secret in GitHub:
- Go to: https://github.com/suddhasish/mlopsaws/settings/secrets/actions
- Add `AWS_ROLE_ARN` with the role ARN value

### Workflow still uses old credentials

**Solution:** Delete old secrets (they're no longer needed):
- Go to: https://github.com/suddhasish/mlopsaws/settings/secrets/actions
- Delete `AWS_ACCESS_KEY_ID`
- Delete `AWS_SECRET_ACCESS_KEY`

---

## 📊 What You Get

### Security Benefits:
- ✅ **No long-lived credentials** in GitHub
- ✅ **Automatic token rotation** (tokens expire after 1 hour)
- ✅ **Fine-grained permissions** per repository
- ✅ **CloudTrail audit logs** show which workflow assumed the role
- ✅ **No secret management** (no keys to rotate)

### Cost:
- **FREE** - OIDC is free, no additional charges

---

## 🎯 Summary Checklist

- [ ] OIDC provider created in AWS
- [ ] IAM role `GitHubActionsMLOpsRole` created
- [ ] Trust policy allows GitHub repository
- [ ] Policies attached (SageMaker, S3, CloudWatch)
- [ ] `AWS_ROLE_ARN` secret added to GitHub
- [ ] Old access key secrets removed (optional)
- [ ] Workflow tested and runs successfully

---

## 📚 Additional Resources

- [AWS OIDC Documentation](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-amazon-web-services)
- [Configure AWS Credentials Action](https://github.com/aws-actions/configure-aws-credentials)
- [Full OIDC Setup Guide](./GITHUB_ACTIONS_OIDC_SETUP.md)

---

**Next:** Once setup is complete, run the workflow and deploy to dev! 🚀
