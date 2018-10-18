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
    id = scrapy.Field()
    team_1 = scrapy.Field()
    team_2 = scrapy.Field()
    results = scrapy.Field()
    date = scrapy.Field()
    date_extracted = scrapy.Field()
    url = scrapy.Field()
    feed = scrapy.Field()
    sport = scrapy.Field()
    tournament = scrapy.Field()
