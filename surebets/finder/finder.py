from collections import defaultdict
from typing import List, Union, Tuple, Iterable

from api.app.models.bets import Bet
from api.app.models.surebets import SureBet, SureBetInUpsert, Outcome
from surebets.helpers import recursive_defaultdict


class SureBetsFinder:
    def __init__(self, bets: List[Bet]):
        self.bets_tree = recursive_defaultdict()
        for bet in bets:
            self.bets_tree[bet.bet_type][bet.bet_scope][bet.is_back][bet.slug] = bet

    def find_all(self) -> List[SureBetInUpsert]:
        all_arbs = []
        for bet_type, bet_scopes in self.bets_tree.items():
            for bet_scope, is_back_bets in bet_scopes.items():
                for is_back, bets in is_back_bets.items():
                    arbs = self._find_all(bet_type, bets.values())
                    if arbs:
                        for outcomes, profit in arbs:
                            all_arbs.append(
                                SureBetInUpsert(
                                    bet_type=bet_type,
                                    bet_scope=bet_scope,
                                    is_back=is_back,
                                    outcomes=outcomes,
                                    profit=profit
                                )
                            )
        return all_arbs

    def find_home_away(self, bets: List[Bet]) -> Iterable[Tuple[List[Outcome], float]]:
        filtered_bets = tuple(filter(lambda x: len(x.odds) == 2, bets))
        rng = range(len(filtered_bets))
        permutations = ((filtered_bets[i], filtered_bets[j]) for i in rng for j in rng if i != j)
        for bet_1, bet_2 in permutations:
            profit = self.get_profit(bet_1.odds[0], bet_2.odds[1])
            if profit > 0:
                outcomes = [
                    self._get_outcome_from_bet(bet_1, 0),
                    self._get_outcome_from_bet(bet_2, 1)
                ]
                yield outcomes, profit

    @staticmethod
    def _get_outcome_from_bet(bet: Bet, odd_idx: int) -> Outcome:
        return Outcome(bookmaker=bet.bookmaker,
                       bookmaker_nice=bet.bookmaker_nice,
                       url=bet.url,
                       odd=bet.odds[odd_idx])

    @staticmethod
    def get_profit(odd_1: float, odd_2: float):
        return 1 - (1 / odd_1 + 1 / odd_2)

    def _find_all(self, bet_type: str, bets: list) -> Union[List[tuple], None]:
        if bet_type in ('Home/Away', 'Draw No Bet'):
            yield from self.find_home_away(bets)








