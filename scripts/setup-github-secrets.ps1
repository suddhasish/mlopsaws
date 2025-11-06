# Setup GitHub Secrets for MLOps Pipeline
# This script helps create IAM user and access keys for GitHub Actions

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "GitHub Actions AWS Setup Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if AWS CLI is installed
try {
    $awsVersion = aws --version
    Write-Host "✓ AWS CLI detected: $awsVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ AWS CLI not found. Please install AWS CLI first." -ForegroundColor Red
    Write-Host "  Download: https://aws.amazon.com/cli/" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# Get current AWS identity
Write-Host "Checking current AWS credentials..." -ForegroundColor Cyan
try {
    $identity = aws sts get-caller-identity --output json | ConvertFrom-Json
    $accountId = $identity.Account
    $currentUser = $identity.Arn
    
    Write-Host "✓ Connected to AWS Account: $accountId" -ForegroundColor Green
    Write-Host "  Current User: $currentUser" -ForegroundColor Gray
} catch {
    Write-Host "✗ Cannot connect to AWS. Please configure AWS CLI credentials." -ForegroundColor Red
    Write-Host "  Run: aws configure" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Step 1: Create IAM User for GitHub" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$iamUser = "github-actions-mlops"

# Check if user already exists
$userExists = aws iam get-user --user-name $iamUser 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ IAM user '$iamUser' already exists" -ForegroundColor Yellow
    $createNew = Read-Host "Do you want to create a new access key for this user? (y/n)"
    if ($createNew -ne "y") {
        Write-Host "Exiting..." -ForegroundColor Gray
        exit 0
    }
} else {
    Write-Host "Creating IAM user: $iamUser" -ForegroundColor Cyan
    aws iam create-user --user-name $iamUser
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ IAM user created successfully" -ForegroundColor Green
        
        # Attach policies
        Write-Host "Attaching IAM policies..." -ForegroundColor Cyan
        
        aws iam attach-user-policy `
            --user-name $iamUser `
            --policy-arn arn:aws:iam::aws:policy/AmazonSageMakerFullAccess
        
        aws iam attach-user-policy `
            --user-name $iamUser `
            --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess
        
        aws iam attach-user-policy `
            --user-name $iamUser `
            --policy-arn arn:aws:iam::aws:policy/IAMReadOnlyAccess
        
        Write-Host "✓ Policies attached" -ForegroundColor Green
    } else {
        Write-Host "✗ Failed to create IAM user" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Step 2: Create Access Key" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Create access key
Write-Host "Creating access key..." -ForegroundColor Cyan
$accessKeyJson = aws iam create-access-key --user-name $iamUser --output json

if ($LASTEXITCODE -eq 0) {
    $accessKey = $accessKeyJson | ConvertFrom-Json
    $accessKeyId = $accessKey.AccessKey.AccessKeyId
    $secretAccessKey = $accessKey.AccessKey.SecretAccessKey
    
    Write-Host "✓ Access key created successfully!" -ForegroundColor Green
    Write-Host ""
} else {
    Write-Host "✗ Failed to create access key" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Step 3: GitHub Secrets Configuration" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Get values from config.yaml
$configPath = ".\config\config.yaml"
if (Test-Path $configPath) {
    Write-Host "Reading configuration from config.yaml..." -ForegroundColor Cyan
    $config = Get-Content $configPath -Raw | ConvertFrom-Yaml
    $bucketName = "mlops-diabetes-dev-891807086260"
    $sagemakerRole = "arn:aws:iam::891807086260:role/service-role/AmazonSageMaker-ExecutionRole-20251026T145759"
} else {
    Write-Host "⚠ config.yaml not found, using default values" -ForegroundColor Yellow
    $bucketName = "mlops-diabetes-dev-891807086260"
    $sagemakerRole = "arn:aws:iam::891807086260:role/service-role/AmazonSageMaker-ExecutionRole-20251026T145759"
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Yellow
Write-Host "⚠ IMPORTANT: SAVE THESE VALUES NOW!" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Yellow
Write-Host ""
Write-Host "Add these secrets to GitHub repository:" -ForegroundColor White
Write-Host "https://github.com/suddhasish/mlopsaws/settings/secrets/actions" -ForegroundColor Cyan
Write-Host ""
Write-Host "-----------------------------------" -ForegroundColor Gray
Write-Host "Secret Name: AWS_ACCESS_KEY_ID" -ForegroundColor White
Write-Host "Value: $accessKeyId" -ForegroundColor Green
Write-Host ""
Write-Host "Secret Name: AWS_SECRET_ACCESS_KEY" -ForegroundColor White
Write-Host "Value: $secretAccessKey" -ForegroundColor Green
Write-Host "⚠ YOU CANNOT RETRIEVE THIS SECRET KEY AGAIN!" -ForegroundColor Red
Write-Host ""
Write-Host "Secret Name: AWS_ACCOUNT_ID" -ForegroundColor White
Write-Host "Value: $accountId" -ForegroundColor Green
Write-Host ""
Write-Host "Secret Name: S3_BUCKET_NAME" -ForegroundColor White
Write-Host "Value: $bucketName" -ForegroundColor Green
Write-Host ""
Write-Host "Secret Name: SAGEMAKER_EXECUTION_ROLE" -ForegroundColor White
Write-Host "Value: $sagemakerRole" -ForegroundColor Green
Write-Host "-----------------------------------" -ForegroundColor Gray
Write-Host ""

# Save to file
$secretsFile = "github-secrets-DO-NOT-COMMIT.txt"
$secretsContent = @"
GitHub Secrets for MLOps Pipeline
Generated: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

⚠ IMPORTANT: DO NOT COMMIT THIS FILE TO GIT!
⚠ Add these secrets to: https://github.com/suddhasish/mlopsaws/settings/secrets/actions

AWS_ACCESS_KEY_ID=$accessKeyId

AWS_SECRET_ACCESS_KEY=$secretAccessKey

AWS_ACCOUNT_ID=$accountId

S3_BUCKET_NAME=$bucketName

SAGEMAKER_EXECUTION_ROLE=$sagemakerRole

---
Instructions:
1. Go to: https://github.com/suddhasish/mlopsaws/settings/secrets/actions
2. Click "New repository secret" for each value above
3. Copy-paste the exact values (including = sign and everything after)
4. Delete this file after adding secrets to GitHub
5. Test: Push a commit and check GitHub Actions workflow
"@

$secretsContent | Out-File -FilePath $secretsFile -Encoding UTF8
Write-Host "✓ Secrets saved to: $secretsFile" -ForegroundColor Green
Write-Host "  ⚠ DELETE THIS FILE AFTER COPYING TO GITHUB!" -ForegroundColor Red
Write-Host ""

# Check if .gitignore includes the secrets file
$gitignorePath = ".\.gitignore"
if (Test-Path $gitignorePath) {
    $gitignoreContent = Get-Content $gitignorePath -Raw
    if ($gitignoreContent -notlike "*github-secrets*") {
        Write-Host "Adding secrets file to .gitignore..." -ForegroundColor Cyan
        Add-Content -Path $gitignorePath -Value "`n# GitHub secrets file`ngithub-secrets-DO-NOT-COMMIT.txt"
        Write-Host "✓ Added to .gitignore" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Next Steps" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Add secrets to GitHub (see above)" -ForegroundColor White
Write-Host "2. Delete file: $secretsFile" -ForegroundColor White
Write-Host "3. Test workflow:" -ForegroundColor White
Write-Host "   git commit --allow-empty -m 'Test: AWS credentials configured'" -ForegroundColor Gray
Write-Host "   git push origin main" -ForegroundColor Gray
Write-Host "4. Monitor: https://github.com/suddhasish/mlopsaws/actions" -ForegroundColor White
Write-Host ""
Write-Host "✓ Setup complete!" -ForegroundColor Green
