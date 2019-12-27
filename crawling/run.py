"""Launch the crawlers every CRAWLING_INTERVAL seconds (5 minutes by default)"""
import os
import sys
import logging

sys.path.insert(0, '..')

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from twisted.internet import reactor
from twisted.internet.task import deferLater

from .spiders.elcomparador import ElComparadorSpider
from .spiders.codere import CodereSpider

CRAWLING_INTERVAL = os.getenv('CRAWLING_INTERVAL', 300)


def sleep(self, *args, seconds):
    """Non blocking sleep callback"""
    return deferLater(reactor, seconds, lambda: None)


def crash(failure):
    logging.error(failure.getTraceback())


def crawl(process, spider):
    def _crawl(result, spider):
        deferred = process.crawl(spider)
        deferred.addCallback(lambda results:
                             logging.info(f"Waiting {CRAWLING_INTERVAL} seconds to start a new crawling process"))
        deferred.addErrback(crash)
        deferred.addCallback(sleep, seconds=CRAWLING_INTERVAL)
        deferred.addCallback(_crawl, spider)
        return deferred
    _crawl(None, spider)


def run():
    process = CrawlerProcess(get_project_settings())
    crawl(process, ElComparadorSpider)
    crawl(process, CodereSpider)
    process.start()


