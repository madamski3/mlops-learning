# Outputs for CI/CD logs
output "ecr_repository" {
  value = var.repository_name
}

output "image_uri" {
  value = module.ecr.image_uri
}

output "predictions_stream_name" {
  value = var.ride_predictions_stream_name
}

output "model_bucket" {
  value = module.s3_buckets.prod_bucket_name
}

output "lambda_function" {
  value = var.lambda_function_name
}
