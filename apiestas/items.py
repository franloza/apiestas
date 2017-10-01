# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class Result(scrapy.Item):
    name = scrapy.Field()
    odd = scrapy.Field()


class Match(scrapy.Item):
    result_1 = scrapy.Field()
    result_2 = scrapy.Field()
    date = scrapy.Field()
    date_extracted = scrapy.Field()
    url = scrapy.Field()
