variable "dev_bucket_name" {
  description = "The name of the S3 bucket that MLFlow experiments will be saved to"
  type        = string
  default     = "mlops-learning-madamski"
}

variable "prod_bucket_name" {
  description = "The name of the S3 bucket that will store the prod model"
  type        = string
}

variable "tags" {
  description = "A map of tags to assign to the S3 bucket."
  type        = map(string)
  default     = {}
}
