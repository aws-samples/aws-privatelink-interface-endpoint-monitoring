# Update Region , VPC ID , SNS Topic

variable "aws_region" {
  default = "us-west-2"
}

variable "vpc_id" {
  default     = "vpc-idxxxxx"
  description = "VPC ID which will be monitored"
}

#10Gbps * 60 = 600 Gigabits/Min = 80530636800 Bytes /Min [75 GB]
#	70% Threshold - High  Alert
#	56371445760  bytes / Min [ 52.5 Gb / Min ]
#95% Threshold - Critical  Alert
#76504104960 bytes / Min [ 71.25 Gb / Min ]

variable "alarm_critical_threshholdbytes" {
  default     = 76504104960
  description = "Critical Threshold limit - Bytes"
}

variable "alarm_threshholdbytes" {
  default     = 56371445760
  description = "High Threshold limit - Bytes"
}

variable "cloudwatch_loggroup" {
  default     = "vpcendpointloggroup"
  description = "AWS Cloudwatch Log Group source to get data"
}


variable "name_space" {
  default     = "vpcendpoint"
  description = "Cloudwatch Metric Custom Namespace"
}

variable "customer" {
  default     = "CustomerNamexxx"
  description = "Customer Name identifier in Alarm Definition"
}

variable "sns_topic_arn" {
  default     = "arn:aws:sns:xxxx"
  description = "SNS Topic for Cloudwatch Alarm configuration"
}

variable "timerange_min" {
  default     = 1
  description = "Last X Minute of log data to read. Match it with EventBridge Scheduler, default 1 Minute"
}


variable "debug" {
  default     = "No"
  description = "Lambda debug mode. If enabled, will print more logging information, to help troubleshoot. Can be tweaked in Lambda Environment Settings also"
}

variable "alarm_forcegenerate" {
  default     = "No"
  description = "If AlarmDefinition already exist for interface endpoint, skip processing it. Make it yes if some alarm definition values need to be overwritten like Thresholds"
}

