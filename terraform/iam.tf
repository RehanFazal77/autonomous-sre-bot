module "iam_eks_role" {
  source    = "terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts-eks"
  version   = "~> 5.0"

  role_name = "sre-bot-sqs-role"

  oidc_providers = {
    ex = {
      provider_arn               = module.eks.oidc_provider_arn
      namespace_service_accounts = ["default:sre-bot-sa"]
    }
  }

  role_policy_arns = {
    policy = aws_iam_policy.sqs_read.arn
  }
}

resource "aws_iam_policy" "sqs_read" {
  name        = "SREBotSQSReadPolicy"
  description = "Allows SRE bot to read from remediation SQS queue"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "sqs:ReceiveMessage",
          "sqs:DeleteMessage",
          "sqs:GetQueueAttributes"
        ]
        Effect   = "Allow"
        Resource = aws_sqs_queue.remediation_queue.arn
      },
    ]
  })
}
