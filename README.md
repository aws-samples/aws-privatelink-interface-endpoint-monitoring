## Monitor network throughput of interface VPC endpoints using Amazon CloudWatch

<h2>Prerequisites</h2>
To deploy the solution, you need the following:
<ul>
 	<li>An AWS account</li>
 	<li>Amazon VPC with interface endpoints configured</li>
 	<li><a href="https://aws.amazon.com/iam/">AWS Identity and Access Management</a> (IAM) role with the correct permissions</li>
 	<li><a href="https://www.terraform.io/">Terraform</a> setup as you will deploy the solution into your AWS account by <a href="https://learn.hashicorp.com/collections/terraform/aws-get-started">launching a Terraform template.</a></li>
 	<li><a href="https://aws.amazon.com/cli/">AWS Command Line Interface</a> v2.1.x</li>
 	<li><a href="https://github.com/git-guides/install-git">Github client</a> v2.x</li>
 	<li>An SNS topic to receive alarm notifications. For instructions, see <a href="https://docs.aws.amazon.com/sns/latest/dg/sns-create-topic.html">Creating an SNS topic</a>.</li>
</ul>

<h3>Deploy the solution using Terraform</h3>
The Terraform template has the following input parameters, which you can modify as appropriate for your use case.
<table style="margin-left: 45px;" border="1" width="0">
<tbody>
<tr>
<td style="background-color: #000000; color: #ffffff; padding-left: 10px;" width="233">Parameter</td>
<td style="background-color: #000000; color: #ffffff; padding-left: 10px;" width="301">Variable</td>
<td style="background-color: #000000; color: #ffffff; padding-left: 10px;" width="301">Default</td>
<td style="background-color: #000000; color: #ffffff; padding-left: 10px;" width="301">Description</td>
</tr>
<tr style="padding-left: 10px;">
<td style="padding-left: 10px;" width="233">AWS Region</td>
<td style="padding-left: 10px;" width="301">aws_region</td>
<td style="padding-left: 10px;" width="301">sa-east-1</td>
<td style="padding-left: 10px;" width="301">The AWS Region to be used for deployment.</td>
</tr>
<tr style="padding-left: 10px;">
<td style="padding-left: 10px;" width="233">Amazon VPC Id</td>
<td style="padding-left: 10px;" width="301">vpc_id</td>
<td style="padding-left: 10px;" width="301"></td>
<td style="padding-left: 10px;" width="301">The ID of the VPC to be monitored.</td>
</tr>
<tr style="padding-left: 10px;">
<td style="padding-left: 10px;" width="233">Alarm Critical Threshold (Bytes)</td>
<td style="padding-left: 10px;" width="301">alarm_critical_threshholdbytes</td>
<td style="padding-left: 10px;" width="301">76504104960</td>
<td style="padding-left: 10px;" width="301">The monitoring threshold, in bytes, for critical alarms.</td>
</tr>
<tr style="padding-left: 10px;">
<td style="padding-left: 10px;" width="233">Alarm Threshhold (Bytes)</td>
<td style="padding-left: 10px;" width="301">alarm_threshholdbytes</td>
<td style="padding-left: 10px;" width="301">56371445760</td>
<td style="padding-left: 10px;" width="301">The monitoring threshold, in bytes, for initial alarms.</td>
</tr>
<tr style="padding-left: 10px;">
<td style="padding-left: 10px;" width="233">CloudWatch Log Group</td>
<td style="padding-left: 10px;" width="301">cloudwatch_loggroup</td>
<td style="padding-left: 10px;" width="301">vpcendpointloggroup</td>
<td style="padding-left: 10px;" width="301">The name of the CloudWatch log group name that will capture flow log data.</td>
</tr>
<tr style="padding-left: 10px;">
<td style="padding-left: 10px;" width="233">CloudWatch Metric NameSpace</td>
<td style="padding-left: 10px;" width="301">name_space</td>
<td style="padding-left: 10px;" width="301">vpcendpoint</td>
<td style="padding-left: 10px;" width="301">The CloudWatch metric namespace that will collect metrics for all endpoint interfaces.</td>
</tr>
<tr style="padding-left: 10px;">
<td style="padding-left: 10px;" width="233">SNS Topic ARN for Alarm notification</td>
<td style="padding-left: 10px;" width="301">sns_topic_arn</td>
<td style="padding-left: 10px;" width="301"></td>
<td style="padding-left: 10px;" width="301">The ARN of the SNS topic configured for the CloudWatch alarm.</td>
</tr>
<tr style="padding-left: 10px;">
<td style="padding-left: 10px;" width="233">Log Processing Interval (Min)</td>
<td style="padding-left: 10px;" width="301">timerange_min</td>
<td style="padding-left: 10px;" width="301">1</td>
<td style="padding-left: 10px;" width="301">The duration, in minutes, the Lambda function will use to capture log data from the CloudWatch log group.</td>
</tr>
</tbody>
</table>
<h2>Deploying the Solution</h2>
<h3>Using AWS CLI to deploy the template</h3>
Run the following command in your AWS CLI environment:
<div class="hide-language">
<pre><code class="lang-txt">$ git clone https://github.com/aws-samples/aws-privatelink-interface-endpoint-monitoring
$ terraform init
#Modify variables.tf input parameters as per environment needs by referring above table 
$ terraform plan
$ terraform apply</code></pre>
</div>
It will take approximately ~10 minutes to deploy the solution. Upon a successful deployment of the template, the following resources are created:
<ul>
 	<li>An IAM role, vpcflowlogcwrole, allows VPC Flow Logs to be written to CloudWatch Logs.</li>
 	<li>A VPC flow log where records are stored in this format:</li>
</ul>
<code style="margin-left: 40px;">${interface-id} ${bytes} ${subnet-id} ${vpc-id} ${account-id}</code>
<table style="margin-left: 45px;" border="1" width="0">
<tbody>
<tr>
<td style="background-color: #000000; color: #ffffff; padding-left: 10px;" width="233">interface-id</td>
<td style="padding-left: 10px;" width="301">The ID of the network interface for which the traffic is recorded.</td>
</tr>
<tr style="padding-left: 10px;">
<td style="background-color: #000000; color: #ffffff; padding-left: 10px;" width="233">bytes</td>
<td style="padding-left: 10px;" width="301">The number of bytes transferred during the flow.</td>
</tr>
<tr style="padding-left: 10px;">
<td style="background-color: #000000; color: #ffffff; padding-left: 10px;" width="233">subnet-id</td>
<td style="padding-left: 10px;" width="301">The ID of the subnet that contains the network interface for which the traffic is recorded.</td>
</tr>
<tr style="padding-left: 10px;">
<td style="background-color: #000000; color: #ffffff; padding-left: 10px;" width="233">vpc-id</td>
<td style="padding-left: 10px;" width="301">The ID of the VPC that contains the network interface for which the traffic is recorded.</td>
</tr>
<tr style="padding-left: 10px;">
<td style="background-color: #000000; color: #ffffff; padding-left: 10px;" width="233">account-id</td>
<td style="padding-left: 10px;" width="301">The AWS account ID of the owner of the source network interface for which traffic is recorded.</td>
</tr>
</tbody>
</table>
<ul>
 	<li>A CloudWatch log group, which captures flow log data in an individual log stream for each interface VPC endpoint.</li>
 	<li>An EventBridge rule that triggers the Lambda function at scheduled intervals.</li>
 	<li>A Lambda function written in Python with environment variables as per user-defined parameters.</li>
 	<li>CloudWatch metrics are created as part of the Lambda function run.</li>
 	<li>Two CloudWatch alarm definitions with each endpoint interface name. Additionally Critical alarms are suffixed with <code><span style="font-style: normal !msorm;"><em>Critical</em></span></code>.</li>
</ul>
<h2>Viewing and visualizing metrics</h2>
After the solution starts to process event data, you can view the metrics and alarm definitions for the interface endpoints.

Now that your data is available in CloudWatch Metrics, you can create an interactive Amazon CloudWatch dashboard using the instructions mentioned here <a href="https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/create_dashboard.html">Creating a CloudWatch dashboard.</a>

<img class="aligncenter size-full wp-image-22282" src="https://d2908q01vomqb2.cloudfront.net/972a67c48192728a34979d9a35164c1295401b71/2021/07/19/Figure-2-CloudWatch-Dashboard.png" alt="The CloudWatch dashboard displays the VPCEndpointMonitor metric." width="3024" height="" />
<p style="text-align: center;"><em> Figure 2: CloudWatch dashboard</em></p>
For every interface endpoint, two alarm definitions are created and configured per user-defined threshold limits.

<img class="aligncenter size-full wp-image-22283" src="https://d2908q01vomqb2.cloudfront.net/972a67c48192728a34979d9a35164c1295401b71/2021/07/19/Figure-3-Alarms-in-CLoudWatch.png" alt="The Alarms page in the CloudWatch console displays alarms for the VpcEndpointMonitor metric." width="2674" height="" />
<p style="text-align: center;"><em>Figure 3: Alarms page in the CloudWatch console</em></p>

<h2>Cleanup</h2>
To avoid any additional charges after you test the solution, run the following command to delete the resources:

<code>$ terraform destroy</code>


## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.

