# -*- coding: utf-8 -*-
import sys
sys.path.append('../../')

import re
import json
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
        self.CRAWLER_NAME = "www_mpfinance_com"

        # default url just use to
        self.Crawler_Url = ""
        self.Crawler_Page_Url = ""

    def crawl(self):
        rowcount = 10
        if (self.flag == 'entry'):
            if self.url.find('instantf') > 0:
                self.Crawler_Url = "http://www.mpfinance.com/fin/getlisting1.php?block=instantf&rowcount=%s",rowcount
                self.Crawler_Page_Url = "http://www.mpfinance.com/fin/instantf2.php?node=%s&issue=%s"
            elif self.url.find('instantp') > 0:
                self.Crawler_Url = "http://www.mpfinance.com/fin/getlisting1.php?block=instantp&rowcount=%s",rowcount
                self.Crawler_Page_Url = "http://www.mpfinance.com/fin/instantp2.php?node=%s&issue=%s"
            elif self.url.find('dailym') > 0:
                col =  self.url[self.url.find('col=')+4:]
                self.Crawler_Url = "http://www.mpfinance.com/fin/getlisting1.php?block=dailym&tagfilter=%s&rowcount=%s"
                self.Crawler_Page_Url = "http://www.mpfinance.com/fin/dailym2.php?col=%s&node=%s&issue=%s"
                if col == '1463484317296':
                    self.Crawler_Url =  self.Crawler_Url % ("%E5%9F%BA%E9%87%91%E7%89%B9%E5%8D%80",rowcount)
                elif col == '1463484340774':
                    self.Crawler_Url = self.Crawler_Url % ("%E7%90%86%E8%B2%A1%E4%BF%A1%E7%AE%B1",rowcount)
                elif col == '1463484365438':
                    self.Crawler_Url = self.Crawler_Url % ("%E7%90%86%E8%B2%A1%E5%B0%88%E9%A1%8C",rowcount)
                elif col == '1463484390304':
                    self.Crawler_Url = self.Crawler_Url % ("%E5%BC%B7%E7%A9%8D%E9%87%91",rowcount)
                self.Crawler_Page_Url = self.Crawler_Page_Url % (col, '%s', '%s')
            self.crawl_entry()
        else:
            self.crawl_item()

        return self.crawler_data

    def crawl_entry(self):
        res = PyQuery(self.Crawler_Url,encoding="utf-8")
        JData = json.loads(res.text())
        for i in JData['listing']:
            print self.Crawler_Page_Url % (i['nodeid'],i['docissue'])
            Job_Data = {
                'sitename': self.sitename,
                'type': self.type,
                'url': self.Crawler_Page_Url % (i['nodeid'],i['docissue']),
                'crawler_name': self.CRAWLER_NAME,
                'flag': 'entry'
            }
            self.crawler_data.append_item_job(**Job_Data)





    def crawl_item(self):
        res = PyQuery(self.url,encoding="utf-8")
        Data = {
                'url': self.url ,
                'title': res('h1.line_1_5em').text() ,
                'time': DateTimeUtil.parseTimeStr(self.url[self.url.find('issue=')+6:],"%Y%m%d") ,
                'rawtime': res('h6.line_3em').text() ,
                'content': res('div.article_content').text() ,
                'sitename': self.sitename ,
                'author': self.sitename ,
                'crawltime':  DateTimeUtil.timeToStr(DateTimeUtil.now()),
                'type': self.type,
                # html field, generate with sha(title_string + content_string)
                'html': sha1(( res('h1.line_1_5em').text() + '' + res('div.article_content').text() ).encode('utf-8')),
                'sentiment': 0,
                'url_sha': sha1(self.url)
            }

        self.crawler_data.append_data(**Data)

    def terminate(self):
        pass

def test():
    sitename = u'mpfinance'
    Blog_type = u'財經'
    test_set = {
        'entry': {
            # 'url': 'http://www.mpfinance.com/fin/instantf1.php',
            # 'url': 'http://www.mpfinance.com/fin/instantp1.php',
            'url': 'http://www.mpfinance.com/fin/dailym3.php?col=%s' % ('1463484390304'),
            'sitename': sitename, 'type': Blog_type, 'flag': 'entry'
        },
        'item': {  # for normal item parse
            'url': 'http://www.mpfinance.com/fin/dailym2.php?col=1463484317296&node=1499799946452&issue=20170712',
            'sitename': sitename, 'type': Blog_type, 'flag': 'item'
        }
    }
    cc = CrawlerClient(**test_set['item'])
    cc.crawl()
    #res = cc.crawl()
    #print json.dumps(res.get_data(), ensure_ascii=False, indent=4)

if __name__ == '__main__':
    test()
