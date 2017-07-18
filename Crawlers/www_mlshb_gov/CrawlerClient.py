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
        self.CRAWLER_NAME = "www_mlshb_gov"


    def crawl(self):
        if (self.flag == 'entry'):
            self.crawl_entry()
            if self.url.find('pn=') > 0 :
                page_num = self.url[self.url.find('pn=')+3 : self.url.find('&')]
                url = urlparse.urlparse(self.url)
                url = urlparse.urlunsplit((url.scheme,url.netloc,url.path,'',''))
                if int(page_num) < 6:
                    page_num = int(page_num) + 1
                    Job_Data = {
                        'sitename': self.sitename,
                        'type': self.type,
                        'url': url + "?pn="+str(page_num)+"&department=&key=",
                        'crawler_name': self.CRAWLER_NAME,
                        'flag': 'entry'
                    }
                    self.crawler_data.append_item_job(**Job_Data)

            else:
                print self.url+"?pn=2&department=&key="
                Job_Data = {
                    'sitename': self.sitename,
                    'type': self.type,
                    'url': self.url+"?pn=2&department=&key=",
                    'crawler_name': self.CRAWLER_NAME,
                    'flag': 'entry'
                }
                self.crawler_data.append_item_job(**Job_Data)
        else:
            self.crawl_item()


        return self.crawler_data

    def crawl_entry(self):
        res = requests.get(self.url,verify = False)
        res.encoding = 'utf-8'
        res = PyQuery(res.text)

        for i in range(0,res('div#news_box li a').length,+1):
            print urlparse.urljoin("https://www.mlshb.gov.tw/tc/", res('div#news_box li a').eq(i).attr('href'))
            Job_Data = {
                'sitename': self.sitename,
                'type': self.type,
                'url': urlparse.urljoin("https://www.mlshb.gov.tw/tc/", res('div#news_box li a').eq(i).attr('href')),
                'crawler_name': self.CRAWLER_NAME,
                'flag': 'item'
            }
            self.crawler_data.append_item_job(**Job_Data)


    def crawl_item(self):
        res = requests.get(self.url, verify=False)
        res.encoding = 'utf-8'
        res = PyQuery(res.text)
        Data = {
                'url': self.url ,
                'title': res('div#ctl00_content_liFdTitle').text() ,
                'time': DateTimeUtil.parseTimeStr(res('div#ctl00_content_liPDate span').text(),"%Y-%m-%d") ,
                'rawtime': res('div#ctl00_content_liPDate span').text() ,
                'content': res('div.txtDetail').text() ,
                'sitename': self.sitename ,
                'author': self.sitename ,
                'crawltime':  DateTimeUtil.timeToStr(DateTimeUtil.now()),
                'type': self.type,
                # html field, generate with sha(title_string + content_string)
                'html': sha1((res('div#ctl00_content_liFdTitle').text() + '' +  res('div.txtDetail').text() ).encode('utf-8')),
                'sentiment': 0,
                'url_sha': sha1(self.url)
            }
        self.crawler_data.append_data(**Data)

    def terminate(self):
        pass

def test():
    sitename = u'mlshb'
    Blog_type = u'新聞稿'
    test_set = {
        'entry': {
            'url': 'https://www.mlshb.gov.tw/tc/PressRelease.aspx?pn=2&department=&key=',
            'sitename': sitename, 'type': Blog_type, 'flag': 'entry'
        },
        'item': {  # for normal item parse
            'url': 'https://www.mlshb.gov.tw/tc/PressReleaseContent.aspx?id=2062&chk=3f0f2a42-cfbe-4155-bd5d-ecd27e613701&mid=15&param=pn%3d1%26department%3d%26key%3d',
            'sitename': sitename, 'type': Blog_type, 'flag': 'item'
        }
    }
    cc = CrawlerClient(**test_set['item'])
    cc.crawl()
    #res = cc.crawl()
    #print json.dumps(res.get_data(), ensure_ascii=False, indent=4)

if __name__ == '__main__':
    test()
