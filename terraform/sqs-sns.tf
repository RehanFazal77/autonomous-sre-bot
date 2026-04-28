resource "aws_sns_topic" "datadog_alerts" {
  name = "datadog-alerts-topic"
}

resource "aws_sqs_queue" "remediation_queue" {
  name = "sre-remediation-queue"
}

resource "aws_sns_topic_subscription" "sns_to_sqs" {
  topic_arn = aws_sns_topic.datadog_alerts.arn
  protocol  = "sqs"
  endpoint  = aws_sqs_queue.remediation_queue.arn
}

resource "aws_sqs_queue_policy" "remediation_queue_policy" {
  queue_url = aws_sqs_queue.remediation_queue.id
  policy    = data.aws_iam_policy_document.sns_to_sqs.json
}

data "aws_iam_policy_document" "sns_to_sqs" {
  statement {
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["sns.amazonaws.com"]
    }
    actions   = ["sqs:SendMessage"]
    resources = [aws_sqs_queue.remediation_queue.arn]
    condition {
      test     = "ArnEquals"
      variable = "aws:SourceArn"
      values   = [aws_sns_topic.datadog_alerts.arn]
    }
  }
}

# Output the SQS URL for the python bot to use
output "sqs_queue_url" {
  value = aws_sqs_queue.remediation_queue.url
}
