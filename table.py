import mysql.connector
import bag
import time


class Table:

    def __init__(self, name, creds: tuple):
        self.name = name
        self.cnx, self.cursor = self.get_table_connect(creds)

    def get_connector(self):
        return self.cnx, self.cursor

    @staticmethod
    def get_table_connect(creds: tuple):
        cnx = mysql.connector.connect(user=creds[0], password=creds[1], host=creds[2], database=creds[3])
        cursor = cnx.cursor(buffered=True)
        return cnx, cursor

    def table_check(self):
        try:
            execute = f"SELECT * FROM {self.name};"
            self.table_execute(execute)
            return True
        except mysql.connector.errors.ProgrammingError:
            return False

    def table_execute(self, query):
        self.cursor.execute(query)
        self.cnx.commit()

    def end_table_connect(self):
        self.cnx.commit()
        self.cursor.close()
        self.cnx.close()

    def proxy_make(self):
        create = f"CREATE TABLE proxy_list (id INT NOT NULL AUTO_INCREMENT," \
                 f" protocol VARCHAR(32), address VARCHAR(64), PRIMARY KEY (id));"
        self.table_execute(create)

    def proxy_append(self, proto, addr):
        insert = f"INSERT INTO proxy_list (protocol, address) VALUES ('{proto}', '{addr}');"
        self.table_execute(insert)

    def table_read(self, number):
        read = f"SELECT * FROM {self.name} WHERE id = {number};"
        self.cursor.execute(read)
        return self.cursor.fetchone()

    def table_len(self):
        length = f"SELECT COUNT(*) FROM {self.name}"
        self.cursor.execute(length)
        return self.cursor.fetchone()

    def table_truncate(self):
        truncate = f"TRUNCATE TABLE {self.name};"
        self.table_execute(truncate)

    def table_make(self):
        create = f"CREATE TABLE {self.name} (id INT NOT NULL AUTO_INCREMENT, article INT, name VARCHAR(128)," \
            f" image VARCHAR(256), url VARCHAR(256), material VARCHAR(128), price INT,  price_sale INT," \
            f" rating INT, review INT, sold INT, timestamp INT, PRIMARY KEY(id));"
        self.table_execute(create)

    def table_append(self, bag: bag):
        insert = f"INSERT into {self.name} (article, name, image, url, material, price, price_sale, rating, review, " \
            f"sold, timestamp) VALUES ('{bag.article}', '{bag.name}', '{bag.image}', '{bag.url}', '{bag.material}', " \
            f"'{bag.price}', '{bag.price_sale}', '{bag.rating}', '{bag.reviews}', '{bag.sold}', '{int(time.time())}');"
        self.table_execute(insert)

    def table_check_presence(self, article):
        select_article = f"SELECT timestamp FROM {self.name} WHERE article = {article};"
        self.cursor.execute(select_article)
        article_list = self.cursor.fetchall()
        time_now = int(time.time())
        for stamp in article_list:
            if time_now - stamp[0] < 86400:
                return True
        return False

    def table_check_material(self):
        select = f"SELECT id, article FROM {self.name} where material = '---';"
        self.cursor.execute(select)
        empty_list = self.cursor.fetchall()
        return empty_list

    def table_update_material(self, id, math):
        update = f"UPDATE {self.name} SET material = '{math}' WHERE (id = {id});"
        self.cursor.execute(update)

