# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
import datetime
import re

from scrapy.loader.processors import MapCompose, TakeFirst, Join
from scrapy.loader import ItemLoader


class ArticlespiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


def add_jobbole(value):
    return value + "-meng"


def date_convert(value):
    try:
        create_time = datetime.datetime.strptime(value, "%Y/%m/%d").date()
    except Exception as e:
        create_time = datetime.datetime.now().date()

    return create_time


def get_nums(value):
    num_re_intance = re.match(r".*(\d+).*", value)
    # re_for_bookmark_num = re.match(r".*(\d+).*", bookmark_num)

    if num_re_intance:
        nums = int(num_re_intance.group(1))
    else:
        nums = 0

    return nums


def remove_comment_tags(value):
    # 去掉tag中提取的评论
    if "评论" in value:
        return ""
    else:
        return value


def return_value(value):
    return value


class ArticleItemLoader(ItemLoader):
    # 自定义Itemloader
    default_output_processor = TakeFirst()


class JobBoleArticleItem(scrapy.Item):
    title = scrapy.Field(
        # input_processor=MapCompose(add_jobbole)
        input_processor=MapCompose(lambda x: x + "-jobbole", add_jobbole)
    )

    create_date = scrapy.Field(
        input_processor=MapCompose(date_convert),
        # output_processor=TakeFirst()
    )

    url = scrapy.Field()

    url_object_id = scrapy.Field()

    front_image_url = scrapy.Field(
        output_processor=MapCompose(return_value),
    )

    front_image_path = scrapy.Field()

    vote_num = scrapy.Field(
        input_processor=MapCompose(get_nums),
    )

    bookmark_num = scrapy.Field(
        input_processor=MapCompose(get_nums),
    )

    comment_num = scrapy.Field(
        input_processor=MapCompose(get_nums),
    )

    info = scrapy.Field(
        input_processor=MapCompose(remove_comment_tags),
        output_processor=Join(","),
    )

    entry = scrapy.Field()
