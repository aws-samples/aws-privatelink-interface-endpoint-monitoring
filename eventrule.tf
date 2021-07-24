#   
resource "aws_cloudwatch_event_rule" "vpcendpointlambdascheduler" {
  name        = "vpcendpointlambdascheduler"
  description = "Launches Lambda function <vpcendpointmonitor>"
  depends_on = [
    aws_lambda_function.lambda_function
  ]
  schedule_expression = "rate(1 minute)"
}

resource "aws_cloudwatch_event_target" "vpclambda" {
  rule      = aws_cloudwatch_event_rule.vpcendpointlambdascheduler.name
  target_id = "lambda"
  arn       = aws_lambda_function.lambda_function.arn
}

resource "aws_lambda_permission" "allow_cloudwatch" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.lambda_function.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.vpcendpointlambdascheduler.arn
}

