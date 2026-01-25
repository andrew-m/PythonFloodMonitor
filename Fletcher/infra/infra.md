# Fletcher infra (walking skeleton)

This folder deploys a minimal AWS Lambda (Python) that writes a small JSON payload to an **existing** S3 bucket.

## Remote Terraform state (recommended)

This project supports remote Terraform state in S3 with a DynamoDB lock table.

Remote state avoids being dependent on a single workstation. It also prevents concurrent `apply` runs from corrupting state.

### Bootstrap (one-time)

This repository includes a small bootstrap Terraform config at `bootstrap/` that creates:

- An S3 bucket to store Terraform state (private, versioning enabled, encryption enabled)
- A DynamoDB table for state locking

Note: S3 bucket names must be globally unique and must use only lowercase letters, numbers, and hyphens (no underscores, no capitals).

Recommended: copy `prod.bootstrap.tfvars.example` to `prod.bootstrap.tfvars` and edit values.

Run these commands in `Fletcher/infra/bootstrap`:

- `terraform init`
- `terraform plan -var-file=prod.bootstrap.tfvars`
- `terraform apply -var-file=prod.bootstrap.tfvars`

If the apply partially succeeds (e.g. lock table created but bucket failed due to naming), fix the bucket name and rerun the same `terraform apply`.

Keep a note of the resulting `state_bucket_name` and `lock_table_name` outputs.

### Configure the backend

The main Terraform config in this directory uses an S3 backend (see `backend.tf`). Backends cannot use normal Terraform variables, so you pass backend settings at init time.

Recommended: copy `backend-prod.hcl.example` to `backend-prod.hcl` and edit values.

Run these commands in `Fletcher/infra`:

- `terraform init -reconfigure -backend-config=backend-prod.hcl`

For future environments, keep the same bucket and table but change the `key`.

Example keys:

- `fletcher/prod/terraform.tfstate`
- `fletcher/test/terraform.tfstate`

## What gets created

- `aws_lambda_function`: `fletcher-walking-skeleton-*`
- `aws_iam_role` + inline policy:
  - `s3:PutObject` to your bucket (optionally restricted to a key prefix)
  - CloudWatch Logs permissions (`CreateLogStream`, `PutLogEvents`)
- `aws_cloudwatch_log_group` with 14-day retention

## Variables

Variables are defined in `variables.tf`.

You can supply variables via:

- a `*.tfvars` file (recommended)
- `-var` CLI flags
- environment variables (`TF_VAR_<name>`)

Note: backend configuration (remote state bucket/table/key) is not supplied via `prod.tfvars`. It is supplied at `terraform init` time via `backend-prod.hcl`.

### About S3 "prefixes"

An S3 "prefix" is **not a bucket configuration**. It is just the start of an object key.

Example: writing an object with key `fletcher/prod/walking-skeleton/20260124T181500Z.json` means the prefix is `fletcher/prod/`.

You **do not** need to create that prefix in S3 ahead of time; S3 will show it like a folder in the console automatically.

If you leave `bucket_key_prefix = ""`, the Lambda will write keys like `walking-skeleton/<timestamp>.json` at the bucket root.

## How to deploy

1. Create a real tfvars file from the template:

   - Copy `prod.tfvars.example` to `prod.tfvars`
   - Replace placeholder values

2. Initialize Terraform:

   - Run `terraform init` in this directory.
   - If you are using remote state, use the `terraform init -reconfigure ...` command shown above.

3. Plan:

   - Run `terraform plan -var-file=prod.tfvars`

4. Apply:

   - Run `terraform apply -var-file=prod.tfvars`

## Idempotency / gotchas

- Terraform is **intended to be idempotent** *as long as it has the same state and inputs*.
  - Re-running `apply` with no config changes should result in `No changes`.

- **State matters**:
  - Terraform tracks what it created in a state file.
  - If you use remote state, losing a workstation is not a problem.
  - If you use local state and lose/delete it, Terraform may try to recreate resources.

- **Name collisions**:
  - Lambda names are global per-region per-account. Keep `lambda_function_name` environment-specific.

- **Existing bucket policies**:
  - This code does not change your bucket policy.
  - If your bucket has a restrictive bucket policy, it may still block writes even if the Lambda role allows them.

- **Least privilege**:
  - If you set `bucket_key_prefix`, the IAM policy restricts writes to that prefix.
  - If you leave it empty, writes are allowed to `arn:aws:s3:::<bucket>/*`.

## How to test

After `apply`, invoke the Lambda (console or CLI). It should write a JSON object into your bucket under:

- `<bucket_key_prefix>/walking-skeleton/` (if a prefix is set)
- `walking-skeleton/` (if prefix is empty)

Then check CloudWatch Logs for the function if anything fails.
