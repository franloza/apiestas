# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy import log
from scrapy.conf import settings
import pymongo
import re


class ApiestasPipeline(object):
    def __init__(self):
        self.pattern = re.compile('[\W_]+')
        uri = "mongodb://{user}:{password}@{host}:{port}/{db}?authSource={auth_source}".format(
            user=settings['MONGODB_USER'],
            password=settings['MONGODB_PASSWORD'],
            host=settings['MONGODB_HOST'],
            port=settings['MONGODB_PORT'],
            db=settings['MONGODB_DB'],
            auth_source=settings['MONGODB_AUTHSOURCE']
        )
        connection = pymongo.MongoClient(uri)
        db = connection[settings['MONGODB_DB']]
        self.collection = db[settings['MONGODB_COLLECTION']]

    def process_item(self, item, spider):
        # Generate ID and set feed
        item['id'] = self.get_id(item)
        item['feed'] = spider.name

        # Insert or update document in DB
        filter = {'feed': spider.name, 'id': item['id']}
        self.collection.update(filter, item, upsert=True)
        log.msg("Match with ID {} added to the matches database".format(item['id']),
                level=log.DEBUG, spider=spider)
        return item

    def get_id(self, item):
        string = ''.join([item['result_1']['name'],
                          item['result_2']['name'],
                          item['date'].strftime('%y%m%d')])
        return self.pattern.sub('', ''.join(string)).lower()


