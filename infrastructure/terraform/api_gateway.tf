# File: infrastructure/terraform/api_gateway.tf

resource "aws_api_gateway_rest_api" "main" {
  name        = "synergyscope-api"
  description = "SynergyScope API Gateway"
}

resource "aws_api_gateway_resource" "synergy" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  parent_id   = aws_api_gateway_rest_api.main.root_resource_id
  path_part   = "synergy"
}

resource "aws_api_gateway_method" "synergy_get" {
  rest_api_id   = aws_api_gateway_rest_api.main.id
  resource_id   = aws_api_gateway_resource.synergy.id
  http_method   = "GET"
  authorization = "NONE"
}