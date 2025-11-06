# GitHub Actions OIDC Setup Script
# Configures AWS IAM for OIDC authentication with GitHub Actions

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "GitHub Actions OIDC Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$githubOrg = "suddhasish"
$githubRepo = "mlopsaws"
$roleName = "GitHubActionsMLOpsRole"
$accountId = "891807086260"

# Check AWS CLI
try {
    $identity = aws sts get-caller-identity --output json | ConvertFrom-Json
    $currentAccountId = $identity.Account
    Write-Host "✓ Connected to AWS Account: $currentAccountId" -ForegroundColor Green
    
    if ($currentAccountId -ne $accountId) {
        Write-Host "⚠ Warning: Expected account $accountId but connected to $currentAccountId" -ForegroundColor Yellow
        $continue = Read-Host "Continue anyway? (y/n)"
        if ($continue -ne "y") { exit 0 }
    }
} catch {
    Write-Host "✗ AWS CLI not configured" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Step 1: Check/Create OIDC Provider" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if OIDC provider exists
$providers = aws iam list-open-id-connect-providers --output json | ConvertFrom-Json
$githubProvider = $providers.OpenIDConnectProviderList | Where-Object { $_.Arn -like "*token.actions.githubusercontent.com*" }

if ($githubProvider) {
    Write-Host "✓ OIDC provider already exists" -ForegroundColor Green
    Write-Host "  ARN: $($githubProvider.Arn)" -ForegroundColor Gray
} else {
    Write-Host "Creating OIDC provider..." -ForegroundColor Cyan
    
    $createResult = aws iam create-open-id-connect-provider `
        --url https://token.actions.githubusercontent.com `
        --client-id-list sts.amazonaws.com `
        --thumbprint-list 6938fd4d98bab03faadb97b34396831e3780aea1 `
        --output json 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ OIDC provider created" -ForegroundColor Green
    } else {
        Write-Host "✗ Failed to create OIDC provider" -ForegroundColor Red
        Write-Host $createResult -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Step 2: Create Trust Policy" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Create trust policy
$trustPolicy = @{
    Version = "2012-10-17"
    Statement = @(
        @{
            Effect = "Allow"
            Principal = @{
                Federated = "arn:aws:iam::${accountId}:oidc-provider/token.actions.githubusercontent.com"
            }
            Action = "sts:AssumeRoleWithWebIdentity"
            Condition = @{
                StringEquals = @{
                    "token.actions.githubusercontent.com:aud" = "sts.amazonaws.com"
                }
                StringLike = @{
                    "token.actions.githubusercontent.com:sub" = "repo:${githubOrg}/${githubRepo}:*"
                }
            }
        }
    )
} | ConvertTo-Json -Depth 10

$trustPolicyFile = "github-trust-policy.json"
$trustPolicy | Out-File -FilePath $trustPolicyFile -Encoding UTF8
Write-Host "✓ Trust policy created: $trustPolicyFile" -ForegroundColor Green

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Step 3: Create/Update IAM Role" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if role exists
$roleExists = aws iam get-role --role-name $roleName 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Role '$roleName' already exists" -ForegroundColor Yellow
    Write-Host "Updating trust policy..." -ForegroundColor Cyan
    
    aws iam update-assume-role-policy `
        --role-name $roleName `
        --policy-document file://$trustPolicyFile
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Trust policy updated" -ForegroundColor Green
    } else {
        Write-Host "✗ Failed to update trust policy" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "Creating role '$roleName'..." -ForegroundColor Cyan
    
    $createRole = aws iam create-role `
        --role-name $roleName `
        --assume-role-policy-document file://$trustPolicyFile `
        --description "GitHub Actions role for MLOps pipeline" `
        --output json
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Role created successfully" -ForegroundColor Green
    } else {
        Write-Host "✗ Failed to create role" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Step 4: Attach IAM Policies" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$policies = @(
    @{Name="AmazonSageMakerFullAccess"; ARN="arn:aws:iam::aws:policy/AmazonSageMakerFullAccess"},
    @{Name="AmazonS3FullAccess"; ARN="arn:aws:iam::aws:policy/AmazonS3FullAccess"},
    @{Name="IAMReadOnlyAccess"; ARN="arn:aws:iam::aws:policy/IAMReadOnlyAccess"}
)

foreach ($policy in $policies) {
    Write-Host "Attaching $($policy.Name)..." -ForegroundColor Cyan
    
    aws iam attach-role-policy `
        --role-name $roleName `
        --policy-arn $policy.ARN 2>$null
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ Attached" -ForegroundColor Green
    } else {
        Write-Host "  ⚠ Already attached or error" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Step 5: Get Role ARN" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$roleInfo = aws iam get-role --role-name $roleName --output json | ConvertFrom-Json
$roleArn = $roleInfo.Role.Arn

Write-Host "✓ Role ARN: $roleArn" -ForegroundColor Green

Write-Host ""
Write-Host "========================================" -ForegroundColor Yellow
Write-Host "GitHub Secrets Configuration" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Yellow
Write-Host ""

Write-Host "Add these secrets to GitHub:" -ForegroundColor White
Write-Host "https://github.com/$githubOrg/$githubRepo/settings/secrets/actions" -ForegroundColor Cyan
Write-Host ""
Write-Host "-----------------------------------" -ForegroundColor Gray
Write-Host "Secret Name: AWS_ROLE_ARN" -ForegroundColor White
Write-Host "Value: $roleArn" -ForegroundColor Green
Write-Host ""
Write-Host "Secret Name: AWS_ACCOUNT_ID" -ForegroundColor White
Write-Host "Value: $accountId" -ForegroundColor Green
Write-Host ""
Write-Host "Secret Name: S3_BUCKET_NAME" -ForegroundColor White
Write-Host "Value: mlops-diabetes-dev-$accountId" -ForegroundColor Green
Write-Host ""
Write-Host "Secret Name: SAGEMAKER_EXECUTION_ROLE" -ForegroundColor White
Write-Host "Value: arn:aws:iam::${accountId}:role/service-role/AmazonSageMaker-ExecutionRole-20251026T145759" -ForegroundColor Green
Write-Host "-----------------------------------" -ForegroundColor Gray
Write-Host ""

# Save to file
$secretsFile = "github-secrets-oidc.txt"
$secretsContent = @"
GitHub Secrets for OIDC Authentication
Generated: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

Add these to: https://github.com/$githubOrg/$githubRepo/settings/secrets/actions

AWS_ROLE_ARN=$roleArn

AWS_ACCOUNT_ID=$accountId

S3_BUCKET_NAME=mlops-diabetes-dev-$accountId

SAGEMAKER_EXECUTION_ROLE=arn:aws:iam::${accountId}:role/service-role/AmazonSageMaker-ExecutionRole-20251026T145759

"@

$secretsContent | Out-File -FilePath $secretsFile -Encoding UTF8
Write-Host "✓ Secrets saved to: $secretsFile" -ForegroundColor Green
Write-Host ""

# Add to .gitignore
$gitignorePath = ".\.gitignore"
if (Test-Path $gitignorePath) {
    $gitignoreContent = Get-Content $gitignorePath -Raw
    if ($gitignoreContent -notlike "*github-secrets-oidc*") {
        Add-Content -Path $gitignorePath -Value "`ngithub-secrets-oidc.txt"
    }
}

# Cleanup
Remove-Item $trustPolicyFile -ErrorAction SilentlyContinue

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Next Steps" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. ✓ OIDC provider created" -ForegroundColor Green
Write-Host "2. ✓ IAM role configured: $roleName" -ForegroundColor Green
Write-Host "3. → Add secrets to GitHub (see $secretsFile)" -ForegroundColor White
Write-Host "4. → Test workflow:" -ForegroundColor White
Write-Host "     git add .github/workflows/mlops_pipeline.yaml" -ForegroundColor Gray
Write-Host "     git commit -m 'chore: Switch to OIDC auth'" -ForegroundColor Gray
Write-Host "     git push origin main" -ForegroundColor Gray
Write-Host "5. → Monitor: https://github.com/$githubOrg/$githubRepo/actions" -ForegroundColor White
Write-Host ""
Write-Host "✓ OIDC setup complete!" -ForegroundColor Green
