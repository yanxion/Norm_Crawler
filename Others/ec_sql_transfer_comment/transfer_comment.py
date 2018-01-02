# -*- coding:utf-8 -*-
import json
import os
import pyodbc
import sys

sys.path.append('Util/')
from SQL_Connect import SQL_Connect
from Util.DateTimeParser.DateTimeParser import Datetimeparser
from Util.TextUtil.SpecialCharUtil import remove_emoji

class transfer_comment():
    def __init__(self):
        self.db = SQL_Connect.SQL_Connect()
        self.db.connect_mysql(os.path.join(os.path.dirname(__file__), "config.ini"))
        self.cnxn = pyodbc.connect(
            "DRIVER={SQL Server};SERVER=;DATABASE=;UID=;PWD=")
        self.sql_cursor = self.cnxn.cursor()
        self.time = Datetimeparser('now', '')
        self.batch_insert_comment_sql = 'INSERT INTO {} (comment_id, item_id, type, url, author, comment, time, useful, rate, crawltime, updatetime)' \
                                        ' VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)' \
                                        'ON DUPLICATE KEY UPDATE author = values(author), comment = values(comment), time = values(time), crawltime = values(crawltime), updatetime = values(updatetime) '
        # self.insert_comment_sql = 'INSERT INTO {} (comment_id, item_id) VALUES (%(comment_id)s, %(item_id)s)'
        self.batch_data = {}
        self.comment_python = {}
        # range(a,b,query_count_num)
        self.query_count_num = 10000
        self.init_setting()

    def init_setting(self):
        """
            初始化設定
        :return:
        """
        # 設定預設的 dict.
        for i in range(7):
            for j in range(10):
                table_name = 'comments_' + str(i) + '_' + str(j)
                self.batch_data[table_name] = []

        # comment_python db 會用到的資料
        self.comment_python['query_time'] = self.time.get_timestamp_from_format('%Y-%m-%d')
        # 檢查comment_python有無今日的資料，沒有的話建一個新的
        if self.db.select_sql(
                "select * from comments_python where query_time = '{}'".format(self.comment_python['query_time'])) == ('0',):
            # item's min&max id
            self.sql_cursor.execute(u"SELECT min(Id), max(Id) FROM Item where Keyword = '资策会' and Type >= 1 and Type <= 6;")
            select_data = self.sql_cursor.fetchall()
            self.comment_python['item_index'] = select_data[0][0]
            self.comment_python['item_total'] = select_data[0][1]
            # tag's min&max id
            self.sql_cursor.execute("SELECT min(Id), max(Id) FROM ItemTag where Type >=1 and Type <= 6 ;")
            select_data = self.sql_cursor.fetchall()
            self.comment_python['tag_index'] = select_data[0][0]
            self.comment_python['tag_total'] = select_data[0][1]
            # ranksc's min&max id
            self.sql_cursor.execute("SELECT min(Id), max(Id) FROM Item where Type >= 1 and Type <= 6;")  # bug!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            select_data = self.sql_cursor.fetchall()
            self.comment_python['ranksc_index'] = select_data[0][0]
            self.comment_python['ranksc_total'] = select_data[0][1]
            # comment's min&max id
            self.sql_cursor.execute("SELECT min(TaobaoProductRateInfoId), max(TaobaoProductRateInfoId) FROM TaobaoProductRateInfo where RateType >= 1 and RateType <= 6;")
            select_data = self.sql_cursor.fetchall()
            self.comment_python['comment_index'] = select_data[0][0]
            self.comment_python['comment_total'] = select_data[0][1]

            self.db.insert_sql(
                'insert into comments_python (item_index, tag_index, ranksc_index, comment_index, query_time, run_tag, ' \
                'item_total, tag_total, ranksc_total, comment_total)values("%s", "%s", "%s", "%s", "%s", 0, "%s", "%s", "%s", "%s");' % (
                    str(self.comment_python['item_index']), str(self.comment_python['tag_index']),
                    str(self.comment_python['ranksc_index']), str(self.comment_python['comment_index']),
                    str(self.comment_python['query_time']),
                    str(self.comment_python['item_total']), str(self.comment_python['tag_total']),
                    str(self.comment_python['ranksc_total']), str(self.comment_python['comment_total'])))
            self.comment_python['run_tag'] = 0

        # 有的話檢查index值到哪，並繼續運行程式直到資料全抓完
        else:
            data = self.db.select_sql(
                    "select comment_index, comment_total, run_tag from comments_python where query_time = '{}'".format(
                        self.comment_python['query_time']))
            self.comment_python['comment_index'] = data[0]
            self.comment_python['comment_total'] = data[1]
            self.comment_python['run_tag'] = data[2]

        # if self.db.select_sql(
        #         "select * from comments_python where query_time = '{}'".format(self.comment_python['query_time'])) == (
        # '0',):
        #     self.sql_cursor.execute("SELECT max(TaobaoProductRateInfoId) FROM TaobaoProductRateInfo;")
        #     self.comment_python['comment_index'] = 0
        #     self.comment_python['comment_total'] = self.sql_cursor.fetchall()[0][0]
        #     self.db.insert_sql(
        #         'insert into comments_python (comment_index, comment_total, query_time, run_tag)'
        #         'values(0, ' + str(self.comment_python['comment_total']) + ', "' + str(
        #             self.comment_python['query_time']) + '", 0)')
        #     self.comment_python['run_tag'] = 0
        # # 有的話檢查index值到哪，並繼續運行程式直到資料全抓完
        # else:
        #     data = self.db.select_sql(
        #         "select comment_index, comment_total, run_tag from comments_python where query_time = '{}'".format(
        #             self.comment_python['query_time']))
        #     self.comment_python['comment_index'] = data[0]
        #     self.comment_python['comment_total'] = data[1]
        #     self.comment_python['run_tag'] = data[2]

    def main(self):
        # 檢查 run_tag 是否為 0
        if self.comment_python['run_tag'] == 0:
            # 抓 index 值
            handle_cnt = self.comment_python['comment_index']
            # 每次從資料庫抓 query_count_num 的筆數
            for low in range(self.comment_python['comment_index'], self.comment_python['comment_total'],
                             self.query_count_num):
                data = {}
                # low = 0 的話，從 0 ~ 0 + 10000， low != 0 的話，比如為 10001，那就從10000 + 1 ~ 10000 + 10000
                if low == 1:
                    select_data = self.get_comment_data(low, low + self.query_count_num - 1)
                else:
                    select_data = self.get_comment_data(low + 1, low + self.query_count_num)

                cnt = 0
                # 將筆數裡所有的 row 一一取出
                for row in select_data:
                    cnt += 1
                    # print cnt, ' , ',
                    data['comment_id'] = row[0]  # RateId
                    data['item_id'] = row[1]  # ItemId
                    data['type'] = row[2]  # RateType
                    data['url'] = row[3]  # Url
                    data['author'] = row[4]  # NickName
                    data['comment'] = remove_emoji(row[5])  # RateContent
                    data['time'] = row[6]  # RateTime
                    data['useful'] = row[7]  # UsefulCount
                    data['rate'] = row[8]  # Score
                    data['crawltime'] = str(row[9])[:-7]  # CrawlTime
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
                self.db.insert_sql(
                    'update comments_python set comment_index = "%s" where query_time = "%s";' % (str(handle_cnt), self.comment_python['query_time']))
            self.db.insert_sql('update comments_python set run_tag = 1, comment_index = -1 where query_time = "%s";' % (self.comment_python['query_time']))

    def get_comment_data(self, num_low, num_high):
        """
            連線到sql server(ms sql).
        :param num_low: 要從筆數 A 抓到筆數 B 的 A.
        :param num_high: 要從筆數 A 抓到筆數 B 的 B.
        :return: A 筆數到 B 筆數的所有資料
        """

        # self.sql_cursor.execute("select * from TaobaoProductRateInfo;")
        self.sql_cursor.execute(
            'SELECT RateId, ItemId, RateType, Url, NickName, RateContent, RateTime, UsefulCount, Score, CrawlTime FROM'
            ' TaobaoProductRateInfo where RateType >=1 and RateType <= 6 and TaobaoProductRateInfoId between ' +
            str(num_low) + ' and ' + str(num_high) + ';')
        # row = self.sql_cursor.fetchone()
        all_data = self.sql_cursor.fetchall()
        return all_data

    def batch_data_handle(self, tuple_data, table_name):
        """
            batch處理，若筆數大於 500 筆做一次 batch insert
        :param tuple_data:
        :param table_name:
        :return:
        """
        self.batch_data[table_name].append(tuple_data)
        if len(self.batch_data[table_name]) >= 500:
            self.batch_insert_comment_db(self.batch_data[table_name], table_name)
            self.batch_data[table_name] = []
            # print self.batch_data

    def batch_insert_comment_db(self, tuple_data, table_name):
        """
            batch insert 進 taobaoTmall 資料庫的 def.
        :param sql_list: batch insert data.
        :param table_name: table name.
        :return:
        """
        # print json.dumps(tuple_data)
        print table_name, ' : batch insert : ', len(tuple_data)
        sql = self.batch_insert_comment_sql.format(table_name)
        self.db.batch_insert_sql(sql, tuple_data)

    def dic_to_tuple(self, data):
        """
            將 dic 轉換為tuple，提供 batch insert 用
        :param data:
        :return: tuple_data : 這筆 dic 的 tuple 資料, table_name : 這筆 dic 資料應該匯入的 comments db，與 type、item_id 組合
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
    a = transfer_comment()
    a.main()
