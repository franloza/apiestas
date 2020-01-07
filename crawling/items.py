# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from enum import Enum


class Bet(scrapy.Item):
    bookmaker = scrapy.Field()
    feed = scrapy.Field()
    date_extracted = scrapy.Field()
    bet_type = scrapy.Field()
    bet_subtype = scrapy.Field()
    odds = scrapy.Field()
    url = scrapy.Field()


class Match(scrapy.Item):
    teams = scrapy.Field()
    commence_time = scrapy.Field()
    sport = scrapy.Field()
    tournament = scrapy.Field()
    tournament_nice = scrapy.Field()
    country =  scrapy.Field()
    bets = scrapy.Field()


class Sports(Enum):
    FOOTBALL = "Football"
    BASKETBALL = "Basketball"
    TENNIS = "Tennis"
    ICE_HOCKEY ="Ice hockey"
    VOLLEYBALL = "Volleyball"


class Bookmakers(Enum):
    BET365 = "Bet365"
    BWIN = "Bwin"
    WILLIAM_HILL = "William Hill"
    INTERWETTEN = "Interwetten"
    MARCAAPUESTAS = "MARCA Apuestas"
    PAF = "Paf"
    BETFAIR = "Betfair"
    LUCKIA = "Luckia"
    SPORT888 = "888 Sport"
    SPORTIUM = "Sportium"
    CODERE = "Codere"
    MARATHON_BET = "Marathon Bet"
    BETWAY = "Betway"
    RETABET= "RETAbet"
    LEOVEGAS="LeoVegas"

