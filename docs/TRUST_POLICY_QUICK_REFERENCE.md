# 🔐 Quick Reference: Trust Policy Setup

**Choose Your Setup Based on Use Case:**

---

## 🎓 Learning / Personal Projects

**Use:** Username-based trust policy

**Setup Time:** 5 minutes

**Command:**
```powershell
$accountId = aws sts get-caller-identity --query Account --output text
$username = "your-github-username"

@"
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {"Federated": "arn:aws:iam::${accountId}:oidc-provider/token.actions.githubusercontent.com"},
    "Action": "sts:AssumeRoleWithWebIdentity",
    "Condition": {
      "StringEquals": {"token.actions.githubusercontent.com:aud": "sts.amazonaws.com"},
      "StringLike": {"token.actions.githubusercontent.com:sub": "repo:${username}/mlopsaws:*"}
    }
  }]
}
"@ | Out-File trust-policy.json -Encoding utf8
```

**Pros:**
- ✅ Quick setup
- ✅ Good for learning
- ✅ No organization needed

**Cons:**
- ❌ Must update if username changes
- ❌ Repo could be deleted
- ❌ Not production-ready

---

## 🏢 Production / Team Projects

**Use:** Organization-based trust policy

**Setup Time:** 15 minutes

**Commands:**
```powershell
$accountId = aws sts get-caller-identity --query Account --output text
$orgName = "your-company-org"  # e.g., "acme-corp"

@"
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {"Federated": "arn:aws:iam::${accountId}:oidc-provider/token.actions.githubusercontent.com"},
    "Action": "sts:AssumeRoleWithWebIdentity",
    "Condition": {
      "StringEquals": {"token.actions.githubusercontent.com:aud": "sts.amazonaws.com"},
      "StringLike": {"token.actions.githubusercontent.com:sub": "repo:${orgName}/mlopsaws:*"}
    }
  }]
}
"@ | Out-File trust-policy.json -Encoding utf8
```

**Pros:**
- ✅ No changes when users leave
- ✅ Centralized team management
- ✅ Better security & audit
- ✅ Production-ready

**Cons:**
- ⚠️ Requires GitHub org (free tier OK)

---

## 🔒 High Security / Enterprise

**Use:** Branch-specific + organization trust

**Setup Time:** 20 minutes

**Production Trust (main branch only):**
```powershell
$accountId = aws sts get-caller-identity --query Account --output text
$orgName = "your-company-org"

@"
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {"Federated": "arn:aws:iam::${accountId}:oidc-provider/token.actions.githubusercontent.com"},
    "Action": "sts:AssumeRoleWithWebIdentity",
    "Condition": {
      "StringEquals": {
        "token.actions.githubusercontent.com:aud": "sts.amazonaws.com",
        "token.actions.githubusercontent.com:sub": "repo:${orgName}/mlopsaws:ref:refs/heads/main"
      }
    }
  }]
}
"@ | Out-File trust-policy-prod.json -Encoding utf8
```

**Pros:**
- ✅ Maximum security
- ✅ Only main branch can deploy to prod
- ✅ Prevents unauthorized deployments
- ✅ Compliance-ready

**Cons:**
- ⚠️ More complex setup
- ⚠️ Requires branch strategy

---

## 🆘 What If User Leaves?

### With Username Trust (Personal)

**Impact:** ⚠️ High - Manual work required

**Steps:**
1. Transfer repo to new user
2. Update trust policy (see commands below)
3. Update GitHub secrets
4. Test workflows

**Time:** 20-30 minutes

**Commands:**
```powershell
# Update trust policy
$newUsername = "new-owner"
$accountId = aws sts get-caller-identity --query Account --output text

# Create new policy
@"
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {"Federated": "arn:aws:iam::${accountId}:oidc-provider/token.actions.githubusercontent.com"},
    "Action": "sts:AssumeRoleWithWebIdentity",
    "Condition": {
      "StringEquals": {"token.actions.githubusercontent.com:aud": "sts.amazonaws.com"},
      "StringLike": {"token.actions.githubusercontent.com:sub": "repo:${newUsername}/mlopsaws:*"}
    }
  }]
}
"@ | Out-File trust-policy-new.json -Encoding utf8

# Update role
aws iam update-assume-role-policy `
  --role-name GitHubActions-MLOps-Dev `
  --policy-document file://trust-policy-new.json
```

### With Organization Trust

**Impact:** ✅ Zero - No changes needed!

**Steps:**
1. Remove user from GitHub org team
2. That's it!

**Time:** 1 minute

**Commands:**
```bash
# In GitHub UI:
# Organization → Teams → [team-name] → Remove member

# No AWS changes needed!
```

---

## 📊 Decision Matrix

| Criteria | Username | Organization | Branch-Specific |
|----------|----------|--------------|----------------|
| **Setup Time** | 5 min | 15 min | 20 min |
| **User Leaves Impact** | High | None | None |
| **Team Size** | 1 person | 2+ people | 2+ people |
| **Production Use** | ❌ No | ✅ Yes | ✅ Yes |
| **Security Level** | Low | Medium | High |
| **Maintenance** | High | Low | Low |
| **Cost** | Free | Free | Free |

---

## 🚀 Migration Path

### From Username → Organization

**Zero-downtime migration:**

```powershell
# 1. Create organization (GitHub UI)

# 2. Create NEW role with org trust
aws iam create-role `
  --role-name GitHubActions-MLOps-Dev-V2 `
  --assume-role-policy-document file://trust-policy-org.json

# 3. Update GitHub secret to new role ARN
# (Keep old role running)

# 4. Transfer repo to org
# GitHub UI: Settings → Transfer

# 5. Test workflows

# 6. Delete old role
aws iam delete-role --role-name GitHubActions-MLOps-Dev
```

**Total downtime:** 0 minutes

---

## 📚 Full Documentation

For complete details, see:
- **[Trust Policy Best Practices](./TRUST_POLICY_BEST_PRACTICES.md)** - Comprehensive guide
- **[Complete Setup Guide](./COMPLETE_SETUP_GUIDE.md)** - Full deployment guide

---

**Quick Decision:**
- 🎓 **Learning?** → Username trust
- 🏢 **Team project?** → Organization trust  
- 🔒 **Production?** → Organization + branch-specific trust

**Last Updated:** November 4, 2025
