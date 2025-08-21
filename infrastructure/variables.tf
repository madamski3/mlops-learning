variable "region" {
  description = "The AWS region to deploy resources in"
  type        = string
  default     = "us-east-2"
}

variable "project_id" {
  description = "The name of the project to use for naming resources"
  type        = string
  default     = "mlops-learning"
}

variable "tags" {
  description = "Tags to apply to the project"
  type        = map(string)
  default = {
    Environment = "staging"
    Project     = "mlops-learning"
    Owner       = "madamski"
  }
}

variable "ride_event_stream_name" {
  description = "The name of the source Kinesis stream for ride events"
  type        = string
  default     = "ride-events"
}

variable "ride_predictions_stream_name" {
  description = "The name of the source Kinesis stream for output ride predictions"
  type        = string
  default     = "ride-predictions"
}

variable "bucket_name" {
  description = "The name of the S3 bucket where ML artifacts are stored"
  type        = string
  default     = "mlops-learning-madamski"
}

variable "repository_name" {
  description = "The name of the ECR repository"
  type        = string
}

variable "lambda_function_local_path" {
  description = "The local path to the Lambda function code"
  type        = string
}

variable "docker_image_local_path" {
  description = "The local path to the Docker image"
  type        = string
}

variable "image_tag" {
  description = "The tag for the Docker image"
  type        = string
  default     = "latest"
}

variable "lambda_function_name" {
  description = "value"
  type = string
}
