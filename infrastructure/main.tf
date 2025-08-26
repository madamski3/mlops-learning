terraform {
  required_version = ">=1.0"
  backend "s3" {
    bucket  = "mlops-environment-terraform"
    key     = "mlops-environment-stg.tfstate"
    region  = "us-east-2"
    encrypt = true
  }
}

provider "aws" {
  region = var.region
}

data "aws_caller_identity" "current_identity" {}

locals {
  account_id = data.aws_caller_identity.current_identity.account_id
}

module "kinesis_streams" {
  source                       = "./modules/kinesis"
  ride_event_stream_name       = var.ride_event_stream_name
  ride_predictions_stream_name = var.ride_predictions_stream_name
  shard_count                  = 1
  retention_period             = 24
  tags                         = var.tags
}

module "s3_buckets" {
  source      = "./modules/s3"
  dev_bucket_name = var.dev_bucket_name
  prod_bucket_name = var.prod_bucket_name
  tags        = var.tags
}

module "ecr" {
  source                     = "./modules/ecr"
  repository_name            = var.repository_name
  lambda_function_local_path = var.lambda_function_local_path
  docker_image_local_path    = var.docker_image_local_path
  image_tag                  = var.image_tag
  region                     = var.region
  # account_id                 = local.account_id
}

module "lambda" {
  source = "./modules/lambda"
  image_uri = module.ecr.image_uri
  lambda_function_name = var.lambda_function_name
  model_bucket = module.s3_buckets.prod_bucket_name
  dev_bucket = module.s3_buckets.dev_bucket_name
  source_stream_arn = module.kinesis_streams.ride_events_stream_arn
  source_stream_name = var.ride_event_stream_name
  output_stream_arn = module.kinesis_streams.ride_predictions_stream_arn
  output_stream_name = var.ride_predictions_stream_name
  lambda_role_name = var.lambda_role_name
  kinesis_read_policy_name = var.kinesis_read_policy_name
  kinesis_write_policy_name = var.kinesis_write_policy_name
  cloudwatch_log_policy_name = var.cloudwatch_log_policy_name
  s3_access_policy_name = var.s3_access_policy_name
}
