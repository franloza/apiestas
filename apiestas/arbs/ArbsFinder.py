from apiestas.utils.db import MongoDB
import json
from fuzzywuzzy import fuzz
from itertools import combinations
from bson.json_util import dumps
from pandas.io.json import json_normalize
import pandas as pd
import numpy as np

class ArbsFinder:
    SIMILARITY_THRESHOLD = 75

    def __init__(self):
        self.collection = MongoDB().collection
        self.matches = self.get_matches()
        self.margins = pd.Series([])

    def find_arbs(self):
        # Check first if there is any match
        if self.matches.empty:
            return {"error":"There are no matches in the database"}
        # Set possible combinations of feeds to find arbs in pairs
        feeds = self.matches.feed.unique()
        feed_pairs = list(combinations(feeds, 2))
        found_arbs = []
        for feeds in feed_pairs:
            found_arbs.extend(self.find_arbs_by_feeds(*feeds))

        # Build response dictionary
        response = {"arbs": found_arbs}
        # Add some stats
        stats = {"matches_processed": self.matches.shape[0],
                 "margins": {
                     "mean": self.margins.mean(),
                     "std": self.margins.std(),
                     "values": self.margins.values}}
        response["stats"] = stats
        return response

    def get_matches(self):
        json_str = dumps(self.collection.find())
        try:
            data = json_normalize(json.loads(json_str))
            data = data.rename(columns={'date.$date': 'date', 'date_extracted.$date': 'date_extracted'})
            # Convert dates
            data['date'] = pd.to_datetime(data['date'], unit='ms')
            data['date_extracted'] = pd.to_datetime(data['date_extracted'], unit='ms')
            data.set_index('_id.$oid', inplace=True)
            return data[data.date > pd.datetime.now()]
        except Exception:
            return pd.DataFrame()

    def find_arbs_by_feeds(self, feed_1, feed_2):
        equal_matches = self.get_equal_matches(feed_1, feed_2)
        arbs = []
        margins = np.array([])
        for match_1, match_2 in equal_matches:
            margin = 1 / match_1["result_1.odd"] + 1 / match_2["result_2.odd"]
            margins = np.append(margins, margin)
            # Find arb in any of the odss combination
            if margin < 1:
                # Arb found!
                arb = {
                    "match_1_info": match_1.to_dict(),
                    "match_2_info": match_2.to_dict(),
                    "arb_info": {
                        "bet_1": {
                            "player": match_1["result_1.name"],
                            "odd": match_1["result_1.odd"],
                            "feed":  match_1["feed"]} ,
                        "bet_2": {
                            "player": match_2["result_2.name"],
                            "odd": match_2["result_2.odd"],
                            "feed": match_2["feed"]},
                        "margin": margin,
                        "return": 1 - margin
                    }
                }
                arbs.append(arb)
            margin = 1 / match_1["result_2.odd"] + 1 / match_2["result_1.odd"]
            if margin < 1:
                # Arb found!
                arb = {
                    "match_1_info": match_1.to_dict(),
                    "match_2_info": match_2.to_dict(),
                    "arb_info": {
                        "bet_1": {
                            "player": match_1["result_2.name"],
                            "odd": match_1["result_2.odd"],
                            "feed": match_1["feed"]}
                        ,
                        "bet_2": {
                            "player": match_2["result_1.name"],
                            "odd": match_2["result_1.odd"],
                            "feed": match_2["feed"]},
                        "margin": margin,
                        "return": 1 - margin
                    }
                }
                arbs.append(arb)

        # Append margins to series
        self.margins = self.margins.append(pd.Series(margins), ignore_index=True)

        return arbs

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
