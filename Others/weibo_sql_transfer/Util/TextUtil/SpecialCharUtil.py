# -*- coding:utf-8 -*-
__author__ = '130803'
import re

def remove_emoji(s):
    try:
        # Wide UCS-4 build
        my_re = re.compile(u'['
            u'\U0001F300-\U0001F64F'
            u'\U0001F680-\U0001F6FF'
            u'\U000131A1]+',
            # u'\u2600-\u26FF\u2700-\u27BF]+',
            re.UNICODE)
    except re.error:
        # Narrow UCS-2 build
        my_re = re.compile(u'('
            u'\ud83c[\udf00-\udfff]|'
            u'\ud83d[\udc00-\ude4f\ude80-\udeff]|'
            u'\ud83e[\udc00-\ude4f\ude80-\udeff]|'
            u'\ud80c[\udda1]|'
            u'[\u2600-\u26FF\u2700-\u27BF]|'
            u'[\u25A3\u2193\u25BC\u1F197\U0001F197])+',
            re.UNICODE)
    # print s
    # print my_re.sub('', s)
    # print

    return my_re.sub('', s)

if __name__ == '__main__':
    s = u'\u597d\u666f\u4e0d\u5e38\u554a\U0001f62d\n\u67d0\u25A3\u2193\u25BC	\u1F197'
    s = u'𓆡对没有礼貌/抄袭的人忍耐为零'
    # s = "''''"
    print s
    print repr(s)
    print remove_emoji(s)
    print repr(remove_emoji(s))


