# -*- coding: utf-8 -*-

import sys

sys.path.append('../../')

from pyquery import PyQuery as pq
from datetime import datetime
import MySQLdb
from Crawlers.CrawlerBase.Crawler import Crawler

from Util.CrawlerDataWrapper.CrawlerDataWrapper import CrawlerDataWrapper
from Util.TextUtil.SpecialCharUtil import remove_emoji

db = MySQLdb.connect("localhost", "user", "user", "blog_crawler", charset='utf8')
cursor = db.cursor()
Insert_Meta = ("INSERT INTO blog_meta (blog_domain, blog_account, blog_name, blog_url) VALUES (%s, %s, %s, %s)")
Insert_Content = ("INSERT INTO blog_content (`blog_domain`,`blog_account`,`blog_url`,`blog_name`,`blog_title`,`blog_type`,`blog_time`,`blog_crawltime`,`blog_content`,`blog_author`,`blog_url_sha` ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,SHA(%s))")
Select_Content_repeat = ("SELECT blog_url_sha FROM blog_content where blog_url_sha = SHA(%s)")
Select_meta_repeat = ("SELECT blog_url FROM blog_meta where blog_url = (%s)")
Insert_Job_List = ("INSERT INTO job_list(`sitename`,`type`,`url`,`crawler_name`,`host`,`flag`,`assign_time`,`url_sha`)VALUES (%s, %s, %s, %s, %s, %s, %s, SHA(%s));")

class CrawlerClient(Crawler):


    def __init__(self, **kwargs):
        super(CrawlerClient, self).__init__(**kwargs)
        self.CRAWLER_NAME = 'www_pixnet_net'
    def crawl(self):
        if self.flag == 'entry':

            if (self.url.find('www.pixnet.net/blog/articles/category/')>1):
                self.parse_rank(self.url)
            else:
                self.parse_author(self.url)
            return None

        elif self.flag == 'item':
            self.parse_blog_content(self.url)



    def parse_rank(self,Web_url):
        cnt = 0
        url_Data = []

        # Web url format.
        if Web_url.count('/') == 6:
            Web_url += "/hot/"
        elif Web_url.count('/') == 7:
            while (Web_url.count('/') > 6):
                Web_url = Web_url[:len(Web_url) - 1]
            Web_url += "/hot/"
        elif Web_url.count('/') == 8:
            while (1):
                if (Web_url[len(Web_url) - 1:] == '/'):
                    break
                else:
                    Web_url = Web_url[:len(Web_url) - 1]

        # crawl all blog url from rank list.
        while (1):
            cnt += 1
            print Web_url + str(cnt)
            url_Data = self.Blog_List_url_Crawler(Web_url + str(cnt))
            if url_Data == []:
                break
            else:
                try:
                    Job_Data = []
                    Job_Data.append(self.sitename)
                    Job_Data.append(self.type)
                    Job_Data.append('https')
                    Job_Data.append(self.CRAWLER_NAME)
                    Job_Data.append('localhost')
                    Job_Data.append('item')
                    Job_Data.append(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'))
                    Job_Data.append('https')

                    for i in url_Data:
                        Job_Data[2] = i
                        Job_Data[7] = i
                        cursor.execute(Insert_Job_List, Job_Data)
                        db.commit()
                except Exception as e:
                    print e


    def parse_author(self,Web_url):
        cnt = 0
        url_Data = []

        # Web url format.
        if Web_url.count('/') == 3:
            Web_url += "/"
        elif Web_url.count('/') == 4:
            while (Web_url.count('/') > 3):
                Web_url = Web_url[:len(Web_url) - 1]
            Web_url += "/"

        # crawl all blog url from Author Blog list.
        while (1):
            cnt += 1
            print Web_url + str(cnt)
            url_Data = self.Blog_Author_List_Crawler(Web_url + str(cnt))
            if url_Data == []:
                break
            else:
                try:
                    Job_Data = []
                    Job_Data.append(self.sitename)
                    Job_Data.append(self.type)
                    Job_Data.append('https')
                    Job_Data.append(self.CRAWLER_NAME)
                    Job_Data.append('localhost')
                    Job_Data.append('item')
                    Job_Data.append(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'))
                    Job_Data.append('https')

                    for i in url_Data:
                        Job_Data[2] = i
                        Job_Data[7] = i
                        cursor.execute(Insert_Job_List, Job_Data)
                        db.commit()
                except Exception as e:
                    print e


    def parse_blog_content(self,Web_url):
        # Meta
        print "Try Crawl Meta " + Web_url + "... ",
        try:
            Data = self.Blog_Meta_Crawler(Web_url)

            # Check Meta Value Repeat.
            cursor.execute(Select_meta_repeat, [Data[3]])
            if cursor.fetchall():
                print "has value."
            else:
                try:
                    # Insert Meta to DB.
                    cursor.execute(Insert_Meta, Data)
                    db.commit()
                    print "done."
                except Exception as e:
                    print e

        except Exception as e:
            print e

        # Content
        print "Try Crawl Content " + Web_url + "... ",
        try:
            Data = self.Blog_Content_Crawler(Web_url)

            # Check Content Value Repeat.
            cursor.execute(Select_Content_repeat, [Data[2]])
            if cursor.fetchall():
                print "has value."
            else:
                try:
                    # Insert Content to DB.
                    cursor.execute(Insert_Content, Data)
                    db.commit()
                    print "done."
                except Exception as e:
                    print e
        except Exception as e:
            print e

    def terminate(self):
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
            'sitename': sitename, 'type': Blog_type, 'flag': 'entry'
        },
        'item': {  # for normal item parse
            'url': 'http://fc781117.pixnet.net/blog/post/109026073-%E8%AD%A6%E5%A4%A7%E5%95%8F%E9%A1%8C%E9%9B%86--2016-02-22%E4%BF%AE%E6%94%B9',
            'sitename': sitename, 'type': Blog_type, 'flag': 'item'
        }
    }
    cc = CrawlerClient(**test_set['entry'])
    cc.crawl()
    #res = cc.crawl()
    #print json.dumps(res.get_data(), ensure_ascii=False, indent=4)

if __name__ == '__main__':
    test()