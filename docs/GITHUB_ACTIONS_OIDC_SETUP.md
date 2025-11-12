# GitHub Actions - AWS OIDC Authentication Setup

**More Secure Alternative to Access Keys**

## Why OIDC?

- ✅ No long-lived credentials in GitHub
- ✅ Automatic credential rotation
- ✅ Short-lived tokens (1 hour)
- ✅ Fine-grained permissions per workflow

## Setup Steps

### Step 1: Create OIDC Identity Provider in AWS

```bash
# Create OIDC provider
aws iam create-open-id-connect-provider \
  --url https://token.actions.githubusercontent.com \
  --client-id-list sts.amazonaws.com \
  --thumbprint-list 6938fd4d98bab03faadb97b34396831e3780aea1
```

### Step 2: Create IAM Role for GitHub Actions

```bash
# Create trust policy
cat > github-actions-trust-policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::891807086260:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
        },
        "StringLike": {
          "token.actions.githubusercontent.com:sub": "repo:suddhasish/mlopsaws:*"
        }
      }
    }
  ]
}
EOF

# Create role
aws iam create-role \
  --role-name GitHubActionsMLOpsRole \
  --assume-role-policy-document file://github-actions-trust-policy.json

# Attach policies
aws iam attach-role-policy \
  --role-name GitHubActionsMLOpsRole \
  --policy-arn arn:aws:iam::aws:policy/AmazonSageMakerFullAccess

aws iam attach-role-policy \
  --role-name GitHubActionsMLOpsRole \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess
```

### Step 3: Update GitHub Actions Workflow

Replace the AWS credentials step with:

```yaml
- name: Configure AWS credentials
  uses: aws-actions/configure-aws-credentials@v4
  with:
    role-to-assume: arn:aws:iam::891807086260:role/GitHubActionsMLOpsRole
    aws-region: us-east-1
```

Remove these from secrets:
- AWS_ACCESS_KEY_ID (no longer needed)
- AWS_SECRET_ACCESS_KEY (no longer needed)

### Step 4: Add Permissions to Workflow

At the top of workflow file, add:

```yaml
permissions:
  id-token: write   # Required for OIDC
  contents: read
```

## Benefits

- **Automatic rotation:** Tokens expire after 1 hour
- **No secret management:** No access keys to rotate
- **Audit trail:** CloudTrail shows which workflow assumed the role
- **Least privilege:** Different roles per environment

## Testing

```bash
# Test the workflow after OIDC setup
# It should authenticate without any secrets
```

## Migration Checklist

- [ ] Create OIDC provider in AWS
- [ ] Create IAM role with trust policy
- [ ] Attach necessary policies to role
- [ ] Update workflow to use role-to-assume
- [ ] Add permissions block to workflow
- [ ] Test workflow run
- [ ] Delete old AWS_ACCESS_KEY_ID secret
- [ ] Delete old AWS_SECRET_ACCESS_KEY secret
- [ ] Delete IAM user access keys (if created specifically for GitHub)

## References

- [AWS OIDC Documentation](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-amazon-web-services)
- [AWS Actions Configure Credentials](https://github.com/aws-actions/configure-aws-credentials)
