# -*- coding: utf-8 -*-
__author__ = '130803'

import re

from Util.DocFetcher.DocFetcher import DocFetcher
from Util.HashUtil.Sha import sha1
from Util.CrawlerDataWrapper.CrawlerDataWrapper import CrawlerDataWrapper
from pyquery import PyQuery
from datetime import datetime


class NewsFetcher:
    def __init__(self):
        self.crawler_data = CrawlerDataWrapper()
        self.issuelist_url = 'http://www.yzzk.com/dat/yzz/issuelist.xml'
        self.contentxml_url_base = 'http://www.yzzk.com/cfm/contentxml.cfm?issue=%s'
        self.article_url_base = 'http://www.yzzk.com/cfm/content_archive.cfm?id=%s&docissue=%s'
        self.sitename = "yzzk"
        self.CONTENT_AUTHOR = "yzzk"

    # get the latest issue number, for constructing article list url.
    def get_latest_issue_num(self):
        fetcher = DocFetcher(self.issuelist_url)
        res = fetcher.fetch()
        if res:
            res = re.sub(u'<\?xml.+?\?>\s', '', res)
        else:
            return None
        doc = PyQuery(res)
        issue_num = doc('rss > channel > item:first-of-type > summary > issue:eq(0)').text()
        return issue_num.strip()

    # get content xml
    def get_contentxml(self, issue_num):
        url = self.contentxml_url_base % issue_num
        fetcher = DocFetcher(url)
        res = fetcher.fetch()
        # remove the xml declare
        if res:
            res = re.sub(u'<\?xml.+?\?>\s', '', res)
        return res.encode('iso-8859-1').decode('utf-8')

    # should return a wrapper, containing all news data.
    def crawl(self):
        """
        data format:
        data = {'url': self.url,
                'title': title_string,
                'time': time_string,
                'rawtime': raw_time_string,
                'content': content_string,
                'sitename': self.sitename,
                'author': self.CONTENT_AUTHOR,
                'crawltime': crawl_time,
                'type': type_string,
                'html': html,
                'sentiment': 0,
                'url_sha': url_sha
                }
        # URL SHA, generate with sha(url)
        url_sha = sha1(self.url.encode('utf-8'))

        # html field, generate with sha(title_string + content_string)
        html = sha1((title_string + '' + content_string).encode('utf-8'))
        :return:
        """
        issue_num = self.get_latest_issue_num()
        plain_xml = self.get_contentxml(issue_num)
        doc = PyQuery(plain_xml)
        item_list = doc('item').items()

        for item in item_list:
            id = item.attr('nodeid')
            # construct the article url
            url = self.article_url_base % (id, issue_num)

            time = item('link').next().text()[:-5]
            time = time[time.find(',')+1:].split(' ')


            Temp = []
            for i in time:
                if not i == '':
                    Temp.append(i)
            time_string =  datetime.strptime( Temp[2] + '-' + Temp[1]+ '-' + Temp[0] + ' ' + Temp[3], "%Y-%b-%d %H:%M:%S")


            data = {'url':  url,
                    'title': item('title').text(),
                    'time': time_string,
                    'rawtime': item('link').next().text(),
                    'content': item('description').text().replace('<p>','').replace('</p>',''),
                    'sitename': self.sitename,
                    'author': self.CONTENT_AUTHOR,
                    'crawltime': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'type': item('summary section1').text(),
                    'html': sha1((item('title').text()+''+item('description').text().replace('<p>','').replace('</p>','')).encode('utf-8')),
                    'sentiment': 0,
                    'url_sha': sha1(url.encode('utf-8'))
            }
            self.crawler_data.append_data(**data)
        return self.crawler_data.get_data()

if __name__ == '__main__':
    f = NewsFetcher()
    f.crawl()

