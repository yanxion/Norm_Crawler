# -*- coding: utf-8 -*-
import random
import sys
import requests
from pyquery.pyquery import PyQuery

sys.path.append('../../')
import json
from Util.CrawlerDataWrapper.CrawlerDataWrapper import CrawlerDataWrapper
from Crawlers.CrawlerBase.Crawler import Crawler
from Util.Crawler_Proxy_Util.Crawler_Proxy_Util import Crawler_Proxy_Util


class CrawlerClient(Crawler):
    def __init__(self, **kwargs):
        super(CrawlerClient, self).__init__(**kwargs)
        self.crawler_data = CrawlerDataWrapper()
        self.proxy_util = Crawler_Proxy_Util()
        self.CRAWLER_NAME = 'm_weibo_cn'
        self.user_info = {}
        self.post_data = {}
        # self.cookies = {
        #     "_T_WM": "7b39c21741fd225fcc27fa88c6442315",
        #     "H5_INDEX": "0_all",
        #     "H5_INDEX_TITLE": "%E5%B0%8F%E8%B3%87III201701",
        #     "ALF": "1507692634",
        #     "SUB": "_2A250s95EDeRhGeBN7VES9yjEyj-IHXVUX-IMrDV6PUJbktBeLUjukW2AcyX87lz7b0B-20tRnd2_EKii0A..",
        #     "SUBP": "0033WrSXqPxfM725Ws9jqgMF55529P9D9W5WXbRZKMGDEEi8D0Z9XzwV5JpX5o2p5NHD95Qce0q0e0Mc1h20Ws4Dqcjdi--fi-z7iKysi--Ri-z0iKnNC-Lieo5pS05p",
        #     "SUHB": "0P1Md7z03PZieU",
        #     "SSOLoginState": "1505100635",
        #     "M_WEIBOCN_PARAMS": "featurecode%3D20000320%26oid%3D4148510829702265%26luicode%3D10000011%26lfid%3D1005052431578944"
        # }

        self.m_cookies = {
            "Cookies": "_T_WM=7b39c21741fd225fcc27fa88c6442315; H5_INDEX=0_all; H5_INDEX_TITLE=%E5%B0%8F%E8%B3%87III201701; ALF=1508395407; SUB=_2A250xMzADeRhGeBN7VES9yjEyj-IHXVURtSIrDV6PUJbktBeLUTukW1ZOkXhvdZb19-PGGT9tvhlNRAydQ..; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9W5WXbRZKMGDEEi8D0Z9XzwV5JpX5o2p5NHD95Qce0q0e0Mc1h20Ws4Dqcjdi--fi-z7iKysi--Ri-z0iKnNC-Lieo5pS05p; SUHB=0u5R9XSEmEqxH2; SSOLoginState=1505803408; M_WEIBOCN_PARAMS=luicode%3D10000011%26lfid%3D1005051055539122%26fid%3D1005051055539122%26uicode%3D10000011"
        }

        self.w_cookies = {
            "Cookies": "_s_tentry=bookshadow.com; Apache=7826666980981.827.1499927382935; SINAGLOBAL=7826666980981.827.1499927382935; ULV=1499927382955:1:1:1:7826666980981.827.1499927382935:; TC-Page-G0=cdcf495cbaea129529aa606e7629fea7; TC-V5-G0=c427b4f7dad4c026ba2b0431d93d839e; __gads=ID=7b3c17eab87a77f2:T=1504750777:S=ALNI_MZKE9frs0WAGan0xHEOwk9fKkSY7w; UM_distinctid=15e5a22bce438b-0a9aad5ed-44490e20-1fa400-15e5a22bce56ad; YF-V5-G0=69afb7c26160eb8b724e8855d7b705c6; crtg_rta=; YF-Ugrow-G0=8751d9166f7676afdce9885c6d31cd61; _ga=GA1.2.1456780803.1502090981; appkey=; SSOLoginState=1504838367; YF-Page-G0=2d32d406b6cb1e7730e4e69afbffc88c; TC-Ugrow-G0=370f21725a3b0b57d0baaf8dd6f16a18; UOR=bookshadow.com,widget.weibo.com,www.facebook.com; wvr=6; WBtopGlobal_register_version=8ebe9c2598f18a02; SUB=_2A250xMzfDeRhGeBN7VES9yjEyj-IHXVXs7kXrDV8PUJbmtBeLW-nkW9iOPZVvjsjAZFAjrZavWWVC42blw..; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9W5WXbRZKMGDEEi8D0Z9XzwV5JpX5o2p5NHD95Qce0q0e0Mc1h20Ws4Dqcjdi--fi-z7iKysi--Ri-z0iKnNC-Lieo5pS05p; SUHB=0jBIRIP6XcZiOF; ALF=1536374365; wb_cusLike_6363376813=Y"
        }

        headers_user_agent = [
            "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko",
            "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.276 Safari/537.36"
        ]

        self.m_headers = {
            "Accept": "text / html, application / xhtml + xml, application / xml;q = 0.9, image / webp, * / *;q = 0.8",
            "Accept - Encoding": "gzip, deflate, sdch",
            "Accept - Language": "zh - TW, zh;q = 0.8, en - US;q = 0.6, en;q = 0.4",
            "Cache - Control": "no - cache",
            "Connection": "keep - alive",
            "Host": "m.weibo.cn",
            "Pragma": "no - cache",
            "Upgrade - Insecure - Requests": "1",
            "User - Agent": headers_user_agent[random.randint(0, len(headers_user_agent) - 1)],
        }

        self.w_headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept - Encoding": "gzip, deflate, sdch",
            "Accept - Language": "zh-TW,zh;q=0.8,en-US;q=0.6,en;q=0.4",
            "Cache - Control": "no - cache",
            "Connection": "keep - alive",
            "Host": "www.weibo.com",
            "Pragma": "no - cache",
            "Upgrade - Insecure - Requests": "1",
            "User - Agent": headers_user_agent[random.randint(0, len(headers_user_agent) - 1)],
        }

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

        uid = "1055539122"
        self.get_m_userinfo(uid)
        self.get_m_all_weibo_post(uid, self.user_info['weibo_id'])

        print "profile : ", self.user_info['profile_id']
        print "weibo_id : ", self.user_info['weibo_id']

        # print "id : ", self.user_info['id']
        # print "screen_name : ", self.user_info['screen_name']
        # print "gender : ", self.user_info['gender']
        # print "location : ", self.user_info['location']
        # print "educationinfo : ", self.user_info['educationinfo']
        # print "companyinfo : ", self.user_info['companyinfo']
        # print "description : ", self.user_info['description']
        # print "tags : ", self.user_info['tags']
        # print "followers_count : ", self.user_info['followers_count']
        # print "follow_count : ", self.user_info['follow_count']
        # print "statuses_count : ", self.user_info['statuses_count']
        # print "verified : ", self.user_info['verified']
        # print "verified_reason : ", self.user_info['verified_reason']
        # print "profile_img_url : ", self.user_info['profile_img_url']
        # print "createdate : ", self.user_info['createdate']

    def get_m_userinfo(self, uid):
        url = 'https://m.weibo.cn/api/container/getIndex?type=uid&value=%s' % (uid)
        print url
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
        url = 'https://m.weibo.cn/api/container/getIndex?type=uid&value=%s&containerid=%s&page=%s' % (uid, weibo_id, 1)
        r = requests.get(url, headers=self.m_headers, cookies=self.m_cookies)
        jdata = json.loads(str(r.text))

        print jdata['cards'][0]['mblog']['id']

        self.get_m_user_post(jdata['cards'][0]['mblog']['id'])
        exit()

    def get_m_user_post(self, post_id):
        url = 'https://m.weibo.cn/statuses/extend?id=%s' % post_id
        r = requests.get(url, headers=self.m_headers, cookies=self.m_cookies)
        jdata = json.loads(str(r.text))
        res = PyQuery(jdata['longTextContent'])
        self.post_data['content'] = res.text()

    def get_m_cardlistinfo(self, uid, profile_id):
        url = 'https://m.weibo.cn/api/container/getIndex?containerid=%s_-_INFO&' \
              'luicode=10000011&lfid=%s&featurecode=20000320&type=uid&value=%s' % (profile_id, profile_id, uid)
        print url
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
        url = 'https://www.weibo.com/p/%s/info?mod=pedit_more' % oid
        r = requests.get(url, headers=self.w_headers, cookies=self.w_cookies)
        res = PyQuery(r.text)
        profile_jdata = '{}'
        for i in range(res('script').length):
            if res('script').eq(i).text().find('"domid":"Pl_Official_PersonalInfo__58"') >= 0:
                profile_data = res('script').eq(i).text()
                profile_jdata = json.loads(profile_data.replace('FM.view(', '')[:-1])

        res = PyQuery(profile_jdata['html'])
        self.user_info['companyinfo'] = res('div.PCD_text_b2').eq(1).find('ul.clearfix span.pt_detail').text()
        self.user_info['educationinfo'] = res('div.PCD_text_b2').eq(2).find('ul.clearfix span.pt_detail').text()
        self.user_info['tags'] = res('div.PCD_text_b2').eq(3).find('ul.clearfix span.pt_detail').text()

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
