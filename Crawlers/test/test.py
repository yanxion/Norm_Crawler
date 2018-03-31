# -*- coding:utf-8 -*-
import os
from Util.SQL_Connect import SQL_Connect
from Util.DateTimeParser.DateTimeParser import Datetimeparser

db = SQL_Connect.SQL_Connect()
dt = Datetimeparser('now', '')
db.connect_mysql(os.path.join(os.path.dirname(__file__), "ibuzz_db_config.ini"))

sql = 'INSERT INTO url_list_python (item_index, query_time, run_tag) VALUES(0, \'%s\', 0)'

for i in range(84, 0, -1):
    print sql % (dt.get_someday_ago(time_format='%Y-%m-%d', day=i))
    db.insert_sql(sql % (dt.get_someday_ago(time_format='%Y-%m-%d', day=i)))

