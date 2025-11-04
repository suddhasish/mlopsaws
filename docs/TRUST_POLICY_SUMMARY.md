# 🎯 Trust Policy Setup - Summary

**Question:** "What if user resigns and leaves the org?"

**Short Answer:** Use **organization-based trust policies** instead of username-based ones.

---

## The Problem

Current default setup uses **personal GitHub username** in trust policy:

```json
"token.actions.githubusercontent.com:sub": "repo:john-doe/mlopsaws:*"
```

**When john-doe leaves:**
- ❌ Repository tied to personal account
- ❌ Must transfer repo ownership
- ❌ Must update AWS trust policy
- ❌ Must update GitHub secrets
- ❌ Potential downtime
- ⏱️ **30-45 minutes of manual work**

---

## The Solution

Use **GitHub organization** instead:

```json
"token.actions.githubusercontent.com:sub": "repo:acme-corp/mlopsaws:*"
```

**When any user leaves:**
- ✅ Repository stays with organization
- ✅ Remove user from GitHub team (1 click)
- ✅ No AWS changes needed
- ✅ Zero downtime
- ⏱️ **10 seconds to remove user**

---

## Quick Decision Guide

### For Learning/Testing
**Use:** Username-based trust  
**Reason:** Quick setup, easy to start  
**Plan:** Migrate to organization before production  

### For Production/Teams
**Use:** Organization-based trust  
**Reason:** No changes when users leave  
**Setup:** 15 minutes (one-time)  

### For Enterprise/High Security
**Use:** Organization + branch-specific trust  
**Reason:** Maximum security + audit control  
**Setup:** 20 minutes (one-time)  

---

## How to Implement

### Option 1: New Setup (Start with Organization)

```powershell
# 1. Create GitHub org (free): https://github.com/organizations/new
# 2. Create repo in org: https://github.com/YOUR_ORG/repositories/new

# 3. Create trust policy
$accountId = aws sts get-caller-identity --query Account --output text
$orgName = "your-org-name"

@"
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {
      "Federated": "arn:aws:iam::${accountId}:oidc-provider/token.actions.githubusercontent.com"
    },
    "Action": "sts:AssumeRoleWithWebIdentity",
    "Condition": {
      "StringEquals": {"token.actions.githubusercontent.com:aud": "sts.amazonaws.com"},
      "StringLike": {"token.actions.githubusercontent.com:sub": "repo:${orgName}/mlopsaws:*"}
    }
  }]
}
"@ | Out-File trust-policy.json -Encoding utf8

# 4. Create IAM role
aws iam create-role `
  --role-name GitHubActions-MLOps-Dev `
  --assume-role-policy-document file://trust-policy.json
```

### Option 2: Migrate Existing Setup (Zero Downtime)

```powershell
# 1. Create org (if not exists)
# 2. Create NEW role with org trust (keep old role running)
aws iam create-role `
  --role-name GitHubActions-MLOps-Dev-V2 `
  --assume-role-policy-document file://trust-policy-org.json

# 3. Update GitHub secret to new role ARN
# 4. Transfer repo to org in GitHub UI
# 5. Test workflows
# 6. Delete old role
aws iam delete-role --role-name GitHubActions-MLOps-Dev
```

---

## User Lifecycle

### When New User Joins
**Username approach:** 20-30 minutes (create IAM user, credentials, access)  
**Organization approach:** 30 seconds (add to GitHub team)

### When User Leaves
**Username approach:** 30-45 minutes (transfer, update, test)  
**Organization approach:** 10 seconds (remove from team)

### When User Changes Role
**Username approach:** 15-20 minutes (update permissions)  
**Organization approach:** 10 seconds (move to different team)

---

## Documentation

**Complete guides created:**

1. **[TRUST_POLICY_BEST_PRACTICES.md](./TRUST_POLICY_BEST_PRACTICES.md)**
   - Comprehensive guide to all approaches
   - Migration strategies
   - Security levels
   - Compliance considerations

2. **[TRUST_POLICY_QUICK_REFERENCE.md](./TRUST_POLICY_QUICK_REFERENCE.md)**
   - Quick decision matrix
   - Copy-paste commands
   - Common scenarios

3. **[TRUST_POLICY_VISUAL_GUIDE.md](./TRUST_POLICY_VISUAL_GUIDE.md)**
   - Visual diagrams
   - User lifecycle flows
   - Decision trees

4. **[COMPLETE_SETUP_GUIDE.md](./COMPLETE_SETUP_GUIDE.md)** (Updated)
   - Added warning about username-based trust
   - Added troubleshooting section for user departures
   - Links to best practices

---

## Updated Files

✅ `docs/TRUST_POLICY_BEST_PRACTICES.md` - NEW  
✅ `docs/TRUST_POLICY_QUICK_REFERENCE.md` - NEW  
✅ `docs/TRUST_POLICY_VISUAL_GUIDE.md` - NEW  
✅ `docs/COMPLETE_SETUP_GUIDE.md` - UPDATED (added warnings)  
✅ `docs/README.md` - UPDATED (added security note)  

---

## Key Takeaways

1. **Personal username in trust policy = Manual work when user leaves**
2. **Organization name in trust policy = Zero changes when user leaves**
3. **GitHub organizations are FREE** (no cost to implement)
4. **Migration takes 20 minutes** with zero downtime
5. **For production, ALWAYS use organization-based trust**

---

## Next Steps

**For New Projects:**
→ Start with organization-based trust from day 1  
→ See: [TRUST_POLICY_QUICK_REFERENCE.md](./TRUST_POLICY_QUICK_REFERENCE.md)

**For Existing Projects:**
→ Migrate to organization when ready for production  
→ See: [TRUST_POLICY_BEST_PRACTICES.md](./TRUST_POLICY_BEST_PRACTICES.md) → Section "Migration Path"

**For Learning:**
→ Username-based is OK for now  
→ Plan to migrate before production deployment

---

**Last Updated:** November 4, 2025  
**Status:** Production-Ready Documentation ✅
