# -*- coding: utf-8 -*-
import base64
import codecs
import json
import random
import re
import urllib
import math
from Tkinter import Image
import requests
import time

class m_weibo_util():
    def __init__(self):
        self.headers = {
            'host': 'passport.weibo.cn',
            # 'Accept': '*/*',
            # 'Accept-Encoding': 'gzip, deflate, br',
            # 'Accept-Language': 'zh-TW,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.110 Safari/537.36',
            # 'Content - Type': 'application/x-www-form-urlencoded',
            # 'Referer': 'https://passport.weibo.cn/signin/login',
            # 'Content-Length': '151',
            "Upgrade-Insecure-Requests": "1",
            'Connection': 'Keep-alive',
            # 'Cookie': 'SCF=Avm3fUS9fSULufP-cUaSv8f_YuwTEtB_DncDdgZJ9HTU4C206LnLo5ytPeWqi0xA58qH5-BC2NorjTMpaf4tY2o.; SUB=_2AkMtXk8PdcPxrAVSnvsWy23qbY5H-jyeiyb5An7oJhMyPRgv7nxWqSfCB2WmvLFnjri4ntESFsrUBcLnrA..; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9W5WXbRZKMGDEEi8D0Z9XzwV5JpX5KMhUgL.Foq0Soe0S0qReKe2dJLoIpjLxK-LBo5L12qLxKnLBoeL1hUiC-.Eeh2Neh2t; SUHB=0Ryq9SdbQYIRot; _T_WM=d802345462b7c0ed23df0267b7550396; M_WEIBOCN_PARAMS=featurecode%3D20000320%26luicode%3D10000011%26lfid%3D102803_ctg1_8999_-_ctg1_8999_home%26fid%3D102803_ctg1_8999_-_ctg1_8999_home%26uicode%3D10000011; H5_INDEX=3; H5_INDEX_TITLE=%E5%B0%8F%E8%B3%87III201701; H5:PWA:UID=1'
        }
        self.session = requests.Session()
        self.index_url = 'https://passport.weibo.cn/signin/login'

    def login(self, username, password):
        self.session.get(self.index_url, headers=self.headers)

        pincode = self.login_pre(username)
        print pincode
        postdata = {
            "username": username,
            "password": password,
            "savestate": "1",
            "ec": "0",
            "pagerefer": "",
            "entry": "mweibo",
            "wentry": "",
            "loginfrom": "",
            "client_id": "",
            "code": "",
            "qq": "",
            "hff": "",
            "hfp": "",
        }
        if not pincode:
            pass
        else:
            postdata["pincode"] = pincode[0]
            postdata["pcid"] = pincode[1]

        self.headers["Host"] = "passport.weibo.cn"
        self.headers["Reference"] = self.index_url
        self.headers["Origin"] = "https://passport.weibo.cn"
        self.headers["Content-Type"] = "application/x-www-form-urlencoded"

        post_url = "https://passport.weibo.cn/sso/login"
        login = self.session.post(post_url, data=postdata, headers=self.headers)
        js = json.loads(login.text)

        if js['msg'] == u'用户名或密码错误':
            return js['msg']
        uid = js["data"]["uid"]
        crossdomain = js["data"]["crossdomainlist"]
        cn = crossdomain["sina.com.cn"]  # "https:" + crossdomain["sina.com.cn"]
        # 下面两个对应不同的登录 weibo.com 还是 m.weibo.cn
        # 一定要注意更改 Host
        # mcn = "https:" + crossdomain["weibo.cn"]
        # com = "https:" + crossdomain['weibo.com']
        self.headers["Host"] = "login.sina.com.cn"
        self.session.get(cn, headers=self.headers)
        self.headers["Host"] = "weibo.cn"
        ht = self.session.get("http://weibo.cn/%s/info" % uid, headers=self.headers)
        # print(ht.url)
        return self.session.cookies
        # pa = r'<title>(.*?)</title>'
        # res = re.findall(pa, ht.text)
        # print res[0]

    def login_pre(self, username):
        params = {
            "checkpin": "1",
            "entry": "mweibo",
            "su": self.get_su(username),
            "callback": "jsonpcallback" + str(int(time.time() * 1000) + math.floor(random.random() * 100000))
        }
        pre_url = "https://login.sina.com.cn/sso/prelogin.php"
        self.headers["Host"] = "login.sina.com.cn"
        self.headers["Referer"] = self.index_url
        pre = self.session.get(pre_url, params=params, headers=self.headers)
        # pa = r'\((.*?)\)'
        # res = re.findall(pa, pre.text)
        # if res == []:
        #     print "好像哪里不对了哦，请检查下你的网络，或者你的账号输入是否正常"
        # else:
        js = json.loads(pre.text)
        if js["showpin"] == 1:
            self.headers["Host"] = "passport.weibo.cn"
            capt = self.session.get("https://passport.weibo.cn/captcha/image", headers=self.headers)
            capt_json = capt.json()
            capt_base64 = capt_json['data']['image'].split("base64,")[1]
            with open('capt.jpg', 'wb') as f:
                f.write(base64.b64decode(capt_base64))
                f.close()
            im = Image.open("capt.jpg")
            im.show()
            im.close()
            cha_code = input("请输入验证码\n>")
            return cha_code, capt_json['data']['pcid']
        else:
            return ""


    def get_su(self, username):
        username_quote = urllib.quote_plus(username)
        username_base64 = base64.b64encode(username_quote.encode('utf-8'))
        return username_base64.decode('utf-8')

    def get_headers(self):
        headers_user_agent = [
            "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko",
            "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.276 Safari/537.36"
        ]

        m_headers = {
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
        return m_headers

    def get_cookies(self, username, password):
        jdata = {}
        try:
            f = codecs.open("m_config.txt", "r", "utf-8")
            jdata = json.loads(f.read().replace('\r\n', ''))
        except Exception as e:
            m_cookies = self.login(username, password)
            jdata['m_cookies'] = requests.utils.dict_from_cookiejar(m_cookies)
            f = codecs.open("m_config.txt", "w", "utf-8")
            f.write(json.dumps(jdata))
            f.close()
        return jdata['m_cookies']






if __name__ == '__main__':
    m_login = m_weibo_util()
    print m_login.login('username', 'password')
