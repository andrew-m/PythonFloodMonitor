variable "aws_region" {
  type        = string
  description = "AWS region to deploy into."
}

variable "bucket_name" {
  type        = string
  description = "Existing S3 bucket name the Lambda will write into."
}

variable "bucket_key_prefix" {
  type        = string
  description = "Optional key prefix to restrict writes under (e.g. 'fletcher'). Leave empty for no prefix restriction."
  default     = ""
}

variable "lambda_function_name" {
  type        = string
  description = "Lambda function name."
  default     = "fletcher-walking-skeleton"
}

variable "tags" {
  type        = map(string)
  description = "Tags applied to created resources."
  default     = {}
}
