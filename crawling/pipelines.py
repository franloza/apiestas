# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy import log
import pymongo
import re
from . import settings as st


class ApiestasPipeline(object):
    def __init__(self):
        self.pattern = re.compile(r'[\W_]+')
        self.collection = pymongo.MongoClient(
            st.MONGO_HOST, st.MONGO_PORT)[st.MONGO_DBNAME][st.MONGO_MATCHES_COLLECTION]

    def process_item(self, item, spider):
        # Generate ID and set feed
        _id = self.get_id(item)

        if self.collection.find_one({"_id": _id}):
            # Update bets
            bets = item["bets"]
            for bet in bets:   
                self.collection.update({"_id": _id, "bets.bookmaker": bet["bookmaker"]},
                        {"$set": {"bets.$": bet}})
            log.msg("Match with ID {} updated with {} bets".format(_id, len(bets)),
                level=log.DEBUG)
        else:
            # Insert match in DB
            item["_id"] = _id
            self.collection.insert(item)
            log.msg("Match with ID {} inserted with {} bets".format(item['_id'], len(item["bets"])),
                level=log.DEBUG)
        return item

    def get_id(self, item):
        string = ''.join([item['team_1'], item["team_2"],
                          item['date'].strftime('%y%m%d')])
        return self.pattern.sub('', ''.join(string)).lower()


