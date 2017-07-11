# -*- coding: utf-8 -*-
__author__ = '130803'

import sys

sys.path.append('../../')

from urlparse import urljoin
from urlparse import urlparse
from pyquery import PyQuery
import re
import json

from Util.DateTimeUtil import DateTimeUtil
from Util.HashUtil.Sha import sha1
from Util.CrawlerDataWrapper.CrawlerDataWrapper import CrawlerDataWrapper
from Util.DocFetcher.DocFetcher import DocFetcher
from Crawlers.CrawlerBase.Crawler import Crawler


class CrawlerClient(Crawler):
    """
        constructor should access job_list row dict as parameter and initialize
    """

    def __init__(self, **kwargs):
        # pass basic crawler info to super class.
        super(CrawlerClient, self).__init__(**kwargs)
        # crawler name must be specified, or it will be None (from super class).
        # suggested form is to use the domain name, and replace the '.' with '_'

        self.CRAWLER_NAME = 'www_juksy_com'
        # if using the ENTRY_NEXT_PAGE_PATTERN, this variable will be involved to construct entry URLs.
        # if using CSS to get next page URL, set this variable to 1 and STOP_CRAWL_PAGE to the page you want to stop.
        self.START_CRAWL_PAGE = 1
        # stopping condition, stop after crawling this amount of pages of entry.
        self.STOP_CRAWL_PAGE = 3
        self.ENTRY_REQUEST_TYPE = 'GET'


# ENTRY NEWS LINK
        # any characters should be in unicode.
        # settings around links in entry page. leave RE empty string if not meant to use it.
        self.ENTRY_NEWS_LINK_CSS = 'a.title'
        # list of patterns and replacements. make sure it's encoded in utf-8.
        self.ENTRY_NEWS_LINK_REPLACE_RE = [

        ]
        self.ENTRY_NEWS_LINK_REPLACE_STRING = [

        ]

# ENTRY NEXT PAGE
        # if the url is in a fixed form, just use %i as page number, which will later be substituted by page num.
        # if the ENTRY_NEXT_PAGE_PATTERN is set, the ENTRY_NEXT_PAGE_CSS|RE|REPLACE won't be used.
        # self.ENTRY_NEXT_PAGE_PATTERN = 'http://www.appledaily.com.tw/realtimenews/section/new/%i'
        self.ENTRY_NEXT_PAGE_PATTERN = 'https://www.juksy.com/channel/2?page=%i'
        # if not using the fixed form, leave the NEXT_PAGE_PATTERN empty string ('')
        self.ENTRY_NEXT_PAGE_CSS = ''
        self.ENTRY_NEXT_PAGE_ATTR = ''
        self.ENTRY_NEXT_PAGE_REPLACE_RE = [

        ]
        self.ENTRY_NEXT_PAGE_REPLACE_STRING = [

        ]

# CONTENT TITLE
        # settings around content title. leave RE empty string if not meant to use it.
        self.CONTENT_TITLE_CSS = 'h1.title'
        # using the REMOVE_CSS will made a copy, and won't affect the original doc.
        self.CONTENT_TITLE_REMOVE_CSS = 'script'
        self.CONTENT_TITLE_REPLACE_RE = [

        ]
        self.CONTENT_TITLE_REPLACE_STRING = [

        ]

# CONTENT AUTHOR
        # todo: implement the author switch
        # settings around content author.
        # if using fixed value as author, leave CSS, RE, REPLACE empty string, vice versa.
        self.CONTENT_AUTHOR = u'Juksy'
        self.CONTENT_AUTHOR_CSS = ''
        self.CONTENT_AUTHOR_REMOVE_CSS = 'script'
        self.CONTENT_AUTHOR_REPLACE_RE = [

        ]
        self.CONTENT_AUTHOR_REPLACE_STRING = [

        ]
        # content type is set by entry list. modify it there.

# CONTENT TIME
        # settings around time. processing order is:
        # 1. remove_css, remove unwanted elements from html doc
        # 2. replace_re, replace the characters
        # 3. matches, matches the time string RE
        # 4. format, match each string in time string to relative field
        self.CONTENT_TIME_CSS = 'span.date'
        self.CONTENT_TIME_REMOVE_CSS = 'script'
        # if use time_matches, content_time_replace_re will still be triggered.
        # if not using, leave the replace re array empty.
        # if more than one matches, remember to assign the index.
        self.CONTENT_TIME_MATCHES = '\d{2} \d{2}, \d{4}'
        self.CONTENT_TIME_MATCHES_INDEX = 0
        # for some special time formats, just try to replace them.
        self.CONTENT_TIME_REPLACE_RE = [
            ' in', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
        ]
        self.CONTENT_TIME_REPLACE_STRING = [
            '', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12'
        ]
        # %Y: year in n digits
        # %y: year in 2 digits, [00, 99]
        # %m: month, [01, 12]
        # %d: day, [01,31]
        # %H: hour in 24H mode, [00, 23]
        # %h: hour in 12H mode, [01, 12]
        # %p: AM/PM
        # %M: minute, [00, 59]
        # %S: second, [00, 61]
        # must encoded in utf-8, DO NOT REMOVE THE ENCODING!
        self.CONTENT_TIME_FORMAT = u'%m %d, %Y'.encode('utf-8')

# CONTENT TEXT
        # settings around content.
        self.CONTENT_TEXT_CSS = 'section.mainArticle'
        self.CONTENT_TEXT_REMOVE_CSS = 'script, span.fr-draggable'
        self.CONTENT_TEXT_REPLACE_RE = [

        ]
        self.CONTENT_TEXT_REPLACE_STRING = [

        ]

# CONTENT NEXT PAGE
        # settings around content next page
        # if not using the content next page feature, leave the CONTENT_TEXT_NEXT_PAGE_CSS an empty string.
        self.CONTENT_TEXT_NEXT_PAGE_CSS = ''
        self.CONTENT_TEXT_NEXT_PAGE_REPLACE_RE = [

        ]
        self.CONTENT_TEXT_NEXT_PAGE_REPLACE_STRING = [

        ]

    # a crawl() MUST be implemented, and should include all works, like fetch, parse, and return in dict format.
    # if it's not a news crawler, DB access should also be included. write to DB yourself, and return a None.
    def crawl(self):
        # fetch part can be replaced with Util.DocFetcher.DocFetcher, if static
        self.html = DocFetcher(self.url).fetch()
        res = self.parse()
        return res

    def parse(self):
        doc = PyQuery(self.html)
        result = None
        if self.flag == 'entry' or self.flag == 'list':
            result = self.parse_list(doc)
        elif self.flag == 'item':
            result = self.parse_item(doc)
        return result

    # returns a list of jobs
    def parse_list(self, doc):
        # todo: go through all pages within a loop and get all news urls first.
        crawler_data = CrawlerDataWrapper()

        for page in range(self.START_CRAWL_PAGE, self.STOP_CRAWL_PAGE + 1):
            print 'Processing page %s...' % page
            # 1st page has been fetched and parsed as the variable doc sent in here.
            # therefore need not to fetch again.
            if page > 1:
                # if next page pattern (fixed URL format) is set, replace the %i with the page number and fetch, parse.
                # if pattern not set, use the
                if self.ENTRY_NEXT_PAGE_PATTERN:
                    next_page_url = re.sub('%i', str(page), self.ENTRY_NEXT_PAGE_PATTERN)
                else:
                    next_page_url = urljoin(self.url, doc(self.ENTRY_NEXT_PAGE_CSS).attr(self.ENTRY_NEXT_PAGE_ATTR))
                    # replace the url with NEXT_PAGE_REPLACE if NEXT_PAGE_REPLACE_RE is defined (not empty string).
                    if self.ENTRY_NEXT_PAGE_REPLACE_RE:
                        next_page_url = self.replace_str(self.ENTRY_NEXT_PAGE_REPLACE_RE,
                                                         self.ENTRY_NEXT_PAGE_REPLACE_STRING, next_page_url)
                next_page_url = urlparse(next_page_url).geturl()
                # update the doc to currently crawling page
                doc = PyQuery(DocFetcher(next_page_url).fetch())

            news_url_list = doc.items(self.ENTRY_NEWS_LINK_CSS)
            # make a job_list formed tuple for each entry page.
            for url in news_url_list:
                target_url = urljoin(self.url, url.attr('href'))
                target_url = urlparse(target_url).geturl()
                item_data = {
                    'sitename': self.sitename,
                    'type': self.type,
                    'url': target_url,
                    'crawler_name': self.CRAWLER_NAME,
                    'flag': 'item'
                }
                # res.append(item_data)
                crawler_data.append_item_job(**item_data)

        return crawler_data

    # returns a dict, representing a news data
    def parse_item(self, doc):
        crawler_data = CrawlerDataWrapper()
        # AD remove area
        # independently remove by each part's REMOVE_CSS

        # TITLE
        title_element = doc(self.CONTENT_TITLE_CSS)
        # if CONTENT_TITLE_REMOVE_CSS is not empty string, remove the elements from title_element.
        # use a copy of doc for the need of element removal, so the removal won't affect the original doc.
        if self.CONTENT_TITLE_REMOVE_CSS:
            title_element = title_element.clone()
            title_element.remove(self.CONTENT_TITLE_REMOVE_CSS)

        title_string = title_element.text()
        # regular expression replacement.
        if self.CONTENT_TITLE_REPLACE_RE:
            title_string = self.replace_str(self.CONTENT_TITLE_REPLACE_RE, self.CONTENT_TITLE_REPLACE_STRING,
                                            title_string)

        # AUTHOR
        # if fixed author's not assigned to CONTENT_AUTHOR, then get the author from the doc.
        if not self.CONTENT_AUTHOR:
            author_element = doc(self.CONTENT_AUTHOR_CSS)
            if self.CONTENT_AUTHOR_REMOVE_CSS:
                author_element = author_element.clone()
                author_element.remove(self.CONTENT_AUTHOR_REMOVE_CSS)

            author_string = author_element.text()
            # regular expression replacement
            if self.CONTENT_AUTHOR_REPLACE_RE:
                author_string = self.replace_str(self.CONTENT_AUTHOR_REPLACE_RE, self.CONTENT_AUTHOR_REPLACE_STRING,
                                                 author_string)
            self.AUTHOR = author_string

        # TYPE
        # if need other ways to fetch type, implement it yourself here.
        # otherwise, it's set and applied in table `entry_list`
        type_string = self.type

        # TIME
        time_element = doc(self.CONTENT_TIME_CSS)
        if self.CONTENT_TIME_REMOVE_CSS:
            time_element = time_element.clone()
            time_element.remove(self.CONTENT_TIME_REMOVE_CSS)

        raw_time_string = time_element.text()

        if self.CONTENT_TIME_REPLACE_RE:
            raw_time_string = self.replace_str(self.CONTENT_TIME_REPLACE_RE, self.CONTENT_TIME_REPLACE_STRING, raw_time_string)
        if self.CONTENT_TIME_MATCHES:
            try:
                raw_time_string = self.matches_str(self.CONTENT_TIME_MATCHES, raw_time_string)[self.CONTENT_TIME_MATCHES_INDEX]
            except IndexError:  # if can't match time string, assign current time string to raw_time_string
                raw_time_string = DateTimeUtil.timeToStr(DateTimeUtil.now())
        time_string = DateTimeUtil.parseTimeStr(raw_time_string, self.CONTENT_TIME_FORMAT)

        # CONTENT
        content_element = doc(self.CONTENT_TEXT_CSS)
        if self.CONTENT_TEXT_REMOVE_CSS:
            content_element = content_element.clone()
            content_element.remove(self.CONTENT_TEXT_REMOVE_CSS)
        content_string = content_element.text()

        if self.CONTENT_TEXT_REPLACE_RE:
            content_string = self.replace_str(self.CONTENT_TEXT_REPLACE_RE, self.CONTENT_TEXT_REPLACE_STRING,
                                              content_string)

        # CRAWL TIME, generate with system time
        crawl_time = DateTimeUtil.timeToStr(DateTimeUtil.now())

        # URL SHA, generate with sha(url)
        url_sha = sha1(self.url.encode('utf-8'))

        # html field, generate with sha(title_string + content_string)
        html = sha1((title_string + '' + content_string).encode('utf-8'))

        # constructing a news data dict, and append to crawler_data.
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
        crawler_data.append_data(**data)

        # if CONTENT_TEXT_NEXT_PAGE_CSS is defined, fetch the next page url, construct an item job, and append to
        # crawler_data.
        if self.CONTENT_TEXT_NEXT_PAGE_CSS:
            content_next_page_url = doc(self.CONTENT_TEXT_NEXT_PAGE_CSS).attr('href')
            if self.CONTENT_TEXT_NEXT_PAGE_REPLACE_RE:
                content_next_page_url = self.replace_str(self.CONTENT_TEXT_NEXT_PAGE_REPLACE_RE,
                                                         self.CONTENT_TEXT_NEXT_PAGE_REPLACE_STRING,
                                                         content_next_page_url)
            content_next_page_item_data = {
                'sitename': self.sitename,
                'type': self.type,
                'url': content_next_page_url,
                'crawler_name': self.CRAWLER_NAME,
                'flag': 'item'
            }
            crawler_data.append_item_job(**content_next_page_item_data)

        # return data
        return crawler_data

    def terminate(self):
        pass

    @staticmethod
    def replace_str(re_pattern_list, re_replacement_list, origin_str):
        for pattern, repl in zip(re_pattern_list, re_replacement_list):
            origin_str = re.sub(pattern, repl, origin_str)
        return origin_str

    @staticmethod
    def matches_str(re_pattern, origin_str):
        return re.findall(re_pattern, origin_str)

def test():
    # remember to fill up these fields for testing.
    sitename = u'Juksy'
    news_type = u'專題'
    test_set = {
        'entry': {
            'url': 'https://www.juksy.com/channel/4',
            'sitename': sitename, 'type': news_type, 'flag': 'entry'
        },
        'item': {  # for normal item parse
                   'url': 'https://www.juksy.com/archives/67699',
                   'sitename': sitename, 'type': news_type, 'flag': 'item'
        }
    }
    cc = CrawlerClient(**test_set['item'])
    res = cc.crawl()
    print json.dumps(res.get_data(), ensure_ascii=False, indent=4)


if __name__ == '__main__':
    test()
