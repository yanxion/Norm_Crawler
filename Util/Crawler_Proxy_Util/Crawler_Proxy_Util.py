# -*- coding: utf-8 -*-
import sys

sys.path.append('../../')
from pyquery import PyQuery
import os
import re
import requests
import json
import random
from Util.SQL_Connect.SQL_Connect import SQL_Connect


class Crawler_Proxy_Util:
    def __init__(self):
        self.localhost_ip = self.get_localhost_ip()
        print "localhost ip : ", self.localhost_ip
        self.db = SQL_Connect()
        self.db.connect_mysql(os.path.join(os.path.dirname(__file__), "config.ini"))
        # proxy setting initial
        self.proxy_method = ''
        self.proxy_ip = ''
        self.proxy_port = ''
        self.proxy_account = ''
        self.proxy_passwd = ''

    def set_proxy(self, method, ip, port, account='', passwd=''):
        self.proxy_method = method
        self.proxy_ip = ip
        self.proxy_port = port
        self.proxy_account = account
        self.proxy_passwd = passwd

    def get_proxy_method(self):
        return self.proxy_method

    def get_random_headers(self):
        headers_user_agent = [
            # "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko",
            # "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36",
            # "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.276 Safari/537.36"
        ]
        headers = {
            # "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            # "Accept-Encoding": "gzip, deflate, sdch",
            # "Accept-Language": "zh-TW,zh;q=0.8,en-US;q=0.6,en;q=0.4",
            "User-Agent": headers_user_agent[random.randint(0, len(headers_user_agent) - 1)],
        }
        return headers

    def get_random_proxy(self, use_set_proxy=False):
        while_cnt = 0
        if use_set_proxy:
            if self.proxy_account and self.proxy_passwd:
                proxies = {
                    "http": self.proxy_method + "://" + self.proxy_account + ':' + self.proxy_passwd + '@' + self.proxy_ip + ":" + self.proxy_port,
                    "https": self.proxy_method + "://" + self.proxy_account + ':' + self.proxy_passwd + '@' + self.proxy_ip + ":" + self.proxy_port
                }
            else:
                proxies = {
                    "http": self.proxy_method + "://" + self.proxy_ip + ":" + self.proxy_port,
                    "https": self.proxy_method + "://" + self.proxy_ip + ":" + self.proxy_port
                }
            return proxies
        else:
            while while_cnt <= 5:
                while_cnt += 1
                proxy_data = self.db.select_sql(
                    "SELECT method, ip, port, account, passwd FROM proxy ORDER BY RAND() LIMIT 1 ;")
                print proxy_data[1],
                if proxy_data[3] and proxy_data[4]:
                    proxies = {
                        "http": proxy_data[0] + "://" + proxy_data[3] + ':' + proxy_data[4] + '@' + proxy_data[
                            1] + ":" + proxy_data[2],
                        "https": proxy_data[0] + "://" + proxy_data[3] + ':' + proxy_data[4] + '@' + proxy_data[
                            1] + ":" + proxy_data[2]
                    }
                else:
                    proxies = {
                        "http": proxy_data[0] + "://" + proxy_data[1] + ":" + proxy_data[2],
                        "https": proxy_data[0] + "://" + proxy_data[1] + ":" + proxy_data[2]
                    }
                if self.is_proxy_available(proxies):
                    return proxies
                else:
                    pass
                    self.db.insert_sql("DELETE FROM proxy WHERE ip = '" + proxy_data[1] + "'")
        return False

    def proxy_requests(self, url, encoding='utf-8', use_set_proxy=False):
        proxies = self.get_random_proxy(use_set_proxy=use_set_proxy)
        headers = self.get_random_headers()
        try:
            r = requests.get(url, headers=headers, proxies=proxies, timeout=10)
            r.encoding = encoding
            return r.text
        except Exception as e:
            return e

    def is_proxy_available(self, proxies):
        try:
            res = requests.get("http://httpbin.org/ip", proxies=proxies, timeout=10)
            res.encoding = 'utf-8'
            # print res.text
            if res.text:
                jdata = json.loads(res.text)
                split_jdata = jdata['origin'].split(',')
                for ip in split_jdata:
                    show_ip = re.sub('[^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}]', '', ip)
                    if show_ip != self.localhost_ip and show_ip and len(split_jdata) == 1:
                        print show_ip.ljust(15), "...Success!"
                        return True
                    else:
                        print "ip compare".ljust(15), "...Faild!"
                        break
            else:
                print "res.text null".ljust(15), "...Faild!"
        except Exception as e:
            print e[0][0:15], "...Faild!"
        return False

    # def proxy_ip_cralwer(self, method, pnum=0):
    #     r = requests.get("http://www.xroxy.com/proxylist.php?port=&type=All_http&ssl=ssl&country=&latency="\
    #                      "&reliability=&sort=reliability&desc=true&pnum=" + str(pnum) + "#table")
    #     res = PyQuery(r.text)
    #     for i in range(res('tr[class^="row"]').size()):
    #         res2 = PyQuery(res('tr[class^="row"]').eq(i))
    #         for j in range(res2('a').size()):
    #             if j == 1:
    #                 ip = res2('a').eq(j).text()
    #             elif j == 2:
    #                 port = res2('a').eq(j).text()
    #
    #         time.sleep(1)
    #         self.set_proxy(method, ip, port)
    #         print method, '_', (ip + ":" + port).ljust(20), "...",
    #         if self.is_proxy_available(self.get_random_proxy(use_set_proxy=True)):
    #             self.db.insert_sql("INSERT INTO proxy(method, ip, port, account, passwd)" \
    #                                " VALUE('%s','%s','%s','%s','%s') ON DUPLICATE KEY UPDATE port = '%s'," \
    #                                " account = '%s',passwd = '%s', method = '%s' ;"
    #                                % (self.proxy_method, self.proxy_ip, self.proxy_port,
    #                                   self.proxy_account,  self.proxy_passwd, self.proxy_port,
    #                                   self.proxy_account, self.proxy_passwd, self.proxy_method))

    def get_localhost_ip(self):
        r = requests.get("http://httpbin.org/ip")
        return r.json()['origin']

    def terminate(self):
        self.db.db_close()


if __name__ == '__main__':
    a = Crawler_Proxy_Util()

    # print a.is_proxy_available(a.get_random_proxy())
    # print a.proxy_requests("http://httpbin.org/headers")

    # a.http_header()
    a.terminate()
