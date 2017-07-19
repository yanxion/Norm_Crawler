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
        self.Get_Argv()
        self.entry_num = 3
        f = codecs.open(self.Crawler_Name + '_' + self.type + "_Entry.txt", "w", "utf-8")
        f = codecs.open(self.Crawler_Name + '_' + self.type + "_Item.txt", "w", "utf-8")
        f = codecs.open(self.Crawler_Name + '_' + self.type + "_Data.txt", "w", "utf-8")

    def Get_Argv(self):
        # get terminal parameter .
        for i in range(0, len(sys.argv), +1):
            if sys.argv[i] == '--c':
                self.Crawler_Name =  sys.argv[i + 1].decode('big5')
                #test_set['Crawler_Name'] = sys.argv[i + 1].decode('big5')
            elif sys.argv[i] == '--u':
                self.url = sys.argv[i + 1].decode('big5')
            elif sys.argv[i] == '--s':
                self.sitename = sys.argv[i + 1].decode('big5')
            elif sys.argv[i] == '--t':
                self.type = sys.argv[i + 1].decode('big5')
            elif sys.argv[i] == '--f':
                self.flag = sys.argv[i + 1].decode('big5')

    def Crawler_Test_Start(self):
        # Dynamic import Crawler Class .
        mod = importlib.import_module('Crawlers.'+self.Crawler_Name+'.CrawlerClient')
        myclass = getattr(mod,'CrawlerClient')

        # simulation Job List .
        test_set = {'url': self.url, 'sitename': self.sitename, 'type': self.type, 'flag': self.flag}

        if self.flag == 'entry':
            # Default Crawl 2 Page .
            for i in range(0,self.entry_num,+1):
                # Crawl entry Page .
                mo = myclass(**test_set)
                self.crawler_data = mo.crawl()
                # Write item to the file .
                self.Write_Txt_File(self.crawler_data.get_data())

                item_test_set = test_set.copy()
                for i in range(len(self.crawler_data.get_data()['item_job'])):
                    item_test_set['url'] = self.crawler_data.get_data()['item_job'][i]['url']
                    item_test_set['flag'] = 'item'
                    item_mo = myclass(**item_test_set)
                    item_data = item_mo.crawl()
                    # Write data to the file .
                    self.Write_Txt_File(item_data.get_data())

                if self.crawler_data.get_data()['entry_job'] == []:
                    break
                else:
                    # entry's next page .
                    test_set['url'] = self.crawler_data.get_data()['entry_job'][0]['url']


        elif self.flag == 'item':
            # just crawl item .
            mo = myclass(**test_set)
            self.crawler_data = mo.crawl()
            self.Write_Txt_File(self.crawler_data.get_data())
                #print self.crawler_data.get_data()


    def Write_Txt_File(self,Data):
        # write some to the file , and check if value is null then dont write.
        if not Data['entry_job'] == []:
            f = codecs.open(self.Crawler_Name + '_' + self.type + "_Entry.txt", "a", "utf-8")
            f.write(json.dumps(Data['entry_job'], ensure_ascii=False, indent=4))
            f.write("\n----------------------------------------------------------------\n")
            f.close()
        if not Data['item_job'] == []:
            f = codecs.open(self.Crawler_Name + '_' + self.type + "_Item.txt", "a", "utf-8")
            f.write(json.dumps(Data['item_job'], ensure_ascii=False, indent=4))
            f.write("\n----------------------------------------------------------------\n")
            f.close()
        if not Data['data'] == []:
            f = codecs.open(self.Crawler_Name + '_' + self.type + "_Data.txt", "a", "utf-8")
            f.write(json.dumps(Data['data'], ensure_ascii=False, indent=4))
            f.write("\n----------------------------------------------------------------\n")
            f.close()


if __name__ == '__main__':
    c = CrawlerTestClass()
    c.Crawler_Test_Start()