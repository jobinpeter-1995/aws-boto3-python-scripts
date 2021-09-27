import boto3
session = boto3.Session(aws_access_key_id="your_access_key",aws_secret_access_key="your_secret_key",region_name="us-east-2")
server_list = []
ec2 = session.client("ec2")
reservations = ec2.describe_instances(Filters=[
        {
            "Name": "instance-state-name",
            "Values": ["running"],
        }
    ]).get("Reservations")
# Appending the list of running servers
for reservation in reservations:
    for instance in reservation["Instances"]:
        id = instance["InstanceId"]
        server_list.append(id)

# creating an object for cloudwatch
cloudwatch = boto3.client('cloudwatch')

#creating a cloudwatch alarm for status check failed instances and routing the alert via SNS
for ec2_instance in server_list:
    cloudwatch.put_metric_alarm(
        AlarmName='Status check failed for Instance ID%s' % ec2_instance,
        EvaluationPeriods=2,
        MetricName='StatusCheckFailed',
        Namespace="AWS/EC2",
        Period=60,
        Statistic='Average',
        Threshold=1,
        ComparisonOperator='GreaterThanOrEqualToThreshold',
        DatapointsToAlarm=2,
        ActionsEnabled=True,
        AlarmActions=['sns_arn'],
        AlarmDescription='Status check failed for the instance %s' % ec2_instance,
        Dimensions=[
            {
              'Name': 'InstanceId',
              'Value': ec2_instance
            },
        ],
    )
