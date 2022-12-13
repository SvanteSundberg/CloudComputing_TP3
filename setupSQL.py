import boto3
from botocore.exceptions import ClientError
import time

AWS_REGION = "us-east-1a"
KEY_PAIR_NAME = 'vockey'
AMI_ID = 'ami-061dbd1209944525c'  # Ubuntu 18.04 LTS
INSTANCE_TYPE = 't2.micro'

# Create a Boto3 resource that is used for creating instances and security groups
ec2_RESOURCE = boto3.resource('ec2', region_name='us-east-1')

# Creates a Boto3 client used that is used for getting the VpcId
ec2_CLIENT = boto3.client('ec2')

# Gets the VpcId from the Boto3 client
response = ec2_CLIENT.describe_vpcs()
vpc_id = response.get('Vpcs', [{}])[0].get('VpcId', '')


def create_security_group():
    '''
    Creates a security group in the existing vpc that allows all traffic on all ports with the name 'security_group'

            Parameters:
                    None

            Returns:
                    security_group_id (str): String with the ID of the created security group.
    '''
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
    '''
    Returns an Ubuntu 18.04 LTS EC2 t2.micro instance with key-pair 'vockey' in availability zone 'us-east-1a'

            Parameters:
                    name (str): A string representing the name of the instance
                    sg_ig (str): Another string representing the security group ID

            Returns:
                    security_group_id (str): String with the ID of the created security group.
    '''
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
    '''
    Creates an security group and 5 different instances by calling 'create_security_group()' and 'createSQLinstance()'.
    Prints out the private IP addresses of each instance.

            Parameters: None

            Returns: None
    '''
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

    print(main.__doc__)


# Runs the main() method
main()
