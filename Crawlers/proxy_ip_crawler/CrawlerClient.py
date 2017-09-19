# -*- coding: utf-8 -*-
import sys
import time

sys.path.append('../../')
import json
import requests
from Util.CrawlerDataWrapper.CrawlerDataWrapper import CrawlerDataWrapper
from Crawlers.CrawlerBase.Crawler import Crawler
from Util.Crawler_Proxy_Util.Crawler_Proxy_Util import Crawler_Proxy_Util
from pyquery import PyQuery


class CrawlerClient(Crawler):
    def __init__(self, **kwargs):
        super(CrawlerClient, self).__init__(**kwargs)
        self.crawler_data = CrawlerDataWrapper()
        self.CRAWLER_NAME = "proxy_ip_crawler"
        self.proxy_crawler = Crawler_Proxy_Util()

    def crawl(self):
        if self.flag == 'entry':
            self.crawl_entry()
        else:
            self.crawl_item()
        return self.crawler_data

    def crawl_entry(self):
        for i in range(20):
            Job_Data = {
                'sitename': self.sitename,
                'type': self.type,
                'url': 'http://www.xroxy.com/proxylist.php?port=&type=All_http&ssl=ssl&country=&latency=&reliability='
                       '&sort=reliability&desc=true&pnum=' + str(i),
                'crawler_name': self.CRAWLER_NAME,
                'flag': 'item',
                'context': '{"method":"http"}',
            }
            self.crawler_data.append_item_job(**Job_Data)

    def crawl_item(self):
        method = json.loads(self.context)['method']
        r = requests.get(self.url)
        res = PyQuery(r.text)
        for i in range(res('tr[class^="row"]').size()):
            res2 = PyQuery(res('tr[class^="row"]').eq(i))
            for j in range(res2('a').size()):
                if j == 1:
                    ip = res2('a').eq(j).text()
                elif j == 2:
                    port = res2('a').eq(j).text()

            time.sleep(1)
            self.proxy_crawler.set_proxy(method, ip, port)
            print method, '_', (ip + ":" + port).ljust(20), "...",

            if self.proxy_crawler.is_proxy_available(self.proxy_crawler.get_random_proxy(use_set_proxy=True)):
                self.proxy_crawler.db.insert_sql("INSERT INTO proxy(method, ip, port, account, passwd)" 
                                                 " VALUE('%s','%s','%s','%s','%s') ON DUPLICATE KEY UPDATE port = '%s'," 
                                                 " account = '%s',passwd = '%s', method = '%s' ;"
                                                 % (self.proxy_crawler.proxy_method, self.proxy_crawler.proxy_ip,
                                                    self.proxy_crawler.proxy_port,
                                                    self.proxy_crawler.proxy_account, self.proxy_crawler.proxy_passwd,
                                                    self.proxy_crawler.proxy_port,
                                                    self.proxy_crawler.proxy_account, self.proxy_crawler.proxy_passwd,
                                                    self.proxy_crawler.proxy_method))

    def terminate(self):
        self.proxy_crawler.terminate()


if __name__ == '__main__':
    sitename = u'proxy'
    crawl_type = u'proxy'
    test_set = {
        'entry': {
            'url': '',
            'sitename': sitename, 'type': crawl_type, 'flag': 'entry'
        },
        'item': {  # for normal item parse
            'url': '',
            'sitename': sitename, 'type': crawl_type, 'flag': 'item'
        }
    }
    cc = CrawlerClient(**test_set['item'])
    cc.crawl()
