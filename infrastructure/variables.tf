variable "aws_region" {
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
