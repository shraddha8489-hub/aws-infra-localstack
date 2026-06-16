resource "aws_sqs_queue" "deadletter" {
  name = "${var.queue_name}-dlq"

  tags = {
    Name        = "${var.queue_name}-dlq"
    Environment = var.environment
    Project     = var.project_name
    ManagedBy   = "terraform"
  }
}

resource "aws_sqs_queue" "this" {
  name                       = var.queue_name
  visibility_timeout_seconds = var.visibility_timeout
  message_retention_seconds  = var.message_retention_seconds

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.deadletter.arn
    maxReceiveCount     = 3
  })

  tags = {
    Name        = var.queue_name
    Environment = var.environment
    Project     = var.project_name
    ManagedBy   = "terraform"
  }
}