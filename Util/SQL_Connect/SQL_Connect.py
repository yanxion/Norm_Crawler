import ConfigParser
import MySQLdb
import os


class SQL_Connect():
    def __init__(self):
        self.sql_data = None
        self.db = None
        self.cursor = None
        self.batch_sql_str = ''
        self.batch_sql_val = ''

    def get_connect_ini(self, path):
        config = ConfigParser.ConfigParser()
        config.read(os.path.join(path, "config.ini"))
        self.sql_data = {
            'Host': config.get('SQL_Connect', 'Host'),
            'Account': config.get('SQL_Connect', 'Account'),
            'Password': config.get('SQL_Connect', 'Password'),
            'Database': config.get('SQL_Connect', 'Database')
        }
        return self.sql_data

    def connect_mysql(self, path):
        self.get_connect_ini(path)

        self.db = MySQLdb.connect(host=self.sql_data['Host'], user=self.sql_data['Account'],
                                  passwd=self.sql_data['Password'], db=self.sql_data['Database']
                                  , charset="utf8")
        self.cursor = self.db.cursor()

    def insert_sql(self, sql_str):
        self.cursor.execute(sql_str)
        self.db.commit()

    def batch_insert_sql(self, sql_str, sql_val):
        self.cursor.executemany(sql_str, sql_val)
        self.db.commit()

    def select_sql(self, sql_str):
        self.cursor.execute(sql_str)

        result = self.cursor.fetchone()
        if result:
            return result
        else:
            return tuple('0')

    def db_close(self):
        self.db.close()


if __name__ == '__main__':
    a = SQL_Connect()
    a.connect_mysql()
    list = []
    for i in range(1, 5, +1):
        list.append((i, i*2))

    list1 = []
    list2 = []
    for i in range(1, 3, +1):
        list1 = []
        for j in range(1, 5, +1):
            list1.append((i, j))
        list2.append((list1))


    print list
    print (list1)
    print tuple(list2)

    a.batch_insert_sql("insert into post (key_url,key_url_sha) values (%s, %s)", list)

    a.db_close()