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
        self.time_am = ['\\bAM\\b', '\\bam\\b', '\\bAm\\b', '\\ba.m.\\b', '上午']
        self.time_pm = ['\\bPM\\b', '\\bpm\\b', '\\bPm\\b', '\\bp.m.\\b', '下午']

        self.default_times_list = re.split('[^0-9]', self.time_to_str(self.now()))
        self.default_times_list[3] = '00'
        self.default_times_list[4] = '00'
        self.default_times_list[5] = '00'
        self.default_field_list = ['%Y', '%m', '%d', '%H', '%M', '%S']

        self.year_padding = year_padding
        if timestring == "now":
            timestring = self.time_to_str(self.now())
            fields = '%Y-%m-%d %H:%M:%S'
            parse_timestring = self.parse_time_str(timestring, fields)
            parse_timestring_list = re.split('[^0-9]', parse_timestring)
            self.default_times_list = parse_timestring_list
        else:
            timestring, fields = self.timestr_fields_format(timestring, fields)
            parse_timestring = self.parse_time_str(timestring, fields)
            parse_timestring_list = re.split('[^0-9]', parse_timestring)

            fields_list = fields # filter(None, re.split(' ', fields))
            for i in range(len(fields_list)):
                if fields_list[i] == '%Y':
                    self.default_times_list[0] = parse_timestring_list[i]
                if fields_list[i] == '%m':
                    self.default_times_list[1] = parse_timestring_list[i]
                if fields_list[i] == '%d':
                    self.default_times_list[2] = parse_timestring_list[i]
                if fields_list[i] == '%H':
                    self.default_times_list[3] = parse_timestring_list[i]
                if fields_list[i] == '%M':
                    self.default_times_list[4] = parse_timestring_list[i]
                if fields_list[i] == '%S':
                    self.default_times_list[5] = parse_timestring_list[i]

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

    def set_am(self, val):
        self.time_am.append(val)

    def set_pm(self, val):
        self.time_pm.append(val)

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

    def get_am(self):
        return self.time_am

    def get_pm(self):
        return self.time_pm

    def timestring_re(self, timestring):
        """
             將月份替換成數字
        :param timestring:
        :return: 替換後的timestring
        """
        # month re
        timestring = timestring.lower()
        month_data = ['jan', 'january', 'feb', 'february', 'mar', 'march', 'apr', 'april', 'may', 'may',
                      'jun', 'june', 'jul', 'july', 'aug', 'august', 'sep', 'september', 'oct', 'october',
                      'nov', 'november', 'dec', 'december'
                      ]
        month_re_data = ['01', '01', '02', '02', '03', '03', '04', '04', '05', '05', '06', '06',
                         '07', '07', '08', '08', '09', '09', '10', '10', '11', '11', '12', '12'
                         ]
        return self.replace_str(month_data, month_re_data, timestring)

    def time_ampm_re(self, timestring, fields):
        """
            將AM與PM裡的文字替換成時間
        :param timestring:
        :param fields:
        :return:
        """
        hour_padding = -1
        if any(re.findall(pattern, timestring) for pattern in self.time_am):
            fields = re.sub('%p', '', fields)
            fields = re.sub('%I', '%H', fields)
            hour_padding = 0
        elif any(re.findall(pattern, timestring) for pattern in self.time_pm):
            fields = re.sub('%p', '', fields)
            fields = re.sub('%I', '%H', fields)
            hour_padding = 12
        return timestring, fields, hour_padding

    def get_timestamp(self):
        """
            將設定時間以 %Y-%m-%d %H:%M:%S 格式回傳
        :return: '%Y-%m-%d %H:%M:%S'格式的時間，失敗則回傳現在時間
        """
        try:
            time_str = self.year + ' ' + self.month + ' ' + self.day + ' ' + self.hour + ' ' + self.min + ' ' + self.sec
            time_format = '%Y %m %d %H %M %S'
            thetime = time.mktime(time.strptime(time_str, time_format.decode('utf-8')))
            result = datetime.datetime.fromtimestamp(thetime).strftime('%Y-%m-%d %H:%M:%S')
            return result
        except:
            return self.time_to_str(self.now())

    def get_timestamp_from_format(self, fields):
        """
            將設定時間以指定格式讀取
        :param fields:指定格式
        :return: '%Y-%m-%d %H:%M:%S'格式的時間，失敗則回傳現在時間
        """
        try:
            time_str = self.year + ' ' + self.month + ' ' + self.day + ' ' + self.hour + ' ' + self.min + ' ' + self.sec
            time_format = '%Y %m %d %H %M %S'
            thetime = time.mktime(time.strptime(time_str, time_format.decode('utf-8')))
            result = datetime.datetime.fromtimestamp(thetime).strftime(fields)
            return result
        except:
            return self.time_to_str(self.now())

    def get_timestamp_from_timestr(self, timestring):
        """
            給予時間以 %Y-%m-%d %H:%M:%S 的格式回傳
        :param timestring:指定時間
        :return: '%Y-%m-%d %H:%M:%S'格式的時間，失敗則回傳現在時間
        """
        try:
            timestring, fields = self.timestr_fields_format(timestring, self.fields)
            return self.parse_time_str(timestring, fields)
        except:
            return self.time_to_str(self.now())

    def get_timeformat_from_timestr_and_fields(self, timestring, fields):
        """
            給予時間與格式回傳正確格式的時間
        :param timestring: 時間
        :param fields: 格式
        :return: '%Y-%m-%d %H:%M:%S'格式的時間，失敗則回傳現在時間
        """
        try:
            timestring, fields = self.timestr_fields_format(timestring, fields)
            return self.parse_time_str(timestring, fields)
        except Exception as e:
            return self.time_to_str(self.now())

    def timestr_fields_format(self, timestring, fields):
        """
            將時間做一些重組動作
        :param timestring:
        :param fields:
        :return:
        """

        timestring, fields, hour_padding = self.time_ampm_re(timestring, fields)
        fields = filter(None, re.split(' ', fields))
        timestring = self.timestring_re(timestring)
        timestring = filter(None, re.split('[^0-9]', timestring))
        # fieldstring = filter(None, re.split(' ', fields))
        for i in range(len(fields)):
            if fields[i] == '%Y':
                self.default_times_list[0] = timestring[i]
            if fields[i] == '%m':
                self.default_times_list[1] = timestring[i]
            if fields[i] == '%d':
                self.default_times_list[2] = timestring[i]
            if fields[i] == '%H':
                self.default_times_list[3] = timestring[i]

            if fields[i] == '%M':
                self.default_times_list[4] = timestring[i]
            if fields[i] == '%S':
                self.default_times_list[5] = timestring[i]

        # fields = ' '.join(fields)
        time_string = self.default_times_list
        fields_string = self.default_field_list

        if self.year_padding:
            cnt = 0
            # for i in fields.split(' '):
            for i in fields_string:
                if i == '%Y' or i == '%y':
                    time_string[cnt] = str(int(time_string[cnt]) + self.year_padding)
                    break
                cnt += 1
        try:
            if time_string[3] == "12" and hour_padding == 0:
                time_string[3] = "0"
            elif time_string[3] == "12" and hour_padding == 12:
                time_string[3] = "12"
            elif hour_padding == -1:
                if time_string[3] == "12":
                    time_string[3] = "12"
            else:
                time_string[3] = str(int(time_string[3]) + hour_padding)
        except:
            pass

        time_string = ' '.join(time_string)
        fields_string = ' '.join(fields_string)

        return time_string, fields_string

    def str_to_time(self, datetimestr):
        return time.mktime(time.strptime(datetimestr, '%Y-%m-%d %H:%M:%S'))

    def now(self):
        return time.time()

    def time_to_str(self, time):
        return datetime.datetime.fromtimestamp(time).strftime('%Y-%m-%d %H:%M:%S')

    def parse_time_str(self, time_str, time_format):
        # print time_str, time_format
        try:
            thetime = time.mktime(time.strptime(time_str, time_format.decode('utf-8')))
            result = datetime.datetime.fromtimestamp(thetime).strftime('%Y-%m-%d %H:%M:%S')
        except Exception as e:  # if the time string can't be parsed, return current time.
            result = datetime.datetime.fromtimestamp(self.now()).strftime('%Y-%m-%d %H:%M:%S')
        return result

    def datetime_to_timestr(self, datetime):
        return self.time_to_str(self.datetime_to_time(datetime))

    def datetime_to_time(self, datetime):
        return time.mktime(datetime.timetuple())

    def start_of_the_day(self):
        today = datetime.date.today()
        unix_time = self.datetime_to_time(today)
        return unix_time

    def get_yesterday(self, time_format='%Y-%m-%d', day=1):
        today = datetime.date.today()
        oneday = datetime.timedelta(days=day)
        yesterday = today - oneday
        timestamp = time.mktime(datetime.datetime.strptime(str(yesterday), '%Y-%m-%d').timetuple())
        return datetime.datetime.fromtimestamp(int(timestamp)).strftime(time_format)

    @staticmethod
    def replace_str(re_pattern_list, re_replacement_list, origin_str):
        for pattern, repl in zip(re_pattern_list, re_replacement_list):
            origin_str = re.sub(pattern, repl, origin_str)
        return origin_str


if __name__ == '__main__':
    # timeparse = Datetimeparser('106-Jun-22 10:35:33 PM', '%Y %m %d %I %M %S %p', 1911)
    # timeparse = Datetimeparser('106-Jun-22', '%Y %m %d', 1911)
    # timeparse = Datetimeparser('2015-Jun-22 10:35:33 PM', "%Y %m %d %I %M %S %p")
    # timeparse = Datetimeparser(u"今天是 2017年12月15日03:11:20的樣子", '%Y %m %d %H %M %S')
    timeparse = Datetimeparser('now', '')

    timeparse.set_am('凌晨')
    # str1 = "2017-03-22"
    # field1 = "%Y %m %d"

    # str1 = "6:35:00 PM"
    # field1 = "%I %M %S %p"
    #
    str1 = "2017-Jun-22 6:35:00 凌晨"
    field1 = "%Y %m %d %I %M %S %p"
    #
    # str1 = "106-05-22 6:35:00 AM"
    # field1 = "%Y %m %d %I %M %S %p"
    #
    # str1 = u"201705226:35:00上午"
    # field1 = "%Y %m %d %I %M %S %p"
    #
    # str1 = u'17-Sep-01 08:38'
    # field1 = '%y %m %d %H %M'
    #
    # str1 = u"今天是 2017年12月15日03:12:20的樣子"
    # field1 = "%Y %m %d %H %M %S"
    print timeparse.time_to_str(timeparse.now())
    print "------------------------------------------------------------"
    print timeparse.get_timestamp()
    print "------------------------------------------------------------"
    # print timeparse.get_timestamp_from_timestr(str1)
    # print "------------------------------------------------------------"
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
    print timeparse.get_yesterday()