from datetime import datetime as dt
from datetime import timedelta as td

import scrapy
import dateparser

from crawling.items import Match
from crawling.utils.utils import extract_with_css

# TODO: Adapt it to new item structure
class SportiumSpider(scrapy.Spider):

    # Attributes
    name = "sportium"
    rotate_user_agent = True
    main_url = 'http://sports.sportium.es/es/'
    pages = ['tennis', 'volleyball']

    def start_requests(self):
        urls = [self.main_url + page for page in self.pages]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        """Parse all the tournaments' matches of a URL associated to a sport category in Sportium.es."""
        for tournament in response.css('ul.classes li.expander ul.types li'):
            yield response.follow(extract_with_css(tournament, 'div a::attr(href)'), self.parse_matches)

    def parse_matches(self, response):
        for match in response.css('table.coupon tbody tr'):
            match_item = Match()
            match_item['odds'] = {}
            for i, player in enumerate(match.css("td.seln")):
                match_item['odds'][extract_with_css(player, "span.seln-name::text")] = float(extract_with_css(player, "span.price.dec::text"))
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
        print(datetime)
        if (datetime - dt.now()) < td(days=-1):
            datetime.year += 1
        return datetime





