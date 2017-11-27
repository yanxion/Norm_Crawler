# -*- coding: utf-8 -*-
import base64

import binascii
import requests
import re
import urllib
from urllib import quote

import rsa

time_am = ['\\bAM\\b', '\\bam\\b', '\\bAm\\b', '\\ba.m.\\b', u'上午']

time_am.append('123')

print time_am