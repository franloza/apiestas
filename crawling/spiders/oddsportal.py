import logging
import urllib.parse
from datetime import datetime

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
    odds_main_url = "https://fb.oddsportal.com"
    download_delay = 0.25
    user_agent = ('Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.131 '
                  'Safari/537.36')
    sports_to_parse = (
        #"soccer",
        #"basketball",
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

        # Constant variables
        self.globals['cons'] = js2xml.make_dict(
            globals_node.xpath('//assign[./left//identifier/@name="cons"]/right/object')[0])
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
                logging.debug(f"Skipping tournament {tournament} because sport {sport} is not in sports to parse list")

    def parse_matches(self, response):
        matches = response.xpath(
                '//table[@id="tournamentTable"]//td[@class="name table-participant"]/a/@href').getall()
        for match in matches:
            yield scrapy.Request(url=response.urljoin(match),
                                 callback=self.parse_match, headers={'user-agent': self.user_agent}, meta=response.meta)

    def parse_match(self, response):
        # Get page info
        javascript = response.xpath("//script[contains(text(),'new PageEvent')]/text()").get()
        parsed = js2xml.parse(javascript)
        page_info = js2xml.make_dict(parsed.xpath('//var[@name="page"]/new/arguments/object')[0])
        page_info['xhash'] = urllib.parse.unquote(page_info['xhash'])
        page_info['xhashf'] = urllib.parse.unquote(page_info['xhashf'])
        response.meta['page_info'] = page_info

        match_dict = {
            'sport' : response.meta['sport'],
            'tournament': response.meta['tournament'],
            'tournament_nice': self.tournament_urls[response.meta['tournament_url']],
            'teams': [page_info["home"], page_info["away"]],
            'country': response.meta["country"],
            'commence_time': int(re.search(r't(\d*)-',
                                           response.xpath('//p[contains(@class,"date datet")]')
                                           .attrib['class']).group(1)),
            'url': response.url
        }
        response.meta['match'] = match_dict

        # Get default betting type and scope ID
        sport_id = str(page_info['sportId'])
        betting_type_id = '3' if self.globals['cons']['moneyLineSports'].get(page_info['sportId']) else '1'
        scope_id = 2
        if (self.globals['cons']['sportBetTypeScopeId'].get(sport_id) and
                self.globals['cons']['sportBetTypeScopeId'][sport_id].get(betting_type_id)):
            scope_id = self.globals['cons']['sportBetTypeScopeId'][sport_id].get(betting_type_id)
        elif self.globals['cons']['betTypeScopeId'].get(betting_type_id):
            scope_id =  self.globals['cons']['betTypeScopeId'].get(betting_type_id)
        elif self.globals['cons']['sportScopeId'].get(sport_id):
            scope_id = self.globals['cons']['sportScopeId'].get(sport_id)

        odds_url = (f'/feed/match/{page_info["versionId"]}-{sport_id}-{page_info["id"]}' 
                    f'-{betting_type_id}-{scope_id}-{page_info["xhash"]}.dat')
        response.meta['first'] = True
        response.meta['betting_type_id'] = betting_type_id
        response.meta["scope_id"] = scope_id
        response.meta["match_url"] = response.url

        yield scrapy.Request(url=urljoin(self.odds_main_url,odds_url),
                             callback=self.parse, headers={'user-agent': self.user_agent,
                                                           'referer': response.url},
                             meta=response.meta)

    def parse(self, response) -> Match:
        parsed = js2xml.parse(response.text)
        parsed_dict = js2xml.make_dict(parsed.xpath('//functioncall/arguments/object')[0])
        if response.meta['first']:
            response.meta['first'] = False
            if parsed_dict.get('d', {}).get('nav'):
                for betting_type_id in parsed_dict['d']['nav']:
                    for scope_id in parsed_dict['d']['nav'][betting_type_id]:
                        odds_url = (f'/feed/match/{response.meta["page_info"]["versionId"]}-'
                                    f'{response.meta["page_info"]["sportId"]}-{response.meta["page_info"]["id"]}'
                                    f'-{betting_type_id}-{scope_id}-{response.meta["page_info"]["xhash"]}.dat')
                        yield scrapy.Request(url=urljoin(self.odds_main_url, odds_url),
                                             callback=self.parse, headers={'user-agent': self.user_agent,
                                                                           'referer': response.url},
                                             meta=response.meta)
            else:
                # There are not odds available for this event.
                match = dict(response.meta['match'])
                match['bets'] = []
                yield Match(**match)
        else:

            for bet_l1 in parsed_dict.get('d', {}).get('oddsdata', []):
                # Bet Level 1: Back or Lay
                for bet_l2 in parsed_dict['d']['oddsdata'][bet_l1]:
                    # Bet Level 2: Odds, volume, movement and bet information
                    bet_info = parsed_dict['d']['oddsdata'][bet_l1][bet_l2]
                    bets = []
                    for bookmaker_id in bet_info['odds']:
                        bet_type = self.globals["betting_type_names"][str(response.meta["betting_type_id"])]['name']
                        odds =  bet_info['odds'][bookmaker_id]
                        if type(odds) == dict:
                            if bet_type == "1X2":
                                odds = [odds[odd_type] for odd_type in ('1', '2', 'X') if odd_type in odds]
                            else:
                                odds = list(odds.values())
                        bet_dict = {
                            "bookmaker": self.bookmakers_data[bookmaker_id]['WebUrl'],
                            "bookmaker_nice": self.bookmakers_data[bookmaker_id]['WebName'],
                            "feed" :  self.name,
                            "date_extracted" :  datetime.utcnow(),
                            "bet_type":  bet_type,
                            "bet_scope":
                                self.globals["scope_names"][str(response.meta["scope_id"])].replace('&nbsp;', ' '),
                            "odds" : odds,
                            "url" :  response.url,
                            "is_back":  bet_info['isBack'],
                        }
                        bet = Bet(**bet_dict)
                        bets.append(bet)
                    match = dict(response.meta['match'])
                    match['bets'] = bets
                    yield Match(**match)
