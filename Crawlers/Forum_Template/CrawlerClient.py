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

        self.START_CRAWL_PAGE = 1
        self.END_CRAWL_PAGE = 3
        self.ENTRY_REQUESTS_TYPE = 'GET'

# Entry.
    # list link.
        self.ENTRY = {}
        self.add_two_dimension(self.ENTRY, 'LINK', 'CSS', '123')
        self.add_two_dimension(self.ENTRY, 'LINK', 'REPLACE_RE', [])
        self.add_two_dimension(self.ENTRY, 'LINK', 'REPLACE_STRING', [])

    # next page url.
        self.add_two_dimension(self.ENTRY, 'NEXT_PAGE', 'CSS', '123')
        self.add_two_dimension(self.ENTRY, 'NEXT_PAGE', 'REPLACE_RE', '456')
        self.add_two_dimension(self.ENTRY, 'NEXT_PAGE', 'REPLACE_STRING', '789')

# Item
    # post title
        self.POST_TITLE_CSS = '#thread_subject'
        self.POST_TITLE_REMOVE_CSS = 'script'
        self.POST_TITLE_REPLACE_RE = []
        self.POST_TITLE_REPLACE_STRING = []
    # post author
        self.POST_AUTHOR_CSS = '.authi .xw1'
        # POST_*_EQ = '' or POST_*_EQ = '數字' ,主文的所在位置 第一層為0，第二層為1
        self.POST_AUTHOR_EQ = '0'
        self.POST_AUTHOR_REMOVE_CSS = 'script'
        self.POST_AUTHOR_REPLACE_RE = []
        self.POST_AUTHOR_REPLACE_STRING = []
    # post content
        self.POST_CONTENT_CSS = '.t_f'
        # POST_*_EQ = '' or POST_*_EQ = '數字' ,主文的所在位置 第一層為0，第二層為1
        self.POST_CONTENT_EQ = '0'
        self.POST_CONTENT_REMOVE_CSS = 'div'
        self.POST_CONTENT_REPLACE_RE = []
        self.POST_CONTENT_REPLACE_STRING = []
    # post time
        self.POST_TIME_CSS = '.authi em'
        # POST_*_EQ = '' or POST_*_EQ = '數字' ,主文的所在位置 第一層為0，第二層為1
        self.POST_TIME_EQ = '0'
        self.POST_TIME_REMOVE_CSS = 'script'
        self.POST_TIME_REPLACE_RE = ['[^0-9-:A-Z]']
        self.POST_TIME_REPLACE_STRING = ['']
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
        self.POST_TIME_FORMAT = u'%Y-%m-%d%I:%M%p'.encode('utf-8')

    # comment author
        self.COMMENT_AUTHOR_CSS = '.authi .xw1'
        # COMMENT_*_EQ = '' or COMMENT_*_EQ = '數字' ,主文的所在位置 第一層為0，第二層為1
        self.COMMENT_AUTHOR_EQ = '0'
        self.COMMENT_AUTHOR_REMOVE_CSS = 'script'
        self.COMMENT_AUTHOR_REPLACE_RE = []
        self.COMMENT_AUTHOR_REPLACE_STRING = []
    # comment content
        self.COMMENT_CONTENT_CSS = '.t_f'
        # COMMENT_*_EQ = '' or COMMENT_*_EQ = '數字' ,主文的所在位置 第一層為0，第二層為1
        self.COMMENT_CONTENT_EQ = '0'
        self.COMMENT_CONTENT_REMOVE_CSS = 'div'
        self.COMMENT_CONTENT_REPLACE_RE = []
        self.COMMENT_CONTENT_REPLACE_STRING = []
    # comment floor
        self.COMMENT_FLOOR_CSS = 'div.pi a[id^="postnum"] '
        # COMMENT_*_EQ = '' or COMMENT_*_EQ = '數字' ,主文的所在位置第一層為0，第二層為1
        self.COMMENT_FLOOR_EQ = '0'
        self.COMMENT_FLOOR_REMOVE_CSS = 'script'
        self.COMMENT_FLOOR_REPLACE_RE = []
        self.COMMENT_FLOOR_REPLACE_STRING = []
    # comment time
        self.COMMENT_TIME_CSS = '.authi em'
        # COMMENT_*_EQ = '' or COMMENT_*_EQ = '數字' ,主文的所在位置 第一層為0，第二層為1
        self.COMMENT_TIME_EQ = '0'
        self.COMMENT_TIME_REMOVE_CSS = 'script'
        self.COMMENT_TIME_REPLACE_RE = ['[^0-9-:A-Z]']
        self.COMMENT_TIME_REPLACE_STRING = ['']
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
        self.COMMENT_TIME_FORMAT = u'%Y-%m-%d%I:%M%p'.encode('utf-8')

    # next page
        # self.ITEM_NEXTPAGE_CSS = u'div.pagination a:contains(下一頁)'
        self.ITEM_NEXTPAGE_CSS = '.nxt'
        self.ITEM_NEXTPAGE_REMOVE_CSS = 'script'
        self.ITEM_NEXTPAGE_REPLACE_RE = []
        self.ITEM_NEXTPAGE_REPLACE_STRING = []



    def crawl(self):
        if self.flag == 'entry':
            self.crawl_entry()
        elif self.flag == 'item':
            self.crawl_item()
        return self.crawler_data

    def crawl_entry(self):

        pass

    def crawl_item(self):
        post_data = self.parse_post()
        # for i in post_data:
        #     print i, ":", post_data[i]

        # comment_data = self.parse_comment()
        # print comment_data
        Web_url = self.url
        while True:
            res = PyQuery(Web_url, encoding="utf-8")
            url_parse = urlparse.urlparse(self.url)

            for i in range(res(self.COMMENT_CONTENT_CSS).length):
                if not (self.url == Web_url and i == int(self.COMMENT_CONTENT_EQ)):
                    comment_data = self.parse_comment(Web_url, i)

                    for j in comment_data:
                        print j, ":", comment_data[j]
                        self.crawler_data.append_data(**comment_data[j])
                    print "-------------------------------------------"

            if res(self.ITEM_NEXTPAGE_CSS).attr('href'):
                Next_Page_url = urlparse.urljoin(url_parse.scheme+"://"+url_parse.netloc, res(self.ITEM_NEXTPAGE_CSS)
                                                 .attr('href'))
                print Next_Page_url
                Web_url = Next_Page_url
            else:
                print "NO Next page"
                break
            print "-------------------------------------------"

    def parse_post(self):
        res = PyQuery(self.url, encoding="utf-8")

        key_url_string = self.url
        key_url_sha_string = sha1(self.url)
        comment_count_string = ''
        sitename_string = self.sitename
        type_string = self.type
        crawltime_string = DateTimeUtil.timeToStr(DateTimeUtil.now())

    # author
        author_element = res(self.POST_AUTHOR_CSS)
        if self.POST_AUTHOR_REMOVE_CSS:
            author_element = author_element.clone()
            author_element.remove(self.POST_AUTHOR_REMOVE_CSS)
        if self.POST_AUTHOR_EQ:
            author_string = author_element.eq(int(self.POST_AUTHOR_EQ)).text()
        else:
            author_string = author_element.text()
        if self.POST_AUTHOR_REPLACE_RE:
            author_string = self.replace_str(self.POST_AUTHOR_REPLACE_RE, self.POST_AUTHOR_REPLACE_STRING,
                                             author_string)

    # title
        title_element = res(self.POST_TITLE_CSS)
        if self.POST_TITLE_REMOVE_CSS:
            title_element = title_element.clone()
            title_element.remove(self.POST_TITLE_REMOVE_CSS)
        title_string = title_element.text()
        if self.POST_TITLE_REPLACE_RE:
            title_string = self.replace_str(self.POST_TITLE_REPLACE_RE, self.POST_TITLE_REPLACE_STRING, title_string)

    # content
        content_element = res(self.POST_CONTENT_CSS)
        if self.POST_CONTENT_REMOVE_CSS:
            content_element = content_element.clone()
            content_element.remove(self.POST_CONTENT_REMOVE_CSS)
        if self.POST_CONTENT_EQ:
            content_string = content_element.eq(int(self.POST_CONTENT_EQ)).text()
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
        if self.POST_TIME_EQ:
            time_string = time_element.eq(int(self.POST_TIME_EQ)).text()
        else:
            time_string = time_element.text()
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

    def parse_comment(self, Web_url, eq):
        res = PyQuery(Web_url, encoding="utf-8")

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
        author_string = author_element.eq(int(eq)).text()
        if self.COMMENT_AUTHOR_REPLACE_RE:
            author_string = self.replace_str(self.COMMENT_AUTHOR_REPLACE_RE, self.COMMENT_AUTHOR_REPLACE_STRING,
                                             author_string)
    # content
        content_element = res(self.COMMENT_CONTENT_CSS)
        if self.COMMENT_CONTENT_REMOVE_CSS:
            content_element = content_element.clone()
            content_element.remove(self.COMMENT_CONTENT_REMOVE_CSS)
        content_string = content_element.eq(int(eq)).text()
        if self.COMMENT_CONTENT_REPLACE_RE:
            content_string = self.replace_str(self.COMMENT_CONTENT_REPLACE_RE, self.COMMENT_CONTENT_REPLACE_STRING,
                                              content_string)
    # floor
        floor_element = res(self.COMMENT_FLOOR_CSS)
        if self.COMMENT_FLOOR_REMOVE_CSS:
            floor_element = floor_element.clone()
            floor_element.remove(self.COMMENT_FLOOR_REMOVE_CSS)
        floor_string = floor_element.eq(int(eq)).text()
        if self.COMMENT_FLOOR_REPLACE_RE:
            floor_string = self.replace_str(self.COMMENT_FLOOR_REPLACE_RE, self.COMMENT_FLOOR_REPLACE_STRING,
                                            floor_string)
        floor_string = self.comment_floor_format(floor_string)

    # time
        time_element = res(self.COMMENT_TIME_CSS)
        if self.COMMENT_TIME_REMOVE_CSS:
            time_element = time_element.clone()
            time_element.remove(self.COMMENT_TIME_REMOVE_CSS)
        time_string = time_element.eq(int(eq)).text()
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

    def terminate(self):
        pass

    def add_two_dimension(self, dict, key_a, key_b, val):
        if key_a in dict:
            dict[key_a].update({key_b: val})
        else:
            dict.update({key_a: {key_b: val}})

    def replace_str(self, re_pattern_list, re_replacement_list, origin_str):
        for pattern, repl in zip(re_pattern_list, re_replacement_list):
            origin_str = re.sub(pattern, repl, origin_str)
        return origin_str


if __name__ == '__main__':
    sitename = u'eyny'
    news_type = u'eyny'
    test_set = {
        'entry': {
            # 'url': 'https://www.mobile01.com/topicdetail.php?f=291&t=5217848&p=1',
            'url': 'http://www01.eyny.com/thread-11256716-1-EY2Y69P2.html',
            'sitename': sitename, 'type': news_type, 'flag': 'entry'
        },
        'item': {  # for normal item parse
            'url': 'http://www01.eyny.com/thread-11256716-1-EY2Y69P2.html',
            'sitename': sitename, 'type': news_type, 'flag': 'item'
        }
    }
    a = CrawlerClient(**test_set['item'])
    a.crawl()
    pass
