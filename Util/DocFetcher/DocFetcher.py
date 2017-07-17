# -*- coding:utf-8 -*-
__author__ = '130803'

import requests
import time
import sys
# from enum import Enum


# class Method(Enum):
#     GET = 1
#     POST = 2


class DocFetcher:
    def __init__(self, url, method='GET', data=None, headers=None, cookies=None):
        self.url = url
        self.https_verify = False
        self.error_msg = None
        self.method = method
        self.data = data
        self.send_headers = headers
        self.send_cookies = cookies
        self.response_headers = None
        self.response_cookies = None

    def fetch(self):
        r = None
        # try for max 5 times
        for i in range(0, 5):
            try:
                if self.method.upper() == 'GET':
                    r = requests.get(self.url, verify=self.https_verify,
                                     params=self.data, headers=self.send_headers, cookies=self.send_cookies)
                elif self.method.upper() == 'POST':
                    r = requests.post(self.url, verify=self.https_verify,
                                      data=self.data, headers=self.send_headers, cookies=self.send_cookies)
                if r:
                    self.response_cookies = r.cookies
                    self.response_headers = r.headers
            except Exception as exc:
                self.error_msg = sys.exc_info()
                time.sleep(5)
            else:
                break
        return r.text if r is not None else None

    def get_response_headers(self):
        return self.response_headers

    def get_response_cookies(self):
        return self.response_cookies

    def get_error_msg(self):
        return self.error_msg

    def get_url(self):
        return self.url

    def set_https_verify(self, to_verify):
        if to_verify:
            self.https_verify = True
        else:
            self.https_verify = False


def test():
    url = 'https://buzzorange.com/2016/03/01/formosa-killings-are-put-at-10000/'
    x = DocFetcher(url)
    x.set_https_verify(False)
    try:
        src = x.fetch()
    except Exception as irw:
        pass

    print src[0:100]
    print x.get_error_msg()

if __name__ == '__main__':
    test()
