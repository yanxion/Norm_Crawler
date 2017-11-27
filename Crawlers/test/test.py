# -*- coding: utf-8 -*-
import base64
import ConfigParser
import binascii
import codecs
import json

import requests
import re
import urllib
from urllib import quote

import rsa


def write_txtfile(name, content):
    f = codecs.open('./' + name + ".txt", "w", "utf-8")
    f.write(content)
    f.close()


def read():
    f = codecs.open("1111.txt", "r", "utf-8")
    # print f.read()
    json_data = f.read().replace('\r\n', '')

    a = json.loads(json_data)
    print a['w_cookies']


read()


# write_txtfile('111', '222')
