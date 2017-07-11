# -*- coding: utf-8 -*-
__author__ = '130803'


class CrawlerDataWrapper:
    def __init__(self):
        self.data = {'entry_job': [],
                     'item_job': [],
                     'data': []}

    def append_entry_job(self, **kwargs):
        self.data['entry_job'].append(kwargs)

    def append_item_job(self, **kwargs):
        self.data['item_job'].append(kwargs)

    def append_data(self, **kwargs):
        self.data['data'].append(kwargs)

    def get_data(self):
        return self.data


def test():
    url = u'https://www.juksy.com/archives/51968'
    sitename = 'Juksy'
    news_type = u'最新'
    flag = 'item'
    crawl_data = {'url': url, 'sitename': sitename, 'type': news_type, 'flag': flag}

    p = CrawlerDataWrapper()
    p.append_entry_job(**crawl_data)

    print p.get_data()

if __name__ == '__main__':
    test()
