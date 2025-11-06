# GitHub Secrets Configuration Guide

## Required Secrets for Each Environment

### **DEV Environment** (Current Setup)

Add these secrets to your GitHub repository:

```
Repository: https://github.com/suddhasish/mlopsaws
Path: Settings → Secrets and variables → Actions → New repository secret
```

| Secret Key | Secret Value | Description |
|------------|--------------|-------------|
| `AWS_ROLE_ARN` | `arn:aws:iam::891807086260:role/GitHubActions-MLOps-Dev` | GitHub Actions OIDC role for AWS authentication |
| `SAGEMAKER_EXECUTION_ROLE` | `arn:aws:iam::891807086260:role/service-role/AmazonSageMaker-ExecutionRole-20251026T145759` | SageMaker execution role for pipeline |
| `S3_BUCKET_NAME` | `mlops-diabetes-dev-891807086260` | S3 bucket for data and model artifacts |
| `AWS_ACCOUNT_ID` | `891807086260` | AWS account ID |

---

### **STAGING Environment** (Future Setup)

When you create staging environment, add these secrets:

| Secret Key | Secret Value | Description |
|------------|--------------|-------------|
| `STAGING_AWS_ROLE_ARN` | `arn:aws:iam::<STAGING_ACCOUNT>:role/GitHubActions-MLOps-Staging` | Staging OIDC role |
| `STAGING_SAGEMAKER_EXECUTION_ROLE` | `arn:aws:iam::<STAGING_ACCOUNT>:role/SageMakerExecutionRole-Staging` | Staging SageMaker role |
| `STAGING_S3_BUCKET_NAME` | `mlops-diabetes-staging` | Staging S3 bucket |
| `STAGING_AWS_ACCOUNT_ID` | `<STAGING_ACCOUNT_ID>` | Staging AWS account ID |

---

### **PRODUCTION Environment** (Future Setup)

For production deployment, add these secrets:

| Secret Key | Secret Value | Description |
|------------|--------------|-------------|
| `PROD_AWS_ROLE_ARN` | `arn:aws:iam::<PROD_ACCOUNT>:role/GitHubActions-MLOps-Prod` | Production OIDC role |
| `PROD_SAGEMAKER_EXECUTION_ROLE` | `arn:aws:iam::<PROD_ACCOUNT>:role/SageMakerExecutionRole-Prod` | Production SageMaker role |
| `PROD_S3_BUCKET_NAME` | `mlops-diabetes-production` | Production S3 bucket |
| `PROD_AWS_ACCOUNT_ID` | `<PROD_ACCOUNT_ID>` | Production AWS account ID |
| `PROD_SNS_TOPIC_ARN` | `arn:aws:sns:us-east-1:<PROD_ACCOUNT>:mlops-prod-alerts` | (Optional) SNS topic for alerts |

---

## How Secrets Are Used

### GitHub Actions Workflow
```yaml
env:
  SAGEMAKER_EXECUTION_ROLE: ${{ secrets.SAGEMAKER_EXECUTION_ROLE }}
  S3_BUCKET_NAME: ${{ secrets.S3_BUCKET_NAME }}
  AWS_ACCOUNT_ID: ${{ secrets.AWS_ACCOUNT_ID }}
```

### Pipeline Runtime (training_pipeline.py)
```python
# Environment variables take precedence over config files
self.role = os.getenv("SAGEMAKER_EXECUTION_ROLE") or self.config["sagemaker"]["role"]
self.bucket = os.getenv("S3_BUCKET_NAME") or self.config["s3"]["bucket_name"]
account_id = os.getenv("AWS_ACCOUNT_ID") or self.config["aws"]["account_id"]
```

---

## Configuration File Strategy

### ✅ **DO** Keep in `environment_config.yaml`:
- Instance types and sizes
- Scaling configurations
- Monitoring schedules
- Evaluation thresholds
- Training hyperparameters
- Resource tags
- Placeholder values (e.g., `PLACEHOLDER_ACCOUNT_ID`)

### ❌ **DON'T** Keep in Config Files:
- AWS Account IDs
- IAM Role ARNs
- S3 Bucket names (if they contain account IDs)
- API keys or credentials
- Any sensitive information

---

## Priority Order (How Values Are Selected)

```
1. Environment Variables (from GitHub Secrets)  ← HIGHEST PRIORITY
   ↓ (if not set)
2. environment_config.yaml[environment]
   ↓ (if not set)  
3. config.yaml (base defaults)  ← LOWEST PRIORITY
```

---

## Testing Locally vs CI/CD

### **Local Development** (No Secrets)
```bash
# Uses values from config files
python pipelines/training_pipeline.py --config config/config.yaml --environment dev
```

### **GitHub Actions** (Uses Secrets)
```yaml
- name: Create/Update SageMaker Pipeline
  env:
    SAGEMAKER_EXECUTION_ROLE: ${{ secrets.SAGEMAKER_EXECUTION_ROLE }}
    S3_BUCKET_NAME: ${{ secrets.S3_BUCKET_NAME }}
    AWS_ACCOUNT_ID: ${{ secrets.AWS_ACCOUNT_ID }}
  run: |
    python pipelines/training_pipeline.py --config config/config.yaml
```

---

## Multi-Environment Setup

For multiple environments, modify your workflow to use environment-specific secrets:

```yaml
jobs:
  deploy-staging:
    environment: staging  # GitHub environment
    steps:
      - name: Deploy to Staging
        env:
          SAGEMAKER_EXECUTION_ROLE: ${{ secrets.STAGING_SAGEMAKER_EXECUTION_ROLE }}
          S3_BUCKET_NAME: ${{ secrets.STAGING_S3_BUCKET_NAME }}
          AWS_ACCOUNT_ID: ${{ secrets.STAGING_AWS_ACCOUNT_ID }}
        run: |
          python pipelines/training_pipeline.py --environment staging
  
  deploy-production:
    environment: production  # Requires manual approval
    steps:
      - name: Deploy to Production
        env:
          SAGEMAKER_EXECUTION_ROLE: ${{ secrets.PROD_SAGEMAKER_EXECUTION_ROLE }}
          S3_BUCKET_NAME: ${{ secrets.PROD_S3_BUCKET_NAME }}
          AWS_ACCOUNT_ID: ${{ secrets.PROD_AWS_ACCOUNT_ID }}
        run: |
          python pipelines/training_pipeline.py --environment production
```

---

## Security Best Practices

✅ **DO:**
- Use GitHub Environments for staging/production (enables manual approval)
- Rotate secrets regularly
- Use separate AWS accounts for dev/staging/prod
- Use OIDC authentication (temporary credentials) over access keys
- Limit secret access with branch protection rules

❌ **DON'T:**
- Commit secrets to Git (even in comments)
- Use production secrets in dev/staging
- Share secrets across multiple repositories
- Log secret values in CI/CD output
- Store secrets in config files

---

## Troubleshooting

### Error: "Context access might be invalid: SAGEMAKER_EXECUTION_ROLE"
**Cause:** Secret doesn't exist in GitHub repository  
**Fix:** Add the secret in GitHub Settings → Secrets and variables → Actions

### Error: "Credentials could not be loaded"
**Cause:** `AWS_ROLE_ARN` secret not set or OIDC not configured  
**Fix:** Verify OIDC provider exists in AWS IAM and `AWS_ROLE_ARN` secret is correct

### Pipeline uses wrong values
**Cause:** Environment variables not passed to Python process  
**Fix:** Check workflow has `env:` block with secrets before `run:` command

---

## Quick Setup Checklist

- [ ] Add `AWS_ROLE_ARN` secret to GitHub
- [ ] Add `SAGEMAKER_EXECUTION_ROLE` secret to GitHub
- [ ] Add `S3_BUCKET_NAME` secret to GitHub
- [ ] Add `AWS_ACCOUNT_ID` secret to GitHub
- [ ] Verify `environment_config.yaml` has placeholders (no real values)
- [ ] Test workflow execution with secrets
- [ ] Verify pipeline logs show correct values being used

---

**Last Updated:** November 6, 2025  
**Repository:** suddhasish/mlopsaws
