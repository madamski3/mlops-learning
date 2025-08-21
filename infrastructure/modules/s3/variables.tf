variable "bucket_name" {
  description = "The name of the S3 bucket to create."
  type        = string
  default     = "mlops-learning-madamski"
}

variable "tags" {
  description = "A map of tags to assign to the S3 bucket."
  type        = map(string)
  default     = {}
}
