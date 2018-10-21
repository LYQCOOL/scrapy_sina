# _*_ encoding:utf-8 _*_
__author__ = 'LYQ'
__date__ = '2018/10/13 12:01'
import requests
from scrapy.selector import Selector
import datetime
# url='https://news.sina.com.cn/society/'
# content=requests.get(url)
# selector=Selector(content)
# # s=selector.css('ul.seo_data_list li a::attr(href)').extract()
# s=selector.css('.feed-card-content').extract()
# for a in s:
#     print(a)
# error_time=datetime.datetime.today().strftime("%Y_%m_%d")
# # print(error_time)
# with open('Sina/mysqlerrors/error_{0}.txt'.format(error_time),'a') as f:
#     f.write('adsa')
#     f.close()
import  MySQLdb
db=MySQLdb.Connect(host="localhost",db="news",user="root",passwd="112358")

