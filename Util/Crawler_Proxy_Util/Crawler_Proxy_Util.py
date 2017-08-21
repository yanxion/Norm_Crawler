# -*- coding: utf-8 -*-
import json
import sys
sys.path.append('../../')
from pyquery import PyQuery
import re
import requests
import time
from Util.SQL_Connect.SQL_Connect import SQL_Connect


class Crawler_Proxy_Util:
    def __init__(self):
        self.localhost_ip = self.get_localhost_ip()
        print "localhost ip : ", self.localhost_ip
        self.db = SQL_Connect()
        self.db.connect_mysql()
        # proxy setting
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

    def http_proxy(self, url, encode='utf-8'):
        proxies = {
            "http": self.proxy_method + "://" + self.proxy_ip + ":" + self.proxy_port + "",
            "https": self.proxy_method + "://" + self.proxy_ip + ":" + self.proxy_port + ""
        }
        try:
            r = requests.get(url, proxies=proxies, timeout=10)
            r.encoding = encode
            return r.text
        except Exception as e:
            print e
            return None

    def compare_ip(self, url, encode='utf-8'):

        print self.proxy_method, '_', (self.proxy_ip+":"+self.proxy_port).ljust(20), "...",
        res = self.http_proxy(url, encode)
        if res:
            # show_ip = res('font').text()
            # show_ip_re = re.match('^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', show_ip)
            try:
                jdata = json.loads(res)
                # print jdata['origin']
                split_jdata = jdata['origin'].split(',')
                for ip in split_jdata:
                    show_ip = re.match('^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', ip)
                    if show_ip.group() != self.localhost_ip:
                        print "show_ip : ", show_ip.group().ljust(15), "...Success!"
                        return 1
            except:
                print "show_ip : ", ''.ljust(15), "...Faild!"
        return None


    def crawler_proxy(self, pnum=0):
        r = requests.get("http://www.xroxy.com/proxylist.php?port=&type=All_http&ssl=ssl&country=&latency="\
                         "&reliability=&sort=reliability&desc=true&pnum=" + str(pnum) + "#table")
        method = 'http'

        res = PyQuery(r.text)
        for i in range(res('tr[class^="row"]').size()):
            res2 = PyQuery(res('tr[class^="row"]').eq(i))
            for j in range(res2('a').size()):
                if j == 1:
                    ip = res2('a').eq(j).text()
                elif j == 2:
                    port = res2('a').eq(j).text()

            time.sleep(1)
            self.set_proxy(method, ip, port)
            if self.get_proxy_method() == 'http':
                proxy_commit = self.compare_ip("http://httpbin.org/ip", encode='utf-8')
            if proxy_commit:
                self.db.insert_sql("INSERT INTO proxy(ip, port, account, passwd, method) \
                                    VALUE('%s','%s','%s','%s','%s');" % (self.proxy_ip, self.proxy_port,
                                                self.proxy_account, self.proxy_passwd, self.proxy_method))

    def get_localhost_ip(self):
        r = requests.get("http://httpbin.org/ip")
        return r.json()['origin']

    def terminate(self):
        self.db.db_close()

if __name__ == '__main__':
    a = Crawler_Proxy_Util()

    for i in range(10):
        a.crawler_proxy(i)
        # pass
    # print a.test_ip()
    # print a.proxy_request("http://myip.com.tw/", encode='utf-8')
    # print a.http_proxy("104.236.13.100", "8888", "http://www.j4.com.tw/james/remoip.php", encode='big5')


    a.terminate()