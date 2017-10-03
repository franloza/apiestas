import json
from collections import namedtuple

import scrapy
import dateparser
from datetime import datetime as dt
from datetime import timedelta as td

from apiestas.items import Match, Result
from apiestas.utils.utils import extract_with_css
import re


class CodereSpider(scrapy.Spider):

    # Attributes
    name = "codere"
    rotate_user_agent = True
    main_url = 'https://m.apuestas.codere.es/csbgonline/home/GetSports?languageCode=es'
    sports = ['Baloncesto', 'Tenis', 'Voleibol']
    #forbidden_categories = {'Campeón', 'Ganador', 'Ganadora'}

    def start_requests(self):
        yield scrapy.Request(url=self.main_url, callback=self.parse)

    def parse(self, response):
        """Parse all the sports in sports list."""
        docs = json.loads(response.body_as_unicode())
        sport_docs = [doc for doc in docs if doc['Name'] in self.sports]
        for sport in sport_docs:
            yield self._getEvents(response, sport['NodeId'], self.parse_sport)

    def parse_sport(self, response):
        """ Parse all the tournament in the sport"""
        tournament_docs = json.loads(response.body_as_unicode())
        for tournament in tournament_docs:
            yield self._getEvents(response, tournament['ParentNodeId'], self.parse_matches)

    def parse_matches(self, response):
        matches = json.loads(response.body_as_unicode())
        for match in matches:
            for game in match['Games']:
                if game['Name'].lower() == 'ganador del partido':
                    results = game['Results']
                    match_item = Match()
                    match_item['result_1'] = Result(name=results[0]['Name'], odd=results[0]['Odd'])
                    match_item['result_2'] = Result(name=results[1]['Name'], odd=results[1]['Odd'])
                    match_item['sport'] = match['SportHandle']
                    match_item['tournament'] = match['LeagueName']
                    # Get Date
                    try:
                        match_item['date'] = dateparser.parse((re.search('(-?\d+)', match['StarDate']).group(0)))
                        match_item['date_extracted'] = dt.now()
                    except AttributeError:
                        continue
                    yield match_item

    def _getEvents(self, response, node_id, callback):
        url = 'https://m.apuestas.codere.es/csbgonline/home/GetEvents?parentid={}'.format(node_id)
        return response.follow(url, callback)


    def _get_datetime(self, date_str, hour_str):
        year_str = str(dt.now().year)
        datetime = dateparser.parse(' '.join([hour_str, date_str, year_str]))
        if (datetime - dt.now()) < td(days=-1):
            datetime.year += 1
        return datetime





