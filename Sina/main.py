# _*_ encoding:utf-8 _*_
__author__ = 'LYQ'
__date__ = '2018/10/13 20:30'
import os
import sys

from scrapy.cmdline import execute
import schedule

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def begin_crawl():
    execute(['scrapy', 'crawl', 'sina', '-s', 'FEED_EXPORT_ENCODING=utf8mb4'])


schedule.every().day.at("19:36").do(begin_crawl)

if __name__=="__main__":
    while True:
        try:
            schedule.run_pending()
        except:
            pass
