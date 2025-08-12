resource "aws_kinesis_stream" "ride_events_stream" {
  name                = var.ride_event_stream_name
  shard_count         = var.shard_count
  retention_period    = var.retention_period
  shard_level_metrics = var.shard_level_metrics
  tags                = var.tags
}

resource "aws_kinesis_stream" "ride_predictions_stream" {
  name                = var.ride_predictions_stream_name
  shard_count         = var.shard_count
  retention_period    = var.retention_period
  shard_level_metrics = var.shard_level_metrics
  tags                = var.tags
}

output "ride_events_stream_arn" {
  description = "The ARN of the Kinesis stream"
  value       = aws_kinesis_stream.ride_events_stream.arn
}

output "ride_predictions_stream_arn" {
  description = "The ARN of the Kinesis stream"
  value       = aws_kinesis_stream.ride_predictions_stream.arn
}
