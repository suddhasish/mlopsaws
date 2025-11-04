# Update GitHub Actions IAM Role Policy with EC2 permissions
# Run this script to add missing EC2 and other Terraform permissions

$RoleName = "GitHubActions-MLOps-Dev"
$PolicyName = "TerraformFullAccess"
$PolicyFile = "github-actions-policy-updated.json"

Write-Host "Updating IAM policy for role: $RoleName" -ForegroundColor Cyan

# Delete old policy if exists
Write-Host "Removing old policy (if exists)..." -ForegroundColor Yellow
aws iam delete-role-policy --role-name $RoleName --policy-name "SageMakerAndS3Access" --profile mlops-dev 2>$null

# Put new policy
Write-Host "Attaching new policy with Terraform permissions..." -ForegroundColor Yellow
aws iam put-role-policy `
    --role-name $RoleName `
    --policy-name $PolicyName `
    --policy-document file://$PolicyFile `
    --profile mlops-dev

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Policy updated successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "New policy includes permissions for:" -ForegroundColor Cyan
    Write-Host "  - SageMaker (full access)" -ForegroundColor White
    Write-Host "  - S3 (bucket and object operations)" -ForegroundColor White
    Write-Host "  - IAM (role management)" -ForegroundColor White
    Write-Host "  - EC2 (VPC, subnets, security groups, networking)" -ForegroundColor White
    Write-Host "  - KMS (encryption key management)" -ForegroundColor White
    Write-Host "  - CloudWatch (logs and alarms)" -ForegroundColor White
    Write-Host "  - SNS (topic management)" -ForegroundColor White
    Write-Host "  - CloudTrail (audit logging)" -ForegroundColor White
    Write-Host "  - Budgets (cost management)" -ForegroundColor White
    Write-Host "  - STS (get caller identity)" -ForegroundColor White
} else {
    Write-Host "✗ Failed to update policy" -ForegroundColor Red
    exit 1
}
