# _*_ encoding:utf-8 _*_
__author__ = 'LYQ'
__date__ = '2018/10/13 12:01'
import requests
from scrapy.selector import Selector
url='https://news.sina.com.cn/society/'
content=requests.get(url)
selector=Selector(content)
# s=selector.css('ul.seo_data_list li a::attr(href)').extract()
s=selector.css('.feed-card-content').extract()
for a in s:
    print(a)

