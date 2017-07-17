# -*- coding: utf-8 -*-
__author__ = '130803'

import re
import json


from Util.DocFetcher.DocFetcher import DocFetcher
from Util.HashUtil.Sha import sha1
from Util.CrawlerDataWrapper.CrawlerDataWrapper import CrawlerDataWrapper
from pyquery import PyQuery
from datetime import datetime


class NewsFetcher:
    def __init__(self):
        self.url = "http://www.rmim.com.tw/news-list-18" #!!!!!!!!
        self.type = u"財產保險"
        self.crawler_data = CrawlerDataWrapper()
        self.sitename = "rmim"
        #self.CONTENT_AUTHOR = "rmim"

    def crawl(self):
        json_data = self.crawl_list_data()
        for list_data in  json_data['data']:
            res = PyQuery(str(list_data['href']), encoding="utf-8")

            if  list_data['author'].find('|') == -1:
                data_author = list_data['author'].replace(' ','')[2:5]
            else:
                data_author = list_data['author'].replace(' ','')[2:list_data['author'].replace(' ','').find('|')]

            data = {
                'url': list_data['href'],
                'title': res('div#news_detail div.cap1').text(),
                'time': datetime.strptime(list_data['publish'],'%Y.%m.%d'),
                'rawtime': list_data['publish'],
                'content': res('div.news_detail_block1x2_col1_row6').text(),
                'sitename': self.sitename,
                'author':data_author,
                'crawltime': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'type': self.type,
                # html field, generate with sha(title_string + content_string)
                'html': sha1((res('div#news_detail div.cap1').text() +''+ res('div.news_detail_block1x2_col1_row6').text()).encode('utf-8')),
                'sentiment': 0,
                'url_sha': sha1(list_data['href'].encode('utf-8'))
            }

            self.crawler_data.append_data(**data)

        return self.crawler_data

    def crawl_list_data(self):
        id = self.url[self.url.find('news-list-')+10:]
        Web_url = "http://www.rmim.com.tw/bg.php"
        Data = {
            'mode': '25',
            'id': id,
            'from': '0',
            'limit': '100'
        }
        x = DocFetcher(Web_url, method='POST', data=Data)

        x.set_https_verify(False)
        enjson = None
        try:
            src = x.fetch()
            enjson = json.loads(src)
        except Exception as e:
            pass

        return enjson

    def terminate(self):
        pass

if __name__ == '__main__':
    f = NewsFetcher()
    f.crawl()

