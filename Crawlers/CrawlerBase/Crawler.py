# encoding:utf-8
__author__ = '130803'
from abc import ABCMeta, abstractmethod
import os

class Crawler(object):
    """
     an abstract class for crawler clients.
    """
    __metaclass__ = ABCMeta

    def __init__(self, **kwargs):
        self.CRAWLER_NAME = None
        self.url = kwargs['url']
        self.sitename = kwargs['sitename']
        self.type = kwargs['type']
        self.flag = kwargs['flag']
        self.crawl_limit_count = 400
        self.crawl_limit_page = 20
        self.html = None
        # any characters should be in unicode.
        self.AUTHOR = None

    @abstractmethod
    def crawl(self):
        raise NotImplementedError("method crawl() should be implemented.")

    @abstractmethod
    def terminate(self):
        raise NotImplementedError("method terminate() should be implemented.")
