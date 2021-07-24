resource "aws_cloudwatch_log_group" "flowcwloggroup" {
  name              = var.cloudwatch_loggroup
  retention_in_days = 1
}

resource "aws_flow_log" "vpcflowlogcw" {
  iam_role_arn             = aws_iam_role.vpcflowlogcwrole.arn
  log_destination          = aws_cloudwatch_log_group.flowcwloggroup.arn
  traffic_type             = "ALL"
  vpc_id                   = var.vpc_id
  max_aggregation_interval = 60
  log_format               = "$${interface-id} $${bytes} $${subnet-id} $${vpc-id} $${account-id}"
  tags = {
    "Name" = "vpcendpointmonitor"
  }
  depends_on = [
    aws_cloudwatch_log_group.flowcwloggroup
  ]
}


resource "aws_iam_role" "vpcflowlogcwrole" {
  name = "vpcflowlogcwrole"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "",
      "Effect": "Allow",
      "Principal": {
        "Service": "vpc-flow-logs.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF
}

resource "aws_iam_role_policy" "vpcflowlogcwrolepolicy" {
  name = "vpcflowlogcwrolepolicy"
  role = aws_iam_role.vpcflowlogcwrole.id

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": [
        "logs:CreateLogStream",
        "logs:PutLogEvents",
        "logs:DescribeLogGroups",
        "logs:DescribeLogStreams"
      ],
      "Effect": "Allow",
      "Resource": "*"
    }
  ]
}
EOF
}