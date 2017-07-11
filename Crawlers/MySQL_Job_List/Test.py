# -*- coding: utf-8 -*-

import MySQLdb
from datetime import datetime
from Crawlers.www_pixnet_net.CrawlerClient import CrawlerClient


db = MySQLdb.connect("localhost", "user", "user", "blog_crawler", charset='utf8')
cursor = db.cursor()



def Job_List_Get():
    Select_SQL = ("SELECT * FROM job_list ")
    cursor.execute(Select_SQL)

    result = cursor.fetchall()[0]

    Data = {'url':result[3],
            'sitename':result[1],
            'type':result[2],
            'flag':result[6]
            }

    cc = CrawlerClient(**Data)
    cc.crawl()

    cursor.execute("DELETE FROM job_list WHERE id = '" + str(result[0]) + "';")
    #db.commit()

    #for record in result:
        #print record


def Job_List_Add():
    Insert_SQL = ("INSERT INTO job_list(`sitename`,`type`,`url`,`crawler_name`,`host`,`flag`,`assign_time`,`url_sha`)VALUES (%s, %s, %s, %s, %s, %s, %s, SHA(%s));")
    Data = []
    Data.append('pixnet')
    Data.append(u'職場甘苦')
    Data.append('https://www.pixnet.net/blog/articles/category/7/hot/')
    #Data.append('http://rulinty.pixnet.net/blog')
    Data.append('www_pixne_net')
    Data.append('localhost')
    Data.append('entry')
    Data.append(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'))
    Data.append('https://www.pixnet.net/blog/articles/category/7/hot/')
    #Data.append('http://rulinty.pixnet.net/blog')
    cursor.execute(Insert_SQL, Data)
    db.commit()



if __name__ == '__main__':
    print datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    #Job_List_Add()

    Job_List_Get()