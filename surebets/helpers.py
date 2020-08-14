from collections import defaultdict

from datetime import datetime
from typing import Union


def recursive_defaultdict():
    return defaultdict(recursive_defaultdict)


def parse_mongo_dates(ob: Union[dict, list]):
    if isinstance(ob, list):
        for v in ob:
            if isinstance(v, dict):
                parse_mongo_dates(v)
    else:
        for k, v in ob.items():
            if isinstance(v, dict):
                if "$date" in v:
                    ob[k] = datetime.utcfromtimestamp(v["$date"] / 1000)
                else:
                    parse_mongo_dates(v)
            elif isinstance(v, list):
                parse_mongo_dates(v)

