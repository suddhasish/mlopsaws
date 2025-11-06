# Environment Variables Reference

This document lists all environment variables used across the MLOps pipeline for overriding sensitive configuration values.

## GitHub Secrets Required

Configure these secrets in your GitHub repository settings (`Settings` → `Secrets and variables` → `Actions`):

### Core AWS Configuration

| Secret Name | Description | Example Value | Used In |
|------------|-------------|---------------|---------|
| `AWS_ROLE_ARN` | IAM role ARN for GitHub Actions OIDC | `arn:aws:iam::891807086260:role/GitHubActionsRole` | All jobs |
| `AWS_ACCOUNT_ID` | AWS Account ID | `891807086260` | Pipeline execution |
| `S3_BUCKET_NAME` | S3 bucket for ML artifacts | `mlops-diabetes-dev-891807086260` | Data upload, Pipeline, Monitoring |
| `SAGEMAKER_EXECUTION_ROLE` | SageMaker execution role ARN | `arn:aws:iam::891807086260:role/service-role/AmazonSageMaker-ExecutionRole-*` | All SageMaker operations |

## Environment Variables in Python Scripts

### Deployment (`src/deployment/deploy.py`)

These environment variables override values from `config/config.yaml`:

| Variable | Config Path | Default from Config | Description |
|----------|-------------|---------------------|-------------|
| `AWS_REGION` | `aws.region` | `us-east-1` | AWS region for deployment |
| `SAGEMAKER_ROLE_ARN` | `sagemaker.role` | From config | IAM role for SageMaker |
| `MODEL_PACKAGE_GROUP_NAME` | `sagemaker.model_registry.model_package_group_name` | `diabetes-classifier-model-group` | Model Registry group |
| `ENDPOINT_INSTANCE_TYPE` | `sagemaker.endpoint.instance_type` | `ml.m5.xlarge` | EC2 instance type for endpoint |

**Usage Example:**
```bash
# Local development (uses config.yaml)
python src/deployment/deploy.py --config config/config.yaml

# CI/CD (uses environment variables)
export AWS_REGION=us-east-1
export SAGEMAKER_ROLE_ARN=arn:aws:iam::123456789012:role/SageMakerRole
export MODEL_PACKAGE_GROUP_NAME=my-model-group
export ENDPOINT_INSTANCE_TYPE=ml.m5.xlarge
python src/deployment/deploy.py --config config/config.yaml
```

### Monitoring (`src/monitoring/model_monitor.py`)

| Variable | Config Path | Default from Config | Description |
|----------|-------------|---------------------|-------------|
| `AWS_REGION` | `aws.region` | `us-east-1` | AWS region for monitoring |
| `SAGEMAKER_ROLE_ARN` | `sagemaker.role` | From config | IAM role for SageMaker |
| `S3_BUCKET` | `s3.bucket_name` | From config | S3 bucket for monitoring outputs |

**Usage Example:**
```bash
# Enable data capture
export AWS_REGION=us-east-1
export SAGEMAKER_ROLE_ARN=arn:aws:iam::123456789012:role/SageMakerRole
export S3_BUCKET=mlops-bucket
python src/monitoring/model_monitor.py --config config/config.yaml --endpoint-name my-endpoint --enable-capture
```

### Training Pipeline (`pipelines/training_pipeline.py`)

| Variable | Config Path | Description |
|----------|-------------|-------------|
| `SAGEMAKER_EXECUTION_ROLE` | `sagemaker.role` | SageMaker execution role |
| `S3_BUCKET_NAME` | `s3.bucket_name` | S3 bucket for training data |
| `AWS_ACCOUNT_ID` | `aws.account_id` | AWS account ID |

## GitHub Actions Workflow Configuration

The workflow automatically injects these environment variables from GitHub Secrets:

### Deploy Job
```yaml
- name: Deploy approved model
  env:
    AWS_REGION: ${{ env.AWS_REGION }}
    SAGEMAKER_ROLE_ARN: ${{ secrets.SAGEMAKER_EXECUTION_ROLE }}
    MODEL_PACKAGE_GROUP_NAME: diabetes-classifier-model-group
    ENDPOINT_INSTANCE_TYPE: ml.m5.xlarge
  run: |
    python src/deployment/deploy.py --config config/config.yaml
```

### Monitoring Job
```yaml
- name: Enable data capture
  env:
    AWS_REGION: ${{ env.AWS_REGION }}
    SAGEMAKER_ROLE_ARN: ${{ secrets.SAGEMAKER_EXECUTION_ROLE }}
    S3_BUCKET: ${{ secrets.S3_BUCKET_NAME }}
  run: |
    python src/monitoring/model_monitor.py --config config/config.yaml
```

## Benefits of This Approach

1. **Security**: Sensitive values never committed to repository
2. **Flexibility**: Different values per environment (dev/staging/prod)
3. **Immutability**: `config.yaml` never modified during execution
4. **CI/CD Friendly**: Seamless secret injection from GitHub Secrets
5. **12-Factor Compliance**: Configuration via environment variables
6. **Auditability**: Clear separation between code and configuration

## Local Development

For local development, you can either:

1. **Use config.yaml** (default behavior):
   ```bash
   python src/deployment/deploy.py --config config/config.yaml
   ```

2. **Set environment variables** (overrides config.yaml):
   ```bash
   export AWS_REGION=us-east-1
   export SAGEMAKER_ROLE_ARN=arn:aws:iam::123456789012:role/MyRole
   python src/deployment/deploy.py --config config/config.yaml
   ```

3. **Use a .env file** (requires python-dotenv):
   ```bash
   # .env file
   AWS_REGION=us-east-1
   SAGEMAKER_ROLE_ARN=arn:aws:iam::123456789012:role/MyRole
   
   # Load and run
   python -c "from dotenv import load_dotenv; load_dotenv()"
   python src/deployment/deploy.py
   ```

## Testing Environment Variable Override

You can verify that environment variables are being used:

```bash
# Test deployment with custom values
export AWS_REGION=us-west-2
export SAGEMAKER_ROLE_ARN=arn:aws:iam::123456789012:role/TestRole
python src/deployment/deploy.py --config config/config.yaml

# Check logs for confirmation:
# INFO - Using AWS Region: us-west-2
# INFO - Using SageMaker Role: arn:aws:iam::123456789012:role/TestRole
```

## Troubleshooting

### Environment Variable Not Working

1. Check if the variable is exported:
   ```bash
   echo $AWS_REGION
   ```

2. Verify the script is reading it:
   ```python
   import os
   print(os.environ.get('AWS_REGION'))
   ```

3. Check GitHub Secrets configuration in repository settings

### Config.yaml Still Being Used

Environment variables take precedence. If config.yaml values are being used:
- Ensure environment variables are exported before running the script
- Check for typos in variable names (they are case-sensitive)
- Verify the script includes the `os.environ.get()` logic

## Migration from Dynamic Config Modification

**Before** (❌ Bad - modifies config.yaml):
```yaml
- name: Update configuration
  run: |
    python -c "
    import yaml
    config = yaml.safe_load(open('config/config.yaml'))
    config['sagemaker']['role'] = '$SAGEMAKER_ROLE'
    yaml.dump(config, open('config/config.yaml', 'w'))
    "
```

**After** (✅ Good - uses environment variables):
```yaml
- name: Deploy model
  env:
    SAGEMAKER_ROLE_ARN: ${{ secrets.SAGEMAKER_EXECUTION_ROLE }}
  run: |
    python src/deployment/deploy.py --config config/config.yaml
```

## Related Documentation

- [GitHub OIDC Setup](../infrastructure/terraform/GITHUB_OIDC_SETUP.md)
- [AWS Secrets Manager Integration](./AWS_SECRETS_MANAGER.md) (if applicable)
- [Configuration Management](./CONFIGURATION.md)
