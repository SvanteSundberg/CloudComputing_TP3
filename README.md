# CloudComputing_TP3

## Benchmarking MySQL standalone vs MySQL cluster on AWS

Use this repository to compare MySQL as standalone vs. cluster.
This project uses sakila-db as a database and Sysbench as benchmarking tool.

**Prerequisites**: Python, Boto3, AWS Cli

### First steps

1. Copy your AWS credentials into **creds.txt**
2. Download **labsuser.pem** file and put it in the working directory
3. Execute **./script.sh** to launch all the necessary instances
4. Note down the private IP adresses that is printed by the script

### MySQL Standalone

Instructions for setting up a MySQL standalone server and benchmark it can be found in **standaloneSetup.txt**.

### MySQL cluster

Instructions for setting up a MySQL cluster and benchmark it can be found in **clusterSetup.txt**.

### Removing instances

The **remove_all.py** script can be executed to remove the instances, Vpc and security group created when running ./script.sh
