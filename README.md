# wildberries.ru parser

The script is designed to parse various sections of the www.wildberries.ru marketplace. It knows how to clean its tables, but theoretically it is needed to accumulate information about how the sales and goods prices in different sections was changing over time.

## Requirements

* python 3.6+
* mysql server 5.7+

How to get it on Ubuntu 18.04+:

1. You need MySQL server and Python pip, if you still don't have them:
	```
	@ sudo apt install python3-pip
	@ sudo apt install mysql-server
	```
2. Install requests module and Python connector to MySQL:
	```
	@ pip3 install requests
	@ pip3 install python-mysql-connector
	```
3. Check MySQL installation and root password, choose default database:
	```
	@ mysql -u root -p
		mysql> USE sys;
	Ctrl-Z
	```

How to get it on Windows:

1. You need MySQL 5.7.xx community server, if you still don't have it:
https://dev.mysql.com/get/Downloads/MySQLInstaller/mysql-installer-community-5.7.28.0.msi

When you'll see "Choosing a setup type", click "Custom" type and click Next.
On the next screen all you need are MySQL Server, MySQL Workbench, MySQL Notifier and Connector/Python.

2. Run MySQL Workbench and choose SYS as the default database.

3. Install requests module and Python connector to MySQL:
	```
	@ pip install requests
	@ pip install mysql.connector
	```

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

**expiry_hours** - each record in MySQL table has a timestamp and if you'll run a script more than once a day for example, too "young" positions will not be updated. 24 hours is good option, you can choose even 1 hour as well as 168 hours (1 week).

**timeout_between_urls** - delay between requests in seconds. It will be a random time from 0 to this timeout. Don't choose too low delay, 3 seconds is ok.

### Command line interface
Usage: crawler.py [-h] [-c] [-d] [-u] [-s] [-n] [-m] database source

Required arguments:
- database = Table name
- source = Page URL from where you start to crawl. URL must be in quotation marks.

Optional arguments:
- -c = Cleans the table before starting. If you want to start some table from scratch.
- -d = Debug mode.
- -u = Updates http proxies table.
- -s = Uses https proxies too. Overrides -u argument.
- -n = Don't uses proxies. It may need for debug mode or if you want to parse less than 100 positions.
- -m = Fills empty material cells. Sometimes positions parse without "material" cell, in this case there will be just "---". In the end of the whole parsing I check and refill such cells, but I left an argument too, just in case, if you want to try to refill them again. It will work only if **expiry_hours** still not passed.

### So. How to use it.

First time you start this crawler in a day, you must use **-u** or **-s** argument, because the proxies are changing constantly.
Example:
```
python crawler.py -u backpacks "https://www.wildberries.ru/catalog/aksessuary/sumki-i-ryukzaki/ryukzaki/ryukzaki"
```
When you see that some section has more than 20000 positions, you must specify your request or many positions in the middle will stay unnoticed. You can split it into two queries or more.
Example:
```
python crawler.py backpacks https://www.wildberries.ru/catalog/aksessuary/sumki-i-ryukzaki/ryukzaki/ryukzaki?price=200;2000
python crawler.py backpacks https://www.wildberries.ru/catalog/aksessuary/sumki-i-ryukzaki/ryukzaki/ryukzaki?price=2000;20000
```
Here I splitted backpack section to *"cheaper than 2000rub"* and *"from 2000rub to 20000rub"*.
You can split and specify these sections using three or even more categories.
Example:
```
python crawler.py backpacks https://www.wildberries.ru/catalog/aksessuary/sumki-i-ryukzaki/ryukzaki/ryukzaki?price=3000;10000&color=0&kind=1&consists=6
```
if you need only *black* *polyester* backpacks *for men* with *the price from 3000rub to 10000rub*.
And so on.

## Contacts

Telegram: @berenzorn

Email: berenzorn@mail.ru

Feel free to contact me if you have a questions. Have a nice day :)
