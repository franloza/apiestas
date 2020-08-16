"""Launch the crawlers every CRAWLING_INTERVAL seconds (5 minutes by default)"""
import os
import sys
import logging
from typing import List

from crawling.enums import Spiders

sys.path.insert(0, '..')

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from twisted.internet import reactor
from twisted.internet.task import deferLater

from crawling.spiders import OddsPortalSpider

CRAWLING_INTERVAL = os.getenv('CRAWLING_INTERVAL', 300)
CRAWLERS = {
    Spiders.OODS_PORTAL: OddsPortalSpider
}


def sleep(self, *args, seconds):
    """Non blocking sleep callback"""
    return deferLater(reactor, seconds, lambda: None)


def crash(failure):
    logging.error(failure.getTraceback())


def start_in_parallel(process: CrawlerProcess, crawlers: list, **kwargs):
    def _crawl(result, spider):
        deferred = process.crawl(spider, **kwargs)
        deferred.addCallback(lambda results:
                             logging.info(f"Waiting {CRAWLING_INTERVAL} seconds to start a new crawling process"))
        deferred.addErrback(crash)
        deferred.addCallback(sleep, seconds=CRAWLING_INTERVAL)
        deferred.addCallback(_crawl, spider)
        return deferred

    process = CrawlerProcess(get_project_settings())
    for crawler in crawlers:
        _crawl(None, crawler)
    process.start()


def start_sequentially(process: CrawlerProcess, crawlers: list, **kwargs):
    print('Starting crawler {}'.format(crawlers[0].__name__))
    deferred = process.crawl(crawlers[0], **kwargs)
    deferred.addErrback(crash)
    if len(crawlers) > 1:
        deferred.addCallback(lambda _: start_sequentially(process, crawlers[1:], **kwargs))
    else:
        deferred.addCallback(lambda results:
                             logging.info(f"Waiting {CRAWLING_INTERVAL} seconds to start a new crawling process"))
        deferred.addCallback(sleep, seconds=CRAWLING_INTERVAL)
        deferred.addCallback(lambda _: start_sequentially(process, CRAWLERS))


def start_process(spiders: List[Spiders] = None, parallel=False, **kwargs):
    crawlers = [CRAWLERS[spider] for spider in spiders] or list(CRAWLERS.values())
    process = CrawlerProcess(settings=get_project_settings())
    if parallel:
        start_in_parallel(process, crawlers, **kwargs)
    else:
        start_sequentially(process, crawlers,  **kwargs)
    process.start()


if __name__ == '__main__':
    start_process()