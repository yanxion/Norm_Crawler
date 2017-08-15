# -*- coding:utf-8 -*-
#  ____    _____   _____   _____   _____   _____   _   _   _____    _____   _____   _____   _____   _____   _____
# |  _ \  /  _  \ |_   _| |  ___| |_   _| |_   _| | \_/ | |  ___|  |  _  \ /  _  \ |  _  \ /  ___| |  ___| |  _  \
# | | | | | |_| |   | |   | |___    | |     | |   |     | | |___   | |_| | | |_| | | |_| | | |___  | |___  | |_| |
# | | | | |  _  |   | |   |  ___|   | |     | |   | \_/ | |  ___|  |  ___/ |  _  | |    _/ |___  | |  ___| |    _/
# | |_| | | | | |   | |   | |___    | |    _| |_  | | | | | |___   | |     | | | | | |\ \   ___| | | |___  | |\ \
# |____/  |_| |_|   |_|   |_____|   |_|   |_____| |_| |_| |_____|  |_|     |_| |_| |_| \_\ |_____/ |_____| |_| \_\

import datetime
import time
import re


class Datetimeparser():

    def __init__(self, timestring, fields, year_padding=0):
        self.fields = fields
        self.year_padding = year_padding
        if timestring == "now":
            parse_timestring = self.parse_time_str("", "")
            parse_timestring_list = re.split('[^0-9]', parse_timestring)
        else:
            timestring, fields = self.timestr_fields_format(timestring, fields)
            parse_timestring = self.parse_time_str(timestring, fields)
            parse_timestring_list = re.split('[^0-9]', parse_timestring)
        self.year = parse_timestring_list[0]
        self.month = parse_timestring_list[1]
        self.day = parse_timestring_list[2]
        self.hour = parse_timestring_list[3]
        self.min = parse_timestring_list[4]
        self.sec = parse_timestring_list[5]

    def set_year_padding(self, num):
        self.year_padding = num

    def set_year(self, num):
        self.year = num

    def set_month(self, num):
        self.month = num

    def set_day(self, num):
        self.day = num

    def set_hour(self, num):
        self.hour = num

    def set_min(self, num):
        self.min = num

    def set_sec(self, num):
        self.sec = num

    def get_year_padding(self):
        return self.year_padding

    def get_year(self):
        return self.year

    def get_month(self):
        return self.month

    def get_day(self):
        return self.day

    def get_hour(self):
        return self.hour

    def get_min(self):
        return self.min

    def get_sec(self):
        return self.sec

    def timestring_re(self, timestring):
        # month re
        timestring = timestring.lower()
        month_data = ['jan', 'january',
                      'feb', 'february',
                      'mar', 'march',
                      'apr', 'april',
                      'may', 'may',
                      'jun', 'june',
                      'jul', 'july',
                      'aug', 'august',
                      'sep', 'september',
                      'oct', 'october',
                      'nov', 'november',
                      'dec', 'december'
                      ]
        month_re_data = ['01', '01',
                         '02', '02',
                         '03', '03',
                         '04', '04',
                         '05', '05',
                         '06', '06',
                         '07', '07',
                         '08', '08',
                         '09', '09',
                         '10', '10',
                         '11', '11',
                         '12', '12'
                         ]
        return self.replace_str(month_data, month_re_data, timestring)

    def get_timestamp(self):
        time_str = self.year+' '+self.month+' '+self.day+' '+self.hour+' '+self.min+' '+self.sec
        time_format = '%Y %m %d %H %M %S'
        thetime = time.mktime(time.strptime(time_str, time_format.decode('utf-8')))
        result = datetime.datetime.fromtimestamp(thetime).strftime('%Y-%m-%d %H:%M:%S')
        return result

    def get_timestamp_form_format(self, fields):
        time_str = self.year + ' ' + self.month + ' ' + self.day + ' ' + self.hour + ' ' + self.min + ' ' + self.sec
        time_format = '%Y %m %d %H %M %S'
        thetime = time.mktime(time.strptime(time_str, time_format.decode('utf-8')))
        result = datetime.datetime.fromtimestamp(thetime).strftime(fields)
        return result

    def get_timestamp_from_timestr(self, timestring):
        timestring, fields = self.timestr_fields_format(timestring, self.fields)
        return self.parse_time_str(timestring, fields)

    def get_timeformat_from_timestr_and_fields(self, timestring, fields):
        timestring, fields = self.timestr_fields_format(timestring, fields)
        return self.parse_time_str(timestring, fields)

    def timestr_fields_format(self, timestring, fields):
        hour_padding = 0
        time_am = ['\\bAM\\b', '\\bam\\b', '\\bAm\\b', '\\ba.m.\\b', u'上午']
        time_pm = ['\\bPM\\b', '\\bpm\\b', '\\bPm\\b', '\\bp.m.\\b', u'下午']

        if any(re.findall(pattern, timestring) for pattern in time_am):
            fields = re.sub('%p', '', fields)
            fields = re.sub('%I', '%H', fields)
        elif any(re.findall(pattern, timestring) for pattern in time_pm):
            fields = re.sub('%p', '', fields)
            fields = re.sub('%I', '%H', fields)
            hour_padding = 12

        fields = filter(None, re.split(' ', fields))
        fields = ' '.join(fields)

        timestring = self.timestring_re(timestring)
        timestring = filter(None, re.split('[^0-9]', timestring))
        if self.year_padding:
            cnt = 0
            for i in fields.split(' '):
                if i == '%Y' or i == '%y':
                    timestring[cnt] = str(int(timestring[cnt]) + self.year_padding)
                    break
                cnt += 1
        timestring[3] = str(int(timestring[3]) + hour_padding)
        timestring = ' '.join(timestring)
        return timestring, fields

    def str_to_time(self, datetimestr):
        return time.mktime(time.strptime(datetimestr, '%Y-%m-%d %H:%M:%S'))

    def now(self):
        return time.time()

    def time_to_str(self, time):
        return datetime.datetime.fromtimestamp(time).strftime('%Y-%m-%d %H:%M:%S')

    def parse_time_str(self, time_str, time_format):
        try:
            thetime = time.mktime(time.strptime(time_str, time_format.decode('utf-8')))
            result = datetime.datetime.fromtimestamp(thetime).strftime('%Y-%m-%d %H:%M:%S')
        except Exception as e:  # if the time string can't be parsed, return current time.
            result = datetime.datetime.fromtimestamp(self.now()).strftime('%Y-%m-%d %H:%M:%S')
            # raise e
        return result

    def datetime_to_timestr(self, datetime):
        return self.time_to_str(self.datetime_to_time(datetime))

    def datetime_to_time(self, datetime):
        return time.mktime(datetime.timetuple())

    def start_of_the_day(self):
        today = datetime.date.today()
        unix_time = self.datetime_to_time(today)
        return unix_time

    @staticmethod
    def replace_str(re_pattern_list, re_replacement_list, origin_str):
        for pattern, repl in zip(re_pattern_list, re_replacement_list):
            origin_str = re.sub(pattern, repl, origin_str)
        return origin_str


if __name__ == '__main__':
    timeparse = Datetimeparser('106-Jun-22 10:35:33 PM', '%Y %m %d %I %M %S %p', 1911)
    # timeparse = Datetimeparser('2015-Jun-22 10:35:33 PM', "%Y %m %d %I %M %S %p")
    # timeparse = Datetimeparser(u"今天是 2017年12月15日03:11:20的樣子", '%Y %m %d %H %M %S')
    # timeparse = Datetimeparser('now', '')

    # str1 = "2017-05-22 6:35:00 PM"
    # field1 = "%Y %m %d %I %M %S %p"
    #
    # str1 = "2017-Jun-22 6:35:00 PM"
    # field1 = "%Y %m %d %I %M %S %p"
    #
    str1 = "106-05-22 6:35:00 AM"
    field1 = "%Y %m %d %I %M %S %p"
    #
    # str1 = u"2017-05-22 6:35:00 上午"
    # field1 = "%Y %m %d %I %M %S %p"
    #
    # str1 = u"今天是 2017年12月15日03:12:20的樣子"
    # field1 = "%Y %m %d %H %M %S"

    print "------------------------------------------------------------"
    print timeparse.get_timestamp()
    print "------------------------------------------------------------"
    print timeparse.get_timestamp_from_timestr(str1)
    print "------------------------------------------------------------"
    print timeparse.get_timeformat_from_timestr_and_fields(str1, field1)

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

    # print parseTimeStr(u'今天是 101年12月15日03:12的樣子'.encode('utf-8'), '%Y年%m月%d日%H:%M')
