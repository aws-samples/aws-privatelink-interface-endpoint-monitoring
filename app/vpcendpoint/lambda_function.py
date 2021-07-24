import boto3
from datetime import datetime, timedelta
import time
import pprint
import json
import os
from aws_embedded_metrics import metric_scope

@metric_scope

def lambda_handler(event, context,metrics):
    try:  
        pp = pprint.PrettyPrinter(indent=2)

        # Create CloudWatch client
        cloudwatch = boto3.client('cloudwatch')
        vpcendclient = boto3.client('ec2')

        
        lvTimerange = int(os.environ.get('timerange_min'))
        lvLoggroup=os.environ.get('cloudwatch_loggroup')
        lvNamespace=os.environ.get('name_space')
        lvSnstopic=os.environ.get('sns_topic_arn')
        lvCustomer=os.environ.get('customer')
        lvDebug=os.environ.get('debug')
        lvAlarmThreshhold=int(os.environ.get('alarm_threshholdbytes'))
        lvAlarmCriticalThreshhold=int(os.environ.get('alarm_critical_threshholdbytes'))
        lvAlarmForceGenerate=os.environ.get('alarm_forcegenerate')
        
        response = cloudwatch.describe_alarms(
               AlarmTypes=['MetricAlarm']
        )
        
        #In order to identify owner of each vpc endpoint, we can use Tag Key 'Name' to store owner name/App name etc
        #Let's Collect All VPC Endpoints 'value' from environments which has Tag Key 'Name'  
        
        eniresponse = vpcendclient.describe_vpc_endpoints()
        vpcendpointids = []
        vpcendpointtags = []
        for r in eniresponse["VpcEndpoints"]:
            try:
                #print(r["Tags"])
                for tags in r["Tags"]:
                    if tags["Key"] == 'Name':
                        owner = tags["Value"]
                        vpcendpointids.append(r["VpcEndpointId"])
                        vpcendpointtags.append(owner)
            except Exception:
                pass
            
        #Collect All Alarnnames, to compare against later
        metricalarms = []
        
        #If we plan to change Alarm threshhold/parameters, make this flag Yes for first Run and then switch back to No..else API cost for Alarm definitin every times lambda runs
        if lvAlarmForceGenerate == "Yes":
            metricalarms = []
        else:
            for r in response["MetricAlarms"]:
                metricalarms.append(r['AlarmName'])

    
        #TimeRange(Min) to pull data from LogGroup. Match it with EventBridge Scheduler time
        
        end_time=datetime.now()  
        start_time=datetime.now() + timedelta(minutes=-lvTimerange)
   
        if lvDebug == "Yes":
            print(end_time)
            print(start_time)
            print((end_time - start_time))
    
        start_timestamp: int = int(1000 * start_time.timestamp())
        end_timestamp: int = int(1000 * end_time.timestamp())
    
        logsClient = boto3.client('logs')
        #Log format ${interface-id} ${bytes} ${subnet-id} ${vpc-id} ${account-id}
        #Using Cloudwatch Insight API to extract time range based log data
        
        startQueryResponse  = logsClient.start_query(
            logGroupNames=[
                lvLoggroup,
            ],
            startTime=start_timestamp,
            endTime=end_timestamp,
            queryString="fields  @message | parse @message '* * * * *' as interfaceid, bytes,subnetid,vpcid,accountid | stats sum(bytes) as TotalBytes by interfaceid",
            limit=10000
        )
    
        queryId = str(startQueryResponse["queryId"])
    
        finalStates = ["Complete", "Failed", "Cancelled"]
        status = ""
        while status not in finalStates:
            response = logsClient.get_query_results(queryId=queryId)
            status = response["status"]
            time.sleep(0.2)
        
        if lvDebug == "Yes":
            responsejson=json.dumps(response["results"])
            pp.pprint(responsejson)
    

        if status != "Complete":
            print("Status------------:", status)
            raise Exception("Cloudwatch LogGroup query did not complete successfully:"+lvLoggroup+"Status:"+status)


       
        # All ENI Array
        # All ENI Describe for Metric and Alarm 
        
        #Lets work on r[0] : ENI having r[1] Bytes
           
        for r in response["results"]:
            
            # Check if Bytes(utilization) exist
            if len(r) > 1:
                  # ${interface-id} ${bytes} ${subnet-id} ${vpc-id} ${account-id}
   
                size = int(r[1]["value"])
                sizebytepersec=size/(lvTimerange*60)
                eniname = r[0]["value"]
               
                eniresponse = vpcendclient.describe_network_interfaces(
                    NetworkInterfaceIds=[
                        eniname
                    ]
                )
                
                #f1 eniname f2 interfacetype f3 vpcendpointname

                #Lets filter on VPC Interface Endpoint types and exclude others
                if eniresponse["NetworkInterfaces"][0]["InterfaceType"] != "vpc_endpoint":
                    if lvDebug == "Yes":
                        print("Skipping if its not vpc interface endpoint:",eniresponse["NetworkInterfaces"][0]["InterfaceType"])
                    continue


                vpcendpointnamerec=eniresponse["NetworkInterfaces"][0]["Description"]
                vpcendpointname=vpcendpointnamerec.split()[-1]
                vpcendpointowner="Unknown"
                eniidentifier=vpcendpointname+"-"+eniname
            
                #Search current vpcendpoint in environment vpcendpoints to get Tag Name from Tagarray which was collected earlier too
                               
                if vpcendpointname in vpcendpointids:
                    vpcendpointowner = vpcendpointtags[vpcendpointids.index(vpcendpointname)]
                else:
                    pass

                print("Processing:",eniname,vpcendpointname)
                print("Eni And Bytes:",r[0]["value"],r[1]["value"])

                if lvDebug == "Yes":
                    print("Generating Metrics for:", eniname,vpcendpointname)
                
                #Generate CloudWatch Metrics Using embedded metric approach     
                print(json.dumps({
                            "_aws": {
                                "Timestamp": int(time.time() * 1000),
                                "CloudWatchMetrics": [
                                    {
                                        "Namespace": lvNamespace,
                                        "Dimensions": [ ["Owner", "Identifier"] ],
                                        "Metrics": [
                                            {
                                                "Name": "NetworkTraffic",
                                                "Unit": "Bytes"
                                            }
                                        ]
                                    }
                                ]
                            },
                            "Owner": vpcendpointowner,
                            "Identifier": eniidentifier,
                            "NetworkTraffic": sizebytepersec
                        }
                    )
                )
                
                #Generate Alarm Definitions
                #2 Alarm Definitions created per endpoint High/Critical
                
                #searchalarm="eni-095caef9b2ae5e1d9"
                #Check if Alarm definition already exist
                if eniidentifier not in metricalarms:
                    
                    if lvDebug == "Yes":
                        print("Generating High Alarm for:", eniidentifier)
                    
                    cloudwatch.put_metric_alarm(
                        AlarmName=eniidentifier,
                        ComparisonOperator='GreaterThanOrEqualToThreshold',
                        EvaluationPeriods=10,
                        MetricName='NetworkTraffic',
                        Namespace=lvNamespace,
                        Period=60,
                        Statistic='Average',
                        Threshold=lvAlarmThreshhold,
                        TreatMissingData="ignore",
                        ActionsEnabled=True,
                        DatapointsToAlarm=1,
                        AlarmActions=[  lvSnstopic ],
                        AlarmDescription='High Network Utilization above 70% limit',
                        Dimensions=[
                            {
                              'Name': 'Customer',
                              'Value': lvCustomer
                            },
                            {
                              'Name': 'Identifier',
                              'Value': eniidentifier
                            }
                        ],
                        Unit='Bytes'
                    )
                    #Generate Critical Alarm Definition
                    
                    if lvDebug == "Yes":
                        print("Generating Critical Alarm for:", eniidentifier)

                    cloudwatch.put_metric_alarm(
                        AlarmName=eniidentifier + "-Critical",
                        ComparisonOperator='GreaterThanOrEqualToThreshold',
                        EvaluationPeriods=1,
                        MetricName='NetworkTraffic',
                        Namespace=lvNamespace,
                        Period=60,
                        Statistic='Average',
                        Threshold=lvAlarmCriticalThreshhold,
                        ActionsEnabled=True,
                        TreatMissingData="ignore",
                        DatapointsToAlarm=1,
                        AlarmActions=[  lvSnstopic ],
                        AlarmDescription='Critical Network Utilization above 100% of normal limits. Entering Burst Mode',
                        Dimensions=[
                            {
                              'Name': 'Customer',
                              'Value': lvCustomer
                            },
                            {
                              'Name': 'Identifier',
                              'Value': eniidentifier
                            }
                        ],
                        Unit='Bytes'
                    )
                else: 
                    if lvDebug == "Yes":
                        print("Not Generating Alarm for:", eniidentifier)


    # print(responsejson)

    except Exception as e:
        print(e.__str__())
        raise
        
