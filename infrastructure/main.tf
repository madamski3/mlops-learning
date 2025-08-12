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
  region = var.aws_region
}

data "aws_caller_identity" "current_identity" {}

locals {
  account_id = data.aws_caller_identity.current_identity.account_id
}

module "kinesis_streams" {
  source                       = "./modules/kinesis"
  ride_event_stream_name       = "ride-events"
  ride_predictions_stream_name = "ride-predictions"
  shard_count                  = 1
  retention_period             = 24
  tags                         = var.tags
}
