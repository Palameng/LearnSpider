# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import codecs
import json
import MySQLdb
import MySQLdb.cursors

from scrapy.pipelines.images import ImagesPipeline
from scrapy.exporters import JsonItemExporter
from twisted.enterprise import adbapi   # 可以将mysql对db的操作转化成异步操作


class ArticlespiderPipeline(object):
    def process_item(self, item, spider):
        return item


class ArticleImagePipeline(ImagesPipeline):
    def item_completed(self, results, item, info):
        for ok, value in results:
            image_file_path = value["path"]
        item["front_image_path"] = image_file_path

        return item


class JsonExporterPipleline(object):
    """
    调用scrapy提供的json export导出的json文件
    """
    def __init__(self):
        self.file = open('articleexport.json', 'wb')
        self.exporter = JsonItemExporter(self.file, encoding="utf-8", ensure_ascii=False)
        self.exporter.start_exporting()

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item


class JsonWithEncodingPipeline(object):
    """
    自定义json文件的导出
    """
    def __init__(self):
        self.file = codecs.open('article.json', 'w', encoding='utf-8')

    def process_item(self, item, spider):
        lines = json.dumps(dict(item), ensure_ascii=False) + "\n"
        self.file.write(lines)
        return item

    def spider_closed(self, spider):
        self.file.close()


class MysqlPipeline(object):
    """
    采用同步的机制写入mysql
    """
    def __init__(self):
        self.conn = MySQLdb.connect('127.0.0.1', 'root', '123456', 'article_spider', charset="utf8", use_unicode=True)
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):
        insert_sql = """
            insert into article(title, create_date, url, bookmark_num)
            VALUES(%s, %s, %s, %s)
        """
        self.cursor.execute(insert_sql, (item["title"], item["create_date"], item["url"], item["bookmark_num"]))
        self.conn.commit()


class MysqlTwistedPipeline(object):
    """
    当scrapy下载页面组装items的时候，其速度是远快于对mysql的插入操作速度的，
    正因为如此需要使用Twisted使得mysql的操作转变为异步操作
    """
    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        dbparams = dict(
                            host=settings["MYSQL_HOST"],
                            db=settings["MYSQL_DBNAME"],
                            user=settings["MYSQL_USER"],
                            passwd=settings["MYSQL_PASSWORD"],
                            charset='utf8',
                            cursorclass=MySQLdb.cursors.DictCursor,
                            use_unicode=True,
                        )

        dbpool = adbapi.ConnectionPool("MySQLdb", **dbparams)
        return cls(dbpool)

    def process_item(self, item, spider):
        """
        使用twisted将mysql插入变成异步执行
        :param item:
        :param spider:
        :return:
        """
        query = self.dbpool.runInteraction(self.do_insert, item)
        query.addErrback(self.handle_error) # 处理异常

    def handle_error(self, failure):
        # 处理异步插入的异常
        print(failure)

    def do_insert(self, cursor, item):
        # 执行具体的插入
        insert_sql = """
            insert into article(title, create_date, url, bookmark_num)
            VALUES(%s, %s, %s, %s)
        """
        cursor.execute(insert_sql, (item["title"], item["create_date"], item["url"], item["bookmark_num"]))

