from api.app.models.bets import Bet
from surebets.finder import SureBetsFinder

import unittest


class TestSureBetsFinder(unittest.TestCase):
    def test_home_away(self):
     test_bets =  [
       {
        "bet_type": "Home/Away",
        "bet_scope": "Full Time",
        "is_back": True,
        "bookmaker": "1XBet",
        "bookmaker_nice": "1xbet",
        "slug": "1xbet",
        "odds": [5.45, 1.13],
        },
       {"bet_type": "Home/Away",
        "bet_scope": "Full Time",
        "is_back": True,
        "bookmaker": "Bet At Home",
        "bookmaker_nice": "bet-at-home",
        "slug": "bet-at-home",
        "odds": [4.67, 1.13],
        },
       {"bet_type": "Home/Away",
        "bet_scope": "Full Time",
        "is_back": True,
        "bookmaker": "Betago",
        "bookmaker_nice": "betago",
        "slug": "betago",
        "odds": [5.00, 1.14],
        },
       {"bet_type": "Home/Away",
        "bet_scope": "Full Time",
        "bookmaker": "BWin",
        "bookmaker_nice": "bwin",
        "is_back": True,
        "slug": "bwin",
        "odds": [4.40, 1.17],
        },
       {"bet_type": "Home/Away",
        "bet_scope": "Full Time",
        "is_back": True,
        "slug": "coolbet",
        "bookmaker": "CoolBet",
        "bookmaker_nice": "coolbet",
        "odds": [5.24, 1.14],
        },
       {"bet_type": "Home/Away",
        "bet_scope": "Full Time",
        "is_back": True,
        "bookmaker": "Unibet",
        "slug": "unibet",
        "bookmaker_nice": "unibet",
        "odds": [4.60, 1.16],
        },
       {"bet_type": "Home/Away",
        "bet_scope": "Full Time",
        "is_back": True,
        "bookmaker": "Pinnacle",
        "slug": "pinnacle",
        "bookmaker_nice": "pinnacle",
        "odds": [5.32, 1.14],
        },
       {"bet_type": "Home/Away",
        "bet_scope": "Full Time",
        "is_back": True,
        "bookmaker": "William Hill",
        "bookmaker_nice": "william-hill",
        "slug": "william-hill",
        "odds": [4.50, 1.17],
        },
       {"bet_type": "Home/Away",
        "bet_scope": "Full Time",
        "is_back": True,
        "bookmaker": "Bookmaker Wrong",
        "bookmaker_nice": "bookmaker-wrong",
        "slug": "test-bookmaker-with-wrong-odds",
        "odds": [4.50, 2.17],
        }
      ]
     surebets = SureBetsFinder([Bet(**bet) for bet in test_bets]).find_all()
     self.assertEqual(len(surebets), 8)


if __name__ == '__main__':
    unittest.main()
