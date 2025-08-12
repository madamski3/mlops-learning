variable "ride_event_stream_name" {
  description = "The name of the Kinesis stream for ride events"
  type        = string
  default     = "ride-events"
}

variable "ride_predictions_stream_name" {
  description = "The name of the Kinesis stream that predictions will be sent to"
  type        = string
  default     = "ride-predictions"
}

variable "shard_count" {
  description = "The number of shards for the Kinesis stream"
  type        = number
  default     = 1
}

variable "retention_period" {
  description = "The retention period for the Kinesis stream in hours"
  type        = number
  default     = 24
}

variable "shard_level_metrics" {
  description = "List of shard level metrics to enable for the Kinesis stream"
  type        = list(string)
  default = [
    "IncomingBytes",
    "OutgoingBytes",
    "IncomingRecords",
    "OutgoingRecords",
    "WriteProvisionedThroughputExceeded",
    "ReadProvisionedThroughputExceeded",
    "IteratorAgeMilliseconds"
  ]
}

variable "tags" {
  description = "Tags to apply to the Kinesis stream"
  type        = map(string)
  default = {
    Environment = "staging"
    Project     = "mlops-learning"
    Owner       = "madamski"
  }
}
