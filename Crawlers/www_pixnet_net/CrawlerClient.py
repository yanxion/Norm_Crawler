# -*- coding: utf-8 -*-

import sys
sys.path.append('../../')

from pyquery import PyQuery as pq
from datetime import datetime
import MySQLdb
from Crawlers.CrawlerBase.Crawler import Crawler
import re

from Util.CrawlerDataWrapper.CrawlerDataWrapper import CrawlerDataWrapper
from Util.TextUtil.SpecialCharUtil import remove_emoji
from Util.SQL_Connect.SQL_Connect import Get_Connect_ini

class CrawlerClient(Crawler):
    def __init__(self, **kwargs):
        self.crawler_data = CrawlerDataWrapper()
        super(CrawlerClient, self).__init__(**kwargs)
        self.CRAWLER_NAME = 'www_pixnet_net'
        self.SQL_Data = Get_Connect_ini()
        self.db = MySQLdb.connect(self.SQL_Data['Host'], self.SQL_Data['Account'], self.SQL_Data['Password'], self.SQL_Data['Database'], charset='utf8')
        self.cursor =  self.db.cursor()
        self.Insert_Meta = ("INSERT INTO blog_meta (domain, account, name, url) VALUES (%s, %s, %s, %s)")
        self.Insert_Content = ("INSERT INTO blog_content (domain,account,url,name,title,type,time,crawltime,content,author,url_sha) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,SHA(%s))")
        self.Select_Content_repeat = ("SELECT url_sha FROM blog_content where url_sha = SHA(%s)")
        self.Select_meta_repeat = ("SELECT url FROM blog_meta where url = (%s)")
        self.meta_flag = 0
    def crawl(self):

        if self.flag == 'entry':
            if (self.url.find('www.pixnet.net/blog/articles/category/')>1):
                # find next page, and append to job_list step 1.
                Web_url = self.url
                Page_num = self.url
                if Web_url.count('/') == 6:
                    Web_url += "/hot/"
                    Page_num = Web_url
                elif Web_url.count('/') == 7:
                    while (Web_url.count('/') > 6):
                        Web_url = Web_url[:len(Web_url) - 1]
                    Web_url += "/hot/"
            else:
                # find next page, and append to job_list step 1.
                Web_url =  self.url
                Page_num = self.url
                if Web_url.count('/') == 3:
                    Web_url += "/"
                    Page_num = Web_url
                elif Web_url.count('/') == 4:
                    while (Web_url.count('/') > 3):
                        Web_url = Web_url[:len(Web_url) - 1]
                    Web_url += "/"

            # find next page, and append to job_list step2 .
            while (Page_num.count('/') > 0):
                if Page_num.count('/') == 1:
                    Page_num = Page_num[Page_num.count('/'):]
                else:
                    Page_num = Page_num[Page_num.count('/') + 1:]

            if Page_num == "":
                Page_num = 1
            Page_num = int(Page_num) + 1

            if Page_num - 1 == 1:
                self.meta_flag = 1

            if (self.url.find('www.pixnet.net/blog/articles/category/') > 1):
                self.parse_rank(self.url)
            else:
                self.parse_author(self.url)


            # append entry
            Job_Data = {
                'sitename': self.sitename,
                'type': self.type,
                'url': Web_url + str(Page_num),
                'crawler_name': self.CRAWLER_NAME,
                'flag': 'entry'
            }
            print Job_Data
            if Page_num <= 11:
                print Page_num
                self.crawler_data.append_entry_job(**Job_Data)
                return self.crawler_data

        elif self.flag == 'item':
            self.parse_blog_meta(self.url)
            self.parse_blog_content(self.url)
        elif self.flag == 'content':
            self.parse_blog_content(self.url)

    def parse_rank(self,Web_url):
        url_Data = self.Blog_List_url_Crawler(Web_url)
        if not url_Data == []:
            Job_Data = {
                'sitename': self.sitename,
                'type': self.type,
                'url': 'http',
                'crawler_name': self.CRAWLER_NAME,
                'flag': 'item'
            }

            for i in url_Data:
                Job_Data['url'] = re.sub("\-.*", "",i)
                print Job_Data
                self.crawler_data.append_item_job(**Job_Data)


    def parse_author(self,Web_url):
        url_Data = self.Blog_Author_List_Crawler(Web_url)
        if not url_Data == []:
            Job_Data = {
                'sitename': self.sitename,
                'type': self.type,
                'url': 'http',
                'crawler_name': self.CRAWLER_NAME,
                'flag': 'item'
            }
            for i in url_Data:
                Job_Data['url'] = re.sub("\-.*", "",i)
                if self.meta_flag == 1:
                    self.meta_flag = 0
                    Job_Data['flag'] = 'item'
                else:
                    Job_Data['flag'] = 'content'
                print Job_Data

                self.crawler_data.append_item_job(**Job_Data)

    def parse_blog_content(self,Web_url):
        # Content
        print "Try Crawl Content " + Web_url + "... ",
        try:
            Data = self.Blog_Content_Crawler(Web_url)

            # Check Content Value Repeat.
            self.cursor.execute(self.Select_Content_repeat, [Data[2]])
            if self.cursor.fetchall():
                print "has value."
            else:
                try:
                    # Insert Content to DB.
                    self.cursor.execute(self.Insert_Content, Data)
                    self.db.commit()
                    print "done."
                except Exception as e:
                    print e
        except Exception as e:
            print e

    def parse_blog_meta(self,Web_url):
        # Meta
        print "Try Crawl Meta " + Web_url + "... ",
        try:
            Data = self.Blog_Meta_Crawler(Web_url)

            # Check Meta Value Repeat.
            self.cursor.execute(self.Select_meta_repeat, [Data[3]])
            if self.cursor.fetchall():
                print "has value."
            else:
                try:
                    # Insert Meta to DB.
                    self.cursor.execute(self.Insert_Meta, Data)
                    self.db.commit()
                    print "done."
                except Exception as e:
                    print e

        except Exception as e:
            print e

    def terminate(self):
        self.db.close()
        pass

    # Rank List Analysis.
    def Blog_List_url_Crawler(self,Web_url):
        url = []
        res = pq(Web_url, encoding="utf-8")

        if (Web_url[len(Web_url)-2:] == "/1"):
            Blog_List_Name = res('div.featured').find('h3').text()
            Blog_List_Url = res('div.featured').find('h3').find('a').attr('href')
            url.append(Blog_List_Url)
        for i in range(0, res('ol.article-list').find('li').length, +1):
            if (res('ol.article-list').find('li').eq(i).find('h3').text() == ""):
                print "!!!!"
                break
            Blog_List_Name = res('ol.article-list').find('li').eq(i).find('h3').text()
            Blog_List_Url = res('ol.article-list').find('li').eq(i).find('h3').find('a').attr('href')
            url.append(Blog_List_Url)
        return url

    # Author List Analysis.
    def Blog_Author_List_Crawler(self,Web_url):
        url = []
        res = pq(Web_url, encoding="utf-8")

        for i in range(0, res('div.article').find('li.title').find('a').length, +1):
            Data = res('div.article').find('li.title').find('h2').find('a').eq(i).attr('href')
            url.append(Data)
        return url

    # Blog Meta Analysis.
    def Blog_Meta_Crawler(self,Web_url):
        Data = []
        res = pq(Web_url, encoding="utf-8")

        Blog_Domain = Web_url[Web_url.find('//') + 2:Web_url.find('/', Web_url.find('//') + 2)][
                      Web_url[7:Web_url.find('/', Web_url.find('//') + 2)].find('.') + 1:]
        Blog_Account = Web_url[Web_url.find('//') + 2:Web_url.find('/', Web_url.find('//') + 2)][
                       :Web_url[7:Web_url.find('/', Web_url.find('//') + 2)].find('.')]
        Blog_Name = res('div#banner').find('a').eq(0).text()

        Blog_Url = Web_url[:Web_url.find('/', Web_url.find('//') + 2)] + "/blog/"

        Data.append(Blog_Domain)
        Data.append(Blog_Account)
        Data.append(remove_emoji(Blog_Name))
        Data.append(Blog_Url)
        return Data

    #Blog Content Analysis.
    def Blog_Content_Crawler(self,Web_url):
        Data = []
        res = pq(Web_url, encoding="utf-8")
        Blog_Domain = Web_url[Web_url.find('//') + 2:Web_url.find('/', Web_url.find('//') + 2)][
                      Web_url[7:Web_url.find('/', Web_url.find('//') + 2)].find('.') + 1:]

        Blog_Account = Web_url[Web_url.find('//') + 2:Web_url.find('/', Web_url.find('//') + 2)][
                       :Web_url[7:Web_url.find('/', Web_url.find('//') + 2)].find('.')]
        Blog_Url = Web_url

        Blog_Name = res('div#banner').find('a').eq(0).text()

        Blog_Title = res('li.title').find('h2').find('a').text()

        Blog_Type = res('ul.refer').find('li').eq(0).find('a').text()

        Blog_Time = datetime.strptime(
            res('li.publish').find('.year').text()[2:] + '-' + res('li.publish').find('.month').text() + '-' + res(
                'li.publish').find('.date').text() + ' ' + res('li.publish').find('.time').text(), "%y-%b-%d %H:%M")

        Blog_Crawler_Time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        Blog_Content = res('div.article-content-inner').find('p').text()

        Blog_Author = res('div.box-text').find('dl').find('dd').eq(0).text()
        if (Blog_Author == ""):
            Blog_Author = res('p.author').text()
            Blog_Author = Blog_Author[:Blog_Author.find(' ')]

        Data.append(Blog_Domain)
        Data.append(Blog_Account)
        Data.append(Blog_Url)
        Data.append(remove_emoji(Blog_Name))
        Data.append(remove_emoji(Blog_Title))
        Data.append(Blog_Type)
        Data.append(str(Blog_Time))
        Data.append(str(Blog_Crawler_Time))
        Data.append(remove_emoji(Blog_Content))
        Data.append(remove_emoji(Blog_Author))
        Data.append(Blog_Url)

        return Data


def test():
    sitename = u'Pixnet'
    Blog_type = u'職場甘苦'
    test_set = {
        'entry': {
            'url': 'https://www.pixnet.net/blog/articles/category/9/',
            # 'url': 'http://fc781117.pixnet.net/blog/',
            'sitename': sitename, 'type': Blog_type, 'flag': 'entry'
        },
        'item': {  # for normal item parse
            'url': 'http://tkbeasytest.pixnet.net/blog/post/4578536',
            'sitename': sitename, 'type': Blog_type, 'flag': 'item'
        }
    }
    cc = CrawlerClient(**test_set['item'])
    cc.crawl()
    #res = cc.crawl()
    #print json.dumps(res.get_data(), ensure_ascii=False, indent=4)

if __name__ == '__main__':
    test()
