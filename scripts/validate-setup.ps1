# =============================================================================
# Setup Validation Script
# Verifies everything is ready before running ML pipeline
# =============================================================================

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet('dev', 'staging', 'production')]
    [string]$Environment = 'dev'
)

function Write-ColorOutput {
    param([string]$Message, [string]$Color = 'White')
    Write-Host $Message -ForegroundColor $Color
}

function Write-Success { param([string]$Message) Write-ColorOutput "✅ $Message" 'Green' }
function Write-Warning-Custom { param([string]$Message) Write-ColorOutput "⚠️  $Message" 'Yellow' }
function Write-Error-Custom { param([string]$Message) Write-ColorOutput "❌ $Message" 'Red' }
function Write-Info { param([string]$Message) Write-ColorOutput "ℹ️  $Message" 'Cyan' }

Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════════════════╗" -ForegroundColor Magenta
Write-Host "║              🔍 MLOps Setup Validation Check                    ║" -ForegroundColor Magenta
Write-Host "╚══════════════════════════════════════════════════════════════════╝" -ForegroundColor Magenta
Write-Host ""

Write-Info "Environment: $Environment"
Write-Host ""

$errors = @()
$warnings = @()
$passed = 0
$total = 0

# =============================================================================
# Check 1: Config file exists and is updated
# =============================================================================
$total++
Write-Host "[$total] Checking config.yaml..." -NoNewline
if (Test-Path "config\config.yaml") {
    $config = Get-Content "config\config.yaml" -Raw
    
    $hasPlaceholders = $false
    if ($config -match "YOUR_AWS_ACCOUNT_ID" -or $config -match "YOUR_ACCOUNT_ID") {
        $hasPlaceholders = $true
        $errors += "config.yaml contains placeholder values (run: .\infrastructure\scripts\update-config.ps1 -Environment $Environment)"
    }
    
    if (-not $hasPlaceholders) {
        Write-Success " OK"
        $passed++
    } else {
        Write-Error-Custom " FAILED"
    }
} else {
    Write-Error-Custom " NOT FOUND"
    $errors += "config\config.yaml not found"
}

# =============================================================================
# Check 2: Data directories
# =============================================================================
$total++
Write-Host "[$total] Checking data directories..." -NoNewline
$dataDirs = @('data', 'data\raw', 'data\processed')
$missingDirs = @()

foreach ($dir in $dataDirs) {
    if (-not (Test-Path $dir)) {
        $missingDirs += $dir
    }
}

if ($missingDirs.Count -eq 0) {
    Write-Success " OK"
    $passed++
} else {
    Write-Warning-Custom " MISSING"
    $warnings += "Data directories will be created automatically: $($missingDirs -join ', ')"
    
    # Create directories
    foreach ($dir in $missingDirs) {
        New-Item -ItemType Directory -Force -Path $dir | Out-Null
    }
    Write-Info "  Created missing directories"
}

# =============================================================================
# Check 3: Virtual environment
# =============================================================================
$total++
Write-Host "[$total] Checking Python virtual environment..." -NoNewline
if (Test-Path "venv\Scripts\activate.ps1" -or Test-Path "venv\Scripts\activate") {
    Write-Success " OK"
    $passed++
} else {
    Write-Warning-Custom " NOT FOUND"
    $warnings += "Virtual environment not found (recommended: python -m venv venv)"
}

# =============================================================================
# Check 4: AWS credentials
# =============================================================================
$total++
Write-Host "[$total] Checking AWS credentials..." -NoNewline
try {
    $identity = aws sts get-caller-identity 2>$null | ConvertFrom-Json
    if ($identity.Account) {
        Write-Success " OK"
        Write-Host "      Account: $($identity.Account)" -ForegroundColor Gray
        Write-Host "      User: $($identity.Arn.Split('/')[-1])" -ForegroundColor Gray
        $passed++
    } else {
        Write-Error-Custom " FAILED"
        $errors += "AWS credentials not valid"
    }
} catch {
    Write-Error-Custom " NOT CONFIGURED"
    $errors += "AWS credentials not configured (run: aws configure)"
}

# =============================================================================
# Check 5: Terraform infrastructure
# =============================================================================
$total++
Write-Host "[$total] Checking Terraform infrastructure..." -NoNewline
$tfStateFile = "infrastructure\terraform\environments\$Environment\terraform.tfstate"
if (Test-Path $tfStateFile) {
    Write-Success " OK"
    $passed++
} else {
    Write-Error-Custom " NOT DEPLOYED"
    $errors += "Terraform infrastructure not deployed (run: .\infrastructure\scripts\deploy-infrastructure.ps1 -Environment $Environment -Action all)"
}

# =============================================================================
# Check 6: Python dependencies
# =============================================================================
$total++
Write-Host "[$total] Checking Python dependencies..." -NoNewline
try {
    # Check if in virtual environment
    if ($env:VIRTUAL_ENV) {
        $pythonCmd = "python"
    } else {
        $pythonCmd = "python"
    }
    
    $null = & $pythonCmd -c "import sagemaker, boto3, pandas, numpy, sklearn, yaml" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Success " OK"
        $passed++
    } else {
        Write-Warning-Custom " MISSING"
        $warnings += "Some Python dependencies missing (run: pip install -r requirements.txt)"
    }
} catch {
    Write-Warning-Custom " CHECK FAILED"
    $warnings += "Could not verify Python dependencies (run: pip install -r requirements.txt)"
}

# =============================================================================
# Check 7: Required Python files
# =============================================================================
$total++
Write-Host "[$total] Checking Python application files..." -NoNewline
$requiredFiles = @(
    'src\processing\download_data.py',
    'src\processing\preprocessing.py',
    'src\training\train.py',
    'src\evaluation\evaluate.py',
    'src\deployment\deploy.py',
    'src\monitoring\model_monitor.py',
    'pipelines\training_pipeline.py'
)

$missingFiles = @()
foreach ($file in $requiredFiles) {
    if (-not (Test-Path $file)) {
        $missingFiles += $file
    }
}

if ($missingFiles.Count -eq 0) {
    Write-Success " OK"
    $passed++
} else {
    Write-Error-Custom " MISSING FILES"
    $errors += "Missing Python files: $($missingFiles -join ', ')"
}

# =============================================================================
# Check 8: requirements.txt
# =============================================================================
$total++
Write-Host "[$total] Checking requirements.txt..." -NoNewline
if (Test-Path "requirements.txt") {
    Write-Success " OK"
    $passed++
} else {
    Write-Error-Custom " NOT FOUND"
    $errors += "requirements.txt not found"
}

# =============================================================================
# Results Summary
# =============================================================================
Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                      Validation Results                          ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Passed: " -NoNewline -ForegroundColor Gray
Write-Host "$passed / $total" -ForegroundColor $(if($passed -eq $total){"Green"}else{"Yellow"})
Write-Host ""

if ($errors.Count -eq 0 -and $warnings.Count -eq 0) {
    Write-Host "╔══════════════════════════════════════════════════════════════════╗" -ForegroundColor Green
    Write-Host "║                  🎉 All Checks Passed! 🎉                       ║" -ForegroundColor Green
    Write-Host "╚══════════════════════════════════════════════════════════════════╝" -ForegroundColor Green
    Write-Host ""
    Write-Host "✅ Your MLOps environment is ready!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  1. Download dataset (if not already done):" -ForegroundColor Cyan
    Write-Host "     python src\processing\download_data.py" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  2. Run the complete ML pipeline:" -ForegroundColor Cyan
    Write-Host "     python pipelines\training_pipeline.py --environment $Environment --execute" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  3. Monitor progress in AWS Console:" -ForegroundColor Cyan
    Write-Host "     https://console.aws.amazon.com/sagemaker/" -ForegroundColor Yellow
    Write-Host ""
    exit 0
    
} else {
    if ($errors.Count -gt 0) {
        Write-Host "╔══════════════════════════════════════════════════════════════════╗" -ForegroundColor Red
        Write-Host "║                      ❌ Errors Found                             ║" -ForegroundColor Red
        Write-Host "╚══════════════════════════════════════════════════════════════════╝" -ForegroundColor Red
        Write-Host ""
        foreach ($error in $errors) {
            Write-Host "  ❌ $error" -ForegroundColor Red
        }
        Write-Host ""
    }
    
    if ($warnings.Count -gt 0) {
        Write-Host "╔══════════════════════════════════════════════════════════════════╗" -ForegroundColor Yellow
        Write-Host "║                      ⚠️  Warnings                                ║" -ForegroundColor Yellow
        Write-Host "╚══════════════════════════════════════════════════════════════════╝" -ForegroundColor Yellow
        Write-Host ""
        foreach ($warning in $warnings) {
            Write-Host "  ⚠️  $warning" -ForegroundColor Yellow
        }
        Write-Host ""
    }
    
    if ($errors.Count -gt 0) {
        Write-Host "Please fix the errors above before proceeding." -ForegroundColor Red
        Write-Host ""
        exit 1
    } else {
        Write-Host "You can proceed with warnings, but it's recommended to address them." -ForegroundColor Yellow
        Write-Host ""
        exit 0
    }
}
