# -*- coding: utf-8 -*-
import random
import sys
import requests
from pyquery.pyquery import PyQuery

sys.path.append('../../')
import json
import base64
import binascii
import requests
import re
import urllib
from Util.CrawlerDataWrapper.CrawlerDataWrapper import CrawlerDataWrapper
from Crawlers.CrawlerBase.Crawler import Crawler
from Util.Crawler_Proxy_Util.Crawler_Proxy_Util import Crawler_Proxy_Util
import w_weibo_util
import m_weibo_util
# from Crawlers.test import test

class CrawlerClient(Crawler):
    def __init__(self, **kwargs):
        super(CrawlerClient, self).__init__(**kwargs)
        self.crawler_data = CrawlerDataWrapper()
        # self.proxy_util = Crawler_Proxy_Util()
        self.CRAWLER_NAME = 'weibo'
        self.user_info = {}
        self.post_data = {}
        self.m_util = m_weibo_util.m_weibo_util()
        self.m_cookies = self.m_util.get_cookies('username', 'password')
        # self.m_cookies = {
        #     "Cookies": "H5_INDEX=0_all; H5_INDEX_TITLE=%E5%B0%8F%E8%B3%87III201701; _T_WM=291f6d6d18abb60a9957b34ac52c1d48; H5:PWA:UID=1; ALF=1512629751; SCF=AljwARrW8XODcbjTChFdgLZIgkXpxse4oI6mfhOEh9BKd9WGkxpi-u8a5eHXgUMBa0NFXoSCHnBAoKMFWDb9MF4.; SUB=_2A253BSq6DeRhGeBN7VES9yjEyj-IHXVUCbbyrDV6PUJbktBeLUb_kW2bzbbJa6JTaoSq5YgTwMMp2x3jDw..; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9W5WXbRZKMGDEEi8D0Z9XzwV5JpX5K-hUgL.Foq0Soe0S0qReKe2dJLoIpjLxK-LBo5L12qLxKnLBoeL1hUiC-.Eeh2Neh2t; SUHB=0qj0iLsEK7Ti_d; SSOLoginState=1510038250; M_WEIBOCN_PARAMS=featurecode%3D20000320%26luicode%3D10000011%26lfid%3D1076032431578944%26fid%3D1076032431578944%26uicode%3D10000011"
        # }

        self.w_util = w_weibo_util.w_weibo_util()
        self.w_cookies = self.w_util.get_cookies('username', 'password')
        # self.w_cookies = {
        #     "Cookies": "_s_tentry=bookshadow.com; Apache=7826666980981.827.1499927382935; SINAGLOBAL=7826666980981.827.1499927382935; ULV=1499927382955:1:1:1:7826666980981.827.1499927382935:; TC-Page-G0=cdcf495cbaea129529aa606e7629fea7; TC-V5-G0=c427b4f7dad4c026ba2b0431d93d839e; __gads=ID=7b3c17eab87a77f2:T=1504750777:S=ALNI_MZKE9frs0WAGan0xHEOwk9fKkSY7w; UM_distinctid=15e5a22bce438b-0a9aad5ed-44490e20-1fa400-15e5a22bce56ad; YF-V5-G0=69afb7c26160eb8b724e8855d7b705c6; YF-Ugrow-G0=8751d9166f7676afdce9885c6d31cd61; appkey=; YF-Page-G0=2d32d406b6cb1e7730e4e69afbffc88c; TC-Ugrow-G0=370f21725a3b0b57d0baaf8dd6f16a18; WBtopGlobal_register_version=8ebe9c2598f18a02; httpsupgrade_ab=SSL; UOR=bookshadow.com,widget.weibo.com,www.google.com.tw; wb_cusLike_6363376813=N; _ga=GA1.2.1456780803.1502090981; _gid=GA1.2.757132637.1510037719; SCF=AljwARrW8XODcbjTChFdgLZIgkXpxse4oI6mfhOEh9BK3s-GU1ATjmQPZ3f9aMKkZq2pDzyY0kktamFt3aaHKPA.; SUB=_2A253BSioDeRhGeBN7VES9yjEyj-IHXVUcx1grDV8PUNbmtBeLRP9kW9c2RjrGgDmYs09Y4TZxl7ONUeXbQ..; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9W5WXbRZKMGDEEi8D0Z9XzwV5JpX5K2hUgL.Foq0Soe0S0qReKe2dJLoIpjLxK-LBo5L12qLxKnLBoeL1hUiC-.Eeh2Neh2t; SUHB=0nlu7bMvgpFy1O; ALF=225458837751; SSOLoginState=1510037752"
        # }
        self.m_headers = self.m_util.get_headers()
        self.w_headers = self.w_util.get_headers()

    def crawl(self):
        if self.flag == 'entry':
            self.crawl_entry()
        elif self.flag == 'item':
            self.crawl_item()
        return self.crawler_data

    def crawl_entry(self):
        pass

    def crawl_item(self):
        # headers = self.proxy_util.get_random_headers()
        # res = requests.get(self.url, cookies=self.cookies, headers=headers)
        self.user_info['id'] = ''
        self.user_info['screen_name'] = ''
        self.user_info['gender'] = ''
        self.user_info['location'] = ''
        self.user_info['educationinfo'] = ''
        self.user_info['companyinfo'] = ''
        self.user_info['description'] = ''
        self.user_info['tags'] = ''
        self.user_info['followers_count'] = ''
        self.user_info['follow_count'] = ''
        self.user_info['statuses_count'] = ''
        self.user_info['verified'] = ''
        self.user_info['verified_reason'] = ''
        self.user_info['profile_img_url'] = ''

        uid = "6363376811"
        self.get_m_userinfo(uid)
        # self.get_m_all_weibo_post(uid, self.user_info['weibo_id'])
        print "profile : ", self.user_info['profile_id']
        print "weibo_id : ", self.user_info['weibo_id']

        print "id : ", self.user_info['id']
        print "screen_name : ", self.user_info['screen_name']
        print "gender : ", self.user_info['gender']
        print "location : ", self.user_info['location']
        print "educationinfo : ", self.user_info['educationinfo']
        print "companyinfo : ", self.user_info['companyinfo']
        print "description : ", self.user_info['description']
        print "tags : ", self.user_info['tags']
        print "followers_count : ", self.user_info['followers_count']
        print "follow_count : ", self.user_info['follow_count']
        print "statuses_count : ", self.user_info['statuses_count']
        print "verified : ", self.user_info['verified']
        print "verified_reason : ", self.user_info['verified_reason']
        print "profile_img_url : ", self.user_info['profile_img_url']
        print "createdate : ", self.user_info['createdate']

    def get_m_userinfo(self, uid):
        """
            get user info from mobile.
            set value in self.user_info dict.
        :param uid:
        :return: profile_id, weibo_id
        """
        url = 'https://m.weibo.cn/api/container/getIndex?type=uid&value=%s' % (uid)
        print '-----', url
        res = requests.get(url, cookies=self.m_cookies, headers=self.m_headers)
        jdata = json.loads(str(res.text))
        self.user_info['profile_id'] = jdata['tabsInfo']['tabs'][0]['containerid']
        self.user_info['weibo_id'] = jdata['tabsInfo']['tabs'][1]['containerid']

        self.user_info['id'] = jdata['userInfo']['id']
        self.user_info['screen_name'] = jdata['userInfo']['screen_name']
        if jdata['userInfo']['gender'] == 'm':
            self.user_info['gender'] = 1
        elif jdata['userInfo']['gender'] == 'f':
            self.user_info['gender'] = 0
        self.user_info['description'] = jdata['userInfo']['description']
        self.user_info['followers_count'] = jdata['userInfo']['followers_count']
        self.user_info['follow_count'] = jdata['userInfo']['follow_count']
        self.user_info['statuses_count'] = jdata['userInfo']['statuses_count']
        if jdata['userInfo']['verified']:
            self.user_info['verified'] = '1'
            self.user_info['verified_reason'] = jdata['userInfo']['verified_reason']
        else:
            self.user_info['verified'] = '0'
            self.user_info['verified_reason'] = ''
        self.user_info['profile_img_url'] = jdata['userInfo']['profile_image_url']
        self.user_info['oid'] = jdata['userInfo']['toolbar_menus'][0]['actionlog']['oid']

        # other info crawler
        self.get_w_userinfo(self.user_info['oid'])
        self.get_m_cardlistinfo(uid, self.user_info['profile_id'])
        return self.user_info['profile_id'], self.user_info['weibo_id']

    def get_m_all_weibo_post(self, uid, weibo_id):
        """
            get uid's all post from mobile.
        :param uid:
        :param weibo_id:
        :return:
        """

        cnt = 0
        while True:
            cnt += 1
            url = 'https://m.weibo.cn/api/container/getIndex?type=uid&value=%s&containerid=%s&page=%s' % (
            uid, weibo_id, cnt)
            r = requests.get(url, headers=self.m_headers, cookies=self.m_cookies)
            jdata = json.loads(str(r.text))
            if jdata['ok'] == 1:
                print '-----', url
                for i in range(len(jdata['cards'])):
                    if 'mblog' in jdata['cards'][i]:
                        self.get_w_user_post(uid, bid=jdata['cards'][i]['mblog']['bid'],
                    source=jdata['cards'][i]['mblog']['source'], id=jdata['cards'][i]['mblog']['id'])
                        print "--------------------------------------------------------"
                break   # ----------------------------------------------------------
            else:
                break
        print 'break'
        exit()
        # self.get_m_user_post(jdata['cards'][0]['mblog']['id'])

    def get_m_user_post(self, post_id):
        """
            get user post
        :param post_id:
        :return:
        """
        url = 'https://m.weibo.cn/statuses/extend?id=%s' % post_id
        r = requests.get(url, headers=self.m_headers, cookies=self.m_cookies)
        jdata = json.loads(str(r.text))
        res = PyQuery(jdata['longTextContent'])
        self.post_data['content'] = res.text()

    def get_w_user_post(self, uid, bid, source, id):
        """
            get user
        :param uid:
        :param bid:
        :param source:
        :param id:
        :return:
        """
        url = 'https://www.weibo.com/' + uid + '/' + bid
        r = requests.get(url, headers=self.w_headers, cookies=self.w_cookies)
        res = PyQuery(r.text)
        post_jdata = '{}'
        for i in range(res('script').length):
            if res('script').eq(i).text().find('"domid":"Pl_Official_WeiboDetail__74"') >= 0:
                post_data = res('script').eq(i).text()
                post_jdata = json.loads(post_data.replace('FM.view(', '')[:-1])
        res = PyQuery(post_jdata['html'])

        content = res('.WB_text').text()
        publish_date = res('div.WB_from a:eq(0)').attr('title')
        if res('div.WB_feed_handle span.line').eq(1).find('em:eq(1)').text() == u'转发':
            forware_count = 0
        else:
            forware_count = res('div.WB_feed_handle span.line').eq(1).find('em:eq(1)').text()

        if res('div.WB_feed_handle span.line').eq(2).find('em:eq(1)').text() == u'评论':
            comment_count = 0
        else:
            comment_count = res('div.WB_feed_handle span.line').eq(2).find('em:eq(1)').text()

        if res('div.WB_feed_handle span.line').eq(3).find('em:eq(1)').text() == u'赞':
            parise_count = 0
        else:
            parise_count = res('div.WB_feed_handle span.line').eq(3).find('em:eq(1)').text()


        print url
        print id
        print 'content : ', content
        print 'publish_date : ', publish_date
        print 'forware_count : ', forware_count
        print 'comment_count : ', comment_count
        print 'parise_count : ', parise_count
        print 'userid : ', self.user_info['id'], self.user_info['screen_name']
        print 'source : ', source




    def get_m_cardlistinfo(self, uid, profile_id):
        """
            get card list info from mobile.
        :param uid:
        :param profile_id:
        :return:
        """
        url = 'https://m.weibo.cn/api/container/getIndex?containerid=%s_-_INFO&' \
              'luicode=10000011&lfid=%s&featurecode=20000320&type=uid&value=%s' % (profile_id, profile_id, uid)
        print '-----', url
        r = requests.get(url, cookies=self.m_cookies, headers=self.m_headers)
        jdata = json.loads(str(r.text))

        for cards_row in jdata['cards']:
            # print cards_row['card_group']
            for cards_data in cards_row['card_group']:
                if 'item_name' in cards_data:
                    # if cards_data['item_name'] == u'标签':
                    #     self.user_info['tags'] = cards_data['item_content']
                    if cards_data['item_name'] == u'所在地':
                        self.user_info['location'] = cards_data['item_content']
                        # if cards_data['item_name'] == u'公司':
                        # self.user_info['companyinfo'] = cards_data['item_content']
                        # if cards_data['item_name'] == u'学校':
                        # self.user_info['educationinfo'] = cards_data['item_content']
                    if cards_data['item_name'] == u'注册时间':
                        self.user_info['createdate'] = cards_data['item_content']
                        # friendCount == follow_cnt?
                        # VerifiedType

    def get_w_userinfo(self, oid):
        """
            get userinfo from web.
        :param oid:
        :return:
        """
        url = 'https://www.weibo.com/p/%s/info?mod=pedit_more' % oid
        r = requests.get(url, headers=self.w_headers, cookies=self.w_cookies)
        res = PyQuery(r.text)

        if res.text() == 'File not found.':
            raise 'web cookie error'
        profile_jdata = '{}'
        for i in range(res('script').length):
            if res('script').eq(i).text().find('"domid":"Pl_Official_PersonalInfo__58"') >= 0:
                profile_data = res('script').eq(i).text()
                profile_jdata = json.loads(profile_data.replace('FM.view(', '')[:-1])
        # print profile_jdata['html']
        res = PyQuery(profile_jdata['html'])
        for i in range(res('div.PCD_text_b2').length):
            title = res('div.PCD_text_b2').eq(i).find('div.obj_name').text()
            if title == u'工作信息':
                self.user_info['companyinfo'] = res('div.PCD_text_b2').eq(i).find('ul.clearfix span.pt_detail').text()
            elif title == u'教育信息':
                self.user_info['educationinfo'] = res('div.PCD_te xt_b2').eq(i).find('ul.clearfix span.pt_detail').text()
            elif title == u'标签信息':
                self.user_info['tags'] = res('div.PCD_text_b2').eq(i).find('ul.clearfix span.pt_detail').text()


    def terminate(self):
        # self.forum_mysql.db_close()
        pass


if __name__ == '__main__':
    sitename = 'weibo'
    news_type = 'weibo'
    test_set = {
        'entry': {
            'url': 'https://m.weibo.cn/u/2431578944?uid=1686546714&luicode=20000174&featurecode=20000320&sudaref=m.weibo.cn',
            'sitename': sitename, 'type': news_type, 'flag': 'entry', 'context': '{}'
        },
        'item': {  # for normal item parse
            'url': 'https://m.weibo.cn/api/container/getIndex?uid=1686546714&luicode=20000174&featurecode=20000320&sudaref=m.weibo.cn&type=uid&value=2431578944&containerid=1076032431578944',
            'sitename': sitename, 'type': news_type, 'flag': 'item', 'context': '{}'
        }
    }
    a = CrawlerClient(**test_set['item'])
    a.crawl()
