# -*- coding: utf-8 -*-
import sys
sys.path.append('../../')
import importlib
import codecs
import json
from Util.CrawlerDataWrapper.CrawlerDataWrapper import CrawlerDataWrapper


class CrawlerTestClass():
    def __init__(self, **kwargs):
        self.crawler_data = CrawlerDataWrapper()
        # Default Crawl Page .
        self.entry_num = 10
        try:
            self.crawler_name = kwargs['crawler_name']
            self.url = kwargs['url']
            self.sitename = kwargs['sitename']
            self.type = kwargs['type']
            self.flag = kwargs['flag']
            self.context = kwargs['context']
        except Exception as e:
            raise Exception("Parameter error .")
        try:
            codecs.open(self.crawler_name + '_' + self.type + "_Entry.txt", "w", "utf-8")
            codecs.open(self.crawler_name + '_' + self.type + "_Item.txt", "w", "utf-8")
            codecs.open(self.crawler_name + '_' + self.type + "_Data.txt", "w", "utf-8")
        except:
            raise Exception("Create a file error .")

    def crawler_test_start(self):
        # Dynamic import Crawler Class .
        try:
            mod = importlib.import_module('Crawlers.' + self.crawler_name + '.CrawlerClient')
            myclass = getattr(mod, 'CrawlerClient')
        except:
            raise Exception("Import module error .")
        # simulation Job List .
        test_set = {'url': self.url, 'sitename': self.sitename, 'type': self.type, 'flag': self.flag, 'context': self.context}

        if self.flag == 'entry':
            for i in range(self.entry_num):
                # Crawl entry Page .
                mo = myclass(**test_set)
                self.crawler_data = mo.crawl()
                # Write item to the file .
                self.write_txt_file(self.crawler_data.get_data())
                item_test_set = test_set.copy()
                for j in range(len(self.crawler_data.get_data()['item_job'])):
                    item_test_set['url'] = self.crawler_data.get_data()['item_job'][j]['url']
                    item_test_set['flag'] = 'item'
                    item_test_set['context'] = self.crawler_data.get_data()['item_job'][j]['context']
                    item_mo = myclass(**item_test_set)
                    item_data = item_mo.crawl()
                    # Write data to the file .
                    try:
                        self.write_txt_file(item_data.get_data())
                    except:
                        print "write txt file error"
                if not self.crawler_data.get_data()['entry_job']:
                    break
                else:
                    # entry's next page .
                    test_set['url'] = self.crawler_data.get_data()['entry_job'][0]['url']

        elif self.flag == 'item':
            # just crawl item .
            mo = myclass(**test_set)
            self.crawler_data = mo.crawl()
            self.write_txt_file(self.crawler_data.get_data())
        else:
            raise Exception("flag value input error .")

    def write_txt_file(self, data):
        # write some to the file , and check if value is null then dont write.
        if not data['entry_job'] == []:
            f = codecs.open(self.crawler_name + '_' + self.type + "_Entry.txt", "a", "utf-8")
            f.write(json.dumps(data['entry_job'], ensure_ascii=False, indent=4))
            f.write("\n----------------------------------------------------------------\n")
            f.close()
        if not data['item_job'] == []:
            f = codecs.open(self.crawler_name + '_' + self.type + "_Item.txt", "a", "utf-8")
            f.write(json.dumps(data['item_job'], ensure_ascii=False, indent=4))
            f.write("\n----------------------------------------------------------------\n")
            f.close()
        if not data['data'] == []:
            f = codecs.open(self.crawler_name + '_' + self.type + "_Data.txt", "a", "utf-8")
            f.write(json.dumps(data['data'], ensure_ascii=False, indent=4))
            f.write("\n----------------------------------------------------------------\n")
            f.close()


if __name__ == '__main__':

    # get terminal parameter .
    argv = {}
    for i in range(0, len(sys.argv), +1):
        if sys.argv[i] == '--c':
            argv['crawler_name'] = sys.argv[i + 1].decode('big5')
        elif sys.argv[i] == '--u':
            argv['url'] = sys.argv[i + 1].decode('big5')
        elif sys.argv[i] == '--s':
            argv['sitename'] = sys.argv[i + 1].decode('big5')
        elif sys.argv[i] == '--t':
            argv['type'] = sys.argv[i + 1].decode('big5')
        elif sys.argv[i] == '--f':
            argv['flag'] = sys.argv[i + 1].decode('big5')
        elif sys.argv[i] == '--x':
            argv['context'] = sys.argv[i + 1].decode('big5')

    c = CrawlerTestClass(**argv)
    c.crawler_test_start()
