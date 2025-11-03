# =============================================================================
# MLOps Infrastructure Deployment Script (PowerShell)
# One-command deployment of complete AWS infrastructure
# =============================================================================

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet('dev', 'staging', 'production')]
    [string]$Environment,
    
    [Parameter(Mandatory=$false)]
    [ValidateSet('init', 'plan', 'apply', 'destroy', 'output', 'all')]
    [string]$Action = 'all',
    
    [Parameter(Mandatory=$false)]
    [switch]$AutoApprove,
    
    [Parameter(Mandatory=$false)]
    [string]$AWSProfile = 'default'
)

# Colors for output
function Write-ColorOutput {
    param([string]$Message, [string]$Color = 'White')
    Write-Host $Message -ForegroundColor $Color
}

function Write-Success { param([string]$Message) Write-ColorOutput "✅ $Message" 'Green' }
function Write-Info { param([string]$Message) Write-ColorOutput "ℹ️  $Message" 'Cyan' }
function Write-Warning { param([string]$Message) Write-ColorOutput "⚠️  $Message" 'Yellow' }
function Write-Error-Custom { param([string]$Message) Write-ColorOutput "❌ $Message" 'Red' }

# Banner
Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════════════════╗" -ForegroundColor Magenta
Write-Host "║         🚀 MLOps Infrastructure Deployment Script 🚀            ║" -ForegroundColor Magenta
Write-Host "╚══════════════════════════════════════════════════════════════════╝" -ForegroundColor Magenta
Write-Host ""

Write-Info "Environment: $Environment"
Write-Info "Action: $Action"
Write-Info "AWS Profile: $AWSProfile"
Write-Host ""

# Validate prerequisites
Write-Info "Validating prerequisites..."

# Check Terraform installation
try {
    $tfVersion = terraform version -json | ConvertFrom-Json
    Write-Success "Terraform installed: $($tfVersion.terraform_version)"
} catch {
    Write-Error-Custom "Terraform not found. Please install Terraform 1.5+"
    Write-Info "Download from: https://www.terraform.io/downloads"
    exit 1
}

# Check AWS CLI installation
try {
    $awsVersion = aws --version
    Write-Success "AWS CLI installed: $awsVersion"
} catch {
    Write-Error-Custom "AWS CLI not found. Please install AWS CLI v2"
    Write-Info "Download from: https://awscli.amazonaws.com/AWSCLIV2.msi"
    exit 1
}

# Check AWS credentials
try {
    $env:AWS_PROFILE = $AWSProfile
    $identity = aws sts get-caller-identity --profile $AWSProfile | ConvertFrom-Json
    Write-Success "AWS credentials valid"
    Write-Info "  Account: $($identity.Account)"
    Write-Info "  User: $($identity.Arn)"
} catch {
    Write-Error-Custom "AWS credentials not configured or invalid"
    Write-Info "Run: aws configure --profile $AWSProfile"
    exit 1
}

# Navigate to environment directory
$envDir = Join-Path $PSScriptRoot "..\terraform\environments\$Environment"
if (-not (Test-Path $envDir)) {
    Write-Error-Custom "Environment directory not found: $envDir"
    exit 1
}

Write-Success "Environment directory found: $envDir"
Set-Location $envDir

# Create symlinks to modules and root Terraform files
Write-Info "Creating symlinks to Terraform modules..."

# Symlink to main.tf, variables.tf, outputs.tf, modules.tf from root
$rootTerraformDir = Join-Path $PSScriptRoot "..\terraform"
$filesToLink = @('main.tf', 'variables.tf', 'outputs.tf', 'modules.tf')

foreach ($file in $filesToLink) {
    $source = Join-Path $rootTerraformDir $file
    $target = Join-Path $envDir $file
    
    if (Test-Path $target) {
        Remove-Item $target -Force
    }
    
    # Create hard link (works better on Windows than symlink)
    cmd /c mklink /H $target $source | Out-Null
}

# Symlink to modules directory
$modulesSource = Join-Path $rootTerraformDir "modules"
$modulesTarget = Join-Path $envDir "modules"

if (Test-Path $modulesTarget) {
    Remove-Item $modulesTarget -Recurse -Force
}
cmd /c mklink /D $modulesTarget $modulesSource | Out-Null

Write-Success "Symlinks created"

# Function to run Terraform init
function Invoke-TerraformInit {
    Write-Info "Running: terraform init"
    terraform init -upgrade
    if ($LASTEXITCODE -ne 0) {
        Write-Error-Custom "Terraform init failed"
        exit 1
    }
    Write-Success "Terraform initialized"
}

# Function to run Terraform plan
function Invoke-TerraformPlan {
    Write-Info "Running: terraform plan"
    terraform plan -var-file="terraform.tfvars" -out="tfplan"
    if ($LASTEXITCODE -ne 0) {
        Write-Error-Custom "Terraform plan failed"
        exit 1
    }
    Write-Success "Terraform plan completed. Review the plan above."
    Write-Warning "Plan saved to: tfplan"
}

# Function to run Terraform apply
function Invoke-TerraformApply {
    if (-not (Test-Path "tfplan")) {
        Write-Warning "No plan file found. Running plan first..."
        Invoke-TerraformPlan
    }
    
    Write-Info "Running: terraform apply"
    
    if ($AutoApprove) {
        terraform apply -auto-approve tfplan
    } else {
        Write-Host ""
        Write-Warning "This will create/modify AWS resources and incur costs."
        Write-Host "Estimated monthly cost for $Environment environment: " -NoNewline
        switch ($Environment) {
            'dev' { Write-Host "$100-150" -ForegroundColor Yellow }
            'staging' { Write-Host "$300-500" -ForegroundColor Yellow }
            'production' { Write-Host "$1000-1500" -ForegroundColor Yellow }
        }
        Write-Host ""
        
        $confirmation = Read-Host "Do you want to proceed? (yes/no)"
        if ($confirmation -ne 'yes') {
            Write-Info "Apply cancelled"
            exit 0
        }
        
        terraform apply tfplan
    }
    
    if ($LASTEXITCODE -ne 0) {
        Write-Error-Custom "Terraform apply failed"
        exit 1
    }
    
    Write-Success "Infrastructure deployed successfully! 🎉"
}

# Function to run Terraform destroy
function Invoke-TerraformDestroy {
    Write-Warning "⚠️  DANGER: This will DESTROY all infrastructure in $Environment environment"
    Write-Host ""
    
    if (-not $AutoApprove) {
        $confirmation = Read-Host "Type '$Environment' to confirm destruction"
        if ($confirmation -ne $Environment) {
            Write-Info "Destroy cancelled"
            exit 0
        }
        
        $confirmation2 = Read-Host "Are you ABSOLUTELY sure? Type 'yes' to confirm"
        if ($confirmation2 -ne 'yes') {
            Write-Info "Destroy cancelled"
            exit 0
        }
    }
    
    Write-Info "Running: terraform destroy"
    terraform destroy -var-file="terraform.tfvars" -auto-approve
    
    if ($LASTEXITCODE -ne 0) {
        Write-Error-Custom "Terraform destroy failed"
        exit 1
    }
    
    Write-Success "Infrastructure destroyed"
}

# Function to show outputs
function Invoke-TerraformOutput {
    Write-Info "Running: terraform output"
    terraform output
    
    Write-Host ""
    Write-Info "To get specific output value:"
    Write-Host "  terraform output -raw s3_bucket_name" -ForegroundColor Gray
    Write-Host "  terraform output -json config_yaml" -ForegroundColor Gray
}

# Execute actions
try {
    switch ($Action) {
        'init' {
            Invoke-TerraformInit
        }
        'plan' {
            Invoke-TerraformInit
            Invoke-TerraformPlan
        }
        'apply' {
            Invoke-TerraformInit
            Invoke-TerraformPlan
            Invoke-TerraformApply
        }
        'destroy' {
            Invoke-TerraformDestroy
        }
        'output' {
            Invoke-TerraformOutput
        }
        'all' {
            Invoke-TerraformInit
            Invoke-TerraformPlan
            Invoke-TerraformApply
            Invoke-TerraformOutput
            
            # Automatically update config.yaml with Terraform outputs
            Write-Info "Updating config.yaml automatically..."
            Write-Host ""
            
            try {
                $updateConfigScript = Join-Path $PSScriptRoot "update-config.ps1"
                if (Test-Path $updateConfigScript) {
                    & $updateConfigScript -Environment $Environment
                } else {
                    Write-Warning "update-config.ps1 not found. Please manually update config/config.yaml"
                    Write-Info "Run: .\infrastructure\scripts\update-config.ps1 -Environment $Environment"
                }
            } catch {
                Write-Warning "Failed to auto-update config.yaml: $_"
                Write-Info "Manually run: .\infrastructure\scripts\update-config.ps1 -Environment $Environment"
            }
        }
    }
    
    Write-Host ""
    Write-Success "Deployment script completed successfully! 🚀"
    Write-Host ""
    
} catch {
    Write-Error-Custom "Deployment failed: $_"
    exit 1
}

# Usage examples
Write-Host ""
Write-Info "Script usage examples:"
Write-Host "  .\deploy-infrastructure.ps1 -Environment dev -Action all" -ForegroundColor Gray
Write-Host "  .\deploy-infrastructure.ps1 -Environment staging -Action plan" -ForegroundColor Gray
Write-Host "  .\deploy-infrastructure.ps1 -Environment production -Action apply -AutoApprove" -ForegroundColor Gray
Write-Host "  .\deploy-infrastructure.ps1 -Environment dev -Action destroy" -ForegroundColor Gray
Write-Host ""
