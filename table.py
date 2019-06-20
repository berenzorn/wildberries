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
        except mysql.connector.errors.ProgrammingError:
            self.table_make()

    def table_execute(self, query):
        self.cursor.execute(query)
        self.cnx.commit()

    def end_table_connect(self):
        self.cnx.commit()
        self.cursor.close()
        self.cnx.close()

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

