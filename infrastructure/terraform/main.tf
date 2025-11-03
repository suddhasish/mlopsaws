# Terraform Backend Configuration
# Stores Terraform state in S3 with DynamoDB locking for team collaboration

terraform {
  required_version = ">= 1.5.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.5"
    }
  }
  
  # Backend configuration - UNCOMMENT after creating S3 bucket manually
  # backend "s3" {
  #   bucket         = "mlops-terraform-state-ACCOUNT_ID"  # Replace with your bucket name
  #   key            = "mlops/terraform.tfstate"
  #   region         = "us-east-1"
  #   encrypt        = true
  #   kms_key_id     = "arn:aws:kms:us-east-1:ACCOUNT_ID:key/KEY_ID"
  #   dynamodb_table = "mlops-terraform-locks"
  #   
  #   # Enable versioning on the S3 bucket for state history
  #   # Enable point-in-time recovery on DynamoDB table
  # }
}

provider "aws" {
  region = var.region
  
  # Default tags applied to all resources
  default_tags {
    tags = {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "Terraform"
      Repository  = var.repository_url
      Owner       = var.owner_email
    }
  }
}

# Data sources
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}
data "aws_availability_zones" "available" {
  state = "available"
}
