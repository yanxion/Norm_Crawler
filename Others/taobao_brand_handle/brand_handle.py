# -*- coding:utf-8 -*-
import codecs
import sys
import json

import os

sys.path.append('../../')
from Util.SQL_Connect import SQL_Connect


class brand_handle():
    def __init__(self):
        self.db = SQL_Connect.SQL_Connect()
        self.db.connect_mysql(os.path.join(os.path.dirname(__file__), "config.ini"))

    def main(self):
        pass

    def data_to_json(self, data):
        jdata = {}
        cnt = 0
        for i in data:
            dic = {}
            dic['id'] = i[0]
            dic['item_id'] = i[1]
            dic['title'] = i[2]
            dic['content'] = i[3]
            dic['brand'] = i[4]
            jdata[cnt] = dic
            cnt += 1
        return jdata

    def make_brand_dict(self):
        query_data = self.db.select_sql_all(
            'SELECT id, item_id, title, content, brand FROM taobao.taobao_itemlist_20171130 WHERE TYPE BETWEEN 3 AND 6 AND brand IS NOT NULL')  # LIMIT 10;')
        jdata = self.data_to_json(query_data)
        brand_dic = {}
        for i in jdata:
            if jdata[i]['brand']:
                brand_dic[jdata[i]['brand']] = 1
        str_handle = ''
        for i in brand_dic:
            print i,
            str_handle += '["' + i + '","' + i + '"],'
        f = codecs.open('category_dic.txt', "w", "utf-8")
        w_data = '{"brand":[' + str_handle[:-1] + ']}'
        f.write(json.dumps(json.loads(w_data), ensure_ascii=False, indent=4))
        f.close()
        # print json.dumps(jdata, ensure_ascii=False, indent=4)

    def brand_handle(self):
        f = codecs.open('brand_dic.txt', "r", "utf-8")
        file_data = f.read().replace('\r\n', '')
        f.close()
        brand_dic = json.loads(file_data)

        query_data = self.db.select_sql_all(
            'SELECT id, item_id, title, content, brand FROM taobao.taobao_itemlist_20171130 WHERE brand IS NULL')
        jdata = self.data_to_json(query_data)
        # f = codecs.open('brand_handle.txt', "w", "utf-8")
        for i in jdata:
            for j in brand_dic['brand']:
                if jdata[i]['title'].find(j[0]) >= 0 or jdata[i]['content'].find(j[0]) >= 0:
                    print j[1]
                    self.db.insert_sql('UPDATE taobao.taobao_itemlist_20171130 SET brand = "' + j[1] + '" WHERE item_id = "' + jdata[i]['item_id'] + '"')
                    # f.write('-------------------------------------------------------------------------\n')
                    # f.write(jdata[i]['title'] + '\n')
                    # f.write(jdata[i]['content'] + '\n')
                    # f.write(j[1] + '\n')
                    # f.write('\n')
        f.close()
        # for i in brand_dic['brand']:
        #     print i

if __name__ == '__main__':
    main = brand_handle()
    # main.make_brand_dict()
    main.brand_handle()
