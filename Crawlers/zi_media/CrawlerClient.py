# -*- coding: utf-8 -*-
import json
import os
import sys
import urlparse
import requests
sys.path.append('../../')
from Util.CrawlerDataWrapper.CrawlerDataWrapper import CrawlerDataWrapper
from Util.DateTimeParser.DateTimeParser import Datetimeparser
from Util.TextUtil.SpecialCharUtil import remove_emoji
from pyquery import PyQuery
from Crawlers.CrawlerBase.Crawler import Crawler
from Util.SQL_Connect.SQL_Connect import SQL_Connect


class CrawlerClient(Crawler):
    def __init__(self, **kwargs):
        super(CrawlerClient, self).__init__(**kwargs)
        self.crawler_data = CrawlerDataWrapper()
        # mysql connect
        self.db = SQL_Connect()
        self.db.connect_mysql(os.path.join(os.path.dirname(__file__), "ibuzz_db_config.ini"))
        self.CRAWLER_NAME = 'zi_media'
        self.timeparse = Datetimeparser('now', '')
        self.insert_meta = "INSERT INTO blog_meta (domain, account, name, url) VALUES (%(domain)s, %(account)s, %(name)s, %(url)s)"
        self.insert_content = "INSERT INTO blog_content (domain, account, url, name, title, type, time, crawltime," \
                              " content, author, url_sha) " \
                              "VALUES (%(domain)s, %(account)s, %(url)s, %(name)s, %(title)s, %(type)s, %(time)s," \
                              " %(crawltime)s, %(content)s, %(author)s, SHA(%(url_sha)s))"
        self.select_content_repeat = "SELECT url_sha FROM blog_content where url_sha = SHA('%s')"
        self.select_meta_repeat = "SELECT url FROM blog_meta where url = '%s'"
        self.meta_flag = 0

    def crawl(self):
        if self.flag == 'entry':
            self.crawl_entry()
        elif self.flag == 'item':
            self.crawl_item()
        return self.crawler_data

    def crawl_entry(self):
        if self.url.find('zi.media/category/') > 1:
            self.meta_flag = -1
            self.parse_rank()
        else:
            self.parse_author()

    def parse_rank(self):
        r = requests.get(self.url)
        res = PyQuery(r.text)

        entry_data = {
            'sitename': self.sitename,
            'type': self.type,
            'url': '',
            'crawler_name': self.CRAWLER_NAME,
            'flag': 'entry',
            'context': '{"data_type": "blog"}'
        }
        entry_url = urlparse.urljoin(self.url, res('.page-arrow-next a').attr('href'))
        if not entry_url == self.url:
            entry_data['url'] = entry_url
            self.crawler_data.append_entry_job(**entry_data)

        item_data = {
            'sitename': self.sitename,
            'type': self.type,
            'url': '',
            'crawler_name': self.CRAWLER_NAME,
            'flag': 'item',
            'context': '{"data_type": "blog"}'
        }

        for i in range(res('.linkListType6-info').length):
            item_url_parse = res('.linkListType6-info').eq(i).find('.linkListType6-info-tit a').attr('href')
            item_url = urlparse.urljoin(self.url, item_url_parse)
            item_data['url'] = item_url
            self.crawler_data.append_item_job(**item_data)

    def parse_author(self):
        r = requests.get(self.url)
        res = PyQuery(r.text)

        entry_data = {
            'sitename': self.sitename,
            'type': self.type,
            'url': '',
            'crawler_name': self.CRAWLER_NAME,
            'flag': 'entry',
            'context': '{"data_type": "blog"}'
        }
        entry_url = urlparse.urljoin(self.url, res('.page-arrow-next a').attr('href'))
        if res('.page .active').text() == '1' and self.meta_flag == -1:
            self.meta_flag = 1
        if not entry_url == self.url:
            entry_data['url'] = entry_url
            self.crawler_data.append_entry_job(**entry_data)

        item_data = {
            'sitename': self.sitename,
            'type': self.type,
            'url': '',
            'crawler_name': self.CRAWLER_NAME,
            'flag': 'item',
            'context': '{"data_type": "blog", "meta_flag": "false"}'
        }

        for i in range(res('.linkListType6-info').length):
            item_url_parse = res('.linkListType6-info').eq(i).find('.linkListType6-info-tit a').attr('href')
            item_url = urlparse.urljoin(self.url, item_url_parse)
            item_data['url'] = item_url
            if self.meta_flag == 1:
                self.meta_flag = 0
                item_data['context'] = '{"data_type": "blog", "meta_flag": "true"}'
            else:
                item_data['context'] = '{"data_type": "blog", "meta_flag": "false"}'
            self.crawler_data.append_item_job(**item_data)

    def crawl_item(self):
        r = requests.get(self.url)
        if 'meta_flag' in self.context:
            if json.loads(self.context)['meta_flag'] == 'false':
                self.blog_content_crawler(r.text)
                return
        self.blog_content_crawler(r.text)
        self.blog_meta_crawler(r.text)

    def blog_content_crawler(self, html_script):

        res = PyQuery(html_script)
        # blog_content data insert.
        content_data = {
            'domain': 'zi.media',
            'account': res('.pageIn .linkListDetails-list a').attr('href')[1:],
            'url': self.url,
            'name': remove_emoji(res('.pageIn .linkListDetails-list a').text()),
            'title': remove_emoji(res('h1.tit-h1-type2').text()),
            'type': self.type,
            'time': res('.pageIn .linkListDetails-list div').eq(1).text() + " 12:00:00",
            'crawltime': self.timeparse.time_to_str(self.timeparse.now()),
            'content': remove_emoji(res('.textArea').text()),
            'author': remove_emoji(res('.pageIn .linkListDetails-list a').text()),
            'url_sha': self.url
        }
        print '┌‒‒content : ', content_data['url'],
        if self.db.select_sql(self.select_content_repeat % content_data['url']) == ('0',):
            try:
                self.db.insert_sql(self.insert_content, content_data)
                print "done."
            except Exception as e:
                print self.url, e
        else:
            print "has value."

    def blog_meta_crawler(self, html_script):
        res = PyQuery(html_script)
        # blog_meta data insert.
        meta_data = {
            'domain': 'zi.media',
            'account': res('.pageIn .linkListDetails-list a').attr('href')[1:],
            'url': urlparse.urljoin(self.url, res('.pageIn .linkListDetails-list a').attr('href')),
            'name': remove_emoji(res('.pageIn .linkListDetails-list a').text()),
        }
        print '└‒‒meta : ', meta_data['url'],

        if self.db.select_sql(self.select_meta_repeat % meta_data['url']) == ('0',):
            try:
                self.db.insert_sql(self.insert_meta, meta_data)
                print "done."
            except Exception as e:
                print self.url, e
        else:
            print "has value."

    def terminate(self):
        self.db.db_close()


if __name__ == '__main__':
    sitename = 'zimedia'
    news_type = 'food'
    test_set = {
        'entry': {
            'url': 'https://zi.media/category/food?PageSpeed=noscript',
            'sitename': sitename, 'type': news_type, 'flag': 'entry', 'context': '{}'
        },
        'item': {  # for normal item parse
            'url': 'https://zi.media/@midosa/post/WQ4zjV',
            'sitename': sitename, 'type': news_type, 'flag': 'item', 'context': '{}'
        }
    }
    a = CrawlerClient(**test_set['item'])
    a.crawl()
    pass
