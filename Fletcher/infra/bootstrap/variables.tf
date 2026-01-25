variable "aws_region" {
  type        = string
  description = "AWS region to create the state bucket and DynamoDB lock table in."
}

variable "state_bucket_name" {
  type        = string
  description = "Globally-unique S3 bucket name to store Terraform state."
}

variable "lock_table_name" {
  type        = string
  description = "DynamoDB table name to use for Terraform state locking."
  default     = "terraform-locks"
}

variable "tags" {
  type        = map(string)
  description = "Tags applied to created resources."
  default     = {}
}
