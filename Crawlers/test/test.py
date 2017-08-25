# -*- coding: utf-8 -*-
import urlparse

import requests
from pyquery import PyQuery
from Util.Forum_MySqlDB_util.Forum_MySqlDB_util import Forum_MySqlDB_util
import os
import re
import dateparser
import ruamel
from Util.Crawler_Proxy_Util.Crawler_Proxy_Util import Crawler_Proxy_Util


a = Crawler_Proxy_Util()
r = a.proxy_requests("http://myip.com", encoding='utf-8')
res = PyQuery(r)
print res('font')

# print dateparser.parse('12/12/12')
# print dateparser.parse(u'星期一, 12 Dec 2014 10:55:50')
# print dateparser.parse(u'2017/二月/05 5:30 PM')
# print dateparser.parse(u'2017/07/05 5:30 早上')
# print dateparser.parse(u'June 13 17 17:50:22')
# print dateparser.parse(u'2小時前')
# print dateparser.parse(u'2017年3月5日 5点30分')



