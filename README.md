## wildberries.ru parser

The script is designed to parse various sections of the www.wildberries.ru marketplace. It knows how to clean its bases, but theoretically it is needed to accumulate information about how the sales and goods prices in different sections was changing over time.

## Requirements

* python 3.6+
* mysql server 5.7+

How to get it on Ubuntu 18.04+:

1. You need MySQL server and Python pip, if you still don't have them:
	```
	@ sudo apt install python3-pip
	@ sudo apt install mysql-server
	```
2. Install Python connector to MySQL:
	```
	@ pip3 install python-mysql-connector
	```

## Checking

1. Check MySQL installation and root password, choose default database:
	```
	@ mysql -u root -p
		mysql> USE sys;
	Ctrl-Z
	```
2. Check database connector in Python:
	```
	@ python3
		>>> import mysql.connector
	```
	If Python shell is silent:
	```
		>>>
	```
	Then you're ready to work with the script. Press Ctrl-Z to exit from shell.

## Usage

First of all you need for real work with this script is a whole bunch of proxy servers or you'll get ban for an hour or so from www.wildberries.ru after showing 100 positions in a short time. Script is designed for work with the premium account on www.hidemyname.org, it will cost $8 for a month. After payment you must send the feedback form on a page https://hidemyname.org/en/feedback/ with request for API access. Once you'll get an e-mail with some keys and options, you're ready.

Next you need to edit **config.ini** file. It has less than ten lines:
```
[mysql]
mysql_user = root
mysql_pass = <mysql root password>
mysql_host = localhost
mysql_base = sys

[params]
expiry_hours = 24
timeout_between_urls = 3
proxy_list_key = <your hidemyname 15-digit key>
```
### Parameters

**expiry_hours** - every line in MySQL database has a timestamp and if you'll run a script more than once a day, too "young" positions will be not updated. 24 hours is good option.

**timeout_between_urls** - delay between requests in seconds. It will be a random time from 0 to this timeout. 

