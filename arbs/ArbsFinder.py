from twisted.python.compat import izip
from apiestas.utils.db import MongoDB
import json
from fuzzywuzzy import fuzz
from sklearn.metrics.pairwise import pairwise_distances
from itertools import combinations
from bson.json_util import dumps
from pandas.io.json import json_normalize
import pandas as pd


class ArbsFinder:
    SIMILARITY_THRESHOLD = 75

    def __init__(self):
        self.collection = MongoDB().collection
        self.matches = self.get_matches()

    def find_arbs(self):
        # Set possible combinations of feeds to find arbs in pairs
        feeds = self.matches.feed.unique()
        feed_pairs = list(combinations(feeds,2))
        for feeds in feed_pairs:
            self.find_arbs_by_feeds(*feeds)

    def get_matches(self):
        json_str = dumps(self.collection.find())
        data = json_normalize(json.loads(json_str))
        data = data.rename(columns={'date.$date': 'date', 'date_extracted.$date': 'date_extracted'})

        # Convert dates
        data['date'] = pd.to_datetime(data['date'], unit='ms')
        data['date_extracted'] = pd.to_datetime(data['date_extracted'], unit='ms')

        return data.set_index('_id.$oid')

    def find_arbs_by_feeds(self, feed_1, feed_2):
        equal_matches = self.get_equal_matches(feed_1, feed_2)
        for match_1, match_2 in equal_matches:
            # Find arb in any of the odss combination
            if (1/match_1["result_1.odd"] + 1/match_2["result_2.odd"]) < 1:
                # Arb found!
                print("Arb found!")
            elif (1/match_1["result_2.odd"] + 1/match_2["result_1.odd"]) < 1:
                # Arb found!
                print("Arb found!")
        print("No arbs :(")

    def get_equal_matches(self, feed_1, feed_2):
        dates = set(self.matches[self.matches.feed == feed_1].date).intersection(
            set(self.matches[self.matches.feed == feed_2].date))
        for date in dates:
            date_mask = self.matches.date == date
            matches_feed_1 = self.matches[date_mask & (self.matches.feed == feed_1)]
            matches_feed_2 = self.matches[date_mask & (self.matches.feed == feed_2)]
            for match in matches_feed_1.iterrows():
                similarity_scores = matches_feed_2.id.apply(
                    lambda id: fuzz.partial_ratio(id, match[1].id))
                most_similar_match = \
                    similarity_scores[similarity_scores == similarity_scores.max()]
                if most_similar_match[0] > self.SIMILARITY_THRESHOLD:
                    yield (match[1], matches_feed_2.loc[most_similar_match.index[0]])


def pairwise(t):
    it = iter(t)
    return izip(it, it)