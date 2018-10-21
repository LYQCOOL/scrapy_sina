# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import codecs
import json
import datetime

from twisted.enterprise import adbapi
import MySQLdb
import MySQLdb.cursors
from scrapy.pipelines.images import ImagesPipeline
from scrapy.exporters import JsonItemExporter

from .settings import BASE_DIR


class SinaPipeline(object):
    def process_item(self, item, spider):
        return item


class MysqlTwistedPipeline(object):
    def __init__(self, dbpool):
        self.dbpool = dbpool

    # 导入setting中的配置（固定函数）
    @classmethod
    def from_settings(cls, setting):
        # 将dbtool传入
        dbparms = dict(
            host=setting["MYSQL_HOST"],
            db=setting["MYSQL_DBNAME"],
            user=setting["MYSQL_USER"],
            password=setting["MYSQL_PASSWORD"],
            charset="utf8",
            cursorclass=MySQLdb.cursors.DictCursor,
            use_unicode=True,
        )
        # twisted异步容器，使用MySQldb模块连接
        dbpool = adbapi.ConnectionPool("MySQLdb", **dbparms)

        return cls(dbpool)

    def process_item(self, item, spider):
        # 使用Twisted将mysql插入变成异步执行
        if "wen_zhang_zheng_wen" in item.keys():
            query = self.dbpool.runInteraction(self.do_insert_content, item)
            query.addErrback(self.handle_error, item, spider)
        elif "ping_lun_id" in item.keys():
            query = self.dbpool.runInteraction(self.do_insert_comment, item)
            # 处理异常
            query.addErrback(self.handle_error, item, spider)
        else:
            query = self.dbpool.runInteraction(self.do_insert_failurl, item)
            query.addErrback(self.handle_error, item, spider)

    def handle_error(self, failure, item, spider):
        try:
            query = self.dbpool.runInteraction(self.do_insert_failurl, item)
        except Exception as e:
            error_time = datetime.datetime.today().strftime("%Y_%m_%d")
            with open(BASE_DIR + "/mysqlerrors/error_{0}.txt".format(error_time), 'a', encoding='utf-8') as f:
                if "wen_zhang_wang_zhi" in item.keys():
                    f.write('出错的文章网址:' + item['wen_zhang_wang_zhi'] + "\n" + "错误信息：" + str(failure) + "\n")
                elif "ping_lun_zhujian" in item.keys():
                    f.write('出错的评论主键:' + item['ping_lun_zhujian'] + "\n" + "错误信息：" + str(failure) + "\n")
                else:
                    f.write("不明的错误信息：" + str(failure)+"异常："+str(e))
                f.close()

    def do_insert_content(self, cursor, item):
        # 执行具体的插入
        insert_sql, params = item.get_insert_sql_content()
        cursor.execute(insert_sql, params)

    def do_insert_comment(self, cursor, item):
        # 执行具体的插入
        insert_sql, params = item.get_insert_sql_comment()
        cursor.execute(insert_sql, params)

    def do_insert_failurl(self, cursor, item):
        error_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        insert_sql = """
        insert into logs(news_url,error_type,error_message,zhan_dian,error_time)
        value(%s,%s,%s,%s,%s)"""
        if "wen_zhang_zheng_wen" in item.keys():
            params = (item['wen_zhang_wang_zhi'], 2, "文章内容相关信息获取丢失或出错" ,1, error_time)
        elif "ping_lun_id" in item.keys():
            params = (item['wen_zhang_wang_zhi'], 3, "文章评论相关信息获取丢失或出错",1, error_time)
        else:
            params=(item['wen_zhang_wang_zhi'],1,"数据库错误",1,error_time)
        cursor.execute(insert_sql, params)
