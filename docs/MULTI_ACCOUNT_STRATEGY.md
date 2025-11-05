# Multi-Account Strategy for MLOps AWS SageMaker

**Status:** Optional Enhancement - Not Required for Current Setup  
**Complexity:** High  
**Timeline:** 2-3 days setup  
**When to Implement:** When you have >3 team members or need production isolation

---

## Your Current Organization Snapshot (as of Nov 4, 2025)

Based on your AWS CLI outputs, here’s your exact current structure:

- Organization ID: o-l1f68to8ko
- Root ID: r-2ddd
- Feature Set: ALL (All org features enabled)
- Available Policy Types (Org): SERVICE_CONTROL_POLICY = ENABLED
- Management Account (aka Master):
  - Account ID: 891807086260
  - Name: suddha25
  - Email: suddhasishk@gmail.com
  - ARN: arn:aws:organizations::891807086260:account/o-l1f68to8ko/891807086260
- Accounts in Organization (1 total):
  - 891807086260 (Status: ACTIVE, JoinedMethod: INVITED)
- Root PolicyTypes: [] (No policy types enabled at the Root yet)

Notes:
- SERVICE_CONTROL_POLICY is enabled at the Organization level, but not yet enabled at the Root (PolicyTypes is empty). If you plan to use SCPs, enable them at the root (see commands below).
- Currently there are no member accounts (only the management account exists in the org).

### Quick Commands (PowerShell)

```powershell
# Identity & Org
aws sts get-caller-identity --profile mlops-dev
aws organizations describe-organization --profile mlops-dev
aws organizations list-roots --profile mlops-dev
aws organizations list-accounts --profile mlops-dev

# (Optional) List Organizational Units under the Root
$rootId = "r-2ddd"
aws organizations list-organizational-units-for-parent `
  --parent-id $rootId `
  --profile mlops-dev

# (Optional) Enable Service Control Policies at Root (be cautious)
# This is safe if you have no SCPs yet; it simply allows SCPs to apply to entities under the root.
aws organizations enable-policy-type `
  --root-id $rootId `
  --policy-type SERVICE_CONTROL_POLICY `
  --profile mlops-dev

# (Optional) List policies attached to the Root (after enabling)
aws organizations list-policies-for-target `
  --target-id $rootId `
  --filter SERVICE_CONTROL_POLICY `
  --profile mlops-dev
```

### Recommended Next Steps

1. Decide if you want to keep a single-account setup (recommended for now) or expand to dev/staging/prod accounts.
2. If you plan to use SCPs later, enable them at the Root now (no impact until you attach specific SCPs).
3. When ready, follow “Implementation Steps” below to create additional accounts and OUs.

---

## When to Use Multi-Account

### ✅ Implement When:

1. **Team Size**: >3 engineers working simultaneously
2. **Production Criticality**: ML models serve production traffic
3. **Compliance**: SOC2, HIPAA, PCI-DSS requirements
4. **Cost Attribution**: Need separate billing per environment
5. **Security**: Want blast radius isolation (dev mistakes don't affect prod)

### ❌ Don't Implement When:

1. **Solo Developer**: Unnecessary complexity for 1-2 people
2. **Proof of Concept**: Single account with workspaces is faster
3. **Limited Budget**: Managing 3+ accounts has overhead
4. **Simple Use Case**: Just learning MLOps

---

## Current Setup vs Multi-Account

### Current: Single Account Multi-Environment

```
AWS Account 891807086260
├── Dev Environment (us-east-1)
│   ├── S3: mlops-diabetes-dev-891807086260
│   ├── SageMaker Endpoints: mlops-diabetes-dev
│   └── IAM Roles: *-dev
├── Staging Environment (us-east-1)
│   ├── S3: mlops-diabetes-staging-891807086260
│   └── SageMaker Endpoints: mlops-diabetes-staging
└── Production Environment (us-east-1)
    ├── S3: mlops-diabetes-production-891807086260
    └── SageMaker Endpoints: mlops-diabetes-production
```

**Pros:**
- ✅ Simple to manage
- ✅ Single bill
- ✅ Fast iteration
- ✅ No cross-account complexity

**Cons:**
- ❌ Dev errors can affect prod
- ❌ Hard to track costs per environment
- ❌ IAM permissions overlap

### Recommended: Multi-Account Strategy

```
AWS Organization
├── Management Account (000000000000)
│   ├── AWS Organizations
│   ├── CloudTrail (organization trail)
│   └── GitHub Actions OIDC Provider
│
├── MLOps-Dev Account (111111111111)
│   ├── Full SageMaker access
│   ├── Experimental features enabled
│   ├── Auto-shutdown: 7 PM weekdays
│   └── Budget: $50/month
│
├── MLOps-Staging Account (222222222222)
│   ├── Production-like configuration
│   ├── Integration testing
│   ├── Model validation
│   └── Budget: $100/month
│
└── MLOps-Production Account (333333333333)
    ├── Locked-down IAM policies
    ├── Manual approval for deployments
    ├── 99.9% SLA monitoring
    └── Budget: $500/month
```

**Pros:**
- ✅ Complete isolation (dev can't break prod)
- ✅ Separate billing and cost tracking
- ✅ Environment-specific IAM policies
- ✅ Compliance-friendly (separate audit trails)
- ✅ Service limits per account (no quota conflicts)

**Cons:**
- ❌ More complex setup (2-3 days)
- ❌ Cross-account IAM roles needed
- ❌ Multiple state backends
- ❌ Higher learning curve

---

## Implementation Steps

### Phase 1: AWS Organization Setup (1 hour)

**1. Create AWS Organization:**

```powershell
# In your current account (becomes Management Account)
aws organizations create-organization --feature-set ALL --profile mlops-dev

# Verify
aws organizations describe-organization --profile mlops-dev
```

**2. Create Member Accounts:**

```powershell
# Create Dev Account
aws organizations create-account `
  --email mlops-dev@yourdomain.com `
  --account-name "MLOps-Dev" `
  --profile mlops-dev

# Create Staging Account
aws organizations create-account `
  --email mlops-staging@yourdomain.com `
  --account-name "MLOps-Staging" `
  --profile mlops-dev

# Create Production Account
aws organizations create-account `
  --email mlops-production@yourdomain.com `
  --account-name "MLOps-Production" `
  --profile mlops-dev

# Check status (repeat until SUCCEEDED)
aws organizations list-accounts --profile mlops-dev
```

**3. Create Organizational Units:**

```powershell
# Create MLOps OU
$rootId = aws organizations list-roots --query 'Roots[0].Id' --output text --profile mlops-dev

aws organizations create-organizational-unit `
  --parent-id $rootId `
  --name "MLOps" `
  --profile mlops-dev

# Move accounts to OU
$ouId = aws organizations list-organizational-units-for-parent --parent-id $rootId --query 'OrganizationalUnits[?Name==`MLOps`].Id' --output text --profile mlops-dev

aws organizations move-account --account-id 111111111111 --source-parent-id $rootId --destination-parent-id $ouId --profile mlops-dev
# Repeat for staging and production
```

---

### Phase 2: Cross-Account IAM Setup (2 hours)

**1. Create Cross-Account Role in Each Member Account:**

Create `infrastructure/iam/cross-account-role.json`:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::000000000000:root"
      },
      "Action": "sts:AssumeRole",
      "Condition": {
        "StringEquals": {
          "sts:ExternalId": "github-actions-mlops"
        }
      }
    }
  ]
}
```

**2. Create Role in Each Account:**

```powershell
# Assume role in Dev account
$devAccountId = "111111111111"

aws iam create-role `
  --role-name GitHubActions-CrossAccount-Terraform `
  --assume-role-policy-document file://infrastructure/iam/cross-account-role.json `
  --profile mlops-dev-account  # Configure this profile first

# Attach same 10 policies as current setup
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
foreach ($policy in $policies) {
    aws iam attach-role-policy --role-name GitHubActions-CrossAccount-Terraform --policy-arn $policy --profile mlops-dev-account
}

# Repeat for staging and production accounts
```

---

### Phase 3: Terraform Multi-Account Structure

**1. Update Directory Structure:**

```
infrastructure/terraform/
├── backend.tf
├── versions.tf
├── accounts/
│   ├── management/
│   │   ├── main.tf (OIDC provider only)
│   │   └── backend.tf
│   ├── dev/
│   │   ├── main.tf
│   │   ├── backend.tf (separate S3 bucket)
│   │   └── terraform.tfvars
│   ├── staging/
│   │   ├── main.tf
│   │   ├── backend.tf
│   │   └── terraform.tfvars
│   └── production/
│       ├── main.tf
│       ├── backend.tf
│       └── terraform.tfvars
└── modules/ (shared across accounts)
```

**2. Create Account-Specific Backend:**

`infrastructure/terraform/accounts/dev/backend.tf`:

```hcl
terraform {
  backend "s3" {
    bucket         = "mlops-terraform-state-dev-111111111111"
    key            = "mlops/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "mlops-terraform-locks-dev"
    encrypt        = true
  }
}
```

**3. Update Provider for Cross-Account:**

`infrastructure/terraform/accounts/dev/main.tf`:

```hcl
terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.region

  # Assume cross-account role
  assume_role {
    role_arn     = "arn:aws:iam::111111111111:role/GitHubActions-CrossAccount-Terraform"
    session_name = "GitHubActions-Terraform-Dev"
    external_id  = "github-actions-mlops"
  }

  default_tags {
    tags = {
      Project     = var.project_name
      Environment = "dev"
      ManagedBy   = "Terraform"
      Account     = "MLOps-Dev"
    }
  }
}

# Use existing modules
module "s3" {
  source = "../../modules/s3"
  # ... same as current setup
}

module "sagemaker" {
  source = "../../modules/sagemaker"
  # ... same as current setup
}

# ... etc
```

---

### Phase 4: GitHub Actions Multi-Account Workflow

**Update `.github/workflows/terraform.yml`:**

```yaml
name: Terraform Multi-Account

on:
  push:
    branches: [main]
    paths:
      - 'infrastructure/terraform/**'
  pull_request:
    branches: [main]
    paths:
      - 'infrastructure/terraform/**'

permissions:
  id-token: write
  contents: read

jobs:
  terraform-dev:
    name: Deploy to Dev Account
    runs-on: ubuntu-latest
    environment: dev
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Configure AWS credentials (Management Account)
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::000000000000:role/GitHubActions-MLOps-Management
          aws-region: us-east-1
      
      - name: Assume Dev Account Role
        run: |
          CREDENTIALS=$(aws sts assume-role \
            --role-arn arn:aws:iam::111111111111:role/GitHubActions-CrossAccount-Terraform \
            --role-session-name GitHubActions-Dev \
            --external-id github-actions-mlops \
            --query 'Credentials.[AccessKeyId,SecretAccessKey,SessionToken]' \
            --output text)
          
          echo "AWS_ACCESS_KEY_ID=$(echo $CREDENTIALS | cut -f1)" >> $GITHUB_ENV
          echo "AWS_SECRET_ACCESS_KEY=$(echo $CREDENTIALS | cut -f2)" >> $GITHUB_ENV
          echo "AWS_SESSION_TOKEN=$(echo $CREDENTIALS | cut -f3)" >> $GITHUB_ENV
      
      - name: Terraform Init (Dev)
        working-directory: infrastructure/terraform/accounts/dev
        run: terraform init
      
      - name: Terraform Plan (Dev)
        working-directory: infrastructure/terraform/accounts/dev
        run: terraform plan -out=tfplan
      
      - name: Terraform Apply (Dev)
        if: github.ref == 'refs/heads/main'
        working-directory: infrastructure/terraform/accounts/dev
        run: terraform apply -auto-approve tfplan

  terraform-staging:
    name: Deploy to Staging Account
    needs: terraform-dev
    runs-on: ubuntu-latest
    environment: staging
    if: github.ref == 'refs/heads/main'
    
    steps:
      # Similar to dev, but for staging account
      - uses: actions/checkout@v4
      
      - name: Configure AWS credentials (Management Account)
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::000000000000:role/GitHubActions-MLOps-Management
          aws-region: us-east-1
      
      - name: Assume Staging Account Role
        run: |
          CREDENTIALS=$(aws sts assume-role \
            --role-arn arn:aws:iam::222222222222:role/GitHubActions-CrossAccount-Terraform \
            --role-session-name GitHubActions-Staging \
            --external-id github-actions-mlops \
            --query 'Credentials.[AccessKeyId,SecretAccessKey,SessionToken]' \
            --output text)
          
          echo "AWS_ACCESS_KEY_ID=$(echo $CREDENTIALS | cut -f1)" >> $GITHUB_ENV
          echo "AWS_SECRET_ACCESS_KEY=$(echo $CREDENTIALS | cut -f2)" >> $GITHUB_ENV
          echo "AWS_SESSION_TOKEN=$(echo $CREDENTIALS | cut -f3)" >> $GITHUB_ENV
      
      - name: Terraform Apply (Staging)
        working-directory: infrastructure/terraform/accounts/staging
        run: |
          terraform init
          terraform apply -auto-approve

  terraform-production:
    name: Deploy to Production Account
    needs: terraform-staging
    runs-on: ubuntu-latest
    environment: production  # Requires manual approval in GitHub
    if: github.ref == 'refs/heads/main'
    
    steps:
      # Similar to staging, but for production account
      - uses: actions/checkout@v4
      
      - name: Configure AWS credentials (Management Account)
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::000000000000:role/GitHubActions-MLOps-Management
          aws-region: us-east-1
      
      - name: Assume Production Account Role
        run: |
          CREDENTIALS=$(aws sts assume-role \
            --role-arn arn:aws:iam::333333333333:role/GitHubActions-CrossAccount-Terraform \
            --role-session-name GitHubActions-Production \
            --external-id github-actions-mlops \
            --query 'Credentials.[AccessKeyId,SecretAccessKey,SessionToken]' \
            --output text)
          
          echo "AWS_ACCESS_KEY_ID=$(echo $CREDENTIALS | cut -f1)" >> $GITHUB_ENV
          echo "AWS_SECRET_ACCESS_KEY=$(echo $CREDENTIALS | cut -f2)" >> $GITHUB_ENV
          echo "AWS_SESSION_TOKEN=$(echo $CREDENTIALS | cut -f3)" >> $GITHUB_ENV
      
      - name: Terraform Apply (Production)
        working-directory: infrastructure/terraform/accounts/production
        run: |
          terraform init
          terraform apply -auto-approve
```

---

## Cost Comparison

### Current Single Account:
- **Dev**: $20-40/month
- **Staging**: $30-60/month (if deployed)
- **Production**: $100-300/month (if deployed)
- **Total**: ~$150-400/month

### Multi-Account:
- **Management Account**: ~$5/month (CloudTrail only)
- **Dev Account**: $20-40/month
- **Staging Account**: $30-60/month
- **Production Account**: $100-300/month
- **Organization Overhead**: $10-20/month (additional CloudTrail, Config)
- **Total**: ~$165-425/month

**Difference**: +$15-25/month (~10% overhead)

---

## Decision Matrix

| Factor | Single Account | Multi-Account | Winner |
|--------|---------------|---------------|--------|
| **Setup Time** | 1 hour | 2-3 days | Single ⭐ |
| **Complexity** | Low | High | Single ⭐ |
| **Security Isolation** | Medium | High | Multi ⭐ |
| **Cost Tracking** | Hard | Easy | Multi ⭐ |
| **Blast Radius** | High | Low | Multi ⭐ |
| **Compliance** | Medium | High | Multi ⭐ |
| **Team Collaboration** | Medium | High | Multi ⭐ |
| **Cost** | Lower | +10% | Single ⭐ |

---

## Recommendation

### For Your Current Setup (Solo/Small Team):

**✅ Stay with Single Account Multi-Environment**

**Reasons:**
1. You're currently in learning/POC phase
2. Single developer workflow
3. Faster iteration
4. Current setup already has dev/staging/prod structure
5. Remote backend (S3 + DynamoDB) already configured

**When to Migrate to Multi-Account:**
- Team grows to 3+ engineers
- Production ML models serve real users
- Need SOC2/compliance certification
- Want separate cost attribution
- Need stricter security isolation

### If You Decide to Migrate (Future):

**Timeline:**
- Week 1: Set up AWS Organization and member accounts
- Week 2: Configure cross-account IAM roles
- Week 3: Migrate Terraform to account-specific structure
- Week 4: Update GitHub Actions workflows
- Week 5: Testing and validation

**Estimated Effort:** 3-4 weeks part-time

---

## Alternative: Terraform Cloud Workspaces (Middle Ground)

If you want better separation without multi-account complexity:

**Terraform Cloud Features:**
- Separate workspaces for dev/staging/prod
- Built-in state management
- Team collaboration
- Cost estimation
- Policy as Code (Sentinel)
- **Free tier**: Up to 5 users

**Setup:**
1. Create Terraform Cloud account
2. Create 3 workspaces (dev, staging, prod)
3. Connect GitHub repository
4. Each workspace uses different tfvars

**Benefits:**
- ✅ Better isolation than current setup
- ✅ No multi-account complexity
- ✅ Free for small teams
- ✅ Better collaboration features
- ❌ Still shares same AWS account

---

## Conclusion

**For Now:** Keep your current single account multi-environment setup. It's appropriate for your project stage.

**Future Migration Path:**
1. **Phase 1** (3-6 months): Add Terraform Cloud workspaces
2. **Phase 2** (6-12 months): Migrate to multi-account if team/compliance needs arise

**Don't use CloudFormation StackSets** - Terraform is superior for your use case.
