# Fix Missing AWS Permissions for Terraform
# Run these commands to add EventBridge, Lambda, and Budgets permissions

$RoleName = "GitHubActions-MLOps-Dev"
$Profile = "mlops-dev"

Write-Host "Adding missing permissions to $RoleName..." -ForegroundColor Cyan
Write-Host ""

# 1. EventBridge (for auto shutdown/startup schedules)
Write-Host "1. Adding EventBridge permissions..." -ForegroundColor Yellow
aws iam attach-role-policy `
    --role-name $RoleName `
    --policy-arn arn:aws:iam::aws:policy/AmazonEventBridgeFullAccess `
    --profile $Profile

# 2. Lambda (for auto shutdown/startup functions)
Write-Host "2. Adding Lambda permissions..." -ForegroundColor Yellow
aws iam attach-role-policy `
    --role-name $RoleName `
    --policy-arn arn:aws:iam::aws:policy/AWSLambda_FullAccess `
    --profile $Profile

Write-Host ""
Write-Host "✓ Permissions added!" -ForegroundColor Green
Write-Host ""
Write-Host "Verifying..." -ForegroundColor Cyan
aws iam list-attached-role-policies --role-name $RoleName --profile $Profile
