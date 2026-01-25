output "lambda_function_name" {
  value = aws_lambda_function.fletcher.function_name
}

output "lambda_role_arn" {
  value = aws_iam_role.lambda.arn
}

output "s3_write_resource" {
  value = local.s3_object_arn_prefix
}
