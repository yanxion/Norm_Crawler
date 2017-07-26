# -*- coding: utf-8 -*-
import urlparse
from pyquery import PyQuery
str = "http://www01.eyny.com/thread-11256716-1-EY2Y69P2.html"

res = PyQuery(str, encoding='utf-8')

print res('div.pi a[id^="postnum"]').text()
# print res('td#postmessage_299981178.t_f').text()