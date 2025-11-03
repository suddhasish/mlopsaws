# 🏗️ MLOps Infrastructure as Code

## 📋 Overview

This directory contains **Terraform infrastructure as code** to provision all AWS resources needed for the MLOps diabetes classification project. The infrastructure is designed following AWS Well-Architected Framework best practices with emphasis on security, reliability, and cost optimization.

## 📁 Directory Structure

```
infrastructure/
├── docs/                                    # Documentation
│   ├── AWS_ACCOUNT_SETUP_GUIDE.md          # Step-by-step AWS account setup
│   ├── AWS_SERVICES_EXPLAINED.md           # Why each service is used
│   └── DEPLOYMENT_GUIDE.md                 # How to deploy infrastructure
│
├── scripts/                                 # Automation scripts
│   └── deploy-infrastructure.ps1           # One-command deployment (PowerShell)
│
└── terraform/                               # Terraform configuration
    ├── main.tf                              # Provider configuration
    ├── variables.tf                         # Variable definitions
    ├── outputs.tf                           # Output values
    ├── modules.tf                           # Module orchestration
    ├── MODULES_TEMPLATE.tf                  # Template for creating modules
    │
    ├── modules/                             # Reusable Terraform modules
    │   ├── s3/                              # S3 buckets with encryption
    │   ├── iam/                             # IAM roles and policies
    │   ├── kms/                             # KMS encryption keys
    │   ├── networking/                      # VPC, subnets, security groups
    │   ├── sagemaker/                       # SageMaker Model Registry
    │   ├── monitoring/                      # CloudWatch, SNS, CloudTrail
    │   ├── budgets/                         # AWS Budgets for cost control
    │   ├── auto_shutdown/                   # Lambda for auto-shutdown (dev)
    │   └── feature_store/                   # RDS for offline feature store
    │
    └── environments/                        # Environment-specific configs
        ├── dev/
        │   └── terraform.tfvars             # Dev environment variables
        ├── staging/
        │   └── terraform.tfvars             # Staging environment variables
        └── production/
            └── terraform.tfvars             # Production environment variables
```

## 🚀 Quick Start

### Prerequisites

1. **Complete AWS Account Setup** (1-2 hours)
   - Follow: [`docs/AWS_ACCOUNT_SETUP_GUIDE.md`](docs/AWS_ACCOUNT_SETUP_GUIDE.md)
   - Creates: AWS account, IAM users, billing alerts, service quotas

2. **Install Required Tools**
   ```powershell
   # Check installations
   terraform version  # Should be >= 1.5.0
   aws --version      # Should be AWS CLI v2
   python --version   # Should be >= 3.8
   ```

3. **Configure AWS Credentials**
   ```powershell
   aws configure
   # Enter: Access Key ID, Secret Access Key, Region (us-east-1), Output (json)
   
   # Verify
   aws sts get-caller-identity
   ```

### Deploy Infrastructure (5-10 minutes)

```powershell
# Navigate to scripts directory
cd infrastructure\scripts

# Deploy DEV environment
.\deploy-infrastructure.ps1 -Environment dev -Action all

# Deploy STAGING environment
.\deploy-infrastructure.ps1 -Environment staging -Action all

# Deploy PRODUCTION environment
.\deploy-infrastructure.ps1 -Environment production -Action all
```

**That's it!** The script will:
1. Initialize Terraform
2. Create execution plan
3. Ask for confirmation
4. Deploy all AWS resources
5. Display outputs and next steps

## 📖 Documentation

### For Beginners
Start here → [`docs/AWS_ACCOUNT_SETUP_GUIDE.md`](docs/AWS_ACCOUNT_SETUP_GUIDE.md)
- AWS account creation
- IAM user setup
- Billing configuration
- Service limit requests
- Security hardening

### Understanding AWS Services
Read → [`docs/AWS_SERVICES_EXPLAINED.md`](docs/AWS_SERVICES_EXPLAINED.md)
- Why we use SageMaker, S3, VPC, etc.
- Security best practices
- Cost optimization strategies
- Service interaction flow

### Deployment Instructions
Follow → [`docs/DEPLOYMENT_GUIDE.md`](docs/DEPLOYMENT_GUIDE.md)
- Step-by-step deployment
- Verification procedures
- Updating infrastructure
- Destroying resources
- Troubleshooting

## 🌍 Multi-Environment Strategy

### DEV Environment
- **Purpose**: Experimentation, rapid iteration
- **Cost**: ~$100/month
- **Security**: Basic
- **Instances**: Small (ml.t3.medium, ml.t2.medium)
- **Approval**: Auto-approved models
- **Auto-shutdown**: Enabled (saves $120/month)

### STAGING Environment
- **Purpose**: Pre-production testing
- **Cost**: ~$300/month
- **Security**: Enhanced (VPC, KMS)
- **Instances**: Production-like (ml.m5.xlarge)
- **Approval**: Manual approval required
- **Monitoring**: Full monitoring enabled

### PRODUCTION Environment
- **Purpose**: Live traffic, business-critical
- **Cost**: ~$1500/month
- **Security**: Maximum (VPC, KMS, GuardDuty, CloudTrail)
- **Instances**: Large (ml.m5.2xlarge)
- **Approval**: Strict manual approval
- **High Availability**: Multi-AZ, 2+ instances

## 🛠️ Common Commands

### Initialize Terraform
```powershell
cd terraform\environments\dev
terraform init
```

### Plan Changes
```powershell
terraform plan -var-file="terraform.tfvars" -out="tfplan"
```

### Apply Changes
```powershell
terraform apply tfplan
```

### View Outputs
```powershell
terraform output
terraform output -raw s3_bucket_name
terraform output -json config_yaml
```

### Destroy Infrastructure
```powershell
terraform destroy -var-file="terraform.tfvars"
```

## 🔧 Customization

### Modify Instance Types
Edit `terraform/environments/*/terraform.tfvars`:
```hcl
sagemaker_training_instance_type = "ml.m5.2xlarge"  # Change this
sagemaker_endpoint_instance_type = "ml.m5.xlarge"   # And this
```

### Enable VPC (for production-like security)
```hcl
enable_vpc = true
enable_vpc_endpoints = true  # Saves costs on data transfer
```

### Enable KMS Encryption
```hcl
enable_kms_encryption = true
kms_key_rotation = true
```

### Configure Budgets
```hcl
budget_amount = 150  # $150/month
budget_alert_thresholds = [50, 80, 100]  # Alert at 50%, 80%, 100%
```

### Add Email Alerts
```hcl
alert_email_endpoints = [
  "ml-team@company.com",
  "your-email@company.com"
]
```

## 🏗️ Infrastructure Components

### Core Services
- **Amazon S3**: Data lake for datasets, models, artifacts
- **Amazon SageMaker**: ML platform (training, deployment, registry)
- **AWS IAM**: Access control and permissions
- **Amazon CloudWatch**: Logging, metrics, alarms
- **Amazon SNS**: Notifications and alerts

### Security Services
- **AWS KMS**: Encryption key management
- **AWS CloudTrail**: Audit logging
- **AWS Config**: Compliance monitoring
- **AWS GuardDuty**: Threat detection
- **VPC**: Network isolation

### Cost Optimization
- **AWS Budgets**: Cost control and alerts
- **S3 Lifecycle Policies**: Automatic archival to Glacier
- **Auto-shutdown Lambda**: Shutdown dev resources overnight
- **Spot Instances**: 90% cost savings on training
- **VPC Endpoints**: Save on data transfer costs

## 🔒 Security Best Practices Implemented

1. **Encryption**
   - ✅ S3 buckets encrypted (AES-256 or KMS)
   - ✅ EBS volumes encrypted
   - ✅ SageMaker endpoints encrypted
   - ✅ CloudWatch logs encrypted

2. **Network Isolation**
   - ✅ VPC with private subnets
   - ✅ No public IP addresses
   - ✅ VPC endpoints (no internet gateway)
   - ✅ Security groups (least privilege)

3. **Access Control**
   - ✅ IAM roles (no long-lived credentials)
   - ✅ Least privilege policies
   - ✅ MFA required for humans
   - ✅ Service-linked roles for AWS services

4. **Audit & Compliance**
   - ✅ CloudTrail enabled (all API calls logged)
   - ✅ AWS Config (compliance monitoring)
   - ✅ S3 bucket policies (deny unencrypted uploads)
   - ✅ GuardDuty (threat detection)

5. **Data Protection**
   - ✅ S3 versioning (track dataset changes)
   - ✅ S3 Block Public Access (prevent leaks)
   - ✅ Lifecycle policies (automatic deletion)
   - ✅ Backup and recovery procedures

## 💰 Cost Estimation

### DEV Environment
| Service | Usage | Monthly Cost |
|---------|-------|--------------|
| SageMaker Training | 20 hours/month (spot) | $5 |
| SageMaker Endpoint | 12 hours/day (auto-shutdown) | $50 |
| S3 Storage | 100 GB | $2 |
| CloudWatch Logs | 10 GB | $5 |
| Data Transfer | 50 GB | $5 |
| **TOTAL** | | **~$67** |

### STAGING Environment
| Service | Usage | Monthly Cost |
|---------|-------|--------------|
| SageMaker Training | 40 hours/month | $20 |
| SageMaker Endpoint | 24/7 (1 instance) | $165 |
| S3 Storage | 500 GB | $12 |
| VPC Endpoints | 3 endpoints | $30 |
| CloudWatch/CloudTrail | | $20 |
| **TOTAL** | | **~$247** |

### PRODUCTION Environment
| Service | Usage | Monthly Cost |
|---------|-------|--------------|
| SageMaker Training | 80 hours/month | $80 |
| SageMaker Endpoints | 24/7 (2-10 instances) | $330-1650 |
| S3 Storage | 2 TB | $47 |
| VPC Endpoints | 5 endpoints | $50 |
| Monitoring (CloudWatch, GuardDuty) | | $80 |
| KMS | 10K requests | $3 |
| **TOTAL** | | **~$590-1910** |

**Cost Optimization Tips**:
- Use spot instances for training (90% savings)
- Enable auto-shutdown for dev (save $120/month)
- Use VPC endpoints (save $200/month on data transfer)
- Archive old data to Glacier (5x cheaper)
- Right-size instances based on actual usage

## 🚨 Troubleshooting

### Issue: "terraform: command not found"
```powershell
# Install Terraform
choco install terraform

# OR download from https://www.terraform.io/downloads
# Add to PATH: C:\terraform\
```

### Issue: "Error: Access Denied"
```powershell
# Check AWS credentials
aws sts get-caller-identity

# Reconfigure if needed
aws configure
```

### Issue: "Quota exceeded for ml.m5.xlarge"
```powershell
# Request quota increase
# AWS Console → Service Quotas → SageMaker
# OR change instance type in terraform.tfvars
sagemaker_training_instance_type = "ml.t3.medium"
```

### Issue: "S3 bucket already exists"
```powershell
# S3 bucket names are globally unique
# Edit terraform.tfvars and change project_name
project_name = "mlops-diabetes-yourcompanyname"
```

### Issue: "State lock failed"
```powershell
# Force unlock (only if no other Terraform process running)
terraform force-unlock <LOCK_ID>
```

More troubleshooting → [`docs/DEPLOYMENT_GUIDE.md#troubleshooting`](docs/DEPLOYMENT_GUIDE.md#troubleshooting)

## 🔄 Infrastructure Updates

### Adding VPC to Existing Infrastructure
```powershell
# 1. Edit terraform.tfvars
enable_vpc = true

# 2. Plan changes
terraform plan -var-file="terraform.tfvars" -out="tfplan"

# 3. Review plan (should show VPC resources being added)

# 4. Apply
terraform apply tfplan
```

### Changing Instance Counts
```powershell
# 1. Edit terraform.tfvars
sagemaker_endpoint_initial_instance_count = 3  # Changed from 2

# 2. Apply (no plan needed for simple changes)
terraform apply -var-file="terraform.tfvars"
```

## 📊 Monitoring & Alerts

After deployment, check:

1. **CloudWatch Dashboard**
   - AWS Console → CloudWatch → Dashboards
   - View: Training job metrics, endpoint latency, errors

2. **SNS Subscriptions**
   - Check your email for subscription confirmation
   - Click "Confirm subscription" link

3. **Budget Alerts**
   - AWS Console → Budgets
   - Verify: Budget amount and alert thresholds

4. **CloudTrail**
   - AWS Console → CloudTrail
   - Verify: Trail is logging events

## 🤝 Contributing

When making infrastructure changes:

1. **Create a branch**
   ```bash
   git checkout -b feature/add-vpc-endpoints
   ```

2. **Make changes to Terraform files**

3. **Test in DEV first**
   ```powershell
   .\deploy-infrastructure.ps1 -Environment dev -Action plan
   ```

4. **Document changes**
   - Update README.md
   - Update DEPLOYMENT_GUIDE.md
   - Add comments in Terraform files

5. **Create pull request**
   ```bash
   git add infrastructure/
   git commit -m "Add VPC endpoints for cost savings"
   git push origin feature/add-vpc-endpoints
   ```

## 📞 Support

- **Documentation**: Start with `docs/` directory
- **Issues**: Create GitHub issue
- **Email**: ml-ops@company.com
- **Slack**: #mlops-infrastructure

## 📝 License

MIT License - See LICENSE file

---

**Last Updated**: November 2025  
**Maintained By**: MLOps Team  
**Terraform Version**: 1.5+  
**AWS Provider Version**: 5.0+
