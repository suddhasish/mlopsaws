# ============================================================================
# Add Missing Permissions to GitHub Actions IAM Role
# ============================================================================
# This script attaches all AWS managed policies needed for Terraform to
# deploy the MLOps infrastructure
# ============================================================================

$RoleName = "GitHubActions-MLOps-Dev"
$Profile = "mlops-dev"

Write-Host "╔════════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  Adding Terraform Permissions to GitHub Actions Role              ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

Write-Host "Role: $RoleName" -ForegroundColor White
Write-Host "Profile: $Profile" -ForegroundColor White
Write-Host ""

# Define policies to attach
$PoliciesToAttach = @(
    @{
        Name = "AmazonEC2FullAccess"
        Arn = "arn:aws:iam::aws:policy/AmazonEC2FullAccess"
        Description = "VPC, subnets, security groups, availability zones"
    },
    @{
        Name = "CloudWatchFullAccess"
        Arn = "arn:aws:iam::aws:policy/CloudWatchFullAccess"
        Description = "CloudWatch logs, alarms, and metrics"
    },
    @{
        Name = "AWSCloudTrailFullAccess"
        Arn = "arn:aws:iam::aws:policy/AWSCloudTrail_FullAccess"
        Description = "CloudTrail for audit logging"
    }
)

$SuccessCount = 0
$FailCount = 0

foreach ($Policy in $PoliciesToAttach) {
    Write-Host "Attaching: " -NoNewline -ForegroundColor Yellow
    Write-Host $Policy.Name -ForegroundColor White
    Write-Host "  Purpose: $($Policy.Description)" -ForegroundColor Gray
    
    try {
        aws iam attach-role-policy `
            --role-name $RoleName `
            --policy-arn $Policy.Arn `
            --profile $Profile 2>&1 | Out-Null
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  ✓ Success" -ForegroundColor Green
            $SuccessCount++
        } else {
            Write-Host "  ✗ Failed" -ForegroundColor Red
            $FailCount++
        }
    } catch {
        Write-Host "  ✗ Error: $_" -ForegroundColor Red
        $FailCount++
    }
    Write-Host ""
}

Write-Host "╔════════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  Summary                                                           ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""
Write-Host "Policies attached: $SuccessCount" -ForegroundColor Green
Write-Host "Failures: $FailCount" -ForegroundColor $(if ($FailCount -gt 0) { "Red" } else { "Gray" })
Write-Host ""

if ($FailCount -eq 0) {
    Write-Host "Verifying all attached policies..." -ForegroundColor Cyan
    Write-Host ""
    aws iam list-attached-role-policies --role-name $RoleName --profile $Profile
    Write-Host ""
    Write-Host "✓ All permissions added successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "The GitHub Actions role now has access to:" -ForegroundColor Cyan
    Write-Host "  ✓ SageMaker (AmazonSageMakerFullAccess)" -ForegroundColor White
    Write-Host "  ✓ S3 (AmazonS3FullAccess)" -ForegroundColor White
    Write-Host "  ✓ IAM (IAMFullAccess)" -ForegroundColor White
    Write-Host "  ✓ EC2 (AmazonEC2FullAccess) ← NEW" -ForegroundColor Green
    Write-Host "  ✓ CloudWatch (CloudWatchFullAccess) ← NEW" -ForegroundColor Green
    Write-Host "  ✓ CloudTrail (AWSCloudTrail_FullAccess) ← NEW" -ForegroundColor Green
    Write-Host ""
    Write-Host "Note: KMS and SNS permissions are included in the above policies" -ForegroundColor Gray
    Write-Host "Note: Budgets permissions need to be added separately if cost controls are needed" -ForegroundColor Gray
} else {
    Write-Host "✗ Some policies failed to attach. Please check the errors above." -ForegroundColor Red
    exit 1
}
