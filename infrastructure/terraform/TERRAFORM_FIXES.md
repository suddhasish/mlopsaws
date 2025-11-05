# Terraform Configuration Fixes

## Issues Fixed

### 1. ✅ Missing `aws_region` Variable
**Error:** `Reference to undeclared input variable "aws_region"`

**Fix:** Added `aws_region` variable to `variables.tf`:
```hcl
variable "aws_region" {
  description = "AWS region for resources (alias for compatibility)"
  type        = string
  default     = "us-east-1"
}
```

**Location:** `infrastructure/terraform/variables.tf` (line ~26)

---

### 2. ✅ Wrong SNS Topic Output Name
**Error:** `This object does not have an attribute named "sns_topic_arn"`

**Fix:** Changed from `module.monitoring.sns_topic_arn` to `module.monitoring.alerts_topic_arn`

The monitoring module outputs `alerts_topic_arn`, not `sns_topic_arn`.

**Location:** `infrastructure/terraform/modules.tf` (line 107)

**Before:**
```hcl
sns_topic_arns = [module.monitoring.sns_topic_arn]
```

**After:**
```hcl
sns_topic_arns = [module.monitoring.alerts_topic_arn]
```

---

### 3. ✅ Unsupported Resource Type
**Error:** `The provider hashicorp/aws does not support resource type "aws_sagemaker_model_quality_job_definition"`

**Fix:** Commented out the entire resource block (lines 89-154 in `modules/sagemaker/main.tf`)

**Reason:** 
- This resource type is not available in AWS Terraform Provider 5.0
- Model monitoring will be configured via Python SDK instead (see `src/monitoring/model_monitor.py`)

**Alternative Approach:**
Model monitoring should be set up using SageMaker Python SDK after deployment:

```python
from sagemaker.model_monitor import DefaultModelMonitor

monitor = DefaultModelMonitor(
    role=sagemaker_role,
    instance_type='ml.m5.large',
    instance_count=1,
    volume_size_in_gb=20,
    max_runtime_in_seconds=3600,
)

monitor.create_monitoring_schedule(
    endpoint_name='diabetes-classifier-prod',
    schedule_cron_expression='cron(0 * * * ? *)',
)
```

---

## How to Apply These Fixes

### Step 1: Verify Configuration
```powershell
cd "d:\MLOPS\MLOPS-AWS\mlops AWS sagemaker\infrastructure\terraform"

# Initialize Terraform (if not already done)
terraform init

# Validate configuration
terraform validate
```

### Step 2: Plan Infrastructure
```powershell
# Preview changes for dev environment
terraform plan -var-file="environments/dev/terraform.tfvars"
```

### Step 3: Apply Infrastructure
```powershell
# Apply changes
terraform apply -var-file="environments/dev/terraform.tfvars" -auto-approve
```

---

## What Gets Created

With these fixes, Terraform will create:

✅ **S3 Bucket:** `mlops-diabetes-dev-891807086260`
✅ **IAM Roles:** SageMaker execution role with necessary permissions
✅ **CloudWatch Log Groups:** For training jobs and endpoints
✅ **SNS Topics:** For alerts and critical alerts
✅ **CloudWatch Alarms:** Model invocation errors, latency (if monitoring enabled)
✅ **Budget Alerts:** Cost tracking at 80% and 100% thresholds
✅ **Model Package Group:** For SageMaker Model Registry (if enabled)

❌ **NOT Created (Commented Out):**
- Model Quality Job Definition (use Python SDK instead)

---

## Environment-Specific Configuration

### Dev Environment (`environments/dev/terraform.tfvars`)
- **Bucket:** `mlops-diabetes-dev-891807086260`
- **VPC:** Disabled (uses default VPC)
- **Monitoring:** Disabled to save costs
- **Spot Instances:** Enabled (90% savings)
- **Budget:** $60/month

### To Enable Monitoring Later
Set in `terraform.tfvars`:
```hcl
enable_sagemaker_monitoring = true
sagemaker_endpoint_name     = "diabetes-classifier-dev"
```

Then configure monitoring via Python:
```powershell
python src/monitoring/model_monitor.py --endpoint-name diabetes-classifier-dev --create-baseline
```

---

## Cost Estimate (After Terraform Apply)

| Resource | Cost |
|----------|------|
| S3 Storage (first 50GB) | ~$1/month |
| CloudWatch Logs (7-day retention) | ~$0.50/month |
| SNS Topics | Free (< 1,000 emails) |
| Budget Alerts | Free |
| **Total Infrastructure** | **~$1.50/month** |

**Note:** Training/inference costs are separate and billed per usage.

---

## Troubleshooting

### Issue: "Terraform not found"
**Solution:** Install Terraform
```powershell
# Using Chocolatey
choco install terraform

# Or download from: https://www.terraform.io/downloads
```

### Issue: "Access Denied" when creating resources
**Solution:** Verify AWS credentials
```powershell
aws sts get-caller-identity
aws configure list
```

### Issue: "Bucket already exists"
**Solution:** 
1. Check if bucket exists: `aws s3 ls s3://mlops-diabetes-dev-891807086260`
2. If it exists, import it into Terraform state:
```powershell
terraform import module.s3.aws_s3_bucket.data mlops-diabetes-dev-891807086260
```

---

## Next Steps

1. ✅ **Apply Terraform** → Creates infrastructure
2. ✅ **Set GitHub Secrets** → Enables CI/CD
3. ✅ **Push to main** → Triggers automated pipeline
4. ⏭️ **Monitor in SageMaker Console** → View training progress
5. ⏭️ **Deploy model** → After training completes
6. ⏭️ **Set up monitoring** → Via Python SDK (not Terraform)

---

## Files Modified

1. `infrastructure/terraform/variables.tf` - Added `aws_region` variable
2. `infrastructure/terraform/modules.tf` - Fixed SNS topic reference
3. `infrastructure/terraform/modules/sagemaker/main.tf` - Commented out unsupported resource

## Verification Checklist

- [x] All variables declared
- [x] All module outputs exist
- [x] No unsupported resources
- [ ] `terraform validate` passes (requires Terraform installed)
- [ ] `terraform plan` shows expected resources
- [ ] `terraform apply` creates infrastructure successfully
