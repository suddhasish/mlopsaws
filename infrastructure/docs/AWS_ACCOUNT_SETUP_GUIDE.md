# 🚀 AWS Account Setup Guide - Complete MLOps Infrastructure

## 📋 Table of Contents
1. [Prerequisites](#prerequisites)
2. [AWS Account Creation & Configuration](#aws-account-creation)
3. [IAM User & Role Setup](#iam-setup)
4. [Service Limits & Quotas](#service-limits)
5. [Security Hardening](#security-hardening)
6. [Network Configuration](#network-configuration)
7. [Cost Management Setup](#cost-management)
8. [Pre-Flight Checklist](#pre-flight-checklist)

---

## 🎯 Prerequisites

### Required Tools
```powershell
# Check if tools are installed
aws --version        # AWS CLI v2.x required
terraform --version  # Terraform v1.5+ required
python --version     # Python 3.8+ required
git --version        # Git 2.x+ required
```

### Install Missing Tools

**AWS CLI v2 (Windows PowerShell)**
```powershell
# Download and install AWS CLI v2
msiexec.exe /i https://awscli.amazonaws.com/AWSCLIV2.msi /quiet

# Verify installation
aws --version
```

**Terraform (Windows PowerShell)**
```powershell
# Using Chocolatey
choco install terraform

# OR download manually from: https://www.terraform.io/downloads
# Add to PATH: C:\terraform\terraform.exe
```

**Python (if not installed)**
```powershell
# Download from: https://www.python.org/downloads/
# During installation, check "Add Python to PATH"
```

### Required Knowledge
- ✅ Basic AWS console navigation
- ✅ Understanding of IAM (users, roles, policies)
- ✅ Command line basics (PowerShell)
- ✅ Basic networking concepts (VPC, subnets, security groups)

---

## 🏢 AWS Account Creation

### Step 1: Create AWS Account (If You Don't Have One)

**Why**: AWS account is the root container for all resources and billing.

1. **Navigate to**: https://aws.amazon.com/
2. **Click**: "Create an AWS Account"
3. **Provide**:
   - Email address (use company email for production)
   - Account name: `mlops-production` or `yourcompany-ml`
   - Root user password (minimum 12 characters, complex)
4. **Contact Information**:
   - Select: Business or Personal
   - Provide: Valid phone number for MFA
5. **Payment Method**:
   - Add: Credit/debit card (required even for free tier)
   - **Note**: You won't be charged unless you exceed free tier limits
6. **Identity Verification**:
   - Receive SMS/call verification code
7. **Support Plan**:
   - Select: Basic (Free) for dev/learning
   - Consider: Developer ($29/month) or Business ($100/month) for production

**🔒 CRITICAL: Secure Root Account Immediately**
```
DO THIS NOW:
1. Enable MFA (Multi-Factor Authentication) on root account
2. Never use root account for daily operations
3. Store root credentials in password manager (1Password, LastPass)
```

### Step 2: Enable MFA on Root Account

**Why**: Root account has unlimited access. MFA prevents unauthorized access even if password is compromised.

1. **Sign in**: https://console.aws.amazon.com/
2. **Click**: Account name (top right) → Security Credentials
3. **Navigate**: Multi-factor authentication (MFA)
4. **Click**: "Activate MFA"
5. **Choose**: Virtual MFA device (recommended)
   - Use: Google Authenticator, Microsoft Authenticator, or Authy
6. **Scan**: QR code with your phone
7. **Enter**: Two consecutive MFA codes
8. **Save**: Recovery codes in secure location

✅ **Verification**: Try logging out and back in - you should be prompted for MFA code

### Step 3: Enable AWS Organizations (Multi-Account Strategy)

**Why**: Best practice is to separate dev/staging/production into different AWS accounts for security isolation and cost tracking.

**For Production Deployments** (Recommended):
```
AWS Organization Structure:
├── Management Account (root, billing only)
├── Dev Account (experimentation, low security)
├── Staging Account (pre-production, medium security)
└── Production Account (live traffic, high security)
```

**Setup Steps**:
1. **Console**: https://console.aws.amazon.com/organizations/
2. **Click**: "Create organization"
3. **Select**: Enable all features
4. **Create**: Organizational Units (OUs)
   - Development OU
   - Staging OU
   - Production OU
5. **Create**: Member accounts
   ```
   Account Name: mlops-dev
   Email: mlops-dev@yourcompany.com (use email aliases)
   
   Account Name: mlops-staging
   Email: mlops-staging@yourcompany.com
   
   Account Name: mlops-production
   Email: mlops-prod@yourcompany.com
   ```

**For Learning/Personal Projects** (Simplified):
- Single AWS account is acceptable
- Use tags to separate environments: `Environment=dev|staging|prod`

### Step 4: Set Up Billing Alerts

**Why**: Prevent unexpected charges. SageMaker costs can escalate quickly if resources aren't shut down.

1. **Navigate**: https://console.aws.amazon.com/billing/
2. **Click**: Billing Preferences
3. **Enable**:
   - ✅ Receive PDF Invoice By Email
   - ✅ Receive Free Tier Usage Alerts
   - ✅ Receive Billing Alerts
4. **Save**: Preferences

5. **Create CloudWatch Billing Alarm**:
   ```powershell
   # Set region to us-east-1 (billing metrics only available here)
   aws cloudwatch put-metric-alarm \
     --region us-east-1 \
     --alarm-name "Billing-Alert-$50" \
     --alarm-description "Alert when charges exceed $50" \
     --metric-name EstimatedCharges \
     --namespace AWS/Billing \
     --statistic Maximum \
     --period 21600 \
     --evaluation-periods 1 \
     --threshold 50 \
     --comparison-operator GreaterThanThreshold \
     --dimensions Name=Currency,Value=USD \
     --alarm-actions arn:aws:sns:us-east-1:ACCOUNT_ID:billing-alerts
   ```

**Recommended Thresholds**:
- Dev: $50/month
- Staging: $150/month
- Production: $1000/month (adjust based on traffic)

---

## 👤 IAM Setup

### Step 1: Create Administrator IAM User (Replace Root)

**Why**: Root account is too powerful for daily use. IAM users have traceable actions in CloudTrail.

**AWS Console Method**:
1. **Navigate**: https://console.aws.amazon.com/iam/
2. **Click**: Users → Add users
3. **User name**: `ml-admin`
4. **Access type**: 
   - ✅ Programmatic access (AWS CLI/SDK)
   - ✅ AWS Management Console access
5. **Console password**: Custom password + require password change
6. **Next**: Permissions
7. **Attach policies**:
   - ✅ `AdministratorAccess` (for initial setup only)
8. **Next**: Tags
   - Key: `Role`, Value: `Administrator`
   - Key: `Team`, Value: `MLOps`
9. **Create user**
10. **Download CSV**: Save credentials securely
11. **Enable MFA**: For this user too

**AWS CLI Method** (automated):
```powershell
# Create IAM user
aws iam create-user --user-name ml-admin

# Attach administrator policy (temporary, will narrow later)
aws iam attach-user-policy \
  --user-name ml-admin \
  --policy-arn arn:aws:iam::aws:policy/AdministratorAccess

# Create access keys
aws iam create-access-key --user-name ml-admin

# Output: Save Access Key ID and Secret Access Key
```

### Step 2: Configure AWS CLI Credentials

**Why**: Enables command-line and Terraform access to AWS.

```powershell
# Configure default profile
aws configure

# Provide:
AWS Access Key ID: [from CSV downloaded]
AWS Secret Access Key: [from CSV downloaded]
Default region name: us-east-1
Default output format: json

# Test configuration
aws sts get-caller-identity

# Expected output:
# {
#     "UserId": "AIDAXXXXXXXXXXXX",
#     "Account": "123456789012",
#     "Arn": "arn:aws:iam::123456789012:user/ml-admin"
# }
```

**Configure Multiple Profiles (for multi-account setup)**:
```powershell
# Dev account
aws configure --profile mlops-dev
# [Enter dev account credentials]

# Staging account
aws configure --profile mlops-staging
# [Enter staging account credentials]

# Production account
aws configure --profile mlops-prod
# [Enter production account credentials]

# Test profiles
aws sts get-caller-identity --profile mlops-dev
aws sts get-caller-identity --profile mlops-staging
aws sts get-caller-identity --profile mlops-prod
```

**Verify Credentials File**:
```powershell
# Windows location
notepad $env:USERPROFILE\.aws\credentials

# Should contain:
[default]
aws_access_key_id = AKIAIOSFODNN7EXAMPLE
aws_secret_access_key = wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY

[mlops-dev]
aws_access_key_id = ...
aws_secret_access_key = ...

[mlops-staging]
aws_access_key_id = ...
aws_secret_access_key = ...

[mlops-prod]
aws_access_key_id = ...
aws_secret_access_key = ...
```

### Step 3: Create SageMaker Execution Role

**Why**: SageMaker needs permissions to access S3, CloudWatch, ECR, and other services on your behalf.

**Create via AWS Console** (Recommended for beginners):
1. **Navigate**: https://console.aws.amazon.com/iam/home#/roles
2. **Click**: Create role
3. **Trusted entity**: AWS service
4. **Use case**: SageMaker
5. **Select**: SageMaker - Execution
6. **Next**: Permissions (pre-populated)
   - `AmazonSageMakerFullAccess` ✅
7. **Add additional policies**:
   - `AmazonS3FullAccess` (we'll narrow this later)
   - `CloudWatchLogsFullAccess`
8. **Role name**: `SageMakerExecutionRole-MLOps`
9. **Description**: "Execution role for MLOps SageMaker jobs"
10. **Create role**
11. **Copy ARN**: `arn:aws:iam::123456789012:role/SageMakerExecutionRole-MLOps`

**🔒 Security Note**: This role has broad permissions. We'll create least-privilege roles via Terraform.

### Step 4: Create Data Scientist IAM Role

**Why**: Team members need SageMaker access without administrator privileges.

**Permissions Required**:
- SageMaker: Read/write notebooks, training jobs, endpoints
- S3: Access to ML data buckets only
- CloudWatch: View logs and metrics
- ECR: Pull container images
- IAM: Pass SageMaker execution role

**We'll create this via Terraform** (see infrastructure/terraform/modules/iam/)

---

## 📊 Service Limits & Quotas

### Step 1: Check Current Limits

**Why**: AWS has default quotas that may be too low for ML workloads.

```powershell
# Check SageMaker quotas
aws service-quotas list-service-quotas \
  --service-code sagemaker \
  --query 'Quotas[?QuotaName==`ml.m5.xlarge for training job usage`]'

# Check common ML instance limits
aws service-quotas get-service-quota \
  --service-code sagemaker \
  --quota-code L-D9459C61  # ml.m5.xlarge training instances

aws service-quotas get-service-quota \
  --service-code sagemaker \
  --quota-code L-9A430B81  # ml.m5.xlarge endpoint instances
```

### Step 2: Request Quota Increases

**Why**: Default limits may prevent running training jobs or deploying endpoints.

**Critical Quotas to Increase**:

| Service | Quota Name | Default | Recommended | Why |
|---------|-----------|---------|-------------|-----|
| SageMaker | `ml.m5.xlarge` training instances | 0-2 | 5 | Parallel training jobs |
| SageMaker | `ml.m5.xlarge` endpoint instances | 0-2 | 10 | Auto-scaling endpoints |
| SageMaker | `ml.t2.medium` endpoint instances | 2 | 5 | Dev endpoints |
| S3 | Bucket count | 100 | 100 | Sufficient (1 per env) |
| EC2 | VPC count | 5 | 5 | Sufficient |
| CloudWatch | Alarms | 5000 | 5000 | Sufficient |

**Request Increase via Console**:
1. **Navigate**: https://console.aws.amazon.com/servicequotas/
2. **Search**: "SageMaker"
3. **Filter**: Applied quotas
4. **Select**: `ml.m5.xlarge for training job usage`
5. **Click**: "Request quota increase"
6. **Enter**: New quota value (e.g., 5)
7. **Request**: Submit
8. **Wait**: Approval (typically 1-3 business days)

**Request Increase via CLI**:
```powershell
# Request ml.m5.xlarge training quota increase to 5
aws service-quotas request-service-quota-increase \
  --service-code sagemaker \
  --quota-code L-D9459C61 \
  --desired-value 5

# Request ml.m5.xlarge endpoint quota increase to 10
aws service-quotas request-service-quota-increase \
  --service-code sagemaker \
  --quota-code L-9A430B81 \
  --desired-value 10
```

### Step 3: Enable Required AWS Services

**Why**: Some services are disabled by default in new accounts.

1. **Navigate**: https://console.aws.amazon.com/
2. **Search and Access Each Service** (to enable):
   - ✅ Amazon SageMaker
   - ✅ Amazon S3
   - ✅ AWS CloudWatch
   - ✅ AWS CloudTrail
   - ✅ Amazon SNS
   - ✅ AWS Secrets Manager
   - ✅ Amazon ECR (Elastic Container Registry)
   - ✅ AWS Systems Manager (Parameter Store)

**Enable via Console**: First-time access to each service enables it

---

## 🔒 Security Hardening

### Step 1: Enable CloudTrail (Audit Logging)

**Why**: Records all API calls for security auditing and compliance. Required for production environments.

**What it logs**:
- Who: IAM user/role that made the call
- What: API action performed (e.g., `CreateTrainingJob`)
- When: Timestamp
- Where: Source IP address
- Result: Success or failure

**Setup**:
1. **Navigate**: https://console.aws.amazon.com/cloudtrail/
2. **Click**: Create trail
3. **Trail name**: `mlops-audit-trail`
4. **Storage location**: 
   - Create new S3 bucket: `mlops-cloudtrail-logs-[account-id]`
   - Enable encryption: ✅ SSE-S3
5. **Log events**:
   - ✅ Management events (read/write)
   - ✅ Data events for S3 buckets (select ML data buckets)
6. **Insights**: Enable CloudTrail Insights (detects anomalies)
7. **Create trail**

**Verify**:
```powershell
aws cloudtrail describe-trails
aws cloudtrail get-trail-status --name mlops-audit-trail
```

### Step 2: Enable AWS Config (Compliance Monitoring)

**Why**: Continuously monitors resource configurations and detects security misconfigurations.

**What it checks**:
- S3 buckets are not publicly accessible
- Encryption is enabled
- IAM policies follow least privilege
- Security group rules are restrictive

**Setup**:
1. **Navigate**: https://console.aws.amazon.com/config/
2. **Click**: Get started
3. **Resource types**: All resources
4. **S3 bucket**: Create bucket `mlops-config-[account-id]`
5. **SNS topic**: Create topic for notifications
6. **IAM role**: Create service-linked role
7. **Rules**: Add managed rules
   - `s3-bucket-public-read-prohibited`
   - `s3-bucket-public-write-prohibited`
   - `encrypted-volumes`
   - `iam-user-mfa-enabled`
   - `sagemaker-endpoint-config-kms-key-configured`

### Step 3: Set Up AWS Secrets Manager

**Why**: Never store credentials in code or config files. Secrets Manager provides secure, rotating secret storage.

**Create Database Credentials Secret** (if using RDS for feature store):
```powershell
aws secretsmanager create-secret \
  --name mlops/database/credentials \
  --description "Database credentials for feature store" \
  --secret-string '{
    "username": "mlops_admin",
    "password": "ChangeThisToStrongPassword123!",
    "engine": "postgres",
    "host": "mlops-db.us-east-1.rds.amazonaws.com",
    "port": 5432,
    "dbname": "features"
  }'

# Enable automatic rotation (requires Lambda function)
aws secretsmanager rotate-secret \
  --secret-id mlops/database/credentials \
  --rotation-lambda-arn arn:aws:lambda:us-east-1:ACCOUNT:function:SecretsManagerRotation \
  --rotation-rules AutomaticallyAfterDays=30
```

### Step 4: Enable GuardDuty (Threat Detection)

**Why**: Monitors for malicious activity and unauthorized behavior.

```powershell
# Enable GuardDuty
aws guardduty create-detector --enable

# Verify
aws guardduty list-detectors
```

### Step 5: Configure S3 Block Public Access (Account-Level)

**Why**: Prevents accidental public exposure of ML datasets and models.

```powershell
aws s3control put-public-access-block \
  --account-id $(aws sts get-caller-identity --query Account --output text) \
  --public-access-block-configuration \
    BlockPublicAcls=true,\
    IgnorePublicAcls=true,\
    BlockPublicPolicy=true,\
    RestrictPublicBuckets=true
```

---

## 🌐 Network Configuration

### Step 1: Decide on VPC Strategy

**Option A: Default VPC** (Simplest, good for learning)
- ✅ Pre-configured by AWS
- ✅ Internet access out-of-the-box
- ⚠️ Less secure (resources have public IPs by default)

**Option B: Custom VPC** (Recommended for production)
- ✅ Full control over network topology
- ✅ Private subnets for SageMaker
- ✅ NAT Gateway for internet access
- ✅ VPC Endpoints for AWS service access (cost-effective)

**We'll create this via Terraform**: See `infrastructure/terraform/modules/networking/`

### Step 2: Understand SageMaker Network Options

**Internet Mode** (Default):
```
SageMaker Training Job → Internet → S3/ECR/CloudWatch
```
- ✅ Simple setup
- ⚠️ Traffic goes over internet
- ⚠️ Data transfer charges

**VPC Mode** (Recommended):
```
SageMaker Training Job → VPC Endpoint → S3/ECR/CloudWatch
```
- ✅ Traffic stays in AWS network
- ✅ No internet exposure
- ✅ Lower latency
- ✅ Cost savings on data transfer

**Network Isolation Mode** (Maximum security):
```
SageMaker Training Job → No network access
```
- ✅ Complete isolation
- ⚠️ Must pre-download all data to EBS volume
- ⚠️ Cannot pull Docker images during runtime

---

## 💰 Cost Management Setup

### Step 1: Enable Cost Explorer

**Why**: Visualize and analyze spending patterns.

1. **Navigate**: https://console.aws.amazon.com/cost-management/
2. **Click**: Cost Explorer
3. **Enable**: Cost Explorer (free)
4. **Create**: Custom reports
   - Filter by Service: SageMaker
   - Filter by Tag: Environment=dev|staging|prod
   - Group by: Instance Type

### Step 2: Create Budget

**Why**: Get alerts before overspending.

```powershell
# Create a $100 monthly budget for dev environment
aws budgets create-budget \
  --account-id $(aws sts get-caller-identity --query Account --output text) \
  --budget file://budget.json \
  --notifications-with-subscribers file://notifications.json

# budget.json
{
  "BudgetName": "MLOps-Dev-Monthly",
  "BudgetLimit": {
    "Amount": "100",
    "Unit": "USD"
  },
  "TimeUnit": "MONTHLY",
  "BudgetType": "COST",
  "CostFilters": {
    "TagKeyValue": ["user:Environment$dev"]
  }
}
```

### Step 3: Tag All Resources

**Why**: Enables cost tracking by environment, project, team.

**Required Tags**:
```
Environment: dev | staging | production
Project: mlops-diabetes
Team: ml-engineering
CostCenter: ML-R&D
Owner: your-email@company.com
AutoShutdown: true | false  (for dev resources)
```

**Enforce via Tag Policies** (AWS Organizations):
```json
{
  "tags": {
    "Environment": {
      "tag_key": {
        "@@assign": "Environment"
      },
      "enforced_for": {
        "@@assign": ["sagemaker:*", "s3:*", "ec2:*"]
      }
    }
  }
}
```

---

## ✅ Pre-Flight Checklist

Before running Terraform, verify all prerequisites:

### Account Setup
- [ ] AWS account created and active
- [ ] Root account MFA enabled
- [ ] Billing alerts configured ($50, $100, $500)
- [ ] Cost Explorer enabled
- [ ] Budgets created per environment

### IAM Configuration
- [ ] Administrator IAM user created (not using root)
- [ ] IAM user MFA enabled
- [ ] AWS CLI configured with credentials
- [ ] Multiple profiles configured (if multi-account)
- [ ] SageMaker execution role created
- [ ] Role ARN copied and saved

### Security
- [ ] CloudTrail enabled and logging
- [ ] AWS Config enabled
- [ ] GuardDuty enabled
- [ ] S3 Block Public Access enabled (account-level)
- [ ] Secrets Manager available

### Service Quotas
- [ ] SageMaker training instance limits checked
- [ ] SageMaker endpoint instance limits checked
- [ ] Quota increases requested (if needed)
- [ ] Quota increase requests approved (wait 1-3 days)

### Tools Installed
- [ ] AWS CLI v2 installed and configured
- [ ] Terraform v1.5+ installed
- [ ] Python 3.8+ installed
- [ ] Git installed
- [ ] Code editor installed (VS Code recommended)

### Network Planning
- [ ] VPC strategy decided (default vs custom)
- [ ] Region selected (us-east-1 recommended for cost)
- [ ] Availability zones planned (minimum 2)

### Terraform Backend
- [ ] S3 bucket for Terraform state created (or will be created)
- [ ] DynamoDB table for state locking planned
- [ ] Bucket versioning enabled
- [ ] Bucket encryption enabled

---

## 🚀 Next Steps

Once checklist is complete:

1. **Navigate to Terraform directory**:
   ```powershell
   cd infrastructure/terraform/environments/dev
   ```

2. **Review variable files**:
   ```powershell
   notepad terraform.tfvars
   # Update with your account ID, region, etc.
   ```

3. **Initialize Terraform**:
   ```powershell
   terraform init
   ```

4. **Plan infrastructure**:
   ```powershell
   terraform plan -out=tfplan
   ```

5. **Review plan carefully** (shows all resources to be created)

6. **Apply infrastructure**:
   ```powershell
   terraform apply tfplan
   ```

7. **Verify resources** in AWS Console

---

## 🆘 Troubleshooting

### Issue: "AWS CLI not found"
```powershell
# Fix: Add to PATH
$env:Path += ";C:\Program Files\Amazon\AWSCLIV2"

# Verify
aws --version
```

### Issue: "Access Denied" errors
```powershell
# Check current identity
aws sts get-caller-identity

# Verify correct profile
aws sts get-caller-identity --profile mlops-dev

# Re-configure credentials
aws configure
```

### Issue: "Quota exceeded" when creating training job
```
Solution:
1. Navigate: https://console.aws.amazon.com/servicequotas/
2. Request quota increase
3. Wait for approval (1-3 business days)
4. Retry
```

### Issue: "MFA token expired"
```
Solution:
1. Re-authenticate with MFA
2. Use aws-vault or aws-mfa tools for automatic token refresh
```

---

## 📚 Additional Resources

- **AWS Well-Architected Framework**: https://aws.amazon.com/architecture/well-architected/
- **SageMaker Best Practices**: https://docs.aws.amazon.com/sagemaker/latest/dg/best-practices.html
- **AWS Security Best Practices**: https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html
- **Terraform AWS Provider**: https://registry.terraform.io/providers/hashicorp/aws/latest/docs

---

**Estimated Setup Time**: 2-4 hours (including quota approval wait time)

**Cost During Setup**: $0 (all setup actions are free tier eligible)

**Last Updated**: November 2025
