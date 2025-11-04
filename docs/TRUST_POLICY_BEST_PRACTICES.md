# 🔒 Trust Policy Best Practices - Production-Ready OIDC Setup

**Problem:** Hardcoding usernames in trust policies creates security risks when users leave the organization.

**Solution:** Use organization-based and repository-based trust policies with proper governance.

---

## ❌ The Problem with Username-Based Trust Policies

### Current Approach (NOT RECOMMENDED for Production)

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::123456789012:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringLike": {
          "token.actions.githubusercontent.com:sub": "repo:john-doe/mlopsaws:*"
        }
      }
    }
  ]
}
```

### Issues:

1. **👤 User Leaves:** When John leaves, you need to:
   - Update trust policy
   - Transfer repository ownership
   - Update all references
   - Potential downtime during transition

2. **🔐 Security Risk:** Personal accounts have:
   - No centralized access control
   - No audit trail at org level
   - Harder to enforce MFA/SSO
   - Repository could be deleted

3. **📊 Governance:** Impossible to:
   - Track who has access across projects
   - Enforce compliance policies
   - Centralize security reviews

---

## ✅ Production-Ready Solution: Organization-Based Trust

### Option 1: GitHub Organization Repository (RECOMMENDED)

**Trust Policy:**

```json
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
          "token.actions.githubusercontent.com:sub": "repo:YOUR_ORG_NAME/mlopsaws:*"
        }
      }
    }
  ]
}
```

**Benefits:**

✅ **User-Independent:** Works with `acme-corp/mlopsaws`, not `john-doe/mlopsaws`  
✅ **No Changes When Users Leave:** Repository stays with organization  
✅ **Centralized Access Control:** Manage via GitHub org teams  
✅ **Better Security:** Enforce org-wide SSO, MFA, security policies  
✅ **Audit Trail:** All actions tracked at org level  
✅ **Compliance:** Meet SOC2, ISO27001 requirements

### Option 2: Branch-Specific Access (PRODUCTION SECURITY)

**Limit access to specific branches:**

```json
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
          "token.actions.githubusercontent.com:sub": [
            "repo:YOUR_ORG_NAME/mlopsaws:ref:refs/heads/main",
            "repo:YOUR_ORG_NAME/mlopsaws:ref:refs/heads/develop"
          ]
        }
      }
    }
  ]
}
```

**Security Benefits:**

🔒 **Production Protection:** Only `main` branch can deploy to production  
🔒 **PR Security:** Feature branches can't assume production roles  
🔒 **Blast Radius Reduction:** Compromised branch ≠ compromised production  
🔒 **Compliance:** Meets separation of duties requirements

### Option 3: Environment-Specific Trust (MULTI-ENVIRONMENT)

**Separate trust policies for each environment:**

**trust-policy-dev.json** (Loose for development):
```json
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
          "token.actions.githubusercontent.com:sub": "repo:YOUR_ORG_NAME/mlopsaws:*"
        }
      }
    }
  ]
}
```

**trust-policy-prod.json** (Strict for production):
```json
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
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com",
          "token.actions.githubusercontent.com:sub": "repo:YOUR_ORG_NAME/mlopsaws:ref:refs/heads/main"
        }
      }
    }
  ]
}
```

**Deployment Strategy:**

- **Dev:** Any branch can deploy → Fast iteration
- **Staging:** Only `develop` and `main` → Pre-production validation  
- **Production:** Only `main` branch → Maximum security

---

## 🏢 Migration Path: Personal → Organization

### If You Currently Have Personal Repository

**Step 1: Create GitHub Organization (Free)**

```bash
# Go to: https://github.com/organizations/new
# Choose: "Free" plan
# Organization name: "acme-corp" (your company)
```

**Step 2: Transfer Repository**

```bash
# In your personal repository:
# Settings → General → Danger Zone → Transfer ownership
# New owner: acme-corp
# Repository name: mlopsaws
```

**Result:** Repository moves from `john-doe/mlopsaws` → `acme-corp/mlopsaws`

**Step 3: Update Trust Policy (One-Time)**

```powershell
# Get your AWS account ID
$accountId = aws sts get-caller-identity --query Account --output text

# Create new trust policy with organization
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
          "token.actions.githubusercontent.com:sub": "repo:acme-corp/mlopsaws:*"
        }
      }
    }
  ]
}
"@ | Out-File -FilePath trust-policy-org.json -Encoding utf8

# Update IAM role
aws iam update-assume-role-policy \
  --role-name GitHubActions-MLOps-Dev \
  --policy-document file://trust-policy-org.json
```

**Step 4: Manage Access via Teams**

```bash
# Create teams in GitHub org:
# Settings → Teams → New team

# Example teams:
# - mlops-admins (full access)
# - mlops-developers (read/write)
# - mlops-viewers (read-only)

# Add users to teams (not to repository directly)
# When user leaves: Remove from team (1 click)
# Repository access unchanged!
```

**Result:** User leaves → Remove from team → Zero AWS changes needed! ✅

---

## 🔐 Advanced Security: Conditional Claims

### Option 4: Multi-Condition Trust (ENTERPRISE)

**Enforce multiple security controls:**

```json
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
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com",
          "token.actions.githubusercontent.com:sub": "repo:YOUR_ORG_NAME/mlopsaws:ref:refs/heads/main"
        },
        "StringLike": {
          "token.actions.githubusercontent.com:actor": [
            "deployment-bot",
            "release-manager"
          ]
        }
      }
    }
  ]
}
```

**What This Does:**

🔒 **Repository Check:** Must be from `YOUR_ORG_NAME/mlopsaws`  
🔒 **Branch Check:** Must be from `main` branch  
🔒 **Actor Check:** Must be triggered by specific GitHub users/bots

**Use Case:** Production deployments only by approved accounts

### Option 5: IP-Based Restrictions (EXTRA PARANOID)

**Combine OIDC with IP allowlist:**

```json
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
          "token.actions.githubusercontent.com:sub": "repo:YOUR_ORG_NAME/mlopsaws:*"
        },
        "IpAddress": {
          "aws:SourceIp": [
            "192.0.2.0/24",
            "203.0.113.0/24"
          ]
        }
      }
    }
  ]
}
```

**Note:** GitHub Actions runners have dynamic IPs - use GitHub's IP ranges or self-hosted runners

---

## 📊 Comparison Table

| Approach | Security | Maintenance | User Leaves Impact | Cost |
|----------|----------|-------------|-------------------|------|
| **Personal Username** | ⚠️ Low | 🔴 High | 🔴 Must update policy | Free |
| **Organization Repo** | ✅ Medium | ✅ Low | ✅ No changes needed | Free |
| **Branch-Specific** | ✅ High | ✅ Low | ✅ No changes needed | Free |
| **Environment-Specific** | ✅✅ Very High | ✅ Medium | ✅ No changes needed | Free |
| **Multi-Condition** | ✅✅✅ Extreme | ⚠️ Medium | ✅ No changes needed | Free |

---

## 🚀 Quick Start: Production-Ready Setup

### Recommended for Production (15 minutes)

**1. Create GitHub Organization (if not exists):**

```bash
# Go to: https://github.com/organizations/new
# Name: your-company-name
# Plan: Free (sufficient for most use cases)
```

**2. Create/Transfer Repository:**

```bash
# If new: Create in organization directly
# If existing: Settings → Transfer ownership → Organization

# Result: https://github.com/your-company-name/mlopsaws
```

**3. Create Production-Grade Trust Policies:**

```powershell
# Get AWS account ID
$accountId = aws sts get-caller-identity --query Account --output text
$orgName = "your-company-name"  # Replace with your GitHub org
$repoName = "mlopsaws"

# Function to create trust policy
function New-TrustPolicy {
    param(
        [string]$Environment,
        [string]$BranchFilter = "*"
    )
    
    $subjectClaim = if ($BranchFilter -eq "*") {
        "repo:${orgName}/${repoName}:*"
    } else {
        "repo:${orgName}/${repoName}:ref:refs/heads/${BranchFilter}"
    }
    
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
          "token.actions.githubusercontent.com:sub": "${subjectClaim}"
        }
      }
    }
  ]
}
"@ | Out-File -FilePath "trust-policy-${Environment}.json" -Encoding utf8
}

# Create policies for each environment
New-TrustPolicy -Environment "dev" -BranchFilter "*"          # Any branch
New-TrustPolicy -Environment "staging" -BranchFilter "develop" # Only develop
New-TrustPolicy -Environment "prod" -BranchFilter "main"       # Only main

Write-Host "✅ Trust policies created!"
Write-Host "   - trust-policy-dev.json (any branch)"
Write-Host "   - trust-policy-staging.json (develop only)"
Write-Host "   - trust-policy-prod.json (main only)"
```

**4. Create IAM Roles:**

```powershell
# Dev Environment (any branch can deploy)
aws iam create-role `
  --role-name GitHubActions-MLOps-Dev `
  --assume-role-policy-document file://trust-policy-dev.json `
  --description "GitHub Actions role for MLOps dev - Org: $orgName"

# Staging Environment (develop branch only)
aws iam create-role `
  --role-name GitHubActions-MLOps-Staging `
  --assume-role-policy-document file://trust-policy-staging.json `
  --description "GitHub Actions role for MLOps staging - Org: $orgName"

# Production Environment (main branch only)
aws iam create-role `
  --role-name GitHubActions-MLOps-Prod `
  --assume-role-policy-document file://trust-policy-prod.json `
  --description "GitHub Actions role for MLOps prod - Org: $orgName"

Write-Host "✅ IAM roles created with organization-based trust!"
```

**5. Attach Policies (Least Privilege):**

```powershell
# Instead of AdministratorAccess, use specific permissions
# See LEAST_PRIVILEGE_POLICIES.md for detailed policies

# For now (dev/learning), use broad permissions:
aws iam attach-role-policy `
  --role-name GitHubActions-MLOps-Dev `
  --policy-arn arn:aws:iam::aws:policy/AdministratorAccess

aws iam attach-role-policy `
  --role-name GitHubActions-MLOps-Staging `
  --policy-arn arn:aws:iam::aws:policy/AdministratorAccess

aws iam attach-role-policy `
  --role-name GitHubActions-MLOps-Prod `
  --policy-arn arn:aws:iam::aws:policy/AdministratorAccess
```

**6. Create GitHub Teams:**

```bash
# In GitHub organization → Settings → Teams

# Create teams:
# 1. mlops-admins (full repo access)
# 2. mlops-developers (write access)
# 3. mlops-data-scientists (read + run workflows)
# 4. mlops-viewers (read-only)
```

**7. Test Access:**

```powershell
# In your GitHub Actions workflow, test assuming role:
# .github/workflows/test-oidc.yml

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
          role-to-assume: arn:aws:iam::${{ secrets.AWS_ACCOUNT_ID }}:role/GitHubActions-MLOps-Dev
          aws-region: us-east-1
      
      - name: Test AWS access
        run: |
          aws sts get-caller-identity
          echo "✅ Successfully assumed role!"
```

---

## 🎯 What Happens When User Leaves

### With Username-Based Trust (OLD WAY) ❌

```
1. User "john-doe" leaves company
2. Personal repo "john-doe/mlopsaws" becomes orphaned
3. Need to:
   ✗ Transfer repository ownership (manual)
   ✗ Update trust policy in AWS (manual)
   ✗ Update GitHub secrets (manual)
   ✗ Update documentation (manual)
   ✗ Test new setup (30 min)
4. Potential downtime during transition
5. Risk of access loss if user deletes repo
```

### With Organization-Based Trust (NEW WAY) ✅

```
1. User "john-doe" leaves company
2. GitHub org admin removes user from team
3. That's it! 
   ✓ Repository stays with organization
   ✓ Trust policy unchanged (uses org name)
   ✓ Workflows continue working
   ✓ Zero downtime
   ✓ No AWS changes needed
4. Add new user:
   ✓ Add to appropriate team (1 click)
   ✓ They inherit repo access
   ✓ No AWS changes needed
```

---

## 🔍 Audit & Compliance

### Tracking Access with Organization

**CloudTrail Query:**
```sql
-- Who assumed the role?
SELECT 
  eventTime,
  userIdentity.principalId,
  requestParameters.roleArn,
  sourceIPAddress
FROM cloudtrail_logs
WHERE eventName = 'AssumeRoleWithWebIdentity'
  AND requestParameters.roleArn LIKE '%GitHubActions-MLOps%'
ORDER BY eventTime DESC;
```

**GitHub Audit Log:**
```bash
# Organization owners can see:
# - Who triggered workflows
# - What branches were used
# - When deployments occurred
# - Team membership changes

# Access: Organization → Settings → Audit log
```

**Compliance Benefits:**

✅ **SOC 2:** Centralized access control + audit trail  
✅ **ISO 27001:** Identity federation + least privilege  
✅ **HIPAA:** No long-lived credentials + encryption  
✅ **PCI DSS:** Role-based access + logging

---

## 📚 Summary: Best Practices

### ✅ DO:

1. **Use GitHub Organizations** for all production repositories
2. **Use branch-specific trust** for production environments
3. **Use environment-specific roles** (dev, staging, prod)
4. **Manage access via teams**, not individual users
5. **Enable CloudTrail** for all AssumeRole events
6. **Document** trust policy architecture
7. **Test** OIDC setup in dev before production
8. **Review** trust policies quarterly

### ❌ DON'T:

1. **Don't hardcode usernames** in trust policies
2. **Don't use personal accounts** for production
3. **Don't grant AdministratorAccess** long-term (dev only)
4. **Don't skip branch restrictions** for production
5. **Don't forget to rotate** OIDC trust if org changes
6. **Don't share AWS credentials** (use OIDC only)

---

## 🆘 Migration Help

### I Already Have Username-Based Trust - What Now?

**Zero-Downtime Migration (30 minutes):**

```powershell
# Step 1: Create GitHub organization
# (Skip if you already have one)

# Step 2: Create NEW roles with org-based trust
# (Keep old roles running for now)
aws iam create-role `
  --role-name GitHubActions-MLOps-Dev-V2 `
  --assume-role-policy-document file://trust-policy-org.json

# Step 3: Update GitHub secrets to use new role
# Settings → Secrets → Edit AWS_ROLE_ARN_DEV
# Old: arn:aws:iam::123456789012:role/GitHubActions-MLOps-Dev
# New: arn:aws:iam::123456789012:role/GitHubActions-MLOps-Dev-V2

# Step 4: Transfer repository to organization
# Settings → Transfer ownership

# Step 5: Test workflows with new roles

# Step 6: Delete old roles once confirmed working
aws iam delete-role --role-name GitHubActions-MLOps-Dev
```

**Total downtime:** 0 minutes (blue-green role deployment)

---

## 📖 Additional Resources

- [GitHub OIDC Documentation](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/about-security-hardening-with-openid-connect)
- [AWS IAM OIDC Guide](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_providers_create_oidc.html)
- [GitHub Organizations Guide](https://docs.github.com/en/organizations)
- [Least Privilege IAM Policies](./LEAST_PRIVILEGE_POLICIES.md)

---

**Last Updated:** November 4, 2025  
**Version:** 1.0  
**Status:** Production-Ready ✅
