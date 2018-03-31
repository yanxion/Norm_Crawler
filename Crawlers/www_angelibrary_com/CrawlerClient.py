# -*- coding: utf-8 -*-
import json
import os
import sys
import urlparse
import requests
import re
sys.path.append('../../')
from Util.CrawlerDataWrapper.CrawlerDataWrapper import CrawlerDataWrapper
from Util.DateTimeParser.DateTimeParser import Datetimeparser
from Util.TextUtil.SpecialCharUtil import remove_emoji
from pyquery import PyQuery
from Crawlers.CrawlerBase.Crawler import Crawler
# from datetime import datetime
from Util.SQL_Connect.SQL_Connect import SQL_Connect
import codecs

class CrawlerClient(Crawler):
    def __init__(self, **kwargs):
        super(CrawlerClient, self).__init__(**kwargs)
        self.crawler_data = CrawlerDataWrapper()
        self.CRAWLER_NAME = 'www_angelibrary_com'
        self.db = SQL_Connect()
        self.db.connect_mysql(os.path.join(os.path.dirname(__file__), "ibuzz_db_config.ini"))
        self.timeparse = Datetimeparser('now', '')
        # self.insert_meta = "INSERT INTO blog_meta (domain, account, name, url) VALUES ('%s', '%s', '%s', '%s')"
        self.insert = "INSERT INTO story (name, content, story_url, youtube_url) VALUES (%(name)s, %(content)s, %(story_url)s, %(youtube_url)s)"

        self.meta_flag = 0

    def crawl(self):
        if self.flag == 'entry':
            self.crawl_entry()
        elif self.flag == 'item':
            self.crawl_item()
        return self.crawler_data

    def crawl_entry(self):
        r = requests.get(self.url)
        r.encoding = 'big5'
        res = PyQuery(r.text)
        for i in range(res('td a').size()):
            name = res('td a').eq(i).text()
            url = "http://www.angelibrary.com/children/gt/" + res('td a').eq(i).attr('href')
            print name, 'crawl......'
            self.crawl_item(name, url)
            # if i == 2:
            #     exit()


    def crawl_item(self, name, url):
        r = requests.get(url)
        r.encoding = 'big5'
        res = PyQuery(r.text)
        content = res('pre').text()
        content = content.replace(u'------------------', '')
        content = content.replace(u'     黃金書屋 youth整理校對', '')
        content = content.replace(u'    轉載請保留，謝謝！', '')

        story_data = {
            'name': name,
            'content': content,
            'story_url': url,
            'youtube_url': '',
        }
        self.write_txtfile(name, content)
        self.db.insert_sql(self.insert, story_data)

    def write_txtfile(self, name, content):
        f = codecs.open('./story/' + name + ".txt", "w", "utf-8")
        f.write(content)
        f.close()

    def terminate(self):
        self.db.db_close()

def test():
    sitename = u'Pixnet'
    Blog_type = u'職場甘苦'
    test_set = {
        'entry': {
            # 'url': 'https://www.pixnet.net/blog/articles/category/9',
            'url': 'http://www.angelibrary.com/children/gt/',
            'sitename': sitename, 'type': Blog_type, 'flag': 'entry', 'context': '{}'
        },
        'item': {  # for normal item parse
            'url': 'http://tkbeasytest.pixnet.net/blog/post/4578536',
            'sitename': sitename, 'type': Blog_type, 'flag': 'item', 'context': '{}'
        }
    }
    cc = CrawlerClient(**test_set['entry'])
    cc.crawl()
    # res = cc.crawl()
    # print json.dumps(res.get_data(), ensure_ascii=False, indent=4)


if __name__ == '__main__':
    test()
