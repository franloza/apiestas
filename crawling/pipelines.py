from datetime import datetime
from typing import Union

import pytz
import json
import logging
from urllib.parse import urlencode

from scrapy import Request

from . import settings as st
from .enums import Spiders


class ApiestasPipeline(object):

    def __init__(self, crawler):
        self.crawler = crawler
        self.api_endpoint = f"http://{st.APIESTAS_API_URL}/api/matches/"
        self.date_tz = pytz.timezone("Europe/Madrid")

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def process_item(self, item, spider):
        if spider.name == Spiders.OODS_PORTAL.value:
            # Match authority
            self.upsert_match(spider, item)
        else:
            if item['bets']:
                self.find_match_and_insert_bet(spider, item)
        return item

    def find_match_and_insert_bet(self, spider, item, similarity=st.APIESTAS_FIND_SIMILARITY_THRESHOLD):
        query = (
            ("commence_time", self._get_apiestas_datetime(item['commence_time'])),
            ("sport", item["sport"].value),
            ("teams", item["teams"][0]),
            ("teams", item["teams"][1]),
            ("similarity", similarity)
        )
        req = Request(f"{self.api_endpoint}find?{urlencode(query)}", callback=self.upsert_bet, method='GET',
                      meta={'item': item}, errback=self.find_match_error_callback,
                      cb_kwargs={'query': query, 'spider': spider})
        self.crawler.engine.crawl(req, spider)

    def upsert_bet(self, response, **kwargs):
        item = response.meta['item']
        spider = kwargs['spider']
        slug = json.loads(response.body)['slug']
        bet = self.get_apiestas_bets(item['bets'])[0]
        req = Request(f"{self.api_endpoint}{slug}/bets", callback=self.upset_success_callback, method='PUT',
                      body=json.dumps(bet), meta={'item': item}, errback=self.upsert_match_error_callback)
        self.crawler.engine.crawl(req, spider)

    def find_match_error_callback(self, failure):
        spider = failure.request.cb_kwargs['spider']
        item = failure.request.meta['item']
        if failure.value.response.status == 404:
            pass
        elif failure.value.response.status == 422:
            new_similarity = failure.request.cb_kwargs['query'][-1][1] + 10
            if new_similarity <= 100:
                self.find_match_and_insert_bet(spider, item, similarity=new_similarity)
        logging.error(json.loads(failure.value.response.body))

    def upsert_match(self, spider, item):
        body = self.get_apiestas_match(spider, item)
        req = Request(self.api_endpoint, callback=self.upset_success_callback, method='PUT',
                      body=json.dumps(body), meta={'item': item}, errback=self.upsert_match_error_callback)
        self.crawler.engine.crawl(req, spider)

    def upset_success_callback(self, response):
        logging.debug(json.loads(response.body))

    def upsert_match_error_callback(self, failure):
        logging.error(json.loads(failure.value.response.body))

    def get_apiestas_match(self, spider, item: dict):
        match = {
            'tournament': item['tournament'],
            'tournament_nice': item['tournament_nice'],
            'url': item['url'],
            'commence_time': self._get_apiestas_datetime(item['commence_time'])
                             if type(item['commence_time']) == str else item['commence_time'],
            "teams": item['teams'],
            "sport": item["sport"].value,
            "feed": spider.name,
            "bets": self.get_apiestas_bets(item.get("bets", []))
        }
        return match

    def get_apiestas_bets(self, item_bets:list) -> list:
        bets = []
        for bet in item_bets:
            if len(bet["odds"]) > 1:
                bet_dict = {
                        "bookmaker": bet["bookmaker"],
                        "bookmaker_nice": bet["bookmaker_nice"],
                        "is_back": bet["is_back"],
                        "bet_type": bet["bet_type"],
                        "bet_scope": bet["bet_scope"],
                        "url": bet["url"],
                        "feed": bet["feed"],
                        "odds": bet["odds"]
                    }
                bets.append(bet_dict)
        return bets

    def _get_apiestas_datetime(self, date: datetime, as_unix=False) -> Union[str, int]:
        utc_datetime = self.date_tz.localize(date, is_dst=None).astimezone(pytz.utc)
        if as_unix:
            return int(utc_datetime.timestamp())
        else:
            return utc_datetime.isoformat()

