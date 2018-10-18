from datetime import datetime as dt
from datetime import timedelta as td

import scrapy
import dateparser

from crawling.items import Match, Result
from crawling.utils.utils import extract_with_css


class MarcaApuestasSpider(scrapy.Spider):

    # Attributes
    name = "marcaapuestas"
    rotate_user_agent = True
    main_url = 'https://deportes.marcaapuestas.es/es/s/'
    pages = ['TENN/Tenis', 'BASK/Baloncesto', '/VOLL/Vóleibol']
    forbidden_categories = {'Campeón', 'Ganador', 'Ganadora'}

    def start_requests(self):
        urls = [self.main_url + page for page in self.pages]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        """Parse all the tournaments' matches of a URL associated to a sport category in MarcaApuestas.com."""
        for tournament in response.css('ul.classes li.expander'):
            for category in tournament.css('ul.types li'):
                category_name = extract_with_css(category, 'div a::text').split()
                # Exclude forbidden categories
                if len(self.forbidden_categories.intersection(set(category_name))) == 0:
                    yield response.follow(extract_with_css(category, 'div a::attr(href)'), self.parse_matches)

    def parse_matches(self, response):
        for match in response.css('table.coupon tbody tr'):
            match_item = Match()
            match_item['results'] = []
            for i, player in enumerate(match.css("td.seln")):
                try:
                    match_item['team_{}'.format(i + 1)] = extract_with_css(player, "span.seln-name::text")
                except KeyError:
                    break
                result_item = Result(name=str(i+1), odd=float(extract_with_css(player, "span.price.dec::text")))
                match_item['results'].append(dict(result_item))
                
            match_item['url'] = response.url
            match_item['date_extracted'] = dt.now()
            match_item['feed'] = self.name

            # Get datetime of the match
            date_str = extract_with_css(match, "td.time span.date::text")
            hour_str = extract_with_css(match, "td.time span.time::text")
            if date_str is not None and hour_str is not None:
                # The match is not live
                match_item['date'] = self._get_datetime(date_str, hour_str)
                yield match_item

    def _get_datetime(self, date_str, hour_str):
        year_str = str(dt.now().year)
        datetime = dateparser.parse(' '.join([hour_str, date_str, year_str]))
        if (datetime - dt.now()) < td(days=-1):
            datetime.year += 1
        return datetime





