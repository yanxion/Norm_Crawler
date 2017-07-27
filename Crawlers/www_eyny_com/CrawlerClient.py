# -*- coding: utf-8 -*-
import sys
import urlparse
sys.path.append('../../')
from pyquery import PyQuery
from Util.HashUtil.Sha import sha1
from Crawlers.CrawlerBase.Crawler import Crawler
from Util.CrawlerDataWrapper.CrawlerDataWrapper import CrawlerDataWrapper
from Util.DateTimeUtil import DateTimeUtil
import re


class CrawlerClient(Crawler):
    def __init__(self, **kwargs):
        self.crawler_data = CrawlerDataWrapper()
        super(CrawlerClient, self).__init__(**kwargs)
        self.CRAWLER_NAME = ''
        self.ENTRY_REQUESTS_TYPE = 'GET'

# Entry.
    # Item link.
        self.ENTRY_LINK_CSS = '.xst'
        self.ENTRY_LINK_ATTR = 'href'
        self.ENTRY_LINK_REMOVE_CSS = 'script'
        self.ENTRY_LINK_REPLACE_RE = []
        self.ENTRY_LINK_REPLACE_STRING = []
    # next page url.
        self.ENTRY_NEXTPAGE_CSS = '.nxt'
        self.ENTRY_NEXTPAGE_ATTR = 'href'
        self.ENTRY_NEXTPAGE_REMOVE_CSS = ''
        self.ENTRY_NEXTPAGE_REPLACE_RE = []
        self.ENTRY_NEXTPAGE_REPLACE_STRING = []

# ITEM
    # next page
        # self.ITEM_NEXTPAGE_CSS = u'div.pagination a:contains(下一頁)'
        self.ITEM_NEXTPAGE_CSS = '.nxt'
        self.ITEM_NEXTPAGE_ATTR = 'href'
        self.ITEM_NEXTPAGE_REMOVE_CSS = 'script'
        self.ITEM_NEXTPAGE_REPLACE_RE = []
        self.ITEM_NEXTPAGE_REPLACE_STRING = []

# POST
    # post setting
        # POST_EQ = '' 代表主文跟回文CSS格式不一樣 | POST_EQ = '數字' ,主文的所在位置 第一層為0，第二層為1
        self.POST_EQ = '0'
    # post title
        self.POST_TITLE_CSS = '#thread_subject'
        self.POST_TITLE_ATTR = ''
        self.POST_TITLE_REMOVE_CSS = 'script'
        self.POST_TITLE_REPLACE_RE = []
        self.POST_TITLE_REPLACE_STRING = []
    # post author
        self.POST_AUTHOR_CSS = '.authi .xw1'
        self.POST_AUTHOR_ATTR = ''
        self.POST_AUTHOR_REMOVE_CSS = 'script'
        self.POST_AUTHOR_REPLACE_RE = []
        self.POST_AUTHOR_REPLACE_STRING = []
    # post content
        self.POST_CONTENT_CSS = '.t_f'
        self.POST_CONTENT_ATTR = ''
        self.POST_CONTENT_REMOVE_CSS = 'div'
        self.POST_CONTENT_REPLACE_RE = []
        self.POST_CONTENT_REPLACE_STRING = []
    # post time
        self.POST_TIME_CSS = '.authi em'
        self.POST_TIME_ATTR = 'title'
        self.POST_TIME_REMOVE_CSS = 'script'
        self.POST_TIME_REPLACE_RE = ['[^0-9-:A-Z]']
        self.POST_TIME_REPLACE_STRING = ['']
        self.POST_TIME_FORMAT = u'%Y-%m-%d%I:%M%p'.encode('utf-8')
        # %Y: year in n digits
        # %y: year in 2 digits, [00, 99]
        # %m: month, [01, 12]
        # %d: day, [01,31]
        # %H: hour in 24H mode, [00, 23]
        # %I: hour in 12H mode, [01, 12]
        # %p: AM/PM
        # %M: minute, [00, 59]
        # %S: second, [00, 61]
        # must encoded in utf-8, DO NOT REMOVE THE ENCODING!

# COMMENT
        # comment setting
        self.COMMENT_EQ_DOCUMENT = 'div.pl div[id^="post_"] table[id^=pid]'
    # comment author
        self.COMMENT_AUTHOR_CSS = '.authi .xw1'
        self.COMMENT_AUTHOR_ATTR = ''
        self.COMMENT_AUTHOR_REMOVE_CSS = 'script'
        self.COMMENT_AUTHOR_REPLACE_RE = []
        self.COMMENT_AUTHOR_REPLACE_STRING = []
    # comment content
        self.COMMENT_CONTENT_CSS = '.t_f'
        self.COMMENT_CONTENT_ATTR = ''
        self.COMMENT_CONTENT_REMOVE_CSS = 'div'
        self.COMMENT_CONTENT_REPLACE_RE = []
        self.COMMENT_CONTENT_REPLACE_STRING = []
    # comment floor
        self.COMMENT_FLOOR_CSS = 'div.pi a[id^="postnum"] '
        self.COMMENT_FLOOR_ATTR = ''
        self.COMMENT_FLOOR_REMOVE_CSS = 'script'
        self.COMMENT_FLOOR_REPLACE_RE = []
        self.COMMENT_FLOOR_REPLACE_STRING = []
    # comment time
        self.COMMENT_TIME_CSS = '.authi em'
        self.COMMENT_TIME_ATTR = 'title'
        self.COMMENT_TIME_REMOVE_CSS = 'script'
        self.COMMENT_TIME_REPLACE_RE = ['[^0-9-:A-Z]']
        self.COMMENT_TIME_REPLACE_STRING = ['']
        self.COMMENT_TIME_FORMAT = u'%Y-%m-%d%I:%M%p'.encode('utf-8')
        # %Y: year in n digits
        # %y: year in 2 digits, [00, 99]
        # %m: month, [01, 12]
        # %d: day, [01,31]
        # %H: hour in 24H mode, [00, 23]
        # %I: hour in 12H mode, [01, 12]
        # %p: AM/PM
        # %M: minute, [00, 59]
        # %S: second, [00, 61]
        # must encoded in utf-8, DO NOT REMOVE THE ENCODING!





    def crawl(self):
        if self.flag == 'entry':
            self.crawl_entry()
        elif self.flag == 'item':
            self.crawl_item()
        return self.crawler_data

    def crawl_entry(self):
        res = PyQuery(self.url, encoding="utf-8")
        for i in range(res(self.ENTRY_LINK_CSS).length):
            item_data = self.parse_item_link(res(self.ENTRY_LINK_CSS).eq(i))
            self.crawler_data.append_item_job(**item_data)
        entry_data = self.parse_next_entry_link(res('html'))
        self.crawler_data.append_entry_job(**entry_data)

    def parse_item_link(self, link_str):
        url_parse = urlparse.urlparse(self.url)
        if self.ENTRY_LINK_ATTR:
            url = link_str.attr(self.ENTRY_LINK_ATTR)
        else:
            url = link_str.text()
        item_url = urlparse.urljoin(url_parse.scheme + "://" + url_parse.netloc, url)
        item_data = {
            'sitename': self.sitename,
            'type': self.type,
            'url': item_url,
            'crawler_name': self.CRAWLER_NAME,
            'flag': 'item'
        }
        return item_data

    def parse_next_entry_link(self, html_script):
        res = PyQuery(html_script)
        url_parse = urlparse.urlparse(self.url)
        if self.ENTRY_NEXTPAGE_ATTR:
            next_page = res(self.ENTRY_NEXTPAGE_CSS).attr(self.ENTRY_NEXTPAGE_ATTR)
        else:
            next_page = res(self.ENTRY_NEXTPAGE_CSS)
        if next_page:
            next_page_url = urlparse.urljoin(url_parse.scheme + "://" + url_parse.netloc, next_page)
            entry_data = {
                'sitename': self.sitename,
                'type': self.type,
                'url': next_page_url,
                'crawler_name': self.CRAWLER_NAME,
                'flag': 'entry'
            }
            return entry_data

    def crawl_item(self):
        web_url = self.url
        while True:
            res = PyQuery(web_url, encoding="utf-8")
            url_parse = urlparse.urlparse(self.url)

            for i in range(res(self.COMMENT_CONTENT_CSS).length):
                if self.url == web_url and i == int(self.POST_EQ):
                    post_data = self.parse_post()
                    print post_data
                    print "-------------------------------------------"
                else:
                    comment_data = self.parse_comment(res(self.COMMENT_EQ_DOCUMENT).eq(i), web_url)
                    print comment_data
                    self.crawler_data.append_data(**comment_data)
                    print "-------------------------------------------"

            if self.ITEM_NEXTPAGE_ATTR:
                next_page = res(self.ITEM_NEXTPAGE_CSS).attr(self.ITEM_NEXTPAGE_ATTR)
            else:
                next_page = res(self.ITEM_NEXTPAGE_CSS)

            if next_page:
                next_page_url = urlparse.urljoin(url_parse.scheme+"://"+url_parse.netloc, next_page)
                web_url = next_page_url
            else:
                post_data['comment_count'] = comment_data['floor']
                self.crawler_data.append_data(**post_data)
                print "NO Next page"
                break

    def parse_post(self):
        res = PyQuery(self.url, encoding="utf-8")
        # res = PyQuery(html_script)

        key_url_string = self.url
        key_url_sha_string = sha1(self.url)
        comment_count_string = ''
        sitename_string = self.sitename
        type_string = self.type
        crawltime_string = DateTimeUtil.timeToStr(DateTimeUtil.now())

    # title
        title_element = res(self.POST_TITLE_CSS)
        if self.POST_TITLE_REMOVE_CSS:
            title_element = title_element.clone()
            title_element.remove(self.POST_TITLE_REMOVE_CSS)
        if self.POST_TITLE_ATTR:
            title_string = title_element.attr(self.POST_TITLE_ATTR)
        else:
            title_string = title_element.text()
        if self.POST_TITLE_REPLACE_RE:
            title_string = self.replace_str(self.POST_TITLE_REPLACE_RE, self.POST_TITLE_REPLACE_STRING, title_string)

    # author
        author_element = res(self.POST_AUTHOR_CSS)
        if self.POST_AUTHOR_REMOVE_CSS:
            author_element = author_element.clone()
            author_element.remove(self.POST_AUTHOR_REMOVE_CSS)
        if self.POST_EQ:
            author_element = author_element.eq(int(self.POST_EQ))
        if self.POST_AUTHOR_ATTR:
            author_string = author_element.attr(self.POST_AUTHOR_ATTR)
        else:
            author_string = author_element.text()

        if self.POST_AUTHOR_REPLACE_RE:
            author_string = self.replace_str(self.POST_AUTHOR_REPLACE_RE, self.POST_AUTHOR_REPLACE_STRING,
                                             author_string)

    # content
        content_element = res(self.POST_CONTENT_CSS)
        if self.POST_CONTENT_REMOVE_CSS:
            content_element = content_element.clone()
            content_element.remove(self.POST_CONTENT_REMOVE_CSS)
        if self.POST_EQ:
            content_element = content_element.eq(int(self.POST_EQ))
        if self.COMMENT_CONTENT_ATTR:
            content_string = content_element.attr(self.COMMENT_CONTENT_ATTR)
        else:
            content_string = content_element.text()
        if self.POST_CONTENT_REPLACE_RE:
            content_string = self.replace_str(self.POST_CONTENT_REPLACE_RE, self.POST_CONTENT_REPLACE_STRING,
                                              content_string)

    # time
        time_element = res(self.POST_TIME_CSS)
        if self.POST_TIME_REMOVE_CSS:
            time_element = time_element.clone()
            time_element.remove(self.POST_TIME_REMOVE_CSS)
        if self.POST_EQ:
            time_string = time_element.eq(int(self.POST_EQ))
        time_string = self.time_format(time_string)
        # if self.POST_TIME_ATTR:
        #     time_string = time_string.attr(self.POST_TIME_ATTR)
        # else:
        #     time_string = time_string.text()
        if self.POST_TIME_REPLACE_RE:
            time_string = self.replace_str(self.POST_TIME_REPLACE_RE, self.POST_TIME_REPLACE_STRING, time_string)
        time_string = DateTimeUtil.parseTimeStr(time_string, self.POST_TIME_FORMAT)
        post_data = {
            "key_url": key_url_string,
            "key_url_sha": key_url_sha_string,
            "author": author_string,
            "title": title_string,
            "content": content_string,
            "comment_count": comment_count_string,
            "sitename": sitename_string,
            "type": type_string,
            "time": time_string,
            "crawltime": crawltime_string,
        }
        return post_data

    def parse_comment(self, html_script, Web_url):
        res = PyQuery(html_script)
        key_url_string = self.url
        key_url_sha_string = sha1(self.url)
        url_string = Web_url
        url_sha_string = sha1(Web_url)
        sitename_string = self.sitename
        type_string = self.type
        crawltime_string = DateTimeUtil.timeToStr(DateTimeUtil.now())

    # author
        author_element = res(self.COMMENT_AUTHOR_CSS)
        if self.COMMENT_AUTHOR_REMOVE_CSS:
            author_element = author_element.clone()
            author_element.remove(self.COMMENT_AUTHOR_REMOVE_CSS)
        if self.COMMENT_AUTHOR_ATTR:
            author_string = author_element.attr(self.COMMENT_AUTHOR_ATTR)
        else:
            author_string = author_element.text()
        if self.COMMENT_AUTHOR_REPLACE_RE:
            author_string = self.replace_str(self.COMMENT_AUTHOR_REPLACE_RE, self.COMMENT_AUTHOR_REPLACE_STRING,
                                             author_string)
    # content
        content_element = res(self.COMMENT_CONTENT_CSS)
        if self.COMMENT_CONTENT_REMOVE_CSS:
            content_element = content_element.clone()
            content_element.remove(self.COMMENT_CONTENT_REMOVE_CSS)
        if self.COMMENT_CONTENT_ATTR:
            content_string = content_element.attr(self.COMMENT_CONTENT_ATTR)
        else:
            content_string = content_element.text()
        if self.COMMENT_CONTENT_REPLACE_RE:
            content_string = self.replace_str(self.COMMENT_CONTENT_REPLACE_RE, self.COMMENT_CONTENT_REPLACE_STRING,
                                              content_string)
    # floor
        floor_element = res(self.COMMENT_FLOOR_CSS)
        if self.COMMENT_FLOOR_REMOVE_CSS:
            floor_element = floor_element.clone()
            floor_element.remove(self.COMMENT_FLOOR_REMOVE_CSS)
        if self.COMMENT_FLOOR_ATTR:
            floor_string = floor_element.attr(self.COMMENT_FLOOR_ATTR)
        else:
            floor_string = floor_element.text()
        if self.COMMENT_FLOOR_REPLACE_RE:
            floor_string = self.replace_str(self.COMMENT_FLOOR_REPLACE_RE, self.COMMENT_FLOOR_REPLACE_STRING,
                                            floor_string)
        floor_string = self.comment_floor_format(floor_string)


    # time
        time_element = res(self.COMMENT_TIME_CSS)
        if self.COMMENT_TIME_REMOVE_CSS:
            time_element = time_element.clone()
            time_element.remove(self.COMMENT_TIME_REMOVE_CSS)
        time_string = self.time_format(time_element)
        # if self.COMMENT_TIME_ATTR:
        #     time_string = time_element.attr(self.COMMENT_TIME_ATTR)
        # else:
        #     time_string = time_element.text()
        if self.COMMENT_TIME_REPLACE_RE:
            time_string = self.replace_str(self.COMMENT_TIME_REPLACE_RE, self.COMMENT_TIME_REPLACE_STRING,
                                           time_string)
        time_string = DateTimeUtil.parseTimeStr(time_string, self.POST_TIME_FORMAT)

        comment_data = {
            'key_url': key_url_string,
            'key_url_sha': key_url_sha_string,
            'url': url_string,
            'url_sha': url_sha_string,
            'author': author_string,
            'content': content_string,
            'floor': floor_string,
            'sitename': sitename_string,
            'type': type_string,
            'time': time_string,
            'crawltime': crawltime_string,
        }

        return comment_data

    def comment_floor_format(self, floor_str):
        if floor_str == u'頭香':
            return 2
        else:
            return re.sub('[^0-9]\s*', '', floor_str)

    def time_format(self, time_str):
        res = PyQuery(time_str)
        if res('span'):
            if self.POST_TIME_ATTR:
                return res('span').attr(self.POST_TIME_ATTR)
        else:
            return time_str.text()

    def terminate(self):
        pass

    def replace_str(self, re_pattern_list, re_replacement_list, origin_str):
        for pattern, repl in zip(re_pattern_list, re_replacement_list):
            origin_str = re.sub(pattern, repl, origin_str)
        return origin_str


if __name__ == '__main__':
    sitename = u'eyny'
    news_type = u'eyny'
    test_set = {
        'entry': {
            'url': 'http://www01.eyny.com/forum.php?mod=forumdisplay&fid=27&page=EY2Y69P2',
            'sitename': sitename, 'type': news_type, 'flag': 'entry'
        },
        'item': {  # for normal item parse
            'url': 'http://www01.eyny.com/thread-11256716-1-EY2Y69P2.html',
            'sitename': sitename, 'type': news_type, 'flag': 'item'
        }
    }
    a = CrawlerClient(**test_set['entry'])
    a.crawl()
    pass
