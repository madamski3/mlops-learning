variable "lambda_function_name" {
  description = "Name of the lambda function that will run the model"
  type        = string
}

variable "image_uri" {
  description = "Uri of the ECR image containing the model that lambda reference"
  type        = string
}

variable "model_bucket" {
  description = "Name of the production S3 bucket for ML models"
  type        = string
}

variable "dev_bucket" {
  description = "Name of the development S3 bucket for ML models"
  type        = string
}

variable "output_stream_arn" {
  description = "ARN of the kinesis stream that we will send model predictions to"
  type        = string
}

variable "output_stream_name" {
  description = "Name of the kinesis stream that we will send model predictions to"
  type        = string
}

variable "source_stream_arn" {
  description = "ARN of the kinesis stream that ride events will be sourced from"
  type        = string
}

variable "source_stream_name" {
  description = "Name of the kinesis stream that ride events will be sourced from"
  type        = string
}

variable "lambda_role_name" {
  description = "Name of the role that will be given to the lambda function"
  type = string
}

variable "kinesis_read_policy_name" {
  description = "Name of the IAM policy allowing the Lambda role to read from Kinesis"
  type = string
}

variable "kinesis_write_policy_name" {
  description = "Name of the IAM policy allowing the Lambda role to write to Kinesis"
  type = string
}

variable "cloudwatch_log_policy_name" {
  description = "Name of the IAM policy allowing the Lambda role to write to Kinesis"
  type = string
}

variable "s3_access_policy_name" {
  description = "Name of the IAM policy allowing the Lambda role to write to Kinesis"
  type = string
}
