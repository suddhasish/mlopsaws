# Fix S3 Access Denied Error for GitHub Actions Role
# This script adds S3 permissions to the GitHubActions-MLOps-Dev role

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Fix S3 Access Permissions" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$roleName = "GitHubActions-MLOps-Dev"
$bucketName = "mlops-diabetes-dev-891807086260"

# Step 1: Check current role policies
Write-Host "Step 1: Checking current role policies..." -ForegroundColor Cyan
Write-Host ""

# Try with Python/boto3 if AWS CLI not available
$pythonScript = @"
import boto3
import json

iam = boto3.client('iam')
s3 = boto3.client('s3')
role_name = '$roleName'
bucket_name = '$bucketName'

print('Current attached policies:')
try:
    policies = iam.list_attached_role_policies(RoleName=role_name)
    for policy in policies['AttachedPolicies']:
        print(f"  - {policy['PolicyName']}: {policy['PolicyArn']}")
except Exception as e:
    print(f"Error: {e}")
    exit(1)

print('\nStep 2: Creating inline policy for S3 access...')

# Create inline policy for S3 access
policy_document = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:PutObject",
                "s3:GetObject",
                "s3:DeleteObject",
                "s3:ListBucket"
            ],
            "Resource": [
                f"arn:aws:s3:::{bucket_name}",
                f"arn:aws:s3:::{bucket_name}/*"
            ]
        }
    ]
}

try:
    iam.put_role_policy(
        RoleName=role_name,
        PolicyName='S3BucketAccess',
        PolicyDocument=json.dumps(policy_document)
    )
    print('✓ Inline policy added successfully')
except Exception as e:
    print(f'Error adding policy: {e}')
    exit(1)

print('\nStep 3: Checking S3 bucket policy...')
try:
    bucket_policy = s3.get_bucket_policy(Bucket=bucket_name)
    print('Current bucket policy exists - checking for explicit denies...')
    policy = json.loads(bucket_policy['Policy'])
    
    has_deny = False
    for statement in policy.get('Statement', []):
        if statement.get('Effect') == 'Deny':
            has_deny = True
            print(f"  ⚠ Found DENY statement: {statement}")
    
    if not has_deny:
        print('  ✓ No explicit deny statements found')
except s3.exceptions.NoSuchBucketPolicy:
    print('  ✓ No bucket policy set (good - no restrictions)')
except Exception as e:
    print(f'  Error checking bucket policy: {e}')

print('\nStep 4: Verifying permissions...')
try:
    # Try to list bucket
    s3.list_objects_v2(Bucket=bucket_name, MaxKeys=1)
    print('✓ Can list bucket objects')
    
    # Try to put test object
    s3.put_object(Bucket=bucket_name, Key='test-access.txt', Body=b'test')
    print('✓ Can upload objects')
    
    # Clean up test object
    s3.delete_object(Bucket=bucket_name, Key='test-access.txt')
    print('✓ Can delete objects')
    
    print('\n✓ All S3 permissions verified!')
except Exception as e:
    print(f'\n✗ Permission test failed: {e}')
    print('\nPossible solutions:')
    print('1. Check if bucket policy has explicit deny')
    print('2. Attach AmazonS3FullAccess managed policy to role')
    print('3. Check SCPs (Service Control Policies) in AWS Organizations')
"@

# Save and run Python script
$scriptPath = "temp_fix_s3_permissions.py"
$pythonScript | Out-File -FilePath $scriptPath -Encoding UTF8

Write-Host "Running permission fix script..." -ForegroundColor Cyan
python $scriptPath

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "✓ Permissions Fixed!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor White
    Write-Host "1. Go to GitHub Actions: https://github.com/suddhasish/mlopsaws/actions" -ForegroundColor Gray
    Write-Host "2. Click on the failed workflow run" -ForegroundColor Gray
    Write-Host "3. Click 'Re-run all jobs'" -ForegroundColor Gray
} else {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "✗ Error fixing permissions" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Manual fix required. See options below:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "OPTION 1: Attach managed policy (easiest)" -ForegroundColor Cyan
    Write-Host "python -c `"import boto3; iam = boto3.client('iam'); iam.attach_role_policy(RoleName='$roleName', PolicyArn='arn:aws:iam::aws:policy/AmazonS3FullAccess')`"" -ForegroundColor Gray
    Write-Host ""
    Write-Host "OPTION 2: Check bucket policy for explicit deny" -ForegroundColor Cyan
    Write-Host "python -c `"import boto3, json; s3 = boto3.client('s3'); print(json.dumps(json.loads(s3.get_bucket_policy(Bucket='$bucketName')['Policy']), indent=2))`"" -ForegroundColor Gray
}

# Cleanup
Remove-Item $scriptPath -ErrorAction SilentlyContinue

Write-Host ""
