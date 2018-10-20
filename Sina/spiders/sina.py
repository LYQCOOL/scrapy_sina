# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
import re
import time
import datetime
import json
import re

from Sina.items import ArticleItemLoader, SinaArticleItem, SinaCommentsItem


class SinaSpider(scrapy.Spider):
    name = 'sina'
    allowed_domains = ['news.sina.com.cn', 'comment5.news.sina.com.cn', 'ent.sina.com.cn',
                       'sports.sina.com.cn', 'finance.sina.com.cn', 'news.sina.com.cn/china']
    start_urls = ['https://news.sina.com.cn/society/',
                  'http://ent.sina.com.cn/',
                  'http://sports.sina.com.cn/',
                  'https://finance.sina.com.cn/',
                  'https://news.sina.com.cn/china/']
    time_today=time.strftime("%Y-%m-%d", time.localtime(time.time()))
    re_list = ['https?://news.sina.com.cn/[a-z]{1,2}/%s/doc-[a-z]{8}\d{7}.shtml' % time_today,
               'http://ent.sina.com.cn/[a-z]+/[a-z]+/%s/doc-[a-z]{8}\d{7}.shtml' % time_today,
               'http://sports.sina.com.cn/[a-z]+/[a-z]+/%s/doc-[a-z]{8}\d{7}.shtml' % time_today,
               'https?://finance.sina.com.cn/[a-z]+/[a-z]+/%s/doc-[a-z]{8}\d{7}.shtml' % time_today,
               'https?://news.sina.com.cn/[a-z]{1,2}/%s/doc-[a-z]{8}\d{7}.shtml' % time_today]

    def parse(self, response):
        all_html=response.text
        num=self.start_urls.index(response.url)
        #获取<ul class="seo_data_list"></ul>中的url（即最新新闻）
        # url_list = response.css('ul.seo_data_list li a::attr(href)').extract()
        url_list=set(re.findall(self.re_list[num],all_html))
        today_time = time.strftime("%Y-%m-%d", time.localtime(time.time()))
        for url in url_list:
            this_time = re.search('\d{4}-\d{2}-\d{2}', url)
            comments_url = 'http://comment5.news.sina.com.cn/page/info?version=1&format=js&channel=sh&newsid=comos-{0}&group=0&compress=0&ie=gbk&oe=gbk&page=1&page_size=20'.format(
                re.split('[\-.]', url)[-2][1:])
            if this_time:
                this_time = this_time.group(0)
                if today_time == this_time:
                    yield Request(url, meta={'comments_url': comments_url}, callback=self.parse_detail)
                else:
                    pass
            else:
                pass

    def parse_detail(self, response):
        item_loader = ArticleItemLoader(item=SinaArticleItem(), response=response)
        comments_url = response.meta.get('comments_url', '')
        item_loader.add_value('wen_zhang_wang_zhi', response.url)
        item_loader.add_css('wen_zhang_biao_ti', 'h1.main-title::text')
        item_loader.add_css('fa_bu_shi_jian', 'span.date::text')
        # item_loader.add_css('ping_lun_shu_liang', 'span.count em a:nth-child(1)::text')
        # item_loader.add_css('can_yu_ren_shu', 'span.count em a:nth-child(2)::text')
        item_loader.add_xpath('wen_zhang_lai_yuan', '(//div[@class="date-source"/a/text)|(//div[@class="date-source"]/span[2]/text())')
        item_loader.add_css('wen_zhang_zheng_wen', 'div.article ')
        item_loader.add_value('do_time', datetime.datetime.now())
        item_loader.add_value('zhan_dian', '新浪网')
        item_loader.add_css('tu_pian_lian_jie', 'div.img_wrapper img::attr(src)')
        item_loader.add_css('wen_zhang_lan_mu', 'div.channel-path a::text')
        item_loader.add_xpath('wen_zhang_zuo_zhe',
                              '(//p[@class="article-editor"]/text())|(//div[@class="show_author"]/text())|(//p[@class="show_author"])/text()')
        item_loader.add_css('guan_jian_ci', 'div.keywords a::text')
        item_loader.add_xpath('xiang_guan_biao_qian',
                              '(//section[@class="article-a_keywords"])|(//p[@class="art_keywords"])')
        # return item_loader.load_item()
        yield Request(comments_url, meta={'item_loader': item_loader}, callback=self.parse_comments)

    def parse_comments(self, response):
        item_loader = response.meta.get('item_loader', '')
        all_comments = response.text
        json_comments = json.loads(re.match('var data=(.*)', all_comments).group(1))["result"]
        if "count" in json_comments.keys():
            item_loader.add_value('can_yu_ren_shu', json_comments['count']['total'])
            item_loader.add_value('ping_lun_shu_liang', json_comments['count']['show'])
            yield item_loader.load_item()
            try:
                new_comments = json_comments['cmntlist']
                news_url = item_loader.load_item()['wen_zhang_wang_zhi']
                if new_comments:
                    yield Request(url=response.url,
                                  meta={"all_page": int(json_comments['count']['show']) / 20, 'news_url': news_url},
                                  callback=self.parse_comments_detail, dont_filter=True)
                else:
                    pass
            except:
                pass
        else:
            item_loader.add_value('can_yu_ren_shu', 0)
            item_loader.add_value('ping_lun_shu_liang', 0)
            yield item_loader.load_item()

    def parse_comments_detail(self, response):
        all_page = response.meta.get('all_page', '')
        news_url = response.meta.get('news_url', '')
        all_comments = response.text
        json_comments = json.loads(re.match('var data=(.*)', all_comments).group(1))["result"]
        new_comments = json_comments['cmntlist']
        for comment in new_comments:
            comment_loader = ArticleItemLoader(item=SinaCommentsItem(), response=response)
            comment_loader.add_value('news_url', news_url)
            comment_loader.add_value('ping_lun_nei_rong', comment['content'])
            comment_loader.add_value('ping_lun_shi_jian', comment['time'])
            comment_loader.add_value('hui_fu_shu', None)
            comment_loader.add_value('dian_zan_shu', comment['agree'])
            comment_loader.add_value('ping_lun_id', comment['mid'])
            comment_loader.add_value('yong_hu_ming', comment['nick'])
            comment_loader.add_value('xing_bie', None)
            comment_loader.add_value('yong_hu_deng_ji', comment['level'])
            comment_loader.add_value('yong_hu_sheng_fen', comment['area'])
            comment_loader.add_value('do_time', datetime.datetime.now())
            comment_loader.add_value('zhan_dian', '新浪网')
            comment_loader.add_value('ping_lun_zhujian', comment['mid'] + news_url)
            # print(comment_loader.load_item())
            yield comment_loader.load_item()
        if int(all_page) > 1:
            the_num = re.match('.*page=(\d+).*', response.url).group(1)
            try:
                the_num = int(the_num)
                the_next_num = the_num + 1
                the_next_url = response.url.replace("page={0}".format(the_num), "page={0}".format(the_next_num))
                all_page = all_page - 1
                yield Request(url=the_next_url,meta={'news_url':news_url}, callback=self.parse_comments_detail)
            except:
                pass


class UpdateCommentSpider(scrapy.Spider):
    #更新评论，待写入，目前用不到
    pass
