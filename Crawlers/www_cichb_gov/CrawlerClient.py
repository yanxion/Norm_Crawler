# -*- coding: utf-8 -*-
import sys
sys.path.append('../../')

import re
import json
import requests
import urlparse

from Util.DocFetcher.DocFetcher import DocFetcher
from Util.HashUtil.Sha import sha1

from Util.DateTimeUtil import DateTimeUtil
from Util.CrawlerDataWrapper.CrawlerDataWrapper import CrawlerDataWrapper
from Crawlers.CrawlerBase.Crawler import Crawler

from pyquery import PyQuery


class CrawlerClient(Crawler):
    def __init__(self, **kwargs):
        super(CrawlerClient, self).__init__(**kwargs)
        self.crawler_data = CrawlerDataWrapper()
        self.CRAWLER_NAME = "www_cichb_gov"


    def crawl(self):
        if (self.flag == 'entry'):
            self.crawl_entry()
        else:
            self.crawl_item()
        return self.crawler_data

    def crawl_entry(self):
        res = requests.get(self.url,verify = False)
        res.encoding = 'big5'
        res = PyQuery(res.text)
        for i in range(0,res('td.box a').length,+1):
            print urlparse.urljoin("https://www.cichb.gov.tw/news/",res('td.box a').eq(i).attr('href'))
            Job_Data = {
                'sitename': self.sitename,
                'type': self.type,
                'url': urlparse.urljoin("https://www.cichb.gov.tw/news/",res('td.box a').eq(i).attr('href')),
                'crawler_name': self.CRAWLER_NAME,
                'flag': 'item'
            }
            self.crawler_data.append_item_job(**Job_Data)


    def crawl_item(self):
        res = requests.get(self.url, verify=False)
        res.encoding = 'big5'
        res = PyQuery(res.text)
        Data = {
                'url': self.url ,
                'title': res('table tr th').eq(1).next().text() ,
                'time': DateTimeUtil.parseTimeStr(res('table tr th').eq(2).next().text(),"%Y-%m-%d") ,
                'rawtime': res('table tr th').eq(2).next().text() ,
                'content': res('table table tr td p').eq(5).text() ,
                'sitename': self.sitename ,
                'author': self.sitename ,
                'crawltime':  DateTimeUtil.timeToStr(DateTimeUtil.now()),
                'type': self.type,
                # html field, generate with sha(title_string + content_string)
                'html': sha1((res('table tr th').eq(1).next().text() + '' + res('table table tr td p').eq(5).text() ).encode('utf-8')),
                'sentiment': 0,
                'url_sha': sha1(self.url)
            }
        self.crawler_data.append_data(**Data)

    def terminate(self):
        pass

def test():
    sitename = u'cichb'
    Blog_type = u'新聞稿'
    test_set = {
        'entry': {
            'url': 'https://www.cichb.gov.tw/news/list_all.asp?cat_id=1',
            'sitename': sitename, 'type': Blog_type, 'flag': 'entry'
        },
        'item': {  # for normal item parse
            'url': 'https://www.cichb.gov.tw/news/news_detail.asp?news_dtl_id=5658',
            'sitename': sitename, 'type': Blog_type, 'flag': 'item'
        }
    }
    cc = CrawlerClient(**test_set['item'])
    cc.crawl()
    #res = cc.crawl()
    #print json.dumps(res.get_data(), ensure_ascii=False, indent=4)

if __name__ == '__main__':
    test()
