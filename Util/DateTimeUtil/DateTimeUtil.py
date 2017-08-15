# -*- coding:utf-8 -*-
import datetime
import time
import re
__author__ = '130803'


def strToTime(datetimestr):
    return time.mktime(time.strptime(datetimestr, '%Y-%m-%d %H:%M:%S'))


def dateTimeToTime(datetime):
    return time.mktime(datetime.timetuple())


def now():
    return time.time()


def timeToStr(time):
    return datetime.datetime.fromtimestamp(time).strftime('%Y-%m-%d %H:%M:%S')

# %Y: year in n digits
# %y: year in 2 digits, [00, 99]
# %m: month, [01, 12]
# %d: day, [01,31]
# %H: hour in 24H mode, [00, 23]
# %I: hour in 12H mode, [01, 12]
# %p: AM/PM
# %M: minute, [00, 59]
# %S: second, [00, 61]
# both time_str and time_format should be utf-8.
def parseTimeStr(time_str, time_format):
    try:
        thetime = time.mktime(time.strptime(time_str, time_format.decode('utf-8')))
        result = datetime.datetime.fromtimestamp(thetime).strftime('%Y-%m-%d %H:%M:%S')
    except Exception as e:  # if the time string can't be parsed, return current time.
        result = datetime.datetime.fromtimestamp(now()).strftime('%Y-%m-%d %H:%M:%S')
        # raise e
    return result


def dateTimeToTimeStr(datetime):
    return timeToStr(dateTimeToTime(datetime))


def startOfTheDay():
    today = datetime.date.today()
    unix_time = dateTimeToTime(today)
    return unix_time

if __name__ == '__main__':
    tstr = 'Sun, 25 Jun 2017 04:30:00 +0800'
    print re.sub('.+?, |\+0800', '', tstr)
    # print parseTimeStr(u'今天是 101年12月15日03:12的樣子'.encode('utf-8'), '%Y年%m月%d日%H:%M')
