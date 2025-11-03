# =============================================================================
# Networking Module - VPC, Subnets, Security Groups, VPC Endpoints
# =============================================================================

# -----------------------------------------------------------------------------
# VPC
# -----------------------------------------------------------------------------
resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-vpc-${var.environment}"
    }
  )
}

# -----------------------------------------------------------------------------
# Private Subnets
# -----------------------------------------------------------------------------
resource "aws_subnet" "private" {
  count             = var.availability_zones_count
  vpc_id            = aws_vpc.main.id
  cidr_block        = cidrsubnet(var.vpc_cidr, 4, count.index)
  availability_zone = data.aws_availability_zones.available.names[count.index]

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-private-subnet-${count.index + 1}-${var.environment}"
      Type = "Private"
    }
  )
}

# -----------------------------------------------------------------------------
# Route Table for Private Subnets
# -----------------------------------------------------------------------------
resource "aws_route_table" "private" {
  vpc_id = aws_vpc.main.id

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-private-rt-${var.environment}"
    }
  )
}

# -----------------------------------------------------------------------------
# Route Table Association for Private Subnets
# -----------------------------------------------------------------------------
resource "aws_route_table_association" "private" {
  count          = var.availability_zones_count
  subnet_id      = aws_subnet.private[count.index].id
  route_table_id = aws_route_table.private.id
}

# -----------------------------------------------------------------------------
# Security Group for SageMaker
# -----------------------------------------------------------------------------
resource "aws_security_group" "sagemaker" {
  name_prefix = "${var.project_name}-sagemaker-${var.environment}-"
  description = "Security group for SageMaker resources"
  vpc_id      = aws_vpc.main.id

  # Allow HTTPS inbound within VPC
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr]
    description = "HTTPS within VPC"
  }

  # Allow all outbound traffic
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow all outbound"
  }

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-sagemaker-sg-${var.environment}"
    }
  )

  lifecycle {
    create_before_destroy = true
  }
}

# -----------------------------------------------------------------------------
# VPC Endpoint for S3 (Gateway Endpoint - No Cost)
# -----------------------------------------------------------------------------
resource "aws_vpc_endpoint" "s3" {
  count        = var.enable_vpc_endpoints ? 1 : 0
  vpc_id       = aws_vpc.main.id
  service_name = "com.amazonaws.${data.aws_region.current.name}.s3"

  route_table_ids = [aws_route_table.private.id]

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-s3-endpoint-${var.environment}"
    }
  )
}

# -----------------------------------------------------------------------------
# VPC Endpoint for SageMaker API (Interface Endpoint)
# -----------------------------------------------------------------------------
resource "aws_vpc_endpoint" "sagemaker_api" {
  count               = var.enable_vpc_endpoints ? 1 : 0
  vpc_id              = aws_vpc.main.id
  service_name        = "com.amazonaws.${data.aws_region.current.name}.sagemaker.api"
  vpc_endpoint_type   = "Interface"
  private_dns_enabled = true

  subnet_ids         = aws_subnet.private[*].id
  security_group_ids = [aws_security_group.sagemaker.id]

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-sagemaker-api-endpoint-${var.environment}"
    }
  )
}

# -----------------------------------------------------------------------------
# VPC Endpoint for SageMaker Runtime (Interface Endpoint)
# -----------------------------------------------------------------------------
resource "aws_vpc_endpoint" "sagemaker_runtime" {
  count               = var.enable_vpc_endpoints ? 1 : 0
  vpc_id              = aws_vpc.main.id
  service_name        = "com.amazonaws.${data.aws_region.current.name}.sagemaker.runtime"
  vpc_endpoint_type   = "Interface"
  private_dns_enabled = true

  subnet_ids         = aws_subnet.private[*].id
  security_group_ids = [aws_security_group.sagemaker.id]

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-sagemaker-runtime-endpoint-${var.environment}"
    }
  )
}

# -----------------------------------------------------------------------------
# VPC Endpoint for CloudWatch Logs (Interface Endpoint)
# -----------------------------------------------------------------------------
resource "aws_vpc_endpoint" "logs" {
  count               = var.enable_vpc_endpoints ? 1 : 0
  vpc_id              = aws_vpc.main.id
  service_name        = "com.amazonaws.${data.aws_region.current.name}.logs"
  vpc_endpoint_type   = "Interface"
  private_dns_enabled = true

  subnet_ids         = aws_subnet.private[*].id
  security_group_ids = [aws_security_group.sagemaker.id]

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-logs-endpoint-${var.environment}"
    }
  )
}

# -----------------------------------------------------------------------------
# VPC Endpoint for ECR API (Interface Endpoint)
# -----------------------------------------------------------------------------
resource "aws_vpc_endpoint" "ecr_api" {
  count               = var.enable_vpc_endpoints ? 1 : 0
  vpc_id              = aws_vpc.main.id
  service_name        = "com.amazonaws.${data.aws_region.current.name}.ecr.api"
  vpc_endpoint_type   = "Interface"
  private_dns_enabled = true

  subnet_ids         = aws_subnet.private[*].id
  security_group_ids = [aws_security_group.sagemaker.id]

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-ecr-api-endpoint-${var.environment}"
    }
  )
}

# -----------------------------------------------------------------------------
# VPC Endpoint for ECR Docker (Interface Endpoint)
# -----------------------------------------------------------------------------
resource "aws_vpc_endpoint" "ecr_dkr" {
  count               = var.enable_vpc_endpoints ? 1 : 0
  vpc_id              = aws_vpc.main.id
  service_name        = "com.amazonaws.${data.aws_region.current.name}.ecr.dkr"
  vpc_endpoint_type   = "Interface"
  private_dns_enabled = true

  subnet_ids         = aws_subnet.private[*].id
  security_group_ids = [aws_security_group.sagemaker.id]

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-ecr-dkr-endpoint-${var.environment}"
    }
  )
}

# -----------------------------------------------------------------------------
# Data Sources
# -----------------------------------------------------------------------------
data "aws_availability_zones" "available" {
  state = "available"
}

data "aws_region" "current" {}
