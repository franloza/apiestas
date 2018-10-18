# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy import log
import pymongo
import re
from db.mongo import MongoDB
from db import settings as st


class ApiestasPipeline(object):
    def __init__(self):
        self.pattern = re.compile(r'[\W_]+')
        self.collection = MongoDB(st.MONGO_MATCHES_COLLECTION).collection

    def process_item(self, item, spider):
        # Generate ID and set feed
        item['id'] = self.get_id(item)

        # Insert or update document in DB
        filter = {'feed': item["feed"], 'id': item['id']}
        self.collection.update(filter, item, upsert=True)
        log.msg("Match with ID {} added to the matches database".format(item['id']),
                level=log.DEBUG)
        return item

    def get_id(self, item):
        string = ''.join([item['team_1'], item["team_2"],
                          item['date'].strftime('%y%m%d')])
        return self.pattern.sub('', ''.join(string)).lower()


