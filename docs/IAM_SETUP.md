# IAM & OIDC Configuration Guide

**Complete guide for setting up AWS IAM roles and GitHub OIDC authentication**

Last Updated: November 4, 2025

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [OIDC Provider Setup](#oidc-provider-setup)
4. [IAM Role Creation](#iam-role-creation)
5. [Policy Attachment](#policy-attachment)
6. [Verification](#verification)
7. [Trust Policy Patterns](#trust-policy-patterns)
8. [Troubleshooting](#troubleshooting)

---

## Overview

### Why OIDC Instead of Access Keys?

**Traditional Method (Insecure):**
- ❌ Store AWS access keys in GitHub Secrets
- ❌ Keys never expire automatically
- ❌ Can leak in logs or error messages
- ❌ Difficult to rotate
- ❌ Broad permissions if compromised

**OIDC Method (Secure):**
- ✅ No long-lived credentials stored
- ✅ Temporary tokens (1-hour lifespan)
- ✅ Automatic expiration
- ✅ Cannot leak (generated on-demand)
- ✅ Granular permissions per environment
- ✅ Full audit trail in CloudTrail

### How It Works

```
┌─────────────────────────────────────────────────────────────┐
│ 1. GitHub Actions Workflow Triggered                        │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. GitHub generates OIDC token with:                        │
│    - Repository: suddhasish/mlopsaws                        │
│    - Branch: main                                           │
│    - Workflow: terraform.yml                                │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. GitHub Actions calls AWS STS:                            │
│    AssumeRoleWithWebIdentity(                               │
│      RoleArn: arn:aws:iam::ACCOUNT:role/GitHubActions-...,  │
│      WebIdentityToken: <OIDC token>                         │
│    )                                                         │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. AWS verifies:                                            │
│    ✓ Token signed by GitHub                                 │
│    ✓ Repository matches trust policy                        │
│    ✓ Audience is sts.amazonaws.com                          │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. AWS returns temporary credentials:                       │
│    - Access Key ID                                          │
│    - Secret Access Key                                      │
│    - Session Token                                          │
│    - Expiration: 1 hour                                     │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ 6. GitHub Actions uses credentials to:                      │
│    - Deploy infrastructure via Terraform                    │
│    - Train ML models on SageMaker                           │
│    - Upload data to S3                                      │
└─────────────────────────────────────────────────────────────┘
```

---

## Prerequisites

**Before starting, you need:**

1. ✅ AWS Account with admin access
2. ✅ AWS CLI installed and configured
3. ✅ GitHub repository created
4. ✅ AWS account ID handy

**Get Your AWS Account ID:**
```powershell
$accountId = aws sts get-caller-identity --query Account --output text --profile mlops-dev
Write-Host "AWS Account ID: $accountId"
```

**Get Your GitHub Details:**
- Username: Your GitHub username (e.g., `suddhasish`)
- Repository: Your repo name (e.g., `mlopsaws`)
- Organization: If using org-based trust (e.g., `acme-corp`)

---

## OIDC Provider Setup

### Step 1: Create OIDC Identity Provider

**Method 1: AWS CLI (Recommended - Faster)**

```powershell
aws iam create-open-id-connect-provider `
  --url https://token.actions.githubusercontent.com `
  --client-id-list sts.amazonaws.com `
  --thumbprint-list 6938fd4d98bab03faadb97b34396831e3780aea1 `
  --profile mlops-dev
```

**Expected Output:**
```json
{
    "OpenIDConnectProviderArn": "arn:aws:iam::891807086260:oidc-provider/token.actions.githubusercontent.com"
}
```

**Method 2: AWS Console**

```
1. Navigate to: https://console.aws.amazon.com/iam/
2. Left menu → Identity providers → Add provider
3. Provider type: OpenID Connect
4. Provider URL: https://token.actions.githubusercontent.com
5. Audience: sts.amazonaws.com
6. Click: Add provider
```

### Step 2: Verify Provider Created

```powershell
aws iam list-open-id-connect-providers --profile mlops-dev
```

**Expected:**
```json
{
    "OpenIDConnectProviderList": [
        {
            "Arn": "arn:aws:iam::ACCOUNT_ID:oidc-provider/token.actions.githubusercontent.com"
        }
    ]
}
```

✅ **Checkpoint:** OIDC provider exists

---

## IAM Role Creation

### Step 1: Define Variables

```powershell
# Get account ID
$accountId = aws sts get-caller-identity --query Account --output text --profile mlops-dev

# Set your GitHub details
$githubUsername = "suddhasish"  # ⚠️ CHANGE THIS
$repoName = "mlopsaws"           # ⚠️ CHANGE THIS
```

### Step 2: Create Trust Policy

**Option A: Inline JSON (Recommended for Windows)**

Avoids file encoding issues:

```powershell
aws iam create-role `
  --role-name GitHubActions-MLOps-Dev `
  --assume-role-policy-document "{\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Principal\":{\"Federated\":\"arn:aws:iam::${accountId}:oidc-provider/token.actions.githubusercontent.com\"},\"Action\":\"sts:AssumeRoleWithWebIdentity\",\"Condition\":{\"StringEquals\":{\"token.actions.githubusercontent.com:aud\":\"sts.amazonaws.com\"},\"StringLike\":{\"token.actions.githubusercontent.com:sub\":\"repo:${githubUsername}/${repoName}:*\"}}}]}" `
  --description "GitHub Actions role for MLOps dev environment" `
  --profile mlops-dev
```

**Option B: File-Based (If Inline Fails)**

```powershell
# Create trust policy file with ASCII encoding
@"
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::${accountId}:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
        },
        "StringLike": {
          "token.actions.githubusercontent.com:sub": "repo:${githubUsername}/${repoName}:*"
        }
      }
    }
  ]
}
"@ | Out-File -FilePath trust-policy-dev.json -Encoding ascii

# Create role from file
aws iam create-role `
  --role-name GitHubActions-MLOps-Dev `
  --assume-role-policy-document file://trust-policy-dev.json `
  --description "GitHub Actions role for MLOps dev environment" `
  --profile mlops-dev
```

### Step 3: Save Role ARN

```powershell
# Get and save the role ARN
$roleArn = aws iam get-role --role-name GitHubActions-MLOps-Dev --query 'Role.Arn' --output text --profile mlops-dev
Write-Host "Role ARN: $roleArn"
Write-Host "Save this for GitHub Secrets!"
```

**Example ARN:**
```
arn:aws:iam::891807086260:role/GitHubActions-MLOps-Dev
```

✅ **Checkpoint:** Role created successfully

---

## Policy Attachment

### Required Policies (All 10)

Attach all 10 AWS managed policies to the role:

```powershell
# 3. Attach all 10 required policies
$policies = @(
    "arn:aws:iam::aws:policy/AmazonSageMakerFullAccess",
    "arn:aws:iam::aws:policy/AmazonS3FullAccess",
    "arn:aws:iam::aws:policy/AmazonEC2FullAccess",
    "arn:aws:iam::aws:policy/IAMFullAccess",
    "arn:aws:iam::aws:policy/CloudWatchFullAccess",
    "arn:aws:iam::aws:policy/AWSCloudTrail_FullAccess",
    "arn:aws:iam::aws:policy/AmazonEventBridgeFullAccess",
    "arn:aws:iam::aws:policy/AWSLambda_FullAccess",
    "arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess",
    "arn:aws:iam::aws:policy/AWSBudgetsActionsWithAWSResourceControlAccess"
)

# Attach each policy
foreach ($policy in $policies) {
    Write-Host "Attaching: $policy"
    aws iam attach-role-policy `
        --role-name GitHubActions-MLOps-Dev `
        --policy-arn $policy `
        --profile mlops-dev
}

Write-Host "✅ All 10 policies attached successfully"
```

### Policy Purposes

| Policy | Why Needed | Key Permissions |
|--------|------------|-----------------|
| **AmazonSageMakerFullAccess** | Create/manage ML models, training jobs, endpoints | `sagemaker:*` |
| **AmazonS3FullAccess** | Store data, models, artifacts | `s3:*` |
| **AmazonEC2FullAccess** | VPC, subnets, security groups, availability zones | `ec2:Describe*`, `ec2:Create*` |
| **IAMFullAccess** | Create SageMaker execution roles | `iam:CreateRole`, `iam:AttachRolePolicy` |
| **CloudWatchFullAccess** | Log groups, alarms, metrics | `logs:*`, `cloudwatch:*` |
| **AWSCloudTrail_FullAccess** | Audit logging for compliance | `cloudtrail:*` |
| **AmazonEventBridgeFullAccess** | Scheduled rules for auto-shutdown | `events:*` |
| **AWSLambda_FullAccess** | Auto-shutdown Lambda functions | `lambda:*` |
| **AmazonDynamoDBFullAccess** | Terraform state locking for concurrent runs | `dynamodb:PutItem`, `dynamodb:GetItem`, `dynamodb:DeleteItem` |
| **AWSBudgetsActionsWithAWSResourceControlAccess** | Create and manage cost budgets | `budgets:ModifyBudget`, `budgets:ViewBudget` |

### Alternative: Custom Policy (Production)

For production, create a custom policy with least-privilege:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "sagemaker:CreateTrainingJob",
        "sagemaker:CreateModel",
        "sagemaker:CreateEndpoint",
        "s3:PutObject",
        "s3:GetObject"
      ],
      "Resource": "*",
      "Condition": {
        "StringEquals": {
          "aws:RequestedRegion": "us-east-1"
        }
      }
    }
  ]
}
```

See `docs/TRUST_POLICY_BEST_PRACTICES.md` for production hardening.

---

## Verification

### Verify Role Configuration

```powershell
# Check role exists
aws iam get-role --role-name GitHubActions-MLOps-Dev --profile mlops-dev

# Check trust policy
aws iam get-role --role-name GitHubActions-MLOps-Dev --query 'Role.AssumeRolePolicyDocument' --profile mlops-dev

# Check attached policies (should show 10)
aws iam list-attached-role-policies --role-name GitHubActions-MLOps-Dev --profile mlops-dev
```

### Expected Output (Attached Policies)

```json
{
    "AttachedPolicies": [
        {"PolicyName": "AmazonSageMakerFullAccess", "PolicyArn": "arn:aws:iam::aws:policy/AmazonSageMakerFullAccess"},
        {"PolicyName": "AmazonS3FullAccess", "PolicyArn": "arn:aws:iam::aws:policy/AmazonS3FullAccess"},
        {"PolicyName": "AmazonEC2FullAccess", "PolicyArn": "arn:aws:iam::aws:policy/AmazonEC2FullAccess"},
        {"PolicyName": "IAMFullAccess", "PolicyArn": "arn:aws:iam::aws:policy/IAMFullAccess"},
        {"PolicyName": "CloudWatchFullAccess", "PolicyArn": "arn:aws:iam::aws:policy/CloudWatchFullAccess"},
        {"PolicyName": "AWSCloudTrail_FullAccess", "PolicyArn": "arn:aws:iam::aws:policy/AWSCloudTrail_FullAccess"},
        {"PolicyName": "AmazonEventBridgeFullAccess", "PolicyArn": "arn:aws:iam::aws:policy/AmazonEventBridgeFullAccess"},
        {"PolicyName": "AWSLambda_FullAccess", "PolicyArn": "arn:aws:iam::aws:policy/AWSLambda_FullAccess"},
        {"PolicyName": "AmazonDynamoDBFullAccess", "PolicyArn": "arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess"},
        {"PolicyName": "AWSBudgetsActionsWithAWSResourceControlAccess", "PolicyArn": "arn:aws:iam::aws:policy/AWSBudgetsActionsWithAWSResourceControlAccess"}
    ]
}
```

✅ **Checkpoint:** All 10 policies attached

### Test OIDC Authentication

Create a test GitHub Actions workflow:

```yaml
name: Test OIDC
on: workflow_dispatch

permissions:
  id-token: write
  contents: read

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::ACCOUNT_ID:role/GitHubActions-MLOps-Dev
          aws-region: us-east-1
      
      - name: Test AWS access
        run: aws sts get-caller-identity
```

**Expected output:**
```json
{
    "UserId": "AROA...:GitHubActions",
    "Account": "891807086260",
    "Arn": "arn:aws:sts::891807086260:assumed-role/GitHubActions-MLOps-Dev/GitHubActions"
}
```

---

## Trust Policy Patterns

### Pattern 1: Single Repository (Current)

**Use Case:** Personal projects, single repo

```json
{
  "Condition": {
    "StringLike": {
      "token.actions.githubusercontent.com:sub": "repo:suddhasish/mlopsaws:*"
    }
  }
}
```

**Allows:**
- ✅ All branches in `suddhasish/mlopsaws`
- ✅ All workflows in the repository

**Blocks:**
- ❌ Different repositories
- ❌ Different GitHub users

### Pattern 2: Specific Branch

**Use Case:** Only production deployments from main

```json
{
  "Condition": {
    "StringEquals": {
      "token.actions.githubusercontent.com:sub": "repo:suddhasish/mlopsaws:ref:refs/heads/main"
    }
  }
}
```

**Allows:**
- ✅ Only `main` branch

**Blocks:**
- ❌ Feature branches
- ❌ Pull requests

### Pattern 3: Organization-Based

**Use Case:** Enterprise with multiple repos

```json
{
  "Condition": {
    "StringLike": {
      "token.actions.githubusercontent.com:sub": "repo:acme-corp/*:*"
    }
  }
}
```

**Allows:**
- ✅ All repos in `acme-corp` organization
- ✅ All branches and workflows

**Benefits:**
- User-independent (no changes when users leave)
- Centralized access management
- Team-based permissions

See `docs/TRUST_POLICY_BEST_PRACTICES.md` for migration guide.

### Pattern 4: Environment-Specific

**Use Case:** Different roles for dev/staging/prod

```json
{
  "Condition": {
    "StringEquals": {
      "token.actions.githubusercontent.com:aud": "sts.amazonaws.com",
      "token.actions.githubusercontent.com:sub": "repo:suddhasish/mlopsaws:environment:production"
    }
  }
}
```

**Allows:**
- ✅ Only production environment deployments

**Blocks:**
- ❌ Development deployments
- ❌ Staging deployments

---

## Troubleshooting

### Issue: Trust Policy Mismatch

**Error:** `Not authorized to perform sts:AssumeRoleWithWebIdentity`

**Check:**
```powershell
# View current trust policy
aws iam get-role --role-name GitHubActions-MLOps-Dev --query 'Role.AssumeRolePolicyDocument' --profile mlops-dev
```

**Verify:**
- Repository name matches exactly: `repo:USERNAME/REPO:*`
- OIDC provider ARN correct
- Audience is `sts.amazonaws.com`

**Fix:**
```powershell
# Update trust policy
aws iam update-assume-role-policy `
  --role-name GitHubActions-MLOps-Dev `
  --policy-document file://trust-policy-dev.json `
  --profile mlops-dev
```

### Issue: Missing Permissions

**Error:** `AccessDenied: User is not authorized to perform: SERVICE:ACTION`

**Solution:** Add missing policy

```powershell
# Example: Adding EventBridge
aws iam attach-role-policy `
  --role-name GitHubActions-MLOps-Dev `
  --policy-arn arn:aws:iam::aws:policy/AmazonEventBridgeFullAccess `
  --profile mlops-dev
```

### Issue: Malformed Policy JSON

**Error:** `MalformedPolicyDocument: This policy contains invalid Json`

**Solution:** Use inline JSON or fix encoding

See `docs/TROUBLESHOOTING.md#4-malformed-iam-policy-document` for detailed solutions.

---

## Multi-Environment Setup

### Create Roles for All Environments

```powershell
$environments = @("dev", "staging", "production")

foreach ($env in $environments) {
    Write-Host "Creating role for $env..."
    
    aws iam create-role `
        --role-name "GitHubActions-MLOps-$env" `
        --assume-role-policy-document "{\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Principal\":{\"Federated\":\"arn:aws:iam::${accountId}:oidc-provider/token.actions.githubusercontent.com\"},\"Action\":\"sts:AssumeRoleWithWebIdentity\",\"Condition\":{\"StringEquals\":{\"token.actions.githubusercontent.com:aud\":\"sts.amazonaws.com\"},\"StringLike\":{\"token.actions.githubusercontent.com:sub\":\"repo:${githubUsername}/${repoName}:*\"}}}]}" `
        --description "GitHub Actions role for MLOps $env environment" `
        --profile mlops-dev
    
    # Attach all policies
    foreach ($policy in $policies) {
        aws iam attach-role-policy `
            --role-name "GitHubActions-MLOps-$env" `
            --policy-arn $policy `
            --profile mlops-dev
    }
    
    Write-Host "✅ Role GitHubActions-MLOps-$env created"
}
```

### GitHub Secrets for Multi-Environment

```
Settings → Secrets → Actions → New repository secret

Add:
- AWS_ROLE_ARN_DEV: arn:aws:iam::ACCOUNT:role/GitHubActions-MLOps-dev
- AWS_ROLE_ARN_STAGING: arn:aws:iam::ACCOUNT:role/GitHubActions-MLOps-staging
- AWS_ROLE_ARN_PROD: arn:aws:iam::ACCOUNT:role/GitHubActions-MLOps-production
- AWS_REGION: us-east-1
```

---

## Security Best Practices

### 1. Least Privilege

**Development:**
- Use full-access policies for quick iteration
- Easier to troubleshoot permission issues

**Production:**
- Create custom policies with minimum permissions
- Use resource-level permissions
- Add condition keys for region, time, etc.

### 2. Environment Isolation

- **Separate roles** per environment (dev/staging/prod)
- **Different AWS accounts** for production (recommended)
- **Approval gates** for production deployments

### 3. Monitoring

```powershell
# Enable CloudTrail logging
aws cloudtrail create-trail `
  --name mlops-audit-trail `
  --s3-bucket-name mlops-cloudtrail-logs-ACCOUNT `
  --profile mlops-dev

# Enable logging
aws cloudtrail start-logging --name mlops-audit-trail --profile mlops-dev
```

### 4. Regular Audits

```powershell
# List all roles with OIDC trust
aws iam list-roles --query 'Roles[?contains(AssumeRolePolicyDocument.Statement[0].Principal.Federated, `token.actions.githubusercontent.com`)]' --profile mlops-dev

# Check role last used
aws iam get-role --role-name GitHubActions-MLOps-Dev --query 'Role.RoleLastUsed' --profile mlops-dev
```

---

## Related Documentation

- **Setup Guide:** `docs/COMPLETE_SETUP_GUIDE.md` - Full deployment guide
- **Troubleshooting:** `docs/TROUBLESHOOTING.md` - Common issues and solutions
- **Trust Policies:** `docs/TRUST_POLICY_BEST_PRACTICES.md` - Advanced patterns
- **Deployment Issues:** `infrastructure/DEPLOYMENT_ISSUES_AND_FIXES.md` - Real-world fixes

---

## Quick Reference

**Create OIDC + Role + Policies (One Command):**

```powershell
# Set variables
$accountId = aws sts get-caller-identity --query Account --output text --profile mlops-dev
$githubUsername = "YOUR_USERNAME"
$repoName = "mlopsaws"

# Create OIDC provider
aws iam create-open-id-connect-provider `
  --url https://token.actions.githubusercontent.com `
  --client-id-list sts.amazonaws.com `
  --thumbprint-list 6938fd4d98bab03faadb97b34396831e3780aea1 `
  --profile mlops-dev

# Create role
aws iam create-role `
  --role-name GitHubActions-MLOps-Dev `
  --assume-role-policy-document "{\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Principal\":{\"Federated\":\"arn:aws:iam::${accountId}:oidc-provider/token.actions.githubusercontent.com\"},\"Action\":\"sts:AssumeRoleWithWebIdentity\",\"Condition\":{\"StringEquals\":{\"token.actions.githubusercontent.com:aud\":\"sts.amazonaws.com\"},\"StringLike\":{\"token.actions.githubusercontent.com:sub\":\"repo:${githubUsername}/${repoName}:*\"}}}]}" `
  --description "GitHub Actions role for MLOps dev environment" `
  --profile mlops-dev

# Attach all 8 policies
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

# Get role ARN
aws iam get-role --role-name GitHubActions-MLOps-Dev --query 'Role.Arn' --output text --profile mlops-dev
```

---

**Last Updated:** November 4, 2025  
**Maintainer:** MLOps Team  
**Status:** ✅ Production Ready
