# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy import log
from fuzzywuzzy import fuzz
import pymongo
import re
from . import settings as st


class ApiestasPipeline(object):
    def __init__(self):
        self.pattern = re.compile(r'[\W_]+')
        self.collection = pymongo.MongoClient(
            st.MONGO_HOST, st.MONGO_PORT)[st.MONGO_DBNAME][st.MONGO_MATCHES_COLLECTION]

    def process_item(self, item, spider):
        # Generate ID
        _id = self.get_id(item)

        if self.collection.find_one({"_id": _id}):
            self.update_item_bets(_id, item)
        else:
            # Insert match in DB only if data comes from elcomparador. Else,
            # do fuzzy matching
            if spider.name == "elcomparador":
                item["_id"] = _id
                self.collection.insert(item)
                log.msg("Match with ID {} inserted with {} bets".format(item['_id'], len(item["bets"])),
                    level=log.DEBUG)
            else:
                new_id = self.search_fuzzy_id(_id)
                if new_id is not None:
                    self.update_item_bets(new_id, item)
                else:
                    log.msg("No similar match  has been found for ID {}"
                    .format(_id),
            level=log.DEBUG)

        return item

    def update_item_bets(self, item_id, item):
        bets = item["bets"]
        for bet in bets:
            query =  {"_id": item_id, "bets.bookmaker": bet["bookmaker"]}
            if self.collection.find(query).count() > 0:
                # If the bet exists, we update it
                self.collection.update_one(query,{"$set": {"bets.$": bet}})
            else:
                # We push it into the array the new bookmaker
                self.collection.update_one({"_id": item_id}, {"$push": {"bets": bet}})
            log.msg("Match with ID {} updated with {} bets".format(item_id, len(bets)),
                level=log.DEBUG)

    def search_fuzzy_id(self, item_id):
        # Get date from ID
        fuzzy_item_id = None
        date_str_search = re.search(r'(\d+)$', item_id)
        if date_str_search:
            date_str = date_str_search.group(1)
            regx = re.compile(r"{}$".format(date_str), re.IGNORECASE)
            candidate_ids = self.collection.find({"_id": regx},{"_id":True})
            max_score = -1
            # If any id matches with the one in DB with a minimum similarity
            # we return it. In case multiple ids are greater than the threshold,
            # we keep only the most similar one.
            for candidate_id in candidate_ids:
                score = fuzz.partial_ratio(item_id, candidate_id["_id"])
                if score > st.FUZZY_SIMILARITY_THRESHOLD and score > max_score:
                    fuzzy_item_id = candidate_id["_id"]
                    max_score = score
        return fuzzy_item_id

    def get_id(self, item):
        string = ''.join([item['team_1'], item["team_2"],
                          item['date'].strftime('%y%m%d')])
        return self.pattern.sub('', ''.join(string)).lower()


