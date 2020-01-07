import logging
import urllib.parse
import js2xml
import re
import json
from urllib.parse import urlsplit, urljoin

import scrapy

from crawling.items import Match, Bet, Sports, Bookmakers


class OddsPortalSpider(scrapy.Spider):

    # Attributes
    name = "oddsportal"
    rotate_user_agent = False
    main_url = "https://www.oddsportal.com"
    download_delay = 0.25
    user_agent = ('Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.131 '
                  'Safari/537.36')
    sports_to_parse = (
        "soccer",
        "basketball",
        "tennis"
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.tournament_urls = {}
        self.bookmakers_data = {}
        self.scope_ids = {}
        self.globals = {}

    def start_requests(self):
        yield scrapy.Request(url=self.main_url, callback=self.setup,
                             headers={'user-agent': self.user_agent}, dont_filter=True)

    def setup(self, response):
        if not self.bookmakers_data:
            bookies_url = response.urljoin(response.xpath("//script[starts-with(@src, '/res/x/bookies')]").attrib['src'])
            yield scrapy.Request(url=bookies_url, callback=self.setup_bookmakers,
                                 headers={'user-agent': self.user_agent}, dont_filter=True)
        elif not self.globals:
            global_url = response.urljoin(response.xpath("//script[starts-with(@src, '/res/x/global')]").attrib['src'])
            yield scrapy.Request(url=global_url, callback=self.setup_globals,
                                 headers={'user-agent': self.user_agent}, dont_filter=True)
        else:
            yield scrapy.Request(url=self.main_url, callback=self.parse_tournaments,
                                 headers={'user-agent': self.user_agent}, dont_filter=True)

    def setup_bookmakers(self, response):
        pattern = r"\bvar\s+bookmakersData\s*=\s*(\{.*?\})\s*;\s*"
        json_data = re.search(pattern, response.text).group(1)
        self.bookmakers_data = json.loads(json_data)
        yield scrapy.Request(url=self.main_url, callback=self.setup,
                             headers={'user-agent': self.user_agent}, dont_filter=True)

    def setup_globals(self, response):
        parsed = js2xml.parse(response.text)
        globals_node = parsed.xpath('//funcdecl[@name="Globals"]')[0]
        xpath_right_assignment = '//assign[./left//identifier/@name="{name}"]/right/object'
        self.globals["betting_type_names"] = (
            js2xml.make_dict(globals_node.xpath('//functioncall[.//identifier/@name="initBettingTypes"]/arguments/object')[0]))
        self.globals["betting_type_ids"] = {value['name']:key for key,value in self.globals["betting_type_names"].items()}
        self.globals["scope_names"] = (js2xml.make_dict(globals_node.xpath(
            xpath_right_assignment.format(name='scopeNames'))[0]))
        self.globals["scope_ids"] = {value:key for key,value in self.globals["scope_names"].items()}
        self.globals["sport_data"] = (js2xml.make_dict(globals_node.xpath(
            xpath_right_assignment.format(name='sportData'))[0]))
        self.globals['sport_names'] = {value['url']: value['name'] for key, value in
                                        self.globals['sport_data'].items()}
        self.globals["sport_data_by_key"] = (js2xml.make_dict(globals_node.xpath(
            xpath_right_assignment.format(name='sportDataByKey'))[0]))
        self.globals['country_data'] = (js2xml.make_dict(globals_node.xpath(
            xpath_right_assignment.format(name='countryData'))[0]))
        self.globals['country_names'] = {value['url']: value['name'] for key, value in
                                        self.globals['country_data'].items()}
        yield scrapy.Request(url=self.main_url, callback=self.setup,
                             headers={'user-agent': self.user_agent}, dont_filter=True)

    def parse_tournaments(self, response):
        xpath = '//li[@class="tournament"]/a/{property}'
        self.tournament_urls = dict(zip(
            response.xpath(xpath.format(property="@href")).getall(),
            response.xpath(xpath.format(property="text()")).getall()))
        for tournament_url in self.tournament_urls:
            sport, country, tournament = urlsplit(tournament_url).path.split('/')[1:4]
            if sport in self.sports_to_parse:
                yield scrapy.Request(url=response.urljoin(tournament_url), callback=self.parse_matches,
                                     headers={'user-agent': self.user_agent},
                                     meta={'tournament_url': tournament_url,
                                           'sport': sport,
                                           'country': country,
                                           'tournament': tournament
                                           })
            else:
                logging.warning(f"Skipping tournament {tournament} because sport {sport} is not in sports to parse list")

    def parse_matches(self, response):
        matches = response.xpath(
                '//table[@id="tournamentTable"]//td[@class="name table-participant"]/a/@href').getall()
        for match in matches:
            yield scrapy.Request(url=response.urljoin(match),
                                 callback=self.parse, headers={'user-agent': self.user_agent}, meta=response.meta)

    def parse(self, response) -> Match:
        # Get page info
        javascript = response.xpath("//script[contains(text(),'new PageEvent')]/text()").get()
        parsed = js2xml.parse(javascript)
        page_info = js2xml.make_dict(parsed.xpath('//var[@name="page"]/new/arguments/object')[0])
        page_info['xhash'] = urllib.parse.unquote(page_info['xhash'])
        page_info['xhashf'] = urllib.parse.unquote(page_info['xhashf'])

        match_dict = {
            'sport' : response.meta['sport'],
            'tournament': response.meta['tournament'],
            'tournament_nice': self.tournament_urls[response.meta['tournament_url']],
            'teams': [page_info["home"], page_info["away"]],
            'country': response.meta["country"],
            'commence_time': int(re.search(r't(\d*)-',
                                           response.xpath('//p[contains(@class,"date datet")]')
                                           .attrib['class']).group(1)),
        }
        # TODO: Parse odds
        return Match(**match_dict)