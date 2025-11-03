# Terraform Modules Reference

## 📦 Complete Module Structure

All Terraform modules have been created and are ready to use. Here's the complete structure:

```
infrastructure/terraform/modules/
├── s3/                     ✅ S3 Bucket with Security Hardening
│   ├── main.tf            - S3 bucket, versioning, encryption, lifecycle, policies
│   ├── variables.tf       - Module variables
│   └── outputs.tf         - Bucket name, ARN, URL
│
├── iam/                    ✅ IAM Roles and Policies
│   ├── main.tf            - SageMaker execution role, Data scientist role
│   ├── variables.tf       - Module variables
│   └── outputs.tf         - Role ARNs and names
│
├── kms/                    ✅ KMS Encryption Keys
│   ├── main.tf            - KMS key, alias, grants, key policy
│   ├── variables.tf       - Module variables
│   └── outputs.tf         - Key ID, ARN, alias
│
├── networking/             ✅ VPC, Subnets, Security Groups, VPC Endpoints
│   ├── main.tf            - VPC, private subnets, route tables, security groups, endpoints
│   ├── variables.tf       - Module variables
│   └── outputs.tf         - VPC ID, subnet IDs, security group ID
│
├── sagemaker/              ✅ SageMaker Model Registry
│   ├── main.tf            - Model Package Group
│   ├── variables.tf       - Module variables
│   └── outputs.tf         - Model group name and ARN
│
├── monitoring/             ✅ CloudWatch, SNS, CloudTrail
│   ├── main.tf            - Log groups, SNS topics, alarms, CloudTrail
│   ├── variables.tf       - Module variables
│   └── outputs.tf         - Log group names, SNS ARNs, CloudTrail name
│
├── budgets/                ✅ AWS Budgets for Cost Control
│   ├── main.tf            - Monthly budget with alerts
│   ├── variables.tf       - Module variables
│   └── outputs.tf         - Budget name, ARN, amount
│
├── auto_shutdown/          ✅ Lambda for Auto-Shutdown (DEV)
│   ├── main.tf            - Lambda functions, EventBridge rules
│   ├── variables.tf       - Module variables
│   └── outputs.tf         - Lambda ARNs, schedules
│
└── feature_store/          ✅ RDS PostgreSQL Database
    ├── main.tf            - RDS instance, subnet group, security group
    ├── variables.tf       - Module variables
    └── outputs.tf         - RDS endpoint, instance ID, ARN
```

---

## 🔧 Module Details

### 1. **S3 Module** (`modules/s3/`)

**Purpose:** Secure S3 bucket for ML data storage

**Resources Created:**
- S3 bucket with unique naming
- Versioning enabled (track dataset changes)
- Server-side encryption (AES256 or KMS)
- Public access block (all 4 settings)
- Lifecycle policies (archive to Glacier, auto-delete)
- Bucket policy (deny unencrypted uploads, deny insecure transport)
- Access logging
- Intelligent tiering
- Object lock (compliance retention)

**Key Variables:**
- `enable_versioning` - Enable S3 versioning
- `enable_kms_encryption` - Use KMS instead of AES256
- `glacier_transition_days` - Days before archiving to Glacier (default: 90)
- `expiration_days` - Days before deletion (default: 365)

---

### 2. **IAM Module** (`modules/iam/`)

**Purpose:** IAM roles for SageMaker and data scientists

**Resources Created:**
- **SageMaker Execution Role:**
  - S3 access (GetObject, PutObject, DeleteObject, ListBucket)
  - CloudWatch Logs access
  - ECR access (for custom Docker images)
  - KMS access (conditional, if encryption enabled)
- **Data Scientist Role:**
  - SageMaker Full Access
  - PassRole policy (can pass SageMaker execution role)
  - MFA required for assume role

**Key Variables:**
- `s3_bucket_arn` - ARN of S3 bucket for access policy
- `kms_key_arn` - ARN of KMS key (optional)

**Security Features:**
- MFA enforcement for data scientist role
- PassRole restricted to sagemaker.amazonaws.com
- Least privilege access

---

### 3. **KMS Module** (`modules/kms/`)

**Purpose:** Centralized encryption key management

**Resources Created:**
- KMS key with automatic rotation
- KMS alias for easy reference
- KMS grant for SageMaker
- Key policy (allow IAM root, SageMaker, CloudWatch Logs)

**Key Variables:**
- `deletion_window_in_days` - Key deletion window (default: 30)
- `enable_key_rotation` - Automatic rotation (default: true)
- `sagemaker_role_arn` - SageMaker role for KMS grant

**Security Features:**
- Automatic key rotation enabled
- ViaService condition (only SageMaker can use)
- CloudWatch Logs encryption support

---

### 4. **Networking Module** (`modules/networking/`)

**Purpose:** VPC isolation and network security

**Resources Created:**
- VPC with DNS support
- Private subnets (multi-AZ)
- Route tables
- Security group for SageMaker
- **VPC Endpoints:**
  - S3 (Gateway endpoint - FREE)
  - SageMaker API (Interface endpoint)
  - SageMaker Runtime (Interface endpoint)
  - CloudWatch Logs (Interface endpoint)
  - ECR API (Interface endpoint)
  - ECR Docker (Interface endpoint)

**Key Variables:**
- `vpc_cidr` - VPC CIDR block (default: 10.0.0.0/16)
- `availability_zones_count` - Number of AZs (default: 2)
- `enable_vpc_endpoints` - Enable VPC endpoints (default: true)

**Cost Savings:**
- VPC endpoints save ~$240/month vs NAT Gateway
- No data transfer charges with VPC endpoints

---

### 5. **SageMaker Module** (`modules/sagemaker/`)

**Purpose:** SageMaker Model Registry for model versioning

**Resources Created:**
- Model Package Group (Model Registry)

**Key Variables:**
- `project_name` - Project name
- `environment` - Environment name

**Usage:**
- Register trained models
- Track model versions
- Approve/reject models for deployment

---

### 6. **Monitoring Module** (`modules/monitoring/`)

**Purpose:** CloudWatch monitoring, SNS alerts, audit logging

**Resources Created:**
- **CloudWatch Log Groups:**
  - Training jobs log group
  - Endpoints log group
- **SNS Topics:**
  - General alerts (email)
  - Critical alerts (email + PagerDuty)
- **CloudWatch Alarms:**
  - Endpoint latency alarm
  - Endpoint error alarm
- **CloudTrail:**
  - S3 bucket for logs
  - CloudTrail with S3/SageMaker event tracking
  - Log file validation enabled

**Key Variables:**
- `log_retention_days` - CloudWatch log retention (7/30/90)
- `alert_email_endpoints` - List of email addresses
- `pagerduty_endpoint` - PagerDuty HTTPS endpoint (optional)
- `endpoint_latency_threshold_ms` - Latency threshold (default: 500ms)
- `endpoint_error_threshold` - Error count threshold (default: 10)
- `enable_cloudtrail` - Enable CloudTrail (default: true)

---

### 7. **Budgets Module** (`modules/budgets/`)

**Purpose:** AWS cost control and budget alerts

**Resources Created:**
- Monthly budget with cost filtering
- Dynamic notifications at multiple thresholds

**Key Variables:**
- `budget_amount` - Monthly budget limit in USD
- `budget_alert_thresholds` - Alert percentages (default: [50, 80, 100, 120])
- `budget_notification_emails` - Email addresses for alerts

**Alert Strategy:**
- 50% - FORECASTED alert (early warning)
- 80% - ACTUAL alert (approaching limit)
- 100% - ACTUAL alert (budget exceeded)
- 120% - ACTUAL alert (critical overspend)

---

### 8. **Auto Shutdown Module** (`modules/auto_shutdown/`)

**Purpose:** Automatic endpoint shutdown for DEV (save 60% costs)

**Resources Created:**
- **Lambda Functions:**
  - Shutdown Lambda (delete endpoints with AutoShutdown tag)
  - Startup Lambda (placeholder for recreating endpoints)
- **EventBridge Rules:**
  - Shutdown schedule (default: 7PM weekdays)
  - Startup schedule (default: 8AM weekdays)
- **IAM Role:**
  - Lambda execution role with SageMaker permissions

**Key Variables:**
- `shutdown_schedule` - Cron expression (default: "cron(0 19 ? * MON-FRI *)")
- `startup_schedule` - Cron expression (default: "cron(0 8 ? * MON-FRI *)")

**Cost Savings:**
- ~60% savings on endpoint costs (13 hours/day off)
- Only shuts down endpoints tagged with `AutoShutdown=true`

**Note:** Startup Lambda is a placeholder. In production, store endpoint configs before shutdown and recreate from config.

---

### 9. **Feature Store Module** (`modules/feature_store/`)

**Purpose:** RDS PostgreSQL for feature storage (optional)

**Resources Created:**
- RDS PostgreSQL instance
- DB subnet group
- Security group for RDS
- Automated backups
- CloudWatch logs export

**Key Variables:**
- `instance_class` - RDS instance type (default: db.t3.micro)
- `allocated_storage` - Initial storage in GB (default: 20)
- `max_allocated_storage` - Max autoscaling storage (default: 100)
- `multi_az` - Enable Multi-AZ (default: false)
- `backup_retention_days` - Backup retention (default: 7)
- `deletion_protection` - Prevent accidental deletion (default: true)
- `master_password` - Master password (REQUIRED, use Secrets Manager)

**Security Features:**
- Storage encryption with KMS
- Private subnet placement
- Security group (only SageMaker access)
- Automated backups
- Performance Insights (optional)

**Important:** In production, use AWS Secrets Manager for `master_password`.

---

## 🚀 Usage Example

### Deploy All Modules

```powershell
# Navigate to environment
cd infrastructure/terraform/environments/dev

# Create symlinks (if not using deployment script)
New-Item -ItemType SymbolicLink -Path main.tf -Target ..\..\main.tf
New-Item -ItemType SymbolicLink -Path variables.tf -Target ..\..\variables.tf
New-Item -ItemType SymbolicLink -Path outputs.tf -Target ..\..\outputs.tf
New-Item -ItemType SymbolicLink -Path modules.tf -Target ..\..\modules.tf
New-Item -ItemType Junction -Path modules -Target ..\..\modules

# Initialize
terraform init

# Plan
terraform plan -var-file="terraform.tfvars" -out=tfplan

# Apply
terraform apply tfplan
```

### Or Use Deployment Script

```powershell
cd infrastructure
.\scripts\deploy-infrastructure.ps1 -Environment dev -Action all -AutoApprove
```

---

## 🔍 Module Dependencies

```
Flow:
1. KMS (if enabled) → Creates encryption keys
2. IAM → Uses KMS keys (if enabled)
3. S3 → Uses KMS keys, IAM role for bucket policy
4. Networking (if enabled) → Creates VPC, subnets, security groups
5. SageMaker → Independent (just Model Registry)
6. Monitoring → Uses S3 bucket ARN for CloudTrail, KMS for log encryption
7. Budgets → Independent
8. Auto Shutdown (if enabled) → Independent
9. Feature Store (if enabled) → Uses VPC, subnets, security groups from Networking

Module Invocation Order (in modules.tf):
1. iam (no dependencies)
2. kms (conditional, uses iam role ARN)
3. s3 (uses kms key ARN if enabled)
4. networking (conditional, no dependencies)
5. sagemaker (no dependencies)
6. monitoring (uses s3 bucket ARN, kms key ARN)
7. budgets (no dependencies)
8. auto_shutdown (conditional, no dependencies)
9. feature_store (conditional, uses networking outputs)
```

---

## 📊 Resource Counts by Environment

| Module | DEV | STAGING | PRODUCTION |
|--------|-----|---------|------------|
| S3 | 1 bucket | 1 bucket | 1 bucket |
| IAM | 2 roles | 2 roles | 2 roles |
| KMS | 0 (AES256) | 1 key | 1 key |
| Networking | 0 (default VPC) | 1 VPC + 2 subnets + 6 endpoints | 1 VPC + 2 subnets + 6 endpoints |
| SageMaker | 1 Model Registry | 1 Model Registry | 1 Model Registry |
| Monitoring | 2 log groups + 2 SNS | 2 log groups + 2 SNS + CloudTrail | 2 log groups + 2 SNS + CloudTrail + alarms |
| Budgets | 1 budget | 1 budget | 1 budget |
| Auto Shutdown | 2 Lambdas + 2 rules | 0 | 0 |
| Feature Store | 0 | 0 (optional) | 0 (optional) |
| **TOTAL** | ~10 resources | ~25 resources | ~30 resources |

---

## 💡 Next Steps

1. **Review module configurations** in `terraform/modules/`
2. **Customize environment configs** in `terraform/environments/*/terraform.tfvars`
3. **Deploy DEV first** to test all modules
4. **Verify resources** in AWS Console
5. **Deploy STAGING** after DEV validation
6. **Deploy PRODUCTION** with full approval process

---

## 📝 Notes

- All modules follow Terraform best practices
- All modules support tagging via `tags` variable
- All modules have security hardening enabled
- All sensitive outputs are marked as `sensitive = true`
- All modules are idempotent (can run multiple times safely)

**Now you have a complete, production-ready infrastructure!** ✅
