resource "aws_iam_role_policy" "lambda_policy" {
  name   = "lambda_policy"
  role   = aws_iam_role.vpcendpoint_lambdarole.id
  policy = file("IAM/lambda_policy.json")
}

resource "aws_iam_role" "vpcendpoint_lambdarole" {
  name               = "vpcendpoint_lambdarole"
  assume_role_policy = file("IAM/lambda_assume_role_policy.json")
}