# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html
import datetime

import scrapy
from scrapy.loader.processors import MapCompose, TakeFirst, Join
from scrapy.loader import ItemLoader
from w3lib.html import remove_tags

from settings import SQL_DATETIME_FORMAT, SQL_DATE_FORMAT, SINA_FABUSHIJIAN_TYPE


class SinaItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


def handle_time(value):
    '''
    处理新浪发布时间格式
    '''
    try:
        new_value = datetime.datetime.strptime(value, SINA_FABUSHIJIAN_TYPE)
    except:
        new_value = datetime.datetime.now()
    return new_value


def return_value(value):
    return value


def remove_content(value):
    '''处理文章格式'''
    try:
        new_value = value.replace('\t', '')
    except:
        new_value = value
    return new_value


class ArticleItemLoader(ItemLoader):
    # 自定义itemloader,值取数组的第一个，修改item中的loader
    default_output_processor = TakeFirst()


class SinaArticleItem(scrapy.Item):
    # 文章网址
    wen_zhang_wang_zhi = scrapy.Field()
    # 文章标题
    wen_zhang_biao_ti = scrapy.Field()
    # 发布时间
    fa_bu_shi_jian = scrapy.Field(
        input_processor=MapCompose(handle_time, )
    )
    # 评论数量
    ping_lun_shu_liang = scrapy.Field()
    # 参与人数
    can_yu_ren_shu = scrapy.Field()
    # 文章来源
    wen_zhang_lai_yuan = scrapy.Field()
    # 文章正文
    wen_zhang_zheng_wen = scrapy.Field(
        input_processor=MapCompose(remove_tags, remove_content),
        # output_processor=MapCompose(return_value,)
    )
    # 抓取时间
    do_time = scrapy.Field()
    # 抓取网站
    zhan_dian = scrapy.Field()
    # print'  # 图片链接'
    tu_pian_lian_jie = scrapy.Field(
        # input_processor=MapCompose(handle_null, ),
        output_processor=Join(",")
    )
    # 文章栏目
    wen_zhang_lan_mu = scrapy.Field()
    # 文章作者
    wen_zhang_zuo_zhe = scrapy.Field()
    # 关键词
    guan_jian_ci = scrapy.Field(
        output_processor=Join(",")
    )
    # 相关标签
    xiang_guan_biao_qian = scrapy.Field()

    # 阅读数量
    yue_du_shu = scrapy.Field()

    def get_insert_sql_content(self):
        if 'tu_pian_lian_jie' in self.keys():
            pass
        else:
            self['tu_pian_lian_jie'] = '无'
        if 'xiang_guan_biao_qian' in self.keys():
            pass
        else:
            self['xiang_guan_biao_qian'] = '无'
        if "guan_jian_ci" in self.keys():
            pass
        else:
            self["guan_jian_ci"]="无"
        if "wen_zhang_zuo_zhe" in self.keys():
            pass
        else:
            self["wen_zhang_zuo_zhe"]="佚名"
        insert_sql = """
        REPLACE INTO sina_article(wen_zhang_wang_zhi,wen_zhang_biao_ti,fa_bu_shi_jian,ping_lun_shu_liang,can_yu_ren_shu,
        wen_zhang_lai_yuan,wen_zhang_zheng_wen,do_time,zhan_dian,tu_pian_lian_jie,wen_zhang_lan_mu,
        wen_zhang_zuo_zhe,guan_jian_ci,xiang_guan_biao_qian)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """
        params = (
            self['wen_zhang_wang_zhi'], self['wen_zhang_biao_ti'], self['fa_bu_shi_jian'], self['ping_lun_shu_liang'],
            self['can_yu_ren_shu'],
            self['wen_zhang_lai_yuan'], self['wen_zhang_zheng_wen'], self['do_time'], self['zhan_dian'],
            self['tu_pian_lian_jie'], self['wen_zhang_lan_mu'],
            self['wen_zhang_zuo_zhe'], self['guan_jian_ci'], self['xiang_guan_biao_qian'])
        return insert_sql, params


class SinaCommentsItem(scrapy.Item):
    # 评论文章url
    news_url = scrapy.Field()
    # 评论内容
    ping_lun_nei_rong = scrapy.Field()
    # 评论时间
    ping_lun_shi_jian = scrapy.Field()
    # 回复数量
    hui_fu_shu = scrapy.Field()
    # 点赞数量
    dian_zan_shu = scrapy.Field()
    # 评论id
    ping_lun_id = scrapy.Field()
    # 用户昵称
    yong_hu_ming = scrapy.Field()
    # 性别
    xing_bie = scrapy.Field()
    # 用户等级
    yong_hu_deng_ji = scrapy.Field()
    # 用户省份
    yong_hu_sheng_fen = scrapy.Field()
    # 抓取时间
    do_time = scrapy.Field()
    # 抓取网站
    zhan_dian = scrapy.Field()
    # 主键
    ping_lun_zhujian = scrapy.Field()

    def get_insert_sql_comment(self):
        if 'hui_fu_shu' in self.keys():
            pass
        else:
            self['hui_fu_shu']='无法查看'
        if 'xing_bie' in self.keys():
            pass
        else:
            self['xing_bie']='无法查看'
        insert_sql = """
           REPLACE INTO sina_comments(news_url,ping_lun_nei_rong,ping_lun_shi_jian,hui_fu_shu,dian_zan_shu,ping_lun_id,
           yong_hu_ming,xing_bie,yong_hu_deng_ji,yong_hu_sheng_fen,do_time,zhan_dian,ping_lun_zhujian)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) 
           """
        params = (
            self['news_url'], self['ping_lun_nei_rong'], self['ping_lun_shi_jian'], self['hui_fu_shu'],
            self['dian_zan_shu'],
            self['ping_lun_id'], self['yong_hu_ming'], self['xing_bie'], self['yong_hu_deng_ji'],
            self['yong_hu_sheng_fen'], self['do_time'],
            self['zhan_dian'], self['ping_lun_zhujian'])
        return insert_sql, params
