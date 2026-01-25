provider "aws" {
  region = var.aws_region
}

locals {
  key_prefix_normalized = var.bucket_key_prefix == "" ? "" : (endswith(var.bucket_key_prefix, "/") ? var.bucket_key_prefix : "${var.bucket_key_prefix}/")

  s3_object_arn_prefix = var.bucket_key_prefix == "" ? "arn:aws:s3:::${var.bucket_name}/*" : "arn:aws:s3:::${var.bucket_name}/${local.key_prefix_normalized}*"

  lambda_zip_path = "${path.module}/build/lambda.zip"
}

data "archive_file" "lambda_zip" {
  type        = "zip"
  output_path = local.lambda_zip_path

  source {
    content  = file("${path.module}/../lambda/app.py")
    filename = "app.py"
  }
}

resource "aws_cloudwatch_log_group" "lambda" {
  name              = "/aws/lambda/${var.lambda_function_name}"
  retention_in_days = 14
  tags              = var.tags
}

resource "aws_iam_role" "lambda" {
  name = "${var.lambda_function_name}-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })

  tags = var.tags
}

resource "aws_iam_role_policy" "lambda" {
  name = "${var.lambda_function_name}-policy"
  role = aws_iam_role.lambda.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "WriteObjectsOnly"
        Effect = "Allow"
        Action = [
          "s3:PutObject"
        ]
        Resource = local.s3_object_arn_prefix
      },
      {
        Sid    = "LambdaLogging"
        Effect = "Allow"
        Action = [
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "${aws_cloudwatch_log_group.lambda.arn}:*"
      }
    ]
  })
}

resource "aws_lambda_function" "fletcher" {
  function_name = var.lambda_function_name
  role          = aws_iam_role.lambda.arn

  runtime          = "python3.12"
  handler          = "app.handler"
  filename         = data.archive_file.lambda_zip.output_path
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256

  timeout     = 10
  memory_size = 128

  environment {
    variables = {
      BUCKET_NAME = var.bucket_name
      KEY_PREFIX  = local.key_prefix_normalized
    }
  }

  depends_on = [
    aws_cloudwatch_log_group.lambda
  ]

  tags = var.tags
}
