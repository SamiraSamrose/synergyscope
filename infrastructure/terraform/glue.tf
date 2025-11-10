# File: infrastructure/terraform/glue.tf

resource "aws_glue_catalog_database" "synergyscope_db" {
  name = "synergyscope"
}

resource "aws_glue_crawler" "match_data" {
  database_name = aws_glue_catalog_database.synergyscope_db.name
  name          = "synergyscope-match-crawler"
  role          = aws_iam_role.glue_role.arn
  
  s3_target {
    path = "s3://${aws_s3_bucket.data_bucket.id}/raw/matches/"
  }
}

resource "aws_iam_role" "glue_role" {
  name = "synergyscope-glue-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "glue.amazonaws.com"
      }
    }]
  })
}