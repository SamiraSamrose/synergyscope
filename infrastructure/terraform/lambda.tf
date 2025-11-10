# File: infrastructure/terraform/lambda.tf

resource "aws_lambda_function" "match_ingestion" {
  filename         = "lambda_functions.zip"
  function_name    = "synergyscope-match-ingestion"
  role            = aws_iam_role.lambda_execution_role.arn
  handler         = "lambda_handlers.match_ingestion_handler"
  source_code_hash = filebase64sha256("lambda_functions.zip")
  runtime         = "python3.11"
  timeout         = 300
  memory_size     = 512
  
  environment {
    variables = {
      S3_BUCKET = aws_s3_bucket.data_bucket.id
      NEPTUNE_ENDPOINT = aws_neptune_cluster.main.endpoint
    }
  }
}

resource "aws_lambda_function" "graph_builder" {
  filename         = "lambda_functions.zip"
  function_name    = "synergyscope-graph-builder"
  role            = aws_iam_role.lambda_execution_role.arn
  handler         = "lambda_handlers.graph_builder_handler"
  runtime         = "python3.11"
  timeout         = 300
  memory_size     = 1024
}