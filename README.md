# CloudComputing_TP3

# Installing SQLstandalone

1. Use putty to ssh to instance
2. Run 'sudo apt-get update'
3. Run 'sudo apt-get -y install mysql-server'
4. Run 'sudo mysql'
5. Set the root password to 'password' by running ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'password';
6. Exit mysql

# Setting up sakila database

7. run wget http://downloads.mysql.com/docs/sakila-db.tar.gz && tar -xzf sakila-db.tar.gz
8. login as root in mysqgl and run the following queries:
   SOURCE /home/ubuntu/sakila-db/sakila-schema.sql;
   SOURCE /home/ubuntu/sakila-db/sakila-data.sql;
   USE sakila;

# Setting up and running sysbench with a read and write

9.  sudo apt-get install sysbench
10. prepare sakilda-db for testing with:
    sysbench /usr/share/sysbench/oltp_read_write.lua --table-size=1000000 --mysql-db=sakila --mysql-user=root --mysql-password=password prepare
11. Run the benchmarking with:
    sysbench /usr/share/sysbench/oltp_read_write.lua --table-size=1000000 --threads=6 --time=60 --max-requests=0 --mysql-db=sakila --mysql-user=root --mysql-password=password run
