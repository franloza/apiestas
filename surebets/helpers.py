from collections import defaultdict


def recursive_defaultdict():
    return defaultdict(recursive_defaultdict)