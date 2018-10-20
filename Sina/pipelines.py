# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import codecs
import json

from twisted.enterprise import adbapi
import MySQLdb
import MySQLdb.cursors
from scrapy.pipelines.images import ImagesPipeline
from scrapy.exporters import JsonItemExporter



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
            print('item出错')



    def handle_error(self, failure, item, spider):
        print(failure)
        print(item)

    def do_insert_content(self, cursor, item):
        # 执行具体的插入
        insert_sql, params = item.get_insert_sql_content()
        cursor.execute(insert_sql, params)

    def do_insert_comment(self, cursor, item):
        # 执行具体的插入
        insert_sql, params = item.get_insert_sql_comment()
        cursor.execute(insert_sql, params)
