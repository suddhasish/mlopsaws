# =============================================================================
# Auto-Update config.yaml from Terraform Outputs
# Run after: terraform apply
# =============================================================================

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet('dev', 'staging', 'production')]
    [string]$Environment
)

function Write-ColorOutput {
    param([string]$Message, [string]$Color = 'White')
    Write-Host $Message -ForegroundColor $Color
}

function Write-Success { param([string]$Message) Write-ColorOutput "✅ $Message" 'Green' }
function Write-Info { param([string]$Message) Write-ColorOutput "ℹ️  $Message" 'Cyan' }
function Write-Error-Custom { param([string]$Message) Write-ColorOutput "❌ $Message" 'Red' }

Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════════════════╗" -ForegroundColor Magenta
Write-Host "║         🔧 Auto-Update Config from Terraform Outputs            ║" -ForegroundColor Magenta
Write-Host "╚══════════════════════════════════════════════════════════════════╝" -ForegroundColor Magenta
Write-Host ""

Write-Info "Environment: $Environment"

# Navigate to environment directory
$envDir = Join-Path $PSScriptRoot "..\terraform\environments\$Environment"

if (-not (Test-Path $envDir)) {
    Write-Error-Custom "Environment directory not found: $envDir"
    exit 1
}

if (-not (Test-Path "$envDir\terraform.tfstate")) {
    Write-Error-Custom "Terraform state not found. Run 'terraform apply' first."
    exit 1
}

Write-Success "Found Terraform state"
Set-Location $envDir

Write-Info "Extracting Terraform outputs..."

try {
    # Get all Terraform outputs
    $outputs = terraform output -json | ConvertFrom-Json
    
    # Extract values
    $accountId = $outputs.config_yaml.value.aws.account_id
    $region = $outputs.config_yaml.value.aws.region
    $bucketName = $outputs.s3_bucket_name.value
    $sagemakerRole = $outputs.sagemaker_execution_role_arn.value
    $modelPackageGroup = $outputs.model_package_group_name.value
    $snsTopicArn = $outputs.sns_topic_alerts_arn.value
    $logGroupTraining = $outputs.cloudwatch_log_group_training.value
    $logGroupEndpoints = $outputs.cloudwatch_log_group_endpoints.value
    
    Write-Success "Extracted values from Terraform outputs"
    
} catch {
    Write-Error-Custom "Failed to extract Terraform outputs: $_"
    exit 1
}

# Navigate to project root
Set-Location $PSScriptRoot\..\..\

$configPath = "config\config.yaml"

if (-not (Test-Path $configPath)) {
    Write-Error-Custom "Config file not found: $configPath"
    exit 1
}

Write-Info "Updating $configPath..."

# Read existing config
$config = Get-Content $configPath -Raw

# Replace placeholder values with actual Terraform outputs
$config = $config -replace '"YOUR_AWS_ACCOUNT_ID"', """$accountId"""
$config = $config -replace 'YOUR_AWS_ACCOUNT_ID', $accountId
$config = $config -replace 'YOUR_ACCOUNT_ID', $accountId
$config = $config -replace 'mlops-diabetes-classification', $bucketName
$config = $config -replace 'arn:aws:iam::YOUR_ACCOUNT_ID:role/SageMakerExecutionRole', $sagemakerRole
$config = $config -replace 'diabetes-classification-models', $modelPackageGroup
$config = $config -replace 'arn:aws:sns:us-east-1:YOUR_ACCOUNT_ID:mlops-alerts', $snsTopicArn
$config = $config -replace '/aws/sagemaker/TrainingJobs', $logGroupTraining
$config = $config -replace '/aws/sagemaker/diabetes-classification', $logGroupEndpoints

# Update region if different
if ($region -ne 'us-east-1') {
    $config = $config -replace 'region: us-east-1', "region: $region"
}

# Save updated config
$config | Set-Content $configPath -Encoding UTF8

Write-Host ""
Write-Success "Config updated successfully!"
Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                    Updated Configuration                         ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""
Write-Host "  AWS Account ID:   " -NoNewline -ForegroundColor Gray
Write-Host $accountId -ForegroundColor Yellow
Write-Host "  Region:           " -NoNewline -ForegroundColor Gray
Write-Host $region -ForegroundColor Yellow
Write-Host "  S3 Bucket:        " -NoNewline -ForegroundColor Gray
Write-Host $bucketName -ForegroundColor Yellow
Write-Host "  SageMaker Role:   " -NoNewline -ForegroundColor Gray
Write-Host $sagemakerRole -ForegroundColor Yellow
Write-Host "  Model Registry:   " -NoNewline -ForegroundColor Gray
Write-Host $modelPackageGroup -ForegroundColor Yellow
Write-Host "  SNS Topic:        " -NoNewline -ForegroundColor Gray
Write-Host $snsTopicArn -ForegroundColor Yellow
Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║                         Next Steps                               ║" -ForegroundColor Green
Write-Host "╚══════════════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "  1. Validate setup:" -ForegroundColor Cyan
Write-Host "     .\scripts\validate-setup.ps1" -ForegroundColor Yellow
Write-Host ""
Write-Host "  2. Download dataset:" -ForegroundColor Cyan
Write-Host "     python src\processing\download_data.py" -ForegroundColor Yellow
Write-Host ""
Write-Host "  3. Run ML pipeline:" -ForegroundColor Cyan
Write-Host "     python pipelines\training_pipeline.py --environment $Environment --execute" -ForegroundColor Yellow
Write-Host ""
