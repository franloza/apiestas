import scrapy
import dateparser
from datetime import datetime as dt
from datetime import timedelta as td


class MarcaApuestasSpider(scrapy.Spider):
    name = "marcaapuestas"

    def start_requests(self):
        urls = [
            'https://deportes.marcaapuestas.es/es/t/30385/Individuales-Masculinos',
            'https://deportes.marcaapuestas.es/es/t/30388/Dobles-masculinos',
            'https://deportes.marcaapuestas.es/es/t/30402/Partidos-de-clasificacion-femenino',
            'https://deportes.marcaapuestas.es/es/t/30399/Individuales-Femeninos',
            'https://deportes.marcaapuestas.es/es/t/25787/Dobles-masculinos'
            ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        # page = response.url.split("/")[-2]
        # filename = 'quotes-%s.html' % page
        # with open(filename, 'wb') as f:
        #     f.write(response.body)
        # self.log('Saved file %s' % filename)
        for match in response.css('table.coupon tbody tr'):
            match_item = {'option_{}'.format(i + 1):
                              {'name': player.css("span.seln-name::text").extract_first(),
                               'odd': player.css("span.price.dec::text").extract_first()}
                          for i, player in enumerate(match.css("td.seln"))}
            match_item['url'] = response.url
            match_item['date_extracted'] = dt.now()
            match_item['date'] = self._get_datetime(
                match.css("td.time span.date::text").extract_first(),
                match.css("td.time span.time::text").extract_first())
            yield match_item


    def _get_datetime(self, date_str, hour_str):
        year_str = str(dt.now().year)
        datetime = dateparser.parse(' '.join([hour_str, date_str, year_str]))
        if (datetime - dt.now()) < td(days=-1):
            datetime.year += 1
        return datetime



