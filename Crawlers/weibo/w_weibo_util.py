# -*- coding: utf-8 -*-
import base64
import binascii
import codecs
import json
import random

import requests
import re
import urllib
import rsa


class w_weibo_util():
    def __init__(self):
        self.login_url = 'http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.19)'
        self.prelogin_url = r'https://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&su=&rsakt=mod&client=ssologin.js(v1.4.15)'  # noqa
        self.headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, sdch",
            "Accept-Language": "zh-TW,zh;q=0.8,en-US;q=0.6,en;q=0.4",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.276 Safari/537.36"
        }

    def login(self, username, password):
        pubkey, servertime, nonce, rsakv = self.prelogin(self.prelogin_url)
        post_data = self.postdata(username, password, pubkey, servertime, nonce, rsakv)
        session = requests.Session()
        response = session.post(self.login_url, params=post_data, headers=self.headers)
        text = response.content.decode('gbk')
        pa = re.compile(r'location\.replace\(\'(.*?)\'\)')
        redirect_url = pa.search(text).group(1)
        response = session.get(redirect_url, headers=self.headers)

        return session.cookies

    def prelogin(self, prelogin_url):
        data = requests.get(prelogin_url).content.decode('utf-8')
        p = re.compile('\((.*)\)')
        data_str = p.search(data).group(1)
        server_data_dict = eval(data_str)
        pubkey = server_data_dict['pubkey']
        servertime = server_data_dict['servertime']
        nonce = server_data_dict['nonce']
        rsakv = server_data_dict['rsakv']
        return pubkey, servertime, nonce, rsakv

    def rsa_encoder(self, username, password, pubkey, servertime, nonce):
        su_url = urllib.quote_plus(username)
        su_encoded = su_url.encode('utf-8')
        su = base64.b64encode(su_encoded)
        su = su.decode('utf-8')
        rsaPublickey = int(pubkey, 16)
        e = int('10001', 16)
        key = rsa.PublicKey(rsaPublickey, e)
        message = str(servertime) + '\t' + str(nonce) + '\n' + str(password)
        password = rsa.encrypt(message.encode('utf-8'), key)
        sp = binascii.b2a_hex(password)
        return su, sp

    def postdata(self, username, password, pubkey, servertime, nonce, rsakv):
        su, sp = self.rsa_encoder(username, password, pubkey, servertime, nonce)
        post_data = {
            'encoding': 'UTF-8',
            'entry': 'weibo',
            'from': '',
            'gateway': '1',
            'nonce': nonce,
            'pagerefer': '',
            'prelt': '645',
            'pwencode': 'rsa2',
            'returntype': 'META',
            'rsakv': rsakv,
            'savestate': '7',
            'servertime': str(servertime),
            'service': 'miniblog',
            'sp': sp,
            'sr': '1920*1080',
            'su': su,
            'url': 'http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack',
            # noqa
            'useticket': '1',
            'vsnf': '1',
        }
        return post_data

    def get_headers(self):
        headers_user_agent = [
            "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko",
            "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.276 Safari/537.36"
        ]

        w_headers = {
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
        return w_headers

    def get_cookies(self, username, password):
        jdata = {}
        try:
            f = codecs.open("w_config.txt", "r", "utf-8")
            jdata = json.loads(f.read().replace('\r\n', ''))
        except Exception as e:
            w_cookies = self.login(username, password)
            jdata['w_cookies'] = requests.utils.dict_from_cookiejar(w_cookies)
            f = codecs.open("w_config.txt", "w", "utf-8")
            f.write(json.dumps(jdata))
            f.close()
        return jdata['w_cookies']



if __name__ == '__main__':
    w_login = w_weibo_util()

    print w_login.login('username', 'password')

