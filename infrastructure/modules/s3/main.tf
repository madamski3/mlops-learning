data "aws_s3_bucket" "artifacts_s3_bucket" {
  bucket = var.dev_bucket_name
}

output "dev_bucket_name" {
  description = "The name of the S3 bucket"
  value       = data.aws_s3_bucket.artifacts_s3_bucket.bucket
}

resource "aws_s3_bucket" "prod_s3_bucket" {
  bucket = var.prod_bucket_name
}

output "prod_bucket_name" {
  description = "The name of the S3 bucket"
  value       = aws_s3_bucket.prod_s3_bucket.bucket
}
