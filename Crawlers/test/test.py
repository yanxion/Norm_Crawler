# -*- coding: utf-8 -*-
import urlparse
from pyquery import PyQuery
from Util.Forum_MySqlDB_util.Forum_MySqlDB_util import Forum_MySqlDB_util
import os

# a = Forum_MySqlDB_util()
# a.connect_mysql()
#
# c = a.select_sql("SELECT comment_count FROM post WHERE key_url_sha = '9c3c8d21e92f7090ec4301ddcc8d5fa1047a2817';")
# print c[0]
# a.db_close()
web_url = 'http://www01.eyny.com/thread-11148331-1-EY2Y69P2.html'

res = PyQuery(web_url, encoding='utf-8')

print res('div.pi a[id^="postnum"] ').length