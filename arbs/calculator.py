from collections import defaultdict
from typing import List, Union

BET_TYPES = {'Winner', '1X2', 'Home/Away', 'Asian Handicap', 'Over/Under', 'Draw No Bet',
             'European Handicap', 'Double Chance', 'To Qualify', 'Correct Score', 'Half Time / Full Time',
             'Odd or Even', 'Both Teams to Score'}


def recursive_defaultdict():
    return defaultdict(recursive_defaultdict)


def process_bets(input_bets: list):
    bets_tree = recursive_defaultdict()
    all_arbs = []
    for bet in input_bets:
        bets_tree[bet["bet_type"]][bet["bet_scope"]][bet["is_back"]][bet["slug"]] = bet
    for bet_type, bet_scopes in bets_tree.items():
        for bet_scope, is_back_bets in bet_scopes.items():
            for is_back, bets in is_back_bets.items():
                arbs = find_arbs(bet_type, bets.values())
                if arbs:
                    for bet_1, bet_2, margin in arbs:
                        all_arbs.append(
                            {"bet_1": bet_1, "bet_2": bet_2, "margin": margin}
                        )
    return all_arbs


def find_arbs(bet_type: str, bets: list) -> Union[List[tuple], None]:
    if bet_type in ('Home/Away', 'Draw No Bet'):
        yield from find_home_away_arbs(bets)


def find_home_away_arbs(bets: list) -> tuple:
    filtered_bets = tuple(filter(lambda x: len(x["odds"]) == 2, bets))
    rng = range(len(filtered_bets))
    permutations = ((filtered_bets[i], filtered_bets[j]) for i in rng for j in rng if i != j)
    for bet_1, bet_2 in permutations:
        margin = get_margin(bet_1["odds"][0], bet_2["odds"][1])
        if margin < 1:
            arb_bet_1, arb_bet_2 = dict(bet_1), dict(bet_2)
            arb_bet_1['arbs_odds'] = bet_1["odds"][0]
            arb_bet_2['arbs_odds'] = bet_2["odds"][0]
            yield arb_bet_1, arb_bet_2, margin


def get_margin(odd_1: float, odd_2: float):
    return 1 / odd_1 + 1 / odd_2







