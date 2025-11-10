# File: infrastructure/terraform/s3.tf

resource "aws_s3_bucket" "data_bucket" {
  bucket = "synergyscope-data-${var.environment}"
  
  tags = {
    Name = "SynergyScope Data"
    Environment = var.environment
  }
}

resource "aws_s3_bucket" "models" {
  bucket = "synergyscope-models-${var.environment}"
}

resource "aws_s3_bucket_versioning" "data_versioning" {
  bucket = aws_s3_bucket.data_bucket.id
  
  versioning_configuration {
    status = "Enabled"
  }
}