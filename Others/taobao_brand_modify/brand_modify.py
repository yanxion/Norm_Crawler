# -*- coding:utf-8 -*-
import sys
import json

import os

sys.path.append('../../')
from Util.SQL_Connect import SQL_Connect


class brand_modify():
    def __init__(self):
        self.db = SQL_Connect.SQL_Connect()
        self.db.connect_mysql(os.path.join(os.path.dirname(__file__), "config.ini"))

    def main(self):
        jdata = {}
        # for i in range(0, 10):
        #     jdata[i] = i
        # # jdata['0'] = '1'
        # # jdata['1'] = '2'
        # # jdata['2'] = '3'
        # # jdata['3'] = '4'
        # print json.dumps(jdata, ensure_ascii=False, indent=4)
        #
        # exit()
        self.make_brand_dict()

    def data_to_json(self, data):
        jdata = {}
        dic = {}
        cnt = 0
        for i in data:
            dic['id'] = i[0]
            dic['item_id'] = i[1]
            dic['title'] = i[2]
            dic['content'] = i[3]
            dic['brand'] = i[4]
            print cnt, dic
            jdata[cnt] = dic
            # print cnt, dic
            # print ' ', jdata[cnt]
            print json.dumps(jdata, ensure_ascii=False, indent=4)
            print '-------------------------------------------------------------------------------------------------'
            print '-------------------------------------------------------------------------------------------------'
            cnt += 1
            if cnt == 10:
                break

        return jdata

    def make_brand_dict(self):
        query_data = self.db.select_sql_all(
            'SELECT id, item_id, title, content, brand FROM taobao.taobao_itemlist_20171122 WHERE TYPE = 5 LIMIT 20;')
        jdata = self.data_to_json(query_data)
        # print json.dumps(jdata, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    main = brand_modify()
    main.main()
