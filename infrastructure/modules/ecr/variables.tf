variable "repository_name" {
  description = "The name of the ECR repository"
  type        = string
}

variable "image_tag" {
  description = "The AWS region where the ECR repository is created"
  type        = string
  default     = "latest"
}

variable "lambda_function_local_path" {
  description = "The local path to the Lambda function code"
  type        = string
}

variable "docker_image_local_path" {
  description = "The local path to the Docker image"
  type        = string
}

variable "region" {
  description = "The AWS region where the ECR repository is created"
  type        = string
  default     = "us-east-2"
}
