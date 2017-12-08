# -*- coding:utf-8 -*-
import sys
import json
import os
import pyodbc

sys.path.append('../../')
from Util.SQL_Connect import SQL_Connect
from Util.DateTimeParser.DateTimeParser import Datetimeparser


class transfer_main():
    def __init__(self):
        self.db = SQL_Connect.SQL_Connect()
        self.db.connect_mysql(os.path.join(os.path.dirname(__file__), "config.ini"))
        self.cnxn = pyodbc.connect(
            "DRIVER={SQL Server};SERVER=server;DATABASE=database;UID=acc;PWD=pass")
        self.sql_cursor = self.cnxn.cursor()
        self.time = Datetimeparser('now', '')
        self.batch_insert_comment_sql = 'INSERT INTO {} (comment_id, item_id, type, url, author, comment, time, useful, rate, crawltime, updatetime)' \
                                        ' VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)' \
                                        'ON DUPLICATE KEY UPDATE author = values(author), comment = values(comment), time = values(time), crawltime = values(crawltime), updatetime = values(updatetime) '
        # self.insert_comment_sql = 'INSERT INTO {} (comment_id, item_id) VALUES (%(comment_id)s, %(item_id)s)'
        self.batch_data = {}
        self.comment_python = {}
        # range(a,b,query_count_num)
        self.query_count_num = 1000
        self.init_setting()

    def init_setting(self):
        """
            init setting.
        :return:
        """
        # default set batch_data dict name.
        for i in range(6):
            for j in range(10):
                table_name = 'comments_' + str(i) + '_' + str(j)
                self.batch_data[table_name] = []

        # comment_python sql db use data.
        self.comment_python['query_time'] = self.time.get_timestamp_from_format('%Y-%m-%d')
        if self.db.select_sql(
                "select * from comments_python where query_time = '{}'".format(self.comment_python['query_time'])) == ('0',):
            self.sql_cursor.execute("SELECT count(*) FROM TaobaoProductRateInfo;")
            self.comment_python['comment_handle_cnt'] = 0
            self.comment_python['comment_total_cnt'] = self.sql_cursor.fetchall()[0][0]
            self.comment_python['last_update_time'] = self.time.time_to_str(self.time.now())
            self.db.insert_sql(
                'insert into comments_python (comment_handle_cnt, comment_total_cnt, query_time, last_update_time, run_tag)'
                'values(0, ' + str(self.comment_python['comment_total_cnt']) + ', "' + str(
                    self.comment_python['query_time']) + '", "' + str(
                    self.comment_python['last_update_time']) + '", -1)')
            self.comment_python['run_tag'] = -1

        else:
            data = self.db.select_sql("select comment_handle_cnt, comment_total_cnt, run_tag from comments_python where query_time = '{}'".format(self.comment_python['query_time']))
            self.comment_python['comment_handle_cnt'] = data[0]
            self.comment_python['comment_total_cnt'] = data[1]
            self.comment_python['run_tag'] = data[2]

    def main(self):
        if self.comment_python['run_tag'] == -1:
            handle_cnt = self.comment_python['comment_handle_cnt']
            for low in range(self.comment_python['comment_handle_cnt'], self.comment_python['comment_total_cnt'], self.query_count_num):
                data = {}
                if low == 0:
                    select_data = self.get_sql_server_data(low, low + self.query_count_num)
                else:
                    select_data = self.get_sql_server_data(low + 1, low + self.query_count_num)

                cnt = 0
                for row in select_data:
                    cnt += 1
                    # print cnt, ' , ',
                    data['comment_id'] = row[0]  # RateId 7
                    data['item_id'] = row[1]  # ItemId 22
                    data['type'] = row[2]  # RateType 24
                    data['url'] = row[3]  # Url 5
                    data['author'] = row[4]  # NickName 4
                    data['comment'] = row[5]  # RateContent 9
                    data['time'] = row[6]  # RateTime 10
                    data['useful'] = row[7]  # UsefulCount 12
                    data['rate'] = row[8]  # Score 11
                    data['crawltime'] = str(row[9])[:-7]  # CrawlTime 21
                    data['updatetime'] = self.time.time_to_str(self.time.now())

                    # self.insert_comment_db(data)
                    tuple_data, table_name = self.dic_to_tuple(data)
                    self.batch_data_handle(tuple_data, table_name)

                print '------------------------'
                for i in range(6):
                    for j in range(10):
                        table_name = 'comments_' + str(i) + '_' + str(j)
                        if len(self.batch_data[table_name]) > 0:
                            self.batch_insert_comment_db(self.batch_data[table_name], table_name)
                            self.batch_data[table_name] = []
                handle_cnt += cnt
                print handle_cnt
                self.db.insert_sql('update comments_python set comment_handle_cnt = ' + str(handle_cnt) + ';')
            self.db.insert_sql('update comments_python set run_tag = 1;')

    def get_sql_server_data(self, num_low, num_high):
        """
            connect to sql server(ms sql).
        :param num_low: 'between a and b' of a.
        :param num_high: 'between a and b' of b.
        :return: select all data
        """
        """
        :return: select all data
        """

        # self.sql_cursor.execute("select * from TaobaoProductRateInfo;")
        self.sql_cursor.execute(
            'SELECT RateId, ItemId, RateType, Url, NickName, RateContent, RateTime, UsefulCount, Score, CrawlTime FROM'
            ' TaobaoProductRateInfo where TaobaoProductRateInfoId between ' + str(num_low) + ' and ' + str(
                num_high) + ';')
        # row = self.sql_cursor.fetchone()
        all_data = self.sql_cursor.fetchall()
        return all_data

    def batch_data_handle(self, tuple_data, table_name):
        """
            handle
        :param tuple_data:
        :param table_name:
        :return:
        """
        # print table_name
        self.batch_data[table_name].append(tuple_data)
        if len(self.batch_data[table_name]) >= 100:
            self.batch_insert_comment_db(self.batch_data[table_name], table_name)
            self.batch_data[table_name] = []
            # print self.batch_data

    def batch_insert_comment_db(self, tuple_data, table_name):
        """
            batch insert into taobaoTamll sql database.
        :param sql_list: batch insert data.
        :param table_name: table name.
        :return:
        """
        print table_name, ' : batch insert : ', len(tuple_data)
        sql = self.batch_insert_comment_sql.format(table_name)
        self.db.batch_insert_sql(sql, tuple_data)

    def dic_to_tuple(self, data):
        """
            dic data to tuple.
            use for batch insert.
        :param data:
        :return: tuple_data, table_name
        """
        table_name = 'comments_' + str(data['type']) + '_' + str(data['item_id'])[-1:]
        tuple_data = []
        tuple_data.append(data['comment_id'])
        tuple_data.append(data['item_id'])
        tuple_data.append(data['type'])
        tuple_data.append(data['url'])
        tuple_data.append(data['author'])
        tuple_data.append(data['comment'])
        tuple_data.append(data['time'])
        tuple_data.append(data['useful'])
        tuple_data.append(data['rate'])
        tuple_data.append(data['crawltime'])
        tuple_data.append(data['updatetime'])
        return tuple_data, table_name


if __name__ == '__main__':
    a = transfer_main()
    a.main()
