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


class CrawlerClient(Crawler):
    def __init__(self, **kwargs):
        super(CrawlerClient, self).__init__(**kwargs)
        self.crawler_data = CrawlerDataWrapper()
        self.CRAWLER_NAME = 'www_pixnet_net'
        self.db = SQL_Connect()
        self.db.connect_mysql(os.path.join(os.path.dirname(__file__), "config.ini"))
        self.timeparse = Datetimeparser('now', '')
        # self.insert_meta = "INSERT INTO blog_meta (domain, account, name, url) VALUES ('%s', '%s', '%s', '%s')"
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
        if self.url.find('/articles/category/') > 1:
            self.parse_rank()
        else:
            self.parse_author()

    def crawl_item(self):
        r = requests.get(self.url)
        r.encoding = 'utf-8'
        if 'meta_flag' in self.context:
            if json.loads(self.context)['meta_flag'] == 'false':
                self.blog_content_crawler(r.text)
                return
        self.blog_content_crawler(r.text)
        self.blog_meta_crawler(r.text)

    def parse_rank(self):
        # find next page, and append to job_list step 1.
        if self.url.find('hot') > 1:
            page_num = self.url[self.url.find('/hot') + 5:]
            next_url = urlparse.urljoin(self.url, str(int(page_num) + 1))
        else:
            page_num = 1
            next_url = urlparse.urljoin(self.url + '/', 'hot/2')

        # append entry
        entry_data = {
            'sitename': self.sitename,
            'type': self.type,
            'url': next_url,
            'crawler_name': self.CRAWLER_NAME,
            'flag': 'entry',
            'context': '{"data_type": "blog"}'
        }
        # page of crawler want to crawl.
        if int(page_num) <= 11:
            self.crawler_data.append_entry_job(**entry_data)
        # -------------------------------------------------
        item_data = {
            'sitename': self.sitename,
            'type': self.type,
            'url': 'http',
            'crawler_name': self.CRAWLER_NAME,
            'flag': 'item',
            'context': '{"data_type": "blog"}'
        }

        r = requests.get(self.url)
        r.encoding = 'utf-8'
        res = PyQuery(r.text)
        if self.url[len(self.url) - 2:] == "/1" or self.url.find('/hot') < 0:
            # Blog_List_Name = res('div.featured h3').text()
            Blog_List_Url = res('div.featured h3 a').attr('href')
            item_data['url'] = re.sub("\-.*", "", Blog_List_Url)
            print item_data
            self.crawler_data.append_item_job(**item_data)
        for i in range(0, res('ol.article-list li').length, +1):
            if (res('ol.article-list li').eq(i).find('h3').text() == ""):
                print "!!!!"
                break
            # Blog_List_Name = res('ol.article-list li').eq(i).find('h3').text()
            Blog_List_Url = res('ol.article-list li').eq(i).find('h3 a').attr('href')
            item_data['url'] = re.sub("\-.*", "", Blog_List_Url)
            print item_data
            self.crawler_data.append_item_job(**item_data)

    def parse_author(self):
        # find next page, and append to job_list step 1.
        if self.url.find('/blog/') > 1 and not self.url[-1] == '/':
            page_num = self.url[self.url.find('/blog/') + 6:]
            next_url = urlparse.urljoin(self.url, str(int(page_num) + 1))
        elif self.url.find('/blog') > 1 and self.url[-1] == 'g':
            page_num = 1
            next_url = urlparse.urljoin(self.url + '/', '2')
        else:
            page_num = 1
            next_url = urlparse.urljoin(self.url, '2')
        if page_num == 1:
            self.meta_flag = 1
        # append entry
        entry_data = {
            'sitename': self.sitename,
            'type': self.type,
            'url': next_url,
            'crawler_name': self.CRAWLER_NAME,
            'flag': 'entry',
            'context': '{"data_type": "blog"}'
        }
        # page of crawler want to crawl.
        if int(page_num) <= 11:
            print entry_data
            self.crawler_data.append_entry_job(**entry_data)
        # -------------------------------------------------
        item_data = {
            'sitename': self.sitename,
            'type': self.type,
            'url': 'http',
            'crawler_name': self.CRAWLER_NAME,
            'flag': 'item',
            'context': '{"data_type": "blog"}'
        }

        r = requests.get(self.url)
        r.encoding = 'utf-8'
        res = PyQuery(r.text)
        for i in range(0, res('div.article li.title a').length, +1):
            Data = res('div.article li.title h2 a').eq(i).attr('href')
            item_data['url'] = re.sub("\-.*", "", Data)
            if self.meta_flag == 1:
                self.meta_flag = 0
                item_data['context'] = '{"data_type": "blog", "meta_flag": "true"}'
            else:
                item_data['context'] = '{"data_type": "blog", "meta_flag": "false"}'
            # print item_data
            self.crawler_data.append_item_job(**item_data)

    def terminate(self):
        self.db.db_close()

    # Blog Content Analysis.
    def blog_content_crawler(self, html_script):
        Web_url = self.url
        res = PyQuery(html_script)
        content_data = {
            # 'domain': Web_url[Web_url.find('//') + 2:Web_url.find('/', Web_url.find('//') + 2)][
            #           Web_url[7:Web_url.find('/', Web_url.find('//') + 2)].find('.') + 1:],
            'domain': 'pixnet.net',
            'account': Web_url[Web_url.find('//') + 2:Web_url.find('/', Web_url.find('//') + 2)][
                       :Web_url[7:Web_url.find('/', Web_url.find('//') + 2)].find('.')],
            'url': self.url,
            'name': remove_emoji(res('div#banner a').eq(0).text()),
            'title': remove_emoji(res('li.title h2 a').text()),
            'type': res('ul.refer li').eq(0).find('a').text(),
            'time': self.timeparse.get_timeformat_from_timestr_and_fields(
                    res('li.publish .year').text() + '-' + res('li.publish .month').text() + '-'
                    + res('li.publish .date').text() + ' ' + res('li.publish .time').text(), "%Y %m %d %H %M"),
            'crawltime': self.timeparse.time_to_str(self.timeparse.now()),
            'content': remove_emoji(res('div.article-content-inner p').text()),
            'author': remove_emoji(res('div.box-text dl dd').eq(0).text()),
            'url_sha': self.url
        }
        if content_data['author'] == '':
            author_temporary = res('p.author').text()
            content_data['author'] = remove_emoji(author_temporary[:author_temporary.find(' ')])

        print '┌‒‒content : ', content_data['url'],
        if self.db.select_sql(self.select_content_repeat % content_data['url']) == ('0',):
            try:
                self.db.insert_sql(self.insert_content, content_data)
                print "done."
            except Exception as e:
                print self.url, e
        else:
            print "has value."

    # Blog Meta Analysis.
    def blog_meta_crawler(self, html_script):
        Web_url = self.url
        res = PyQuery(html_script)
        meta_data = {
            'domain': Web_url[Web_url.find('//') + 2:Web_url.find('/', Web_url.find('//') + 2)][
                      Web_url[7:Web_url.find('/', Web_url.find('//') + 2)].find('.') + 1:],
            'account': Web_url[Web_url.find('//') + 2:Web_url.find('/', Web_url.find('//') + 2)][
                       :Web_url[7:Web_url.find('/', Web_url.find('//') + 2)].find('.')],
            'url': Web_url[:Web_url.find('/', Web_url.find('//') + 2)] + "/blog/",
            'name': remove_emoji(res('div#banner a').eq(0).text()),
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


def test():
    sitename = u'Pixnet'
    Blog_type = u'職場甘苦'
    test_set = {
        'entry': {
            # 'url': 'https://www.pixnet.net/blog/articles/category/9',
            'url': 'http://fc781117.pixnet.net/blog',
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
