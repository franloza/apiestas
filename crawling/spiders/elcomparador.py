from datetime import datetime as dt
from datetime import timedelta as td
from urllib import parse
import re

import scrapy
import dateparser

from crawling.items import Match, Result, Bet, Sports, Bookmakers
from crawling.utils.utils import extract_with_css


class ElComparadorSpider(scrapy.Spider):

    # Attributes
    name = "elcomparador"
    rotate_user_agent = True
    main_url = 'http://www.elcomparador.com/html/contenido/mas_partidos.php?deporte={sport}&fecha={date}'

    SPORTS_MAP = {1: Sports.FOOTBALL, 23: Sports.BASKETBALL, 2: Sports.TENNIS,
                  5: Sports.ICE_HOCKEY}
    BOOKMAKERS_MAP = {
        "bet365": Bookmakers.BET365,
        "bwin": Bookmakers.BWIN, 
        "willhill": Bookmakers.WILLIAM_HILL,
        "interwetten": Bookmakers.INTERWETTEN,
        "marcaapuestas": Bookmakers.MARCAAPUESTAS,
        "paf": Bookmakers.PAF,
        "betfair": Bookmakers.BETFAIR,
        "luckia": Bookmakers.LUCKIA,
        "sport888": Bookmakers.SPORT888,
        "sportium": Bookmakers.SPORTIUM}
    URL_MAP = {
            Bookmakers.BET365 : "http://www.bet365.com/betslip/instantbet/default.aspx?{}",
            Bookmakers.WILLIAM_HILL :'http://sports.williamhill.es/bet_esp/es/betting/e/{}',
            Bookmakers.SPORT888 : 'https://www.888sport.es/apuestas-online/',
            Bookmakers.MARCAAPUESTAS : 'https://deportes.marcaapuestas.es/es/',
            Bookmakers.BWIN : "{}",
            Bookmakers.BETFAIR : "{}",
            Bookmakers.INTERWETTEN : "https://www.interwetten.es/es/apuestas-deportivas/",
            Bookmakers.PAF : "https://www.paf.es/betting/fixed_odds#/",
            Bookmakers.SPORTIUM : "https://sports.sportium.es/es",
            Bookmakers.LUCKIA : "'https://www.luckia.es/apuestas/?btag=#/event/{}'"
        }
    TIME_WINDOW = 7 # Days

    def start_requests(self):
        dates = [dt.now() + td(days=i) for i in range(0, self.TIME_WINDOW)]
        for sport in self.SPORTS_MAP.keys():
            for date in dates:
                url = self.main_url.format(sport=sport, date=date.strftime("%Y-%m-%d"))
                yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        """Parse all the sports"""
        tournament_name = ""
        bookmakers = None
        qry_params = parse.urlparse(response.url).query
        date = parse.parse_qs(qry_params)["fecha"][0]
        sport = self.SPORTS_MAP[int(parse.parse_qs(qry_params)["deporte"][0])].value
        # Check if there are matches for this date
        if response.css(".sin_partidos"):
            self.logger.info('No matches for date %s and sport %s', date, sport)
            return
        for element in response.selector.xpath("//body/div"):
            identifier = element.xpath("@id").extract()[0]           
            if identifier == "separador":
                # New tournament
                tournament_name = extract_with_css(element.css(".titulo_comp"), "::text")\
                                  .split("-")[-1].strip()
            elif identifier == "contenedor_evento":
                if element.css("span"):
                    # New match
                    match_item = Match()
                    match_item["tournament"] = tournament_name
                    # Get time of match
                    match_datetime = "{date} {hour}".format(
                        date=date,
                        hour=extract_with_css(element.css("span"), "::text"))
                    match_item["date"] = dt.strptime(match_datetime, "%Y-%m-%d %H:%M")
                    # Get teams
                    teams = element.css(".equipo")
                    if len(teams) == 2:
                        match_item["team_1"] = extract_with_css(teams[0], "::text")
                        match_item["team_2"] = extract_with_css(teams[1], "::text")
                    else:
                        continue
                    # Get bets
                    results = element.css("div#contenedor_cuotas div#fila_cuotas")
                    bets = {}
                    for result_elem in results:
                        result_name = extract_with_css(result_elem, ".apuesta::text")
                        if result_name == "X":
                            bookmakers_odds = result_elem.css("div.par")
                        else:
                            bookmakers_odds = result_elem.css("div.impar")
                        if len(bookmakers_odds) == len(bookmakers):
                            for idx, odds_elem in enumerate(bookmakers_odds):
                                # Get odds
                                if odds_elem.css("a"):
                                    url_js = odds_elem.xpath("a/@href").extract()[0]
                                    url = self.get_url_bet_from_js(url_js)
                                    odds = float(extract_with_css(odds_elem.xpath("a"), "::text"))
                                    if bookmakers[idx].value not in bets:
                                        bets[bookmakers[idx].value] = Bet(
                                            {'bookmaker': bookmakers[idx].value,
                                             'url': url, 'feed': self.name, 'results': [],
                                             'date_extracted': dt.now()})
                                    bets[bookmakers[idx].value]["results"].append(
                                        Result({"name": result_name, "odds": odds})
                                    )
                        else:
                            break
                    match_item["bets"] = list(bets.values())                          
                    match_item["sport"] = sport
                    yield match_item
                else:
                    # Get bookmakers
                    bookmakers = []
                    bookmakers_elems = element.css("div#celda_logos a img")
                    for elem in bookmakers_elems:
                        elem_name = elem.xpath("@src").extract()[0]
                        elem_search = re.search(r'(\w+).png$', elem_name, re.IGNORECASE)
                        if elem_search:
                            bookmakers.append(self.BOOKMAKERS_MAP[elem_search.group(1)])

    def get_url_bet_from_js(self, js_str):
        elem_search = re.search(r"\('?(.*)'?,'(.*)','?(.*)?', ?'?(.*)'?\)", js_str)
        if elem_search:
            bookmaker_id = elem_search.group(1)
            bookmaker = elem_search.group(2)
            deeplink_coupon = elem_search.group(3)
            destination_id = elem_search.group(4)
            try:      
                return self.get_bet_url(bookmaker_id, bookmaker, deeplink_coupon, destination_id)
            except Exception:
                return ""

    def get_bet_url(self, bookmaker_id, bookmaker, deeplink_coupon, destination_id):
        return self.URL_MAP[self.BOOKMAKERS_MAP[bookmaker]].format(deeplink_coupon)


