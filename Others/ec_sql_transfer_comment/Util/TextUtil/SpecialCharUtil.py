__author__ = '130803'
import re

def remove_emoji(s):
    try:
        # Wide UCS-4 build
        my_re = re.compile(u'['
            u'\U0001F300-\U0001F64F'
            u'\U0001F680-\U0001F6FF'
            u'\u2600-\u26FF\u2700-\u27BF]+',
            re.UNICODE)
    except re.error:
        # Narrow UCS-2 build
        my_re = re.compile(u'('
            u'\ud83c[\udf00-\udfff]|'
            u'\ud83d[\udc00-\ude4f\ude80-\udeff]|'
            u'\ud83e[\udc00-\ude4f\ude80-\udeff]|'
            u'[\u2600-\u26FF\u2700-\u27BF])+',
            re.UNICODE)
    return my_re.sub('', s)

if __name__ == '__main__':
    # s = u'\u597d\u666f\u4e0d\u5e38\u554a\U0001f62d\n\u67d0'
    s = "''''"
    print repr(remove_emoji(s))


