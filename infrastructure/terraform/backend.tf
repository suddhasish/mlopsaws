# Terraform Remote Backend Configuration
# S3 bucket stores state files
# DynamoDB table provides state locking to prevent concurrent modifications

terraform {
  backend "s3" {
    bucket         = "mlops-terraform-state-891807086260"
    key            = "mlops-diabetes/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "mlops-terraform-locks"
    
    # Uncomment if using specific AWS profile locally
    # profile = "mlops-dev"
  }
}
