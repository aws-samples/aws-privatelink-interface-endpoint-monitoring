resource "null_resource" "install_python_dependencies" {
  triggers = {
    build = "timestamp()"
  }
  provisioner "local-exec" {
    command = "pip3 install -r ${path.module}/app/vpcendpoint/requirements.txt -t ${path.module}/app/vpcendpoint/"
  }
}

data "archive_file" "vpcendpoint" {
	  type        = "zip"
    source_dir  = "app/vpcendpoint/"
    output_path = "app/vpcendpoint/lambda_function.zip"
    depends_on = [null_resource.install_python_dependencies]
 }

resource "aws_lambda_function" "lambda_function" {
  description   = "Processes Cloudwatch Logstreams of VPC Endpoint ENI"
  filename         = data.archive_file.vpcendpoint.output_path
  source_code_hash = data.archive_file.vpcendpoint.output_base64sha256

  function_name = "vpc_interface_endpoint_monitoring"
  role          = aws_iam_role.vpcendpoint_lambdarole.arn
  handler       = "lambda_function.lambda_handler"
  runtime     = "python3.8"
  memory_size = 512
  timeout     = 300

  environment {
    variables = {
      alarm_forcegenerate            = var.alarm_forcegenerate,
      alarm_critical_threshholdbytes = var.alarm_critical_threshholdbytes,
      alarm_threshholdbytes          = var.alarm_threshholdbytes,
      cloudwatch_loggroup            = var.cloudwatch_loggroup,
      customer                       = var.customer,
      debug                          = var.debug,
      name_space                     = var.name_space,
      sns_topic_arn	                 = var.sns_topic_arn,
      timerange_min                  = var.timerange_min
    }
  }

}

