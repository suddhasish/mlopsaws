# 🔐 Trust Policy Setup - Visual Guide

## The Problem

```
┌─────────────────────────────────────────────────────────────┐
│         WHAT HAPPENS WHEN USER LEAVES?                      │
└─────────────────────────────────────────────────────────────┘

SCENARIO: John Doe leaves the company

┌─────────────────────────────────────────────────────────────┐
│  OPTION 1: Username-Based Trust (Current Default)          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Trust Policy:                                              │
│  "repo:john-doe/mlopsaws:*"                                 │
│                                                             │
│  ❌ PROBLEMS:                                               │
│  1. Repository ownership tied to user                       │
│  2. Must transfer repo to new owner                         │
│  3. Must update trust policy in AWS                         │
│  4. Must update GitHub secrets                              │
│  5. Potential downtime during transition                    │
│  6. Risk of repo deletion if user angry                     │
│                                                             │
│  ⏱️ TIME TO FIX: 30 minutes                                 │
│  🔴 DOWNTIME: Possible during transition                    │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  OPTION 2: Organization-Based Trust (Recommended)           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Trust Policy:                                              │
│  "repo:acme-corp/mlopsaws:*"                                │
│                                                             │
│  ✅ SOLUTION:                                               │
│  1. Repository owned by organization                        │
│  2. Remove user from team (1 click)                         │
│  3. No AWS changes needed                                   │
│  4. No GitHub secret changes needed                         │
│  5. Zero downtime                                           │
│  6. Repository stays with company                           │
│                                                             │
│  ⏱️ TIME TO FIX: 1 minute                                   │
│  🟢 DOWNTIME: Zero                                          │
└─────────────────────────────────────────────────────────────┘
```

---

## The Solution: Organization-Based Trust

### Architecture Comparison

```
┌─────────────────────────────────────────────────────────────┐
│  USERNAME-BASED (Not Recommended for Production)            │
└─────────────────────────────────────────────────────────────┘

GitHub Personal Account
    │
    └── john-doe/mlopsaws (Repository)
            │
            ├── Workflow triggers
            │
            ▼
    AWS IAM Role: GitHubActions-MLOps-Dev
        Trust Policy:
        "repo:john-doe/mlopsaws:*"
            │
            ▼
        ❌ If john-doe leaves:
           - Repo orphaned
           - Trust policy broken
           - Manual updates required


┌─────────────────────────────────────────────────────────────┐
│  ORGANIZATION-BASED (Production-Ready) ✅                    │
└─────────────────────────────────────────────────────────────┘

GitHub Organization: acme-corp
    │
    ├── Teams
    │   ├── mlops-admins (John, Sarah)
    │   ├── mlops-developers (Mike, Lisa)
    │   └── mlops-viewers (Others)
    │
    └── acme-corp/mlopsaws (Repository)
            │
            ├── Workflow triggers
            │
            ▼
    AWS IAM Role: GitHubActions-MLOps-Dev
        Trust Policy:
        "repo:acme-corp/mlopsaws:*"
            │
            ▼
        ✅ If John leaves:
           - Remove from team
           - Repository stays
           - Trust policy unchanged
           - Zero AWS changes
```

---

## Step-by-Step Visual Guide

### Scenario 1: New Setup (Starting Fresh)

```
START
  │
  ├─ Are you learning/testing? ─── YES ──► Use USERNAME trust
  │                                         (Quick setup)
  │                                         (Update later for production)
  │
  └─ Are you in production/team? ─── YES ──► Use ORGANIZATION trust
                                              (Follow steps below)

ORGANIZATION SETUP:
┌──────────────────────────────────────────────────────────┐
│ Step 1: Create GitHub Organization (5 min)              │
│ https://github.com/organizations/new                    │
│ - Name: your-company-name                               │
│ - Plan: Free (sufficient)                               │
└──────────────────────────────────────────────────────────┘
                    ▼
┌──────────────────────────────────────────────────────────┐
│ Step 2: Create Repository in Organization (2 min)       │
│ https://github.com/organizations/YOUR-ORG/repositories  │
│ - Click "New repository"                                │
│ - Name: mlopsaws                                        │
│ - Private/Public: Your choice                           │
└──────────────────────────────────────────────────────────┘
                    ▼
┌──────────────────────────────────────────────────────────┐
│ Step 3: Create Teams (3 min)                            │
│ Organization → Settings → Teams                         │
│ - mlops-admins (full access)                            │
│ - mlops-developers (write)                              │
│ - mlops-viewers (read)                                  │
└──────────────────────────────────────────────────────────┘
                    ▼
┌──────────────────────────────────────────────────────────┐
│ Step 4: Create Trust Policy with Org Name (5 min)       │
│ PowerShell:                                             │
│ $orgName = "your-company-name"                          │
│ # Creates: trust-policy.json                            │
│ # Contains: "repo:your-company-name/mlopsaws:*"         │
└──────────────────────────────────────────────────────────┘
                    ▼
┌──────────────────────────────────────────────────────────┐
│ Step 5: Create IAM Roles (5 min)                        │
│ aws iam create-role \                                   │
│   --role-name GitHubActions-MLOps-Dev \                 │
│   --assume-role-policy-document file://trust-policy.json│
└──────────────────────────────────────────────────────────┘
                    ▼
                  DONE! ✅
```

### Scenario 2: Migration (Existing Personal Setup)

```
CURRENT STATE: john-doe/mlopsaws
                    │
                    ▼
GOAL: acme-corp/mlopsaws

MIGRATION PATH (Zero Downtime):
┌──────────────────────────────────────────────────────────┐
│ Step 1: Create Organization (if not exists) (5 min)     │
└──────────────────────────────────────────────────────────┘
                    ▼
┌──────────────────────────────────────────────────────────┐
│ Step 2: Create NEW IAM Role with Org Trust (5 min)      │
│ Role: GitHubActions-MLOps-Dev-V2                        │
│ Trust: "repo:acme-corp/mlopsaws:*"                      │
│ (Keep old role running!)                                │
└──────────────────────────────────────────────────────────┘
                    ▼
┌──────────────────────────────────────────────────────────┐
│ Step 3: Update GitHub Secret (2 min)                    │
│ AWS_ROLE_ARN_DEV → Point to new role ARN               │
│ (Old role still exists as backup)                       │
└──────────────────────────────────────────────────────────┘
                    ▼
┌──────────────────────────────────────────────────────────┐
│ Step 4: Transfer Repository (5 min)                     │
│ GitHub → Settings → Transfer ownership                  │
│ New owner: acme-corp                                    │
│ Repo becomes: acme-corp/mlopsaws                        │
└──────────────────────────────────────────────────────────┘
                    ▼
┌──────────────────────────────────────────────────────────┐
│ Step 5: Test Workflow (3 min)                           │
│ Push to develop → Verify deployment works               │
└──────────────────────────────────────────────────────────┘
                    ▼
┌──────────────────────────────────────────────────────────┐
│ Step 6: Delete Old Role (1 min)                         │
│ aws iam delete-role --role-name GitHubActions-MLOps-Dev │
│ (Original username-based role)                          │
└──────────────────────────────────────────────────────────┘
                    ▼
              MIGRATED! ✅
    Total Downtime: 0 minutes
```

---

## Security Levels Comparison

```
┌─────────────────────────────────────────────────────────────┐
│  SECURITY LEVEL 1: Basic (Learning)                        │
├─────────────────────────────────────────────────────────────┤
│  Trust Policy:                                              │
│  "repo:john-doe/mlopsaws:*"                                 │
│                                                             │
│  Allows: Any branch in john-doe's repo                      │
│  Security: ⚠️ Low                                           │
│  Use for: Learning, personal projects                       │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  SECURITY LEVEL 2: Organization (Production)                │
├─────────────────────────────────────────────────────────────┤
│  Trust Policy:                                              │
│  "repo:acme-corp/mlopsaws:*"                                │
│                                                             │
│  Allows: Any branch in organization's repo                  │
│  Security: ✅ Medium                                        │
│  Use for: Team projects, production                         │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  SECURITY LEVEL 3: Branch-Specific (High Security)          │
├─────────────────────────────────────────────────────────────┤
│  Trust Policy (Dev):                                        │
│  "repo:acme-corp/mlopsaws:*"                                │
│                                                             │
│  Trust Policy (Prod):                                       │
│  "repo:acme-corp/mlopsaws:ref:refs/heads/main"              │
│                                                             │
│  Allows: Only main branch can deploy to production         │
│  Security: ✅✅ High                                         │
│  Use for: Enterprise, regulated industries                  │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  SECURITY LEVEL 4: Multi-Condition (Maximum)                │
├─────────────────────────────────────────────────────────────┤
│  Trust Policy:                                              │
│  - Repo: "acme-corp/mlopsaws"                               │
│  - Branch: "main"                                           │
│  - Actor: "deployment-bot" OR "release-manager"             │
│                                                             │
│  Allows: Only specific users from main branch               │
│  Security: ✅✅✅ Maximum                                     │
│  Use for: Financial, healthcare, critical systems           │
└─────────────────────────────────────────────────────────────┘
```

---

## User Lifecycle Management

```
┌─────────────────────────────────────────────────────────────┐
│  EVENT: New Developer Joins                                │
└─────────────────────────────────────────────────────────────┘

USERNAME-BASED:                   ORGANIZATION-BASED:
❌ Complex                        ✅ Simple

1. Create IAM user in AWS         1. Add to GitHub team
2. Generate access keys              └── Done! (30 seconds)
3. Share credentials securely
4. Update trust policy?           AWS: No changes needed
5. Grant repo access              Workflows: Work immediately
                                  Security: Inherit team permissions
⏱️ Time: 20-30 minutes            ⏱️ Time: 30 seconds


┌─────────────────────────────────────────────────────────────┐
│  EVENT: Developer Changes Teams                            │
└─────────────────────────────────────────────────────────────┘

USERNAME-BASED:                   ORGANIZATION-BASED:
❌ Complex                        ✅ Simple

1. Revoke old repo access         1. Move between teams
2. Grant new repo access             └── Done! (10 seconds)
3. Update IAM permissions?
4. Verify workflows still work    AWS: No changes needed
                                  Permissions: Auto-updated
⏱️ Time: 15-20 minutes            ⏱️ Time: 10 seconds


┌─────────────────────────────────────────────────────────────┐
│  EVENT: Developer Leaves Company                           │
└─────────────────────────────────────────────────────────────┘

USERNAME-BASED:                   ORGANIZATION-BASED:
❌ Complex                        ✅ Simple

1. Transfer repo ownership        1. Remove from team
2. Update trust policy               └── Done! (10 seconds)
3. Update GitHub secrets
4. Verify all workflows           Repository: Stays with org
5. Update documentation           Trust policy: Unchanged
6. Test deployments               Workflows: Keep working
                                  Documentation: No changes
⏱️ Time: 30-45 minutes            ⏱️ Time: 10 seconds
🔴 Risk: Downtime possible        🟢 Risk: Zero


┌─────────────────────────────────────────────────────────────┐
│  EVENT: Security Audit                                      │
└─────────────────────────────────────────────────────────────┘

USERNAME-BASED:                   ORGANIZATION-BASED:
❌ Manual                         ✅ Automated

1. List all personal repos        1. Query org audit log
2. Check each trust policy           └── Centralized view
3. Verify access for each user
4. Manual reconciliation          GitHub: Shows all activity
                                  AWS CloudTrail: Shows role usage
⏱️ Time: 2-4 hours                Team Access: Clear hierarchy
                                  
                                  ⏱️ Time: 15 minutes
```

---

## Cost Comparison

```
┌─────────────────────────────────────────────────────────────┐
│  COST ANALYSIS                                              │
└─────────────────────────────────────────────────────────────┘

                        USERNAME        ORGANIZATION
GitHub Account          FREE            FREE
GitHub Organization     N/A             FREE (public/small teams)
AWS IAM OIDC           FREE            FREE
AWS IAM Roles          FREE            FREE
GitHub Actions Minutes  2000/mo FREE    2000/mo FREE

HIDDEN COSTS:
Developer Time         HIGH            LOW
  - Setup:             2 hrs           1 hr
  - User onboarding:   30 min          30 sec
  - User offboarding:  45 min          10 sec
  - Maintenance:       5 hrs/yr        30 min/yr

Downtime Risk          MEDIUM          NONE
Security Risk          MEDIUM          LOW
Compliance Overhead    HIGH            LOW

TOTAL COST (Annual):
  - Cash:              $0              $0
  - Time:              ~10 hrs         ~2 hrs
  - Risk:              $$              $
```

---

## Decision Tree

```
                        START
                          │
                          ▼
                Is this for production?
                          │
              ┌───────────┴───────────┐
              │                       │
             YES                     NO
              │                       │
              ▼                       ▼
    Do you have a team?      Just learning?
              │                       │
      ┌───────┴───────┐              ▼
     YES             NO          USERNAME-BASED
      │               │          ✅ Quick setup
      ▼               │          ⚠️ Migrate later
  ORGANIZATION        │
  ✅ Recommended      │
      │               │
      ▼               ▼
  High security   Create org now
  required?       (free, easy)
      │               │
  ┌───┴───┐          │
 YES     NO           │
  │       │           │
  ▼       ▼           ▼
BRANCH  ORG        ORG-BASED
SPECIFIC-BASED     ✅ Future-proof
✅ Maximum
  security


RECOMMENDATIONS:
┌────────────────────────────────────────┐
│ Learning/Testing:                      │
│ → USERNAME-BASED                       │
│   (Migrate to org before production)   │
├────────────────────────────────────────┤
│ Team/Production (2+ people):           │
│ → ORGANIZATION-BASED                   │
│   (Setup org from day 1)               │
├────────────────────────────────────────┤
│ Enterprise/Regulated:                  │
│ → ORGANIZATION + BRANCH-SPECIFIC       │
│   (Maximum security)                   │
└────────────────────────────────────────┘
```

---

## Quick Commands

### Create Organization Trust Policy

```powershell
$accountId = aws sts get-caller-identity --query Account --output text
$orgName = "YOUR_ORG_NAME"  # e.g., acme-corp

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
"@ | Out-File trust-policy-org.json -Encoding utf8
```

### Update Existing Role

```powershell
aws iam update-assume-role-policy `
  --role-name GitHubActions-MLOps-Dev `
  --policy-document file://trust-policy-org.json
```

---

**See Full Documentation:**
- [Trust Policy Best Practices](./TRUST_POLICY_BEST_PRACTICES.md)
- [Quick Reference](./TRUST_POLICY_QUICK_REFERENCE.md)

**Last Updated:** November 4, 2025
