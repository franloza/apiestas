from collections import namedtuple

import scrapy
import dateparser
from datetime import datetime as dt
from datetime import timedelta as td

#from scrapy_splash import SplashRequest
#from apiestas.items import Match, Result
#from apiestas.utils.utils import extract_with_css


class LuckiaSpider(scrapy.Spider):

    # Attributes
    name = "luckia"
    rotate_user_agent = True
    main_url = 'https://sports.luckia.es/'
    pages = ['tenis']

    def start_requests(self):
        urls = [self.main_url + page for page in self.pages]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse, meta={
                'splash': {
                    'args': {
                        'html': 1,
                        'png': 1}}})

    def parse(self, response):
        # Get IDs of the tournaments
        for tournament in response.css('li.league_check'):
            id = tournament.root.attrib['onclick']
            yield SplashRequest(
                response.url,
                endpoint='render.html',
                args={'js_source': id},
                callback=self.parse_tournament
            )

    def parse_tournament(self, response):
        # TODO: ASPX Page with Javascript request. Difficult to process
        raise NotImplementedError()


    def _get_datetime(self, date_str, hour_str):
        year_str = str(dt.now().year)
        datetime = dateparser.parse(' '.join([hour_str, date_str, year_str]))
        if (datetime - dt.now()) < td(days=-1):
            datetime.year += 1
        return datetime





