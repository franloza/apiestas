# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from enum import Enum


class Bet(scrapy.Item):
    bookmaker = scrapy.Field()
    bookmaker_nice = scrapy.Field()
    feed = scrapy.Field()
    date_extracted = scrapy.Field()
    bet_type = scrapy.Field()
    bet_scope = scrapy.Field()
    odds = scrapy.Field()
    url = scrapy.Field()
    is_back = scrapy.Field()
    handicap = scrapy.Field()


class Match(scrapy.Item):
    teams = scrapy.Field()
    commence_time = scrapy.Field()
    sport = scrapy.Field()
    tournament = scrapy.Field()
    tournament_nice = scrapy.Field()
    country = scrapy.Field()
    bets = scrapy.Field()
    url = scrapy.Field()


