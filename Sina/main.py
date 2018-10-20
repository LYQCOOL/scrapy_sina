# _*_ encoding:utf-8 _*_
__author__ = 'LYQ'
__date__ = '2018/10/13 20:30'
import os
import sys
from scrapy.cmdline import execute
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
execute(['scrapy','crawl','sina','-s','FEED_EXPORT_ENCODING=utf8mb4'])

