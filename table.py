import mysql.connector


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

    def table_execute(self, query):
        self.cursor.execute(query)
        self.cnx.commit()

    def end_table_connect(self):
        self.cnx.commit()
        self.cursor.close()
        self.cnx.close()

    def table_drop(self, table):
        truncate = f"TRUNCATE TABLE {table};"
        self.table_execute(truncate)

    def table_make(self, table):
        create = f"CREATE TABLE {table} (id INT NOT NULL AUTO_INCREMENT, article INT, name VARCHAR(128)," \
                 f" image VARCHAR(256), url VARCHAR(256), price INT,  price_sale INT, rating INT, review INT," \
                 f" sold INT, timestamp INT, PRIMARY KEY(id));"
        self.table_execute(create)

    def table_push(self, table, article):
        push = f"INSERT into {table} (article) VALUES ({str(article)});"
        self.table_execute(push)

    def table_append(self, table, array):
        """
        Form insert string for sql query
        :param array: list from get_bag_page with query info
        :return:
        """
        insert = f"INSERT into {table} (article, name, image, url, price," \
                 f" price_sale, rating, review, sold, timestamp) VALUES ("
        for i in array:
            insert += f'\'{str(i)}\', '
        insert = insert[:-2] + ");"
        self.table_execute(insert)

    def table_select_by_article(self, table, article):
        select_article = f"SELECT article, timestamp from {table} WHERE article = {str(article)};"
        print(select_article)
        self.cursor.execute(select_article)
        article_list = self.cursor.fetchall()
        tm_list = [index[1] for index in article_list]
        bags_list = []
        for index in sorted(tm_list, reverse=True):
            select = f"SELECT article, name, image, rating, review, sold " \
                     f"from {table} WHERE timestamp = {str(index)};"
            print(select)
            self.cursor.execute(select)
            bags_list.append(self.cursor.fetchone())
        for index in bags_list:
            print(index)
        self.cnx.commit()
