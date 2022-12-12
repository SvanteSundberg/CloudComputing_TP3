import boto3
from botocore.exceptions import ClientError
import time

AWS_REGION = "us-east-1a"
KEY_PAIR_NAME = 'vockey'
AMI_ID = 'ami-061dbd1209944525c'  # ubuntu 18.04
INSTANCE_TYPE = 't2.micro'


ec2_RESOURCE = boto3.resource('ec2', region_name='us-east-1')
ec2_CLIENT = boto3.client('ec2')
elb = boto3.client('elbv2')
cloudwatch = boto3.client('cloudwatch')

response = ec2_CLIENT.describe_vpcs()
vpc_id = response.get('Vpcs', [{}])[0].get('VpcId', '')


def create_security_group():
    try:
        security_group = ec2_RESOURCE.create_security_group(GroupName='security_group',
                                                            Description='Allows all inbound and outbound traffic',
                                                            VpcId=vpc_id,
                                                            )
        security_group_id = security_group.group_id
        security_group.authorize_ingress(
            DryRun=False,
            IpPermissions=[
                {
                    'FromPort': -1,
                    'ToPort': -1,
                    'IpProtocol': '-1',
                    'IpRanges': [
                        {
                            'CidrIp': '0.0.0.0/0',
                            'Description': "Allows all inbound traffic"
                        },
                    ]
                }
            ]
        )

        print('Security Group Created %s in vpc %s.' %
              (security_group_id, vpc_id))
        return security_group_id
    except ClientError as e:
        print(e)


def createSQLinstance(name, sg_id):
    instance = ec2_RESOURCE.create_instances(
        ImageId=AMI_ID,
        InstanceType=INSTANCE_TYPE,
        KeyName=KEY_PAIR_NAME,
        MinCount=1,
        MaxCount=1,
        # UserData=user_data,
        TagSpecifications=[
            {
                'ResourceType': 'instance',
                'Tags': [
                    {
                        'Key': 'Name',
                        'Value': name
                    },
                ]
            },
        ],
        SecurityGroupIds=[sg_id],
        Placement={
            'AvailabilityZone': AWS_REGION}
    )
    return instance


def main():
    security_id = create_security_group()
    print('Launching instances...')
    standalone = createSQLinstance('standalone_SQL', security_id)
    Mgmt_Node = createSQLinstance('Mgmt_Node', security_id)
    Data_Node1 = createSQLinstance('Data_Node1', security_id)
    Data_Node2 = createSQLinstance('Data_Node2', security_id)
    Data_Node3 = createSQLinstance('Data_Node3', security_id)
    standalone[0].wait_until_running()
    print('standalone_SQL instance has private IP: ' +
          standalone[0].private_ip_address)
    Mgmt_Node[0].wait_until_running()
    print('Mgmt_Node instance has private IP: ' +
          Mgmt_Node[0].private_ip_address)
    Data_Node1[0].wait_until_running()
    print('Data_Node1 instance has private IP: ' +
          Data_Node1[0].private_ip_address)
    Data_Node2[0].wait_until_running()
    print('Data_Node2 instance has private IP: ' +
          Data_Node2[0].private_ip_address)
    Data_Node3[0].wait_until_running()
    print('Data_Node3 instance has private IP: ' +
          Data_Node3[0].private_ip_address)
    print('Done')


main()
