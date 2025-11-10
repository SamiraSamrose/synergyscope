# File: infrastructure/terraform/sagemaker.tf

resource "aws_sagemaker_model" "gnn_model" {
  name               = "synergyscope-gnn-model"
  execution_role_arn = aws_iam_role.sagemaker_role.arn
  
  primary_container {
    image = "763104351884.dkr.ecr.us-east-1.amazonaws.com/pytorch-inference:2.0.0-gpu-py310"
    model_data_url = "s3://${aws_s3_bucket.models.id}/gnn_model.tar.gz"
  }
}

resource "aws_sagemaker_endpoint_configuration" "gnn_config" {
  name = "synergyscope-gnn-config"
  
  production_variants {
    variant_name           = "primary"
    model_name            = aws_sagemaker_model.gnn_model.name
    instance_type         = "ml.g4dn.xlarge"
    initial_instance_count = 1
  }
}

resource "aws_sagemaker_endpoint" "gnn_endpoint" {
  name                 = "synergyscope-gnn-endpoint"
  endpoint_config_name = aws_sagemaker_endpoint_configuration.gnn_config.name
}

resource "aws_iam_role" "sagemaker_role" {
  name = "synergyscope-sagemaker-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "sagemaker.amazonaws.com"
      }
    }]
  })
}