# -*- coding:utf-8 -*-
import hashlib
import json
import os
import pyodbc
import sys
import urllib

import time

sys.path.append('Util/')
from SQL_Connect import SQL_Connect
from Util.DateTimeParser.DateTimeParser import Datetimeparser
from Util.TextUtil.SpecialCharUtil import remove_emoji


class transfer_main():
    def __init__(self):
        self.db = SQL_Connect.SQL_Connect()
        self.db.connect_mysql(os.path.join(os.path.dirname(__file__), "config.ini"))
        self.cnxn = pyodbc.connect(
            "DRIVER={SQL Server};SERVER=;DATABASE=;UID=;PWD=")
        self.sql_cursor = self.cnxn.cursor()
        self.time = Datetimeparser('now', '')
        self.item_batch_insert_sql = 'INSERT INTO {} (id, userID, cat, ppath, item_id, TYPE, origin_url, origin_url_md5, url, category, keyword, title, image, content, seller_id, seller, shopname, seller_location, price, origin_price, unitPrice, tradeNum, comments, rate, ratesum, shanghai_express, collection, place, province, brand, crawltime, updatetime, SHA) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE id= values(id), userID= values(userID), cat= values(cat), ppath= values(ppath), item_id= values(item_id), TYPE= values(TYPE), origin_url= values(origin_url), origin_url_md5= values(origin_url_md5), url= values(url), category= values(category), keyword= values(keyword), title= values(title), image= values(image), content= values(content), seller_id= values(seller_id), seller= values(seller), shopname= values(shopname), seller_location= values(seller_location), price= values(price), origin_price= values(origin_price), unitPrice= values(unitPrice), tradeNum= values(tradeNum), comments= values(comments), rate= values(rate), ratesum= values(ratesum), shanghai_express= values(shanghai_express), collection= values(collection), place= values(place), province= values(province), brand= values(brand), crawltime= values(crawltime), updatetime= values(updatetime)'
        self.tag_batch_insert_sql = 'INSERT INTO {} (id, item_id, type, tag, posi, count, crawltime, updatetime, attribute) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE item_id= values(item_id), type= values(type), tag= values(tag), posi= values(posi), count= values(count), crawltime= values(crawltime), updatetime= values(updatetime), attribute=values(attribute)'
        self.rank_batch_insert_sql = 'INSERT INTO {} (id, ori_url, url, rank_name, cat1, cat2, cat3, no_num, keyword, attention, sc_percent, sc_num, sell_num, sell_price, location, seller_name, sha1) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE ori_url= values(ori_url), url= values(url), rank_name= values(rank_name), cat1= values(cat1), cat2= values(cat2), cat3= values(cat3), no_num= values(no_num), keyword= values(keyword), attention= values(attention), sc_percent= values(sc_percent), sc_num= values(sc_num), sell_num= values(sell_num), sell_price= values(sell_price), location= values(location), seller_name= values(seller_name), sha1= values(sha1)'
        self.batch_data = {}
        self.comment_python = {}
        # range(a,b,query_count_num)
        self.query_count_num = 1000
        self.crawldate = ''
        # 檢查以前querytime資料是否有需補齊
        self.expired_data_fill()

        # 寫進今天應該抓取的資料
        self.init_setting()

    def init_setting(self, query_datetime=''):
        """
            初始化設定
        :return:
        """
        # comment_python sql db use data.
        if query_datetime == '':
            query_datetime = self.time.get_yesterday(time_format='%Y-%m-%d')
        self.comment_python['query_time'] = query_datetime
        self.crawldate = self.comment_python['query_time'].replace('-', '')
        # 檢查comment_python有無今日的資料，沒有的話建一個新的
        if self.db.select_sql("select * from url_list_python where query_time = '{}'".format(self.comment_python['query_time'])) == ('0',):
            self.db.insert_sql(
                'insert into url_list_python (item_index, tag_index, ranksc_index, comment_index, query_time, run_tag, '
                'item_total, tag_total, ranksc_total, comment_total)values(0, 0, 0, 0, "%s", 0, 0, 0, 0, 0);' %
                (self.comment_python['query_time']))
        index_data = self.db.select_sql(
                "select item_index, tag_index, ranksc_index from url_list_python where query_time = '{}'".format(self.comment_python['query_time']))
        # 如果item_index是0的話，抓取sql server 上最大跟最小值
        if index_data[0] == 0:
            # item's min&max id
            self.sql_cursor.execute('SELECT min(Id), max(Id) FROM Item where Type >=1 and Type <= 6 and '
                                    'CONVERT(VARCHAR(25), CrawlTime, 126) LIKE \'' + self.comment_python['query_time'] + '%\';')
            select_data = self.sql_cursor.fetchall()
            if select_data[0][0]:
                self.comment_python['item_index'] = select_data[0][0]
                self.comment_python['item_total'] = select_data[0][1]
            else:
                self.comment_python['item_index'] = 0
                self.comment_python['item_total'] = 0
            self.db.insert_sql('UPDATE url_list_python SET item_index = %s, item_total = %s WHERE query_time = "%s"' %
                               (self.comment_python['item_index'], self.comment_python['item_total'], self.comment_python['query_time']))
            self.comment_python['run_tag'] = 0
        else:
            # 檢查index值到哪，並繼續運行程式直到資料全抓完
            data = self.db.select_sql(
                "select item_index, item_total, run_tag from url_list_python where query_time = '{}'".format(
                    self.comment_python['query_time']))
            self.comment_python['item_index'] = data[0]
            self.comment_python['item_total'] = data[1]

        # 如果tag_index是0的話，抓取sql server 上最大跟最小值
        if index_data[1] == 0:
            # tag's min&max id
            self.sql_cursor.execute('SELECT min(Id), max(Id) FROM ItemTag where Type >=1 and Type <= 6 and '
                                    'CONVERT(VARCHAR(25), CrawlTime, 126) LIKE \'' + self.comment_python['query_time'] + '%\';')
            select_data = self.sql_cursor.fetchall()
            if select_data[0][0]:
                self.comment_python['tag_index'] = select_data[0][0]
                self.comment_python['tag_total'] = select_data[0][1]
            else:
                self.comment_python['tag_index'] = 0
                self.comment_python['tag_total'] = 0
            self.db.insert_sql('UPDATE url_list_python SET tag_index = %s, tag_total = %s WHERE query_time = "%s"' %
                               (self.comment_python['tag_index'], self.comment_python['tag_total'], self.comment_python['query_time']))
            self.comment_python['run_tag'] = 0
        else:
            # 檢查index值到哪，並繼續運行程式直到資料全抓完
            data = self.db.select_sql(
                "select tag_index, tag_total, run_tag from url_list_python where query_time = '{}'".format(
                    self.comment_python['query_time']))
            self.comment_python['tag_index'] = data[0]
            self.comment_python['tag_total'] = data[1]

        # 如果ranksc_index是0的話，抓取sql server 上最大跟最小值
        if index_data[2] == 0:
            # ranksc's min&max id
            self.sql_cursor.execute('SELECT min(Id), max(Id) FROM RankSc where CONVERT(VARCHAR(25), CrawlTime, 126)'
                                    ' LIKE \'' + self.comment_python['query_time'] + '%\';')
            select_data = self.sql_cursor.fetchall()
            if select_data[0][0]:
                self.comment_python['ranksc_index'] = select_data[0][0]
                self.comment_python['ranksc_total'] = select_data[0][1]
            else:
                self.comment_python['ranksc_index'] = 0
                self.comment_python['ranksc_total'] = 0
            self.db.insert_sql('UPDATE url_list_python SET ranksc_index = %s, ranksc_total = %s WHERE query_time = "%s"' %
                               (self.comment_python['ranksc_index'], self.comment_python['ranksc_total'], self.comment_python['query_time']))
            self.comment_python['run_tag'] = 0
        else:
            # 檢查index值到哪，並繼續運行程式直到資料全抓完
            data = self.db.select_sql(
                "select ranksc_index, ranksc_total, run_tag from url_list_python where query_time = '{}'".format(
                    self.comment_python['query_time']))
            self.comment_python['ranksc_index'] = data[0]
            self.comment_python['ranksc_total'] = data[1]
            self.comment_python['run_tag'] = data[2]

        self.batch_data['taobao_itemlist_' + str(self.crawldate)] = []
        self.batch_data['taobao_items_tags_' + str(self.crawldate)] = []
        self.batch_data['taobao_rank_sc_' + str(self.crawldate)] = []

        # 複製舊有的 table 套上 crawldate 日期
        try:
            self.db.insert_sql('CREATE TABLE taobao_itemlist_' + str(self.crawldate) + ' LIKE taobao_itemlist;')
            print 'taobao_itemlist_' + str(self.crawldate) + ' table created.'
        except:
            print 'has taobao_itemlist_' + str(self.crawldate) + ' table.'
        try:
            self.db.insert_sql('CREATE TABLE taobao_items_tags_' + str(self.crawldate) + ' LIKE taobao_items_tags;')
            print 'taobao_items_tags_' + str(self.crawldate) + ' table created.'
        except:
            print 'has taobao_items_tags_' + str(self.crawldate) + ' table.'
        try:
            self.db.insert_sql('CREATE TABLE taobao_rank_sc_' + str(self.crawldate) + ' LIKE taobao_rank_sc;')
            print 'taobao_rank_sc_' + str(self.crawldate) + ' table created.'
        except:
            print 'has taobao_rank_sc_' + str(self.crawldate) + ' table.'

    def expired_data_fill(self):
        need_expire = self.db.select_sql_all('select run_tag, query_time from url_list_python where run_tag = 0')
        for i in need_expire:
            self.init_setting(i[1])
            self.main()

    def main(self):
        # 檢查 run_tag 是否為 0
        if self.comment_python['run_tag'] == 0:
            if self.comment_python['item_index'] != -1:
                self.transfer_item()
                self.sql_cursor.execute('select count(*) from Item where Type >= 1 and Type <= 6 and CONVERT(VARCHAR(25), CrawlTime, 126)'
                                    ' LIKE \'' + self.comment_python['query_time'] + '%\';')
                item_total_cnt = self.sql_cursor.fetchall()[0][0]
                self.db.insert_sql('update url_list_python set item_index = -1, item_total = "%s",'
                                   ' last_update_time = "%s" where query_time = "%s";' %
                                   (item_total_cnt, self.time.time_to_str(self.time.now()),
                                    self.comment_python['query_time']))
            if self.comment_python['tag_index'] != -1:
                self.transfer_tag()
                self.sql_cursor.execute('select count(*) from ItemTag where Type >=1 and Type <= 6 and CONVERT(VARCHAR(25), CrawlTime, 126)'
                                    ' LIKE \'' + self.comment_python['query_time'] + '%\';')
                tag_total_cnt = self.sql_cursor.fetchall()[0][0]
                self.db.insert_sql('update url_list_python set tag_index = -1, tag_total = "%s",'
                                   ' last_update_time = "%s" where query_time = "%s";' %
                                   (tag_total_cnt, self.time.time_to_str(self.time.now()),
                                    self.comment_python['query_time']))
            if self.comment_python['ranksc_index'] != -1:
                self.transfer_rank()
                self.sql_cursor.execute('select count(*) from RankSc where CONVERT(VARCHAR(25), CrawlTime, 126)'
                                    ' LIKE \'' + self.comment_python['query_time'] + '%\';')
                rank_total_cnt = self.sql_cursor.fetchall()[0][0]
                self.db.insert_sql('update url_list_python set ranksc_index = -1, ranksc_total = "%s",'
                                   ' last_update_time = "%s" where query_time = "%s";' %
                                   (rank_total_cnt, self.time.time_to_str(self.time.now()),
                                    self.comment_python['query_time']))
            index_msg = self.db.select_sql(
                'SELECT item_index, tag_index, ranksc_index, comment_index FROM url_list_python WHERE query_time = "{}"'.format(
                    self.comment_python['query_time']))
            if index_msg[0] == -1 and index_msg[1] == -1 and index_msg[2] == -1 and index_msg[3] == -1:
                self.db.insert_sql('update url_list_python set run_tag = 1 where query_time = "%s";' %
                                   (self.comment_python['query_time']))

    def transfer_item(self):
        # 抓 index 值
        handle_cnt = self.comment_python['item_index']
        table_name = 'taobao_itemlist_' + self.crawldate
        # 每次從資料庫抓 query_count_num 的筆數
        for low in range(self.comment_python['item_index'], self.comment_python['item_total'], self.query_count_num):
            data = {}
            # get item data 比如low為 10000，那就從10000 + 1 ~ 10000 + 10000
            select_data = self.get_item_data(low, low + self.query_count_num - 1)

            cnt = 0
            # 將筆數裡所有的 row 一一取出
            for row in select_data:
                cnt += 1
                # print cnt, ' , ',
                data['id'] = row[0]  # id
                data['userID'] = row[1]  # UserId
                data['cat'] = row[2]  # categoryId
                data['ppath'] = row[3]  # PPath
                data['item_id'] = row[4]  # itemId
                data['type'] = row[5]  # Tpye
                data['origin_url'] = row[6]  # OriginUrl
                data['origin_url_md5'] = hashlib.md5(data['origin_url'].encode('utf8')).hexdigest()  # OriginUrlMd5
                data['url'] = row[8]  # URL
                data['category'] = row[9]  # Category
                data['keyword'] = row[10]  # Keyword
                data['title'] = (row[11])  # Title
                data['image'] = row[12]  # Image
                data['content'] = (row[13])  # Content
                data['seller_id'] = row[14]  # SellerId
                data['seller'] = row[15]  # Seller
                data['shopname'] = (row[16])  # ShopName
                data['seller_location'] = row[17]  # SellerLocation
                data['price'] = row[18]  # Price
                data['origin_price'] = row[19]  # OriginPrice
                data['unitPrice'] = row[20]  # UnitPrice
                data['tradeNum'] = row[21]  # TradeNum
                # data['dailyTradeNum'] = ''  # Comments
                # data['monthlyTradeDiff'] = ''  # Score
                # data['monthlyTradeDiffRatio'] = ''  # Score
                # data['weeklyTradeRankDiff'] = ''  # Score
                data['comments'] = row[22]  # Comments
                data['rate'] = row[23]  # Rate
                data['ratesum'] = row[24]  # RateSum
                data['shanghai_express'] = row[25]  # ShangHaiExpress
                data['collection'] = row[26]  # Collection
                data['place'] = row[27]  # Place
                data['province'] = row[28]  # Provice
                data['brand'] = (row[29])  # BrandName
                data['crawltime'] = str(row[30])[:-7]  # CrawlTime
                data['updatetime'] = self.time.time_to_str(self.time.now())
                data['sha'] = hashlib.sha1(str(data['item_id']) + str(data['type']) + str(data['origin_url_md5'])).hexdigest()  # Sha

                tuple_data = self.item_dic_to_tuple(data)
                self.batch_data_handle(tuple_data, table_name)

            print '------------------------'
            if len(self.batch_data[table_name]) > 0:
                self.batch_insert_db(self.batch_data[table_name], table_name)
                self.batch_data[table_name] = []
            if cnt == 0:
                cnt = self.query_count_num
            handle_cnt += cnt
            print handle_cnt
            self.db.insert_sql(
                'update url_list_python set item_index = "%s" where query_time = "%s";' % (
                    str(handle_cnt), self.comment_python['query_time']))

    def transfer_tag(self):
        # 抓 index 值
        handle_cnt = self.comment_python['tag_index']
        table_name = 'taobao_items_tags_' + self.crawldate
        # 每次從資料庫抓 query_count_num 的筆數
        for low in range(self.comment_python['tag_index'], self.comment_python['tag_total'], self.query_count_num):
            data = {}
            # get tag data 比如low為 10000，那就從10000 + 1 ~ 10000 + 10000
            select_data = self.get_tag_data(low, low + self.query_count_num - 1)

            cnt = 0
            # 將筆數裡所有的 row 一一取出
            for row in select_data:
                cnt += 1
                # print cnt, ' , ',
                data['id'] = row[0]  # Id
                data['item_id'] = row[1]  # ItemId
                data['type'] = row[2]  # Type
                data['tag'] = remove_emoji(row[3])  # Tags
                if row[4]:
                    data['posi'] = row[4]  # Posi
                else:
                    data['posi'] = -2
                data['count'] = row[5]  # Count
                data['crawltime'] = str(row[6])[:-7]  # CrawlTime
                data['updatetime'] = self.time.time_to_str(self.time.now())
                data['attribute'] = ''  # Attribute

                tuple_data = self.tag_dic_to_tuple(data)
                self.batch_data_handle(tuple_data, table_name)

            print '------------------------'
            if len(self.batch_data[table_name]) > 0:
                self.batch_insert_db(self.batch_data[table_name], table_name)
                self.batch_data[table_name] = []
            if cnt == 0:
                cnt = self.query_count_num
            handle_cnt += cnt
            print handle_cnt
            self.db.insert_sql(
                'update url_list_python set tag_index = "%s" where query_time = "%s";' % (
                    str(handle_cnt), self.comment_python['query_time']))

    def transfer_rank(self):
        # 抓 index 值
        handle_cnt = self.comment_python['ranksc_index']
        table_name = 'taobao_rank_sc_' + self.crawldate
        # 每次從資料庫抓 query_count_num 的筆數
        for low in range(self.comment_python['ranksc_index'], self.comment_python['ranksc_total'], self.query_count_num):
            data = {}
            # get rank data 比如low為 10000，那就從10000 + 1 ~ 10000 + 10000
            select_data = self.get_rank_data(low, low + self.query_count_num - 1)
            cnt = 0
            # 將筆數裡所有的 row 一一取出
            for row in select_data:
                cnt += 1
                # print cnt, ' , ',
                data['id'] = row[0]  # Id
                data['ori_url'] = row[1]  # originurl
                data['url'] = row[2]  # url
                data['rank_name'] = row[3]  # rankname
                data['cat1'] = row[4]  # cat1
                data['cat2'] = row[5]  # cat2
                data['cat3'] = row[6]  # cat3
                data['no_num'] = row[7]  # nounm
                data['keyword'] = row[8]  # keyword
                if row[9]:
                    data['attention'] = row[9]  # attention
                else:
                    data['attention'] = 0
                data['sc_percent'] = row[10].replace('%', '')  # scpercent
                if row[11]:
                    data['sc_num'] = row[11]  # scnum
                else:
                    data['sc_num'] = -1
                if row[12]:
                    data['sell_num'] = row[12]  # sellnum
                else:
                    data['sell_num'] = -1
                if row[13]:
                    data['sell_price'] = row[13]  # sellprice
                else:
                    data['sell_price'] = 0
                if row[14]:
                    data['location'] = row[14]  # location
                else:
                    data['location'] = ''
                if row[15]:
                    data['seller_name'] = row[15]  # sellername
                else:
                    data['seller_name'] = ''
                data['sha1'] = hashlib.sha1(str(data['rank_name'].encode('utf-8')) + str(data['url'].encode('utf-8'))
                                            + str(data['cat3'].encode('utf-8'))).hexdigest()  # Sha

                tuple_data = self.rank_dic_to_tuple(data)
                self.batch_data_handle(tuple_data, table_name)

            print '------------------------'
            if len(self.batch_data[table_name]) > 0:
                self.batch_insert_db(self.batch_data[table_name], table_name)
                self.batch_data[table_name] = []
            if cnt == 0:
                cnt = self.query_count_num
            handle_cnt += cnt
            print handle_cnt
            self.db.insert_sql(
                'update url_list_python set ranksc_index = "%s" where query_time = "%s";' % (
                    str(handle_cnt), self.comment_python['query_time']))

    def get_item_data(self, num_low, num_high):
        """
            連線到sql server(ms sql) item表
        :param num_low: 要從筆數 A 抓到筆數 B 的 A.
        :param num_high: 要從筆數 A 抓到筆數 B 的 B.
        :return: A 筆數到 B 筆數的所有資料
        """

        sql = 'select id, UserId, categoryId, PPath, itemId, Type, OriginUrl, OriginUrlMd5, URL, Category, Keyword,' \
              'Title, Image, Content, SellerId, Seller, ShopName, SellerLocation, Price, OriginPrice, UnitPrice, TradeNum,' \
              'Comments, Rate, RateSum, ShangHaiExpress, Collection, Place, Provice, BrandName, CrawlTime, Sha from item' \
              ' where id between ' + str(num_low) + ' and ' + str(num_high) + \
              ' and Type between 1 and 6 '  \
              ' and CONVERT(VARCHAR(25), CrawlTime, 126) LIKE \'' + self.comment_python['query_time'] + '%\';'
        self.sql_cursor.execute(sql)
        # row = self.sql_cursor.fetchone()
        all_data = self.sql_cursor.fetchall()
        return all_data

    def get_tag_data(self, num_low, num_high):
        """
            連線到sql server(ms sql) tag表
        :param num_low: 要從筆數 A 抓到筆數 B 的 A.
        :param num_high: 要從筆數 A 抓到筆數 B 的 B.
        :return: A 筆數到 B 筆數的所有資料
        """

        sql = 'select Id, ItemId, Type, Tags, Posi, Count, CrawlTime, Attribute from ItemTag' \
              ' where id between ' + str(num_low) + ' and ' + str(num_high) + \
              ' and Type between 1 and 6' \
              ' and CONVERT(VARCHAR(25), CrawlTime, 126) LIKE \'' + self.comment_python['query_time'] + '%\';'
        self.sql_cursor.execute(sql)
        # row = self.sql_cursor.fetchone()
        all_data = self.sql_cursor.fetchall()
        return all_data

    def get_rank_data(self, num_low, num_high):
        """
            連線到sql server(ms sql) item表
        :param num_low: 要從筆數 A 抓到筆數 B 的 A.
        :param num_high: 要從筆數 A 抓到筆數 B 的 B.
        :return: A 筆數到 B 筆數的所有資料
        """

        sql = "select id, originurl, url, rankname, cat1, cat2, cat3, nonum, keyword, attention, scpercent, scnum," \
              " sellnum, sellprice, location, sellername from RankSc" \
              " where id between " + str(num_low) + ' and ' + str(num_high) + \
              ' and CONVERT(VARCHAR(25), CrawlTime, 126) LIKE \'' + self.comment_python['query_time'] + '%\';'
        self.sql_cursor.execute(sql)
        # row = self.sql_cursor.fetchone()
        all_data = self.sql_cursor.fetchall()
        return all_data

    def item_dic_to_tuple(self, data):
        """
            將 dic 轉換為tuple，提供 batch insert 用
        :param data:
        :return: tuple_data : 這筆 dic 的 tuple 資料, table_name : 這筆 dic 資料應該匯入的 comments db，與 type、item_id 組合
        """
        # table_name = 'comments_' + str(data['type']) + '_' + str(data['item_id'])[-1:]

        tuple_data = []
        tuple_data.append(data['id'])
        tuple_data.append(data['userID'])
        tuple_data.append(data['cat'])
        tuple_data.append(data['ppath'])
        tuple_data.append(data['item_id'])
        tuple_data.append(data['type'])
        tuple_data.append(data['origin_url'])
        tuple_data.append(data['origin_url_md5'])
        tuple_data.append(data['url'])
        tuple_data.append(data['category'])
        tuple_data.append(data['keyword'])
        tuple_data.append(data['title'])
        tuple_data.append(data['image'])
        tuple_data.append(data['content'])
        tuple_data.append(data['seller_id'])
        tuple_data.append(data['seller'])
        tuple_data.append(data['shopname'])
        tuple_data.append(data['seller_location'])
        tuple_data.append(data['price'])
        tuple_data.append(data['origin_price'])
        tuple_data.append(data['unitPrice'])
        tuple_data.append(data['tradeNum'])
        # tuple_data.append(data['dailyTradeNum'])
        # tuple_data.append(data['monthlyTradeDiff'])
        # tuple_data.append(data['monthlyTradeDiffRatio'])
        # tuple_data.append(data['weeklyTradeRankDiff'])
        tuple_data.append(data['comments'])
        tuple_data.append(data['rate'])
        tuple_data.append(data['ratesum'])
        tuple_data.append(data['shanghai_express'])
        tuple_data.append(data['collection'])
        tuple_data.append(data['place'])
        tuple_data.append(data['province'])
        tuple_data.append(data['brand'])
        tuple_data.append(data['crawltime'])
        tuple_data.append(data['updatetime'])
        tuple_data.append(data['sha'])
        return tuple_data

    def tag_dic_to_tuple(self, data):
        """
            將 dic 轉換為tuple，提供 batch insert 用
        :param data:
        :return: tuple_data : 這筆 dic 的 tuple 資料, table_name : 這筆 dic 資料應該匯入的 comments db，與 type、item_id 組合
        """
        # table_name = 'comments_' + str(data['type']) + '_' + str(data['item_id'])[-1:]

        tuple_data = []
        tuple_data.append(data['id'])
        tuple_data.append(data['item_id'])
        tuple_data.append(data['type'])
        tuple_data.append(data['tag'])
        tuple_data.append(data['posi'])
        tuple_data.append(data['count'])
        tuple_data.append(data['crawltime'])
        tuple_data.append(data['updatetime'])
        tuple_data.append(data['attribute'])
        return tuple_data

    def rank_dic_to_tuple(self, data):
        """
            將 dic 轉換為tuple，提供 batch insert 用
        :param data:
        :return: tuple_data : 這筆 dic 的 tuple 資料, table_name : 這筆 dic 資料應該匯入的 comments db，與 type、item_id 組合
        """
        # table_name = 'comments_' + str(data['type']) + '_' + str(data['item_id'])[-1:]

        tuple_data = []

        tuple_data.append(data['id'])
        tuple_data.append(data['ori_url'])
        tuple_data.append(data['url'])
        tuple_data.append(data['rank_name'])
        tuple_data.append(data['cat1'])
        tuple_data.append(data['cat2'])
        tuple_data.append(data['cat3'])
        tuple_data.append(data['no_num'])
        tuple_data.append(data['keyword'])
        tuple_data.append(data['attention'])
        tuple_data.append(data['sc_percent'])
        tuple_data.append(data['sc_num'])
        tuple_data.append(data['sell_num'])
        tuple_data.append(data['sell_price'])
        tuple_data.append(data['location'])
        tuple_data.append(data['seller_name'])
        tuple_data.append(data['sha1'])
        return tuple_data

    def batch_data_handle(self, tuple_data, table_name):
        """
            batch處理，若筆數大於 500 筆做一次 batch insert
        :param tuple_data:
        :param table_name:
        :return:
        """
        # print table_name
        self.batch_data[table_name].append(tuple_data)
        if len(self.batch_data[table_name]) >= 500:
            self.batch_insert_db(self.batch_data[table_name], table_name)
            self.batch_data[table_name] = []
            # print self.batch_data

    def batch_insert_db(self, tuple_data, table_name):
        """
            batch insert 進 taobaoTmall 資料庫的 def.
        :param sql_list: batch insert data.
        :param table_name: table name.
        :return:
        """
        print table_name, ' : batch insert : ', len(tuple_data)
        if table_name.find('itemlist') > 0:
            sql = self.item_batch_insert_sql.format(table_name)
        elif table_name.find('tags') > 0:
            sql = self.tag_batch_insert_sql.format(table_name)
        elif table_name.find('rank') > 0:
            sql = self.rank_batch_insert_sql.format(table_name)
        try:
            self.db.batch_insert_sql(sql, tuple_data)
        except Exception as e:
            print e

if __name__ == '__main__':
    a = transfer_main()
    a.main()
