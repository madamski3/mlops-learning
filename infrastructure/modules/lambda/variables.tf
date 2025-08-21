variable "lambda_function_name" {
  description = "Name of the lambda function that will run the model"
  type        = string
}

variable "image_uri" {
  description = "Uri of the ECR image containing the model that lambda reference"
  type        = string
}

variable "model_bucket" {
  description = "ARN of the kinesis stream that we will send model predictions to"
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
