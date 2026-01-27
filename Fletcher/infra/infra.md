# Fletcher infra (walking skeleton)

This folder deploys a minimal AWS Lambda (Python) that writes a small JSON payload to an **existing** S3 bucket.

## Common commands (prod)

Run these commands in `Fletcher/infra`.

### Terraform

- `terraform init -reconfigure -backend-config=backend-prod.hcl`
- `terraform plan -var-file=prod.tfvars -out=prod.tfplan`
- `terraform apply prod.tfplan`

### Invoke the Lambda (smoke test)

- `aws lambda invoke --region eu-west-1 --function-name fletcher-walking-skeleton-prod out.json`
- `cat out.json`

## What gets created

- `aws_lambda_function`: `fletcher-walking-skeleton-*`
- `aws_iam_role` + inline policy:
  - `s3:PutObject` to your bucket (optionally restricted to a key prefix)
  - CloudWatch Logs permissions (`CreateLogStream`, `PutLogEvents`)
- `aws_cloudwatch_log_group` with 14-day retention

## Remote state (S3 + DynamoDB)

This setup stores Terraform state in S3 and uses a DynamoDB table for state locking.

- **Backend configuration** is supplied at `terraform init` time via `backend-prod.hcl` (not via `prod.tfvars`).
- For additional environments, keep the same state bucket and lock table but change the backend `key`.

Example backend state keys:

- `fletcher/prod/terraform.tfstate`
- `fletcher/test/terraform.tfstate`

## Notes / gotchas

- **Name collisions**:
  - Lambda names are global per-region per-account. Keep `lambda_function_name` environment-specific.

- **Existing bucket policies**:
  - This code does not change your bucket policy.
  - If your bucket has a restrictive bucket policy, it may still block writes even if the Lambda role allows them.

- **Least privilege**:
  - If you set `bucket_key_prefix`, the IAM policy restricts writes to that prefix.
  - If you leave it empty, writes are allowed to `arn:aws:s3:::<bucket>/*`.

## Smoke test behavior

After invoking the Lambda, it should write a JSON object into your bucket under:

- `<bucket_key_prefix>/walking-skeleton/` (if a prefix is set)
- `walking-skeleton/` (if prefix is empty)

## Bootstrap remote state (one-time)

This repository includes a small bootstrap Terraform config at `bootstrap/` that creates:

- An S3 bucket to store Terraform state
- A DynamoDB table for state locking

S3 bucket naming constraints: bucket names must be globally unique and must use only lowercase letters, numbers, and hyphens.

Run these commands in `Fletcher/infra/bootstrap`:

- `terraform init`
- `terraform plan -var-file=prod.bootstrap.tfvars`
- `terraform apply -var-file=prod.bootstrap.tfvars`
