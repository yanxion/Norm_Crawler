# -*- coding: utf-8 -*-
import json
import sys
import urllib
from urlparse import urljoin
import urlparse
sys.path.append('../../')
import re
import requests
from Util.HashUtil.Sha import sha1
# from Util.DateTimeUtil import DateTimeUtil
from Util.DateTimeParser import DateTimeParser
from Util.CrawlerDataWrapper.CrawlerDataWrapper import CrawlerDataWrapper
from Crawlers.CrawlerBase.Crawler import Crawler
from pyquery import PyQuery


class CrawlerClient(Crawler):
    def __init__(self, **kwargs):
        super(CrawlerClient, self).__init__(**kwargs)
        self.crawler_data = CrawlerDataWrapper()
        self.CRAWLER_NAME = "www_msn_com"
        self.time_util = DateTimeParser.Datetimeparser('now', '')
        self.data = {
            'url': '',
            'title': '',
            'time': '',
            'rawtime': '',
            'content': '',
            'sitename': '',
            'author': '',
            'crawltime': '',
            'type': '',
            # # html field, generate with sha(title_string + content_string)
            'html': '',
            'sentiment': 0,
            'url_sha': '',
        }

    def crawl(self):
        if self.flag == 'entry':
            self.crawl_entry()
        else:
            self.crawl_item()

        return self.crawler_data

    def crawl_entry(self):
        r = requests.get(self.url, headers=self.get_headers())
        r_re = re.sub('<\?.*\?>', '', r.text)
        res = PyQuery(r_re)
        res('.financeheaderitemtemplate').remove()
        res('div.slide').remove()
        for i in range(res('div.sectioncontent ul li a').size()):
            # print res('div.sectioncontent ul li a').eq(i).text()
            url = res('div.sectioncontent ul li a').eq(i).attr('href').encode('utf8')

            url = urllib.unquote(url)
            msn_parse = urlparse.urlparse('https://www.msn.com')
            url_parse = urlparse.urlparse(url)
            parse_data = [msn_parse.scheme, msn_parse.netloc, url_parse.path, url_parse.fragment, '']
            entry_url = urlparse.urlunsplit(parse_data)

            # print urljoin('https://www.msn.com', url)
            # print urljoin('https://www.msn.com', urllib.quote(url))
            # print urljoin('https://www.msn.com', urllib.quote(url).encode('utf-8'))
            Job_Data = {
                'sitename': self.sitename,
                'type': self.type,
                'url': urllib.quote(urljoin('https://www.msn.com', entry_url)),
                'crawler_name': self.CRAWLER_NAME,
                'flag': 'item',
                'context': '{"time":"' + str(i) + '"}'
            }
            Job_Data['url'] = Job_Data['url'].replace('%3A//', '://')
            self.crawler_data.append_item_job(**Job_Data)

    def crawl_item(self):
        # time =json.loads(self.context)['time']
        r = requests.get(self.url, headers=self.get_headers())
        r.encoding = 'utf-8'
        r_re = re.sub('<\?.*\?>', '', r.text)
        res = PyQuery(r_re)
        res('script').remove()
        try:
            self.data['url'] = self.url
            self.data['title'] = res('div#precontent header h1, div#primary-video-title h1').text()
            self.data['rawtime'] = res(
                'div.authorinfo-txt time, div.primary-video-metadata span.date time').text()
            self.data['content'] = res('section.articlebody, .body-text, .primary-video-description-text').text()
            self.data['sitename'] = self.sitename
            self.data['crawltime'] = self.time_util.time_to_str(self.time_util.now())
            self.data['type'] = self.type
            self.data['sentiment'] = 0
            self.data['url_sha'] = sha1(self.url)

            # time handle
            if res('div.authorinfo-txt time, div.primary-video-metadata span.date time').attr('datetime'):
                self.data['time'] = self.time_util.get_timeformat_from_timestr_and_fields(
                    res('div.authorinfo-txt time, div.primary-video-metadata span.date time').attr('datetime')[:-5],
                    '%Y %m %d %H %M %S')
            else:
                self.data['time'] = self.time_util.get_timeformat_from_timestr_and_fields('', '%Y %m %d %H %M %S')

            # html handle
            self.data['html'] = sha1(self.data['title'].encode('utf-8') + '' + self.data['content'].encode('utf-8'))

            # author handle
            if res('div.authorinfotb div.authorinfo-txt span.authorname-txt').text():
                self.data['author'] = res('div.authorinfotb div.authorinfo-txt span.authorname-txt').text()
            elif res('div.authorinfotb div.sourcename-txt.truncate').text():
                self.data['author'] = res('div.authorinfotb div.sourcename-txt.truncate').text()
            elif res('div.metadata-and-share a').attr('aria-label'):  # Video
                self.data['author'] = res('div.metadata-and-share a').attr('aria-label')
            else:
                self.data['author'] = self.sitename

        except Exception as e:
            print "------------------------------------"
            for i in self.data:
                print i, self.data[i]
            print "Error : "
            print "    ", self.url
            print "    ", e
            print "------------------------------------"
            return

        # for i in self.data:
        #     print i, ': ', self.data[i]
        self.crawler_data.append_data(**self.data)

    def get_headers(self):
        """
            set headers
        :return: headers
        """

        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, sdch",
            "Accept-Language": "zh-TW,zh;q=0.8,en-US;q=0.6,en;q=0.4",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.276 Safari/537.36"
        }
        return headers

    def terminate(self):
        pass


def test():
    sitename = u'MSNnews'
    Blog_type = u'財經'
    test_set = {
        'entry': {
            'url': 'https://www.msn.com/zh-tw/travel/hiking',
            'sitename': sitename, 'type': Blog_type, 'flag': 'entry', 'context': '{}'
        },
        'item': {  # for normal item parse
            'url': 'https://www.msn.com/zh-tw/travel/hiking/%E3%80%90%E5%8D%B3%E6%99%82%E6%96%B0%E8%81%9E%E7%85%A7%E7%89%87%E3%80%91%E7%99%BB%E5%B1%B1%E8%88%87%E5%81%A5%E8%A1%8C-%E4%B8%80%E6%89%8B%E7%85%A7%E7%89%87%E8%B3%87%E8%A8%8A/ss-BBAIXVn',
            # 'url': 'https://www.msn.com/zh-tw/money/topstories/%E6%93%A0%E4%B8%8B%E9%AB%98%E9%80%9A-%E8%81%AF%E7%99%BC%E7%A7%91%E6%9C%89%E6%A9%9F%E6%9C%83%E5%90%83%E8%98%8B%E6%9E%9C/ar-AAuhLAE',
            'sitename': sitename, 'type': Blog_type, 'flag': 'item', 'context': '{"time":"10"}'
        }
    }
    cc = CrawlerClient(**test_set['entry'])
    cc.crawl()
    res = cc.crawl()
    # print json.dumps(res.get_data(), ensure_ascii=False, indent=4)


if __name__ == '__main__':
    test()
