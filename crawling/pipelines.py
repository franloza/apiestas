import pytz
import json
import logging

from scrapy import Request

from . import settings as st


class ApiestasPipeline(object):

    def __init__(self, crawler):
        self.crawler = crawler
        self.api_host = f"{st.APIESTAS_API_HOST}:{st.APIESTAS_API_PORT}"
        self.date_tz = pytz.timezone("Europe/Madrid")

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def process_item(self, item, spider):
        if spider.name == "elcomparador":
            self.upsert_match(spider, item)
        else:
            pass
        return item

    def upsert_match(self, spider, item):
        body = self.get_apiestas_match(spider, item)
        req = Request(f"http://{self.api_host}/api/matches/", callback=self.upset_match_success_callback, method='PUT',
                      body=json.dumps(body), meta={'item': item}, errback=self.upsert_match_error_callback)
        self.crawler.engine.crawl(req, spider)

    def upset_match_success_callback(self, response):
        logging.debug(json.loads(response.body))

    def upsert_match_error_callback(self, failure):
        logging.error(json.loads(failure.value.response.body))

    def get_sport_code(self, sport: str):
        return sport.replace(' ', '_').lower()

    def get_apiestas_match(self, spider, item: dict):
        match = {
            'tournament': item['tournament'],
            'commence_time':
                self.date_tz.localize(item['date'], is_dst=None).astimezone(pytz.utc).strftime("%Y-%m-%dT%H:%M:%S%z"),
            "teams": [item['team_1'], item['team_2']],
            "sport": self.get_sport_code(item["sport"]),
            "feed": spider.name,
        }
        if item["bets"]:
            match['bets'] = self.get_apiestas_bets(item["bets"])
        return match

    def get_apiestas_bets(self, item_bets:list) -> list:
        bets = []
        for bet in item_bets:
            bet_dict = {
                    "bookmaker": bet["bookmaker"],
                    "url": bet["url"],
                    "feed": bet["feed"]
                }
            bet_odds = dict(bet['odds'])
            if len(bet_odds) == 3 and 'X' in bet_odds:
                # There is a draw. Append at the end
                draw_odds = bet_odds.pop('X')
                odds = list(bet_odds.values())
                odds.append(draw_odds)
            elif len(bet_odds) >= 2:
                odds = list(bet_odds.values())
            else:
                continue
            bet_dict['odds'] = odds
            bets.append(bet_dict)
        return bets


