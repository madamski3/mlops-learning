resource "aws_s3_bucket" "artifacts_s3_bucket" {
  bucket = var.bucket_name
}

output "bucket_name" {
  description = "The name of the S3 bucket"
  value       = aws_s3_bucket.artifacts_s3_bucket.bucket
}
