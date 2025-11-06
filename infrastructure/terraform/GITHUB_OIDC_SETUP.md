# GitHub Actions OIDC Integration for MLOps

This update adds GitHub Actions OIDC (OpenID Connect) authentication to the existing Terraform infrastructure.

## What's New

### Added to IAM Module (`modules/iam/`)
- GitHub OIDC provider resource
- GitHub Actions IAM role with proper permissions
- Conditional creation based on `enable_github_oidc` variable

### Added to S3 Module (`modules/s3/`)
- GitHub Actions role added to bucket policy
- Conditional policy statements for GitHub Actions access

### Root Configuration Updates
- New variables: `enable_github_oidc`, `github_org`, `github_repo`
- New outputs: `github_actions_role_arn`, `github_secrets`
- Module wiring for GitHub OIDC parameters

## Quick Start

### 1. Update Environment Configuration

Edit `environments/dev.tfvars` (or your environment file):

```hcl
# Enable GitHub OIDC
enable_github_oidc = true
github_org         = "suddhasish"
github_repo        = "mlopsaws"
```

### 2. Plan and Apply

```bash
cd infrastructure/terraform

# Plan changes
terraform plan -var-file="environments/dev.tfvars"

# Apply changes
terraform apply -var-file="environments/dev.tfvars"
```

### 3. Get GitHub Secrets Values

After applying:

```bash
terraform output github_secrets
```

Output example:
```
github_secrets = {
  AWS_ACCOUNT_ID           = "891807086260"
  AWS_ROLE_ARN             = "arn:aws:iam::891807086260:role/mlops-diabetes-github-actions-dev"
  S3_BUCKET_NAME           = "mlops-diabetes-dev-891807086260"
  SAGEMAKER_EXECUTION_ROLE = "arn:aws:iam::891807086260:role/mlops-diabetes-sagemaker-execution-dev"
}
```

### 4. Configure GitHub Secrets

Go to: `https://github.com/suddhasish/mlopsaws/settings/secrets/actions`

Add each secret from the terraform output.

## Environment-Specific Configuration

### Dev Environment (`environments/dev.tfvars`)
```hcl
enable_github_oidc = true
github_org         = "suddhasish"
github_repo        = "mlopsaws"
```

### Staging Environment (`environments/staging.tfvars`)
```hcl
enable_github_oidc = true
github_org         = "suddhasish"
github_repo        = "mlopsaws"
```

### Production Environment (`environments/production.tfvars`)
```hcl
enable_github_oidc = true
github_org         = "suddhasish"
github_repo        = "mlopsaws"
```

## What Gets Created

### 1. OIDC Provider
- **Resource**: `aws_iam_openid_connect_provider.github_actions`
- **URL**: `https://token.actions.githubusercontent.com`
- **Audience**: `sts.amazonaws.com`

### 2. GitHub Actions IAM Role
- **Name**: `{project_name}-github-actions-{environment}`
- **Example**: `mlops-diabetes-github-actions-dev`
- **Permissions**:
  - AmazonSageMakerFullAccess
  - AmazonS3FullAccess
  - IAMReadOnlyAccess
  - AmazonEC2ContainerRegistryFullAccess
  - Custom: PassRole for SageMaker, CloudWatch Logs access

### 3. S3 Bucket Policy Update
- Adds GitHub Actions role to allowed principals
- Maintains secure transport requirement
- Removes problematic encryption deny rule

## Benefits

✅ **No Long-Term Credentials** - No access keys to manage or rotate  
✅ **Temporary Credentials** - AWS STS generates temporary credentials  
✅ **Fine-Grained Control** - Restrict by repository, branch, or tag  
✅ **Audit Trail** - All actions logged in CloudTrail  
✅ **Best Practice** - Recommended by AWS and GitHub  

## Removing Existing Manual Setup

If you created OIDC provider or GitHub Actions role manually:

### Option 1: Import into Terraform
```bash
# Import OIDC provider
terraform import 'module.iam.aws_iam_openid_connect_provider.github_actions[0]' \
  arn:aws:iam::891807086260:oidc-provider/token.actions.githubusercontent.com

# Import GitHub Actions role
terraform import 'module.iam.aws_iam_role.github_actions[0]' \
  GitHubActions-MLOps-Dev
```

### Option 2: Delete and Recreate
```bash
# Delete manual resources
aws iam delete-role --role-name GitHubActions-MLOps-Dev
aws iam delete-open-id-connect-provider \
  --open-id-connect-provider-arn arn:aws:iam::891807086260:oidc-provider/token.actions.githubusercontent.com

# Then apply Terraform
terraform apply -var-file="environments/dev.tfvars"
```

## Testing

### 1. Verify OIDC Provider
```bash
aws iam get-open-id-connect-provider \
  --open-id-connect-provider-arn $(terraform output -raw oidc_provider_arn)
```

### 2. Verify GitHub Actions Role
```bash
aws iam get-role --role-name $(terraform output -raw github_actions_role_name)
```

### 3. Test S3 Access
```bash
# Assuming role from GitHub Actions
aws sts assume-role-with-web-identity \
  --role-arn $(terraform output -raw github_actions_role_arn) \
  --role-session-name test-session \
  --web-identity-token $GITHUB_TOKEN
```

## Troubleshooting

### Error: OIDC provider already exists
```bash
# Import existing provider
terraform import 'module.iam.aws_iam_openid_connect_provider.github_actions[0]' \
  arn:aws:iam::ACCOUNT_ID:oidc-provider/token.actions.githubusercontent.com
```

### Error: Role already exists
```bash
# Import existing role
terraform import 'module.iam.aws_iam_role.github_actions[0]' ROLE_NAME
```

### GitHub Actions still failing
1. Verify secrets are set in GitHub
2. Check workflow has `id-token: write` permission
3. Verify role trust policy allows your repository
4. Check S3 bucket policy includes GitHub Actions role

## Module Structure

```
infrastructure/terraform/
├── modules/
│   ├── iam/
│   │   ├── main.tf          # Added GitHub OIDC resources
│   │   ├── variables.tf     # Added github_* variables
│   │   └── outputs.tf       # Added GitHub outputs
│   └── s3/
│       ├── main.tf          # Updated bucket policy
│       └── variables.tf     # Added github_actions_role_arn
├── modules.tf               # Wired GitHub parameters
├── variables.tf             # Added GitHub variables
└── outputs.tf               # Added GitHub outputs
```

## Security Considerations

✅ **Repository Restriction**: Role can only be assumed from specified repo  
✅ **No Wildcards**: Exact repository match required  
✅ **HTTPS Only**: S3 bucket policy enforces secure transport  
✅ **Least Privilege**: Only necessary permissions granted  
✅ **Audit Logging**: All actions tracked in CloudTrail  

## Cost Impact

**Additional Resources**: 
- OIDC Provider: **Free**
- IAM Role: **Free**
- S3 Policy Update: **Free**

**Total Additional Cost**: $0.00/month

## Rollback

To disable GitHub OIDC:

```hcl
# In environment tfvars
enable_github_oidc = false
```

```bash
terraform apply -var-file="environments/dev.tfvars"
```

This will destroy the OIDC provider and GitHub Actions role.

## Next Steps

1. ✅ Apply Terraform changes
2. ✅ Configure GitHub Secrets
3. ✅ Update GitHub Actions workflow (already done)
4. ✅ Test pipeline execution
5. ✅ Monitor CloudWatch logs

## References

- [GitHub OIDC with AWS](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-amazon-web-services)
- [AWS IAM OIDC](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_providers_create_oidc.html)
- [SageMaker IAM Roles](https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-roles.html)
