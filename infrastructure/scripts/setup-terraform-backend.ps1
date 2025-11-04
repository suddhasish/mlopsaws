# Terraform Remote Backend Setup Script
# Creates S3 bucket and DynamoDB table for Terraform state management
# Run this ONCE before using Terraform with remote backend

# Set variables
$accountId = "891807086260"
$bucketName = "mlops-terraform-state-$accountId"
$tableName = "mlops-terraform-locks"
$region = "us-east-1"
$profile = "mlops-dev"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Terraform Remote Backend Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Create S3 bucket for state storage
Write-Host "[1/5] Creating S3 bucket: $bucketName" -ForegroundColor Yellow
try {
    aws s3api create-bucket `
        --bucket $bucketName `
        --region $region `
        --profile $profile
    Write-Host "✅ S3 bucket created successfully" -ForegroundColor Green
} catch {
    if ($_.Exception.Message -like "*BucketAlreadyOwnedByYou*") {
        Write-Host "✅ S3 bucket already exists (owned by you)" -ForegroundColor Green
    } else {
        Write-Host "❌ Failed to create S3 bucket: $_" -ForegroundColor Red
        exit 1
    }
}
Write-Host ""

# 2. Enable versioning (allows state recovery)
Write-Host "[2/5] Enabling versioning on S3 bucket" -ForegroundColor Yellow
aws s3api put-bucket-versioning `
    --bucket $bucketName `
    --versioning-configuration Status=Enabled `
    --profile $profile
Write-Host "✅ Versioning enabled" -ForegroundColor Green
Write-Host ""

# 3. Enable server-side encryption
Write-Host "[3/5] Enabling encryption on S3 bucket" -ForegroundColor Yellow
aws s3api put-bucket-encryption `
    --bucket $bucketName `
    --server-side-encryption-configuration '{
        "Rules": [{
            "ApplyServerSideEncryptionByDefault": {
                "SSEAlgorithm": "AES256"
            },
            "BucketKeyEnabled": true
        }]
    }' `
    --profile $profile
Write-Host "✅ Encryption enabled (AES256)" -ForegroundColor Green
Write-Host ""

# 4. Block public access (security best practice)
Write-Host "[4/5] Blocking public access to S3 bucket" -ForegroundColor Yellow
aws s3api put-public-access-block `
    --bucket $bucketName `
    --public-access-block-configuration '{
        "BlockPublicAcls": true,
        "IgnorePublicAcls": true,
        "BlockPublicPolicy": true,
        "RestrictPublicBuckets": true
    }' `
    --profile $profile
Write-Host "✅ Public access blocked" -ForegroundColor Green
Write-Host ""

# 5. Create DynamoDB table for state locking
Write-Host "[5/5] Creating DynamoDB table: $tableName" -ForegroundColor Yellow
try {
    aws dynamodb create-table `
        --table-name $tableName `
        --attribute-definitions AttributeName=LockID,AttributeType=S `
        --key-schema AttributeName=LockID,KeyType=HASH `
        --billing-mode PAY_PER_REQUEST `
        --region $region `
        --profile $profile `
        --tags Key=Project,Value=mlops-diabetes Key=ManagedBy,Value=Manual
    Write-Host "✅ DynamoDB table created successfully" -ForegroundColor Green
    
    # Wait for table to be active
    Write-Host "   Waiting for table to become active..." -ForegroundColor Yellow
    aws dynamodb wait table-exists `
        --table-name $tableName `
        --region $region `
        --profile $profile
    Write-Host "   Table is now active" -ForegroundColor Green
} catch {
    if ($_.Exception.Message -like "*ResourceInUseException*") {
        Write-Host "✅ DynamoDB table already exists" -ForegroundColor Green
    } else {
        Write-Host "❌ Failed to create DynamoDB table: $_" -ForegroundColor Red
        exit 1
    }
}
Write-Host ""

# Verification
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Verification" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check S3 bucket
Write-Host "S3 Bucket:" -ForegroundColor Yellow
aws s3api get-bucket-versioning --bucket $bucketName --profile $profile
Write-Host ""

# Check DynamoDB table
Write-Host "DynamoDB Table:" -ForegroundColor Yellow
aws dynamodb describe-table --table-name $tableName --query 'Table.TableStatus' --output text --profile $profile
Write-Host ""

# Summary
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Setup Complete! ✅" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Backend Configuration:" -ForegroundColor Yellow
Write-Host "  S3 Bucket: $bucketName" -ForegroundColor White
Write-Host "  DynamoDB Table: $tableName" -ForegroundColor White
Write-Host "  Region: $region" -ForegroundColor White
Write-Host "  Encryption: AES256" -ForegroundColor White
Write-Host "  Versioning: Enabled" -ForegroundColor White
Write-Host "  Public Access: Blocked" -ForegroundColor White
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "  1. cd infrastructure/terraform" -ForegroundColor White
Write-Host "  2. terraform init -migrate-state" -ForegroundColor White
Write-Host "  3. Answer 'yes' to migrate existing state to S3" -ForegroundColor White
Write-Host ""
Write-Host "Estimated Monthly Cost:" -ForegroundColor Yellow
Write-Host "  S3: ~`$0.02/month (state file < 100KB)" -ForegroundColor White
Write-Host "  DynamoDB: ~`$0.00/month (on-demand, minimal usage)" -ForegroundColor White
Write-Host "  Total: < `$0.05/month" -ForegroundColor White
Write-Host ""
