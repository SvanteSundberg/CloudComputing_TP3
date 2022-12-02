import boto3
from botocore.exceptions import ClientError
import time

AWS_REGION = "us-east-1a"
KEY_PAIR_NAME = 'vockey'
AMI_ID = 'ami-08c40ec9ead489470'  # Amazon Linux 2
INSTANCE_TYPE = 't2.micro'
USER_DATA = '''#!/bin/bash
    sudo apt-get update
    sudo mkdir -p /opt/mysqlcluster/home
    cd /opt/mysqlcluster/home
    sudo wget http://dev.mysql.com/get/Downloads/MySQL-Cluster-7.2/mysql-cluster-gpl-7.2.1-linux2.6-x86_64.tar.gz


    sudo tar xvf mysql-cluster-gpl-7.2.1-linux2.6-x86_64.tar.gz
    sudo ln -s mysql-cluster-gpl-7.2.1-linux2.6-x86_64 mysqlc

    #set up paths globally

    echo 'export MYSQLC_HOME=/opt/mysqlcluster/home/mysqlc' | sudo tee /etc/profile.d/mysqlc.sh
    echo 'export PATH=$MYSQLC_HOME/bin:$PATH' | sudo tee -a /etc/profile.d/mysqlc.sh

    source /etc/profile.d/mysqlc.sh

    #install libncurses5
    sudo apt-get update && sudo apt-get -y install libncurses5
        '''

ec2_RESOURCE = boto3.resource('ec2', region_name='us-east-1')
ec2_CLIENT = boto3.client('ec2')
elb = boto3.client('elbv2')
cloudwatch = boto3.client('cloudwatch')

response = ec2_CLIENT.describe_vpcs()
vpc_id = response.get('Vpcs', [{}])[0].get('VpcId', '')


# Creates a security group with 3 inbound rules allowing TCP traffic through custom ports
def create_security_group():
    # We will create a security group in the existing VPC
    try:
        security_group = ec2_RESOURCE.create_security_group(GroupName='security_group',
                                                            Description='Allows traffic on ports 22,80,433',
                                                            VpcId=vpc_id,
                                                            )
        security_group_id = security_group.group_id
        security_group.authorize_ingress(
            DryRun=False,
            IpPermissions=[
                {
                    'FromPort': 22,
                    'ToPort': 22,
                    'IpProtocol': 'TCP',
                    'IpRanges': [
                        {
                            'CidrIp': '0.0.0.0/0',
                            'Description': "Allows inbound ssh traffic"
                        },
                    ]
                },
                {
                    'FromPort': 80,
                    'ToPort': 80,
                    'IpProtocol': 'TCP',
                    'IpRanges': [
                        {
                            'CidrIp': '0.0.0.0/0',
                            'Description': "Allows inbound http traffic"
                        },
                    ]
                },
                {
                    'FromPort': 433,
                    'ToPort': 433,
                    'IpProtocol': 'TCP',
                    'IpRanges': [
                        {
                            'CidrIp': '0.0.0.0/0',
                            'Description': "Allows inbound https traffic"
                        },
                    ]
                }
            ]
        )
        ec2_CLIENT.authorize_security_group_egress(
            GroupId=security_group_id,
            IpPermissions=[
                {
                    'FromPort': 80,
                    'ToPort': 80,
                    'IpProtocol': 'TCP',
                    'IpRanges': [
                        {
                            'CidrIp': '0.0.0.0/0',
                            'Description': "Allows outbound http traffic"
                        },
                    ]
                },
                {
                    'FromPort': 22,
                    'ToPort': 22,
                    'IpProtocol': 'TCP',
                    'IpRanges': [
                        {
                            'CidrIp': '0.0.0.0/0',
                            'Description': "Allows outbound SSH traffic"
                        },
                    ]
                },
                {
                    'FromPort': 433,
                    'ToPort': 433,
                    'IpProtocol': 'TCP',
                    'IpRanges': [
                        {
                            'CidrIp': '0.0.0.0/0',
                            'Description': "Allows outbound https traffic"
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


def standaloneSQL(security_group_id):
    instance = ec2_RESOURCE.create_instances(
        ImageId=AMI_ID,
        InstanceType=INSTANCE_TYPE,
        KeyName=KEY_PAIR_NAME,
        MinCount=1,
        MaxCount=1,
        TagSpecifications=[
            {
                'ResourceType': 'instance',
                'Tags': [
                    {
                        'Key': 'Name',
                        'Value':  'standaloneSQL'
                    },
                ]
            },
        ],
        SecurityGroupIds=[security_group_id],
        Placement={
            'AvailabilityZone': AWS_REGION}
    )
    # instance[0].wait_until_running()
    # instance[0].load()
    return instance


def SQLCluster(security_group_id):
    instances = []
    for i in range(0, 4):
        instance = ec2_RESOURCE.create_instances(
            ImageId=AMI_ID,
            InstanceType=INSTANCE_TYPE,
            KeyName=KEY_PAIR_NAME,
            MinCount=1,
            MaxCount=1,
            UserData=USER_DATA,
            TagSpecifications=[
                {
                    'ResourceType': 'instance',
                    'Tags': [
                        {
                            'Key': 'Name',
                            'Value':  'SQLCluster'+str(i)
                        },
                    ]
                },
            ],
            SecurityGroupIds=[security_group_id],
            Placement={
                'AvailabilityZone': AWS_REGION}
        )
        # instance[0].wait_until_running()
        # instance[0].load()
        instances.append(instance)
    return instances


def main():
    security_id = create_security_group()
    standalone = standaloneSQL(security_id)
    cluster = SQLCluster(security_id)
    time.sleep(30)
    standalone[0].wait_until_running()
    standalone[0].load()
    for i in cluster:
        i[0].wait_until_running()
        i[0].load()
    print('done')


main()
