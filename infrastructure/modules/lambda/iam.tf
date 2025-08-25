# Lambda execution role assume policy
data "aws_iam_policy_document" "lambda_assume_role" {
  statement {
    effect = "Allow"
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "model_lambda_role" {
  name               = "model_lambda_role"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json
}

# Kinesis input stream read permissions
data "aws_iam_policy_document" "kinesis_input_access" {
  statement {
    effect = "Allow"
    actions = [
      "kinesis:DescribeStream",
      "kinesis:GetShardIterator",
      "kinesis:GetRecords",
      "kinesis:ListShards"
    ]
    resources = [var.source_stream_arn]
  }

  statement {
    effect = "Allow"
    actions = ["kinesis:ListStreams"]
    resources = ["*"]
  }
}

resource "aws_iam_policy" "allow_kinesis_processing" {
  name        = "allow_kinesis_processing"
  path        = "/"
  description = "IAM policy for reading from kinesis stream"
  policy      = data.aws_iam_policy_document.kinesis_input_access.json
}

resource "aws_iam_role_policy_attachment" "model_kinesis_permissions" {
  role       = aws_iam_role.model_lambda_role.name
  policy_arn = aws_iam_policy.allow_kinesis_processing.arn
}

# Kinesis output stream write permissions
data "aws_iam_policy_document" "kinesis_output_access" {
  statement {
    effect = "Allow"
    actions = [
      "kinesis:PutRecords",
      "kinesis:PutRecord"
    ]
    resources = [var.output_stream_arn]
  }
}

resource "aws_iam_policy" "kinesis_output_access" {
  name        = "kinesis_output_access"
  description = "IAM policy for writing to kinesis output stream"
  policy      = data.aws_iam_policy_document.kinesis_output_access.json
}

resource "aws_iam_role_policy_attachment" "kinesis_output_access" {
  role       = aws_iam_role.model_lambda_role.name
  policy_arn = aws_iam_policy.kinesis_output_access.arn
}

resource "aws_lambda_permission" "allow_cloudwatch_to_trigger_lambda" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.model_lambda.function_name
  principal     = "events.amazonaws.com"
  source_arn    = var.source_stream_arn
}


# CloudWatch Logs permissions
data "aws_iam_policy_document" "cloudwatch_logs" {
  statement {
    effect = "Allow"
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]
    resources = ["arn:aws:logs:*:*:*"]
  }
}

resource "aws_iam_policy" "allow_logging" {
  name        = "allow_logging"
  path        = "/"
  description = "IAM policy for logging from a lambda"
  policy      = data.aws_iam_policy_document.cloudwatch_logs.json
}


resource "aws_iam_role_policy_attachment" "lambda_logs" {
  role       = aws_iam_role.model_lambda_role.name
  policy_arn = aws_iam_policy.allow_logging.arn
}


# S3 model bucket access permissions
data "aws_iam_policy_document" "s3_model_access" {
  statement {
    effect = "Allow"
    actions = [
      "s3:ListAllMyBuckets",
      "s3:GetBucketLocation",
      "s3:ListBucket"
    ]
    resources = ["arn:aws:s3:::*"]
  }

  statement {
    effect = "Allow"
    actions = [
      "s3:GetObject",
      "s3:ListBucket"
    ]
    resources = [
      "arn:aws:s3:::${var.model_bucket}",
      "arn:aws:s3:::${var.model_bucket}/*"
    ]
  }

  statement {
    effect = "Allow"
    actions = [
      "s3:GetObject",
      "s3:ListBucket"
    ]
    resources = [
      "arn:aws:s3:::${var.dev_bucket}",
      "arn:aws:s3:::${var.dev_bucket}/*"
    ]
  }
}

resource "aws_iam_policy" "model_lambda_s3_policy" {
  name        = "model_lambda_s3_policy"
  description = "IAM policy for lambda accessing S3"
  policy      = data.aws_iam_policy_document.s3_model_access.json
}

resource "aws_iam_role_policy_attachment" "iam-policy-attach" {
  role       = aws_iam_role.model_lambda_role.name
  policy_arn = aws_iam_policy.model_lambda_s3_policy.arn
}
