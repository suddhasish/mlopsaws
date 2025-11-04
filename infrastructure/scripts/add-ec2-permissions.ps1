# Add EC2 permissions to GitHub Actions IAM Role for Terraform
# This script attaches the AWS managed EC2FullAccess policy to the role

$RoleName = "GitHubActions-MLOps-Dev"
$PolicyArn = "arn:aws:iam::aws:policy/AmazonEC2FullAccess"

Write-Host "Adding EC2 permissions to role: $RoleName" -ForegroundColor Cyan
Write-Host ""

# Attach EC2 full access policy
Write-Host "Attaching AmazonEC2FullAccess managed policy..." -ForegroundColor Yellow

& aws iam attach-role-policy `
    --role-name $RoleName `
    --policy-arn $PolicyArn `
    --profile mlops-dev

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ EC2 permissions added successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Verifying attached policies..." -ForegroundColor Cyan
    & aws iam list-attached-role-policies --role-name $RoleName --profile mlops-dev
    Write-Host ""
    Write-Host "The role now has permissions for:" -ForegroundColor Cyan
    Write-Host "  - SageMaker (AmazonSageMakerFullAccess)" -ForegroundColor White
    Write-Host "  - S3 (AmazonS3FullAccess)" -ForegroundColor White
    Write-Host "  - IAM (IAMFullAccess)" -ForegroundColor White
    Write-Host "  - EC2 (AmazonEC2FullAccess) ← NEW" -ForegroundColor Green
} else {
    Write-Host "✗ Failed to attach policy" -ForegroundColor Red
    Write-Host "Please ensure AWS CLI is configured and you have permission to modify IAM roles" -ForegroundColor Yellow
    exit 1
}
