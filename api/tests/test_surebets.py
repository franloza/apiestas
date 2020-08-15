from datetime import datetime, timezone, timedelta

import json


def test_list_surebets(client, collection):
    past_match_with_surebets = {
            "sport": "basketball",
            "tournament": "test-cup",
            "tournament_nice": "Test Cup",
            "teams": [
                "Testonia Basket",
                "Real Testing"
            ],
            "commence_time": datetime(2020, 8, 13, 20, 30, 00, tzinfo=timezone.utc),
            "url": '',
            "bets": [
                {
                    "bookmaker": "testbet",
                    "bookmaker_nice": "Test Bet",
                    "bet_type": "Winner",
                    "bet_scope": "Full Time",
                    "is_back": True,
                    "url": "https://data.testingportal.com/feed/match/1-12-jRKgDPoT-2-12-abcd1.dat",
                    "odds": [
                        1.6,
                        3.6,
                    ],
                    "slug": "testonia-basket-real-testing-sport-basketball-test-cup-1597350600-testbet-winner-full-time",
                    "feed": "testfeed_1"
                },
                {
                    "bookmaker": "test-365",
                    "bookmaker_nice": "Test 365",
                    "bet_type": "Winner",
                    "bet_scope": "Full Time",
                    "is_back": True,
                    "url": "https://data.testingportal.com/feed/match/1-12-jRKgDPoT-2-12-abcd2.dat",
                    "odds": [
                        1.7,
                        3.2,
                    ],
                    "slug": "testonia-basket-real-testing-sport-basketball-test-cup-1597350600-testbet-winner-full-time",
                    "feed": "testfeed_1"
                },
            ],
            "surebets": [
                {
                    "bet_type": "Winner",
                    "bet_scope": "Full Time",
                    "is_back": True,
                    "profit": 0.0625,
                    "slug": "testonia-basket-real-testing-sport-basketball-test-cup-1597350600-testbet-test-365",
                    "created_at": datetime(2020, 8, 11, 20, 25, 58),
                    "updated_at": datetime(2020, 8, 11, 20, 25, 58),
                    "outcomes": [
                        {
                            "bookmaker": "testbet",
                            "bookmaker_nice": "Test Bet",
                            "url": "https://data.testingportal.com/feed/match/1-12-jRKgDPoT-2-12-abcd1.dat",
                            "odd": 1.6
                        },
                        {
                            "bookmaker": "test-365",
                            "bookmaker_nice": "Test 365",
                            "url": "https://data.testingportal.com/feed/match/1-12-jRKgDPoT-2-12-abcd2.dat",
                            "odd": 3.2
                        },
                    ],
                },
                {
                    "bet_type": "Winner",
                    "bet_scope": "Full Time",
                    "is_back": True,
                    "profit": 0.133986928104575,
                    "slug": "testonia-basket-real-testing-sport-basketball-test-cup-1597350600-test-365-testbet",
                    "created_at": datetime(2020, 8, 11, 20, 25, 58),
                    "updated_at": datetime(2020, 8, 11, 20, 25, 58),
                    "outcomes": [
                        {
                            "bookmaker": "test-365",
                            "bookmaker_nice": "Test 365",
                            "url": "https://data.testingportal.com/feed/match/1-12-jRKgDPoT-2-12-abcd2.dat",
                            "odd": 1.7,
                        },
                        {
                            "bookmaker": "testbet",
                            "bookmaker_nice": "Test Bet",
                            "url": "https://data.testingportal.com/feed/match/1-12-jRKgDPoT-2-12-abcd1.dat",
                            "odd": 3.6
                        }
                    ]
                }
            ],
            "slug": "testonia-basket-real-testing-sport-basketball-test-cup-1597350600",
            "feed": "testfeed_1"
        }
    future_match_with_surebets = dict(past_match_with_surebets)
    expected_commence_time = (datetime.utcnow() + timedelta(days=1)).replace(microsecond=0)
    future_match_with_surebets["commence_time"] = expected_commence_time
    collection.insert_many(
        [
            future_match_with_surebets,
            past_match_with_surebets
        ]
    )

    # Surebets with filters
    response = client.get("/api/matches/surebets/", params={
        "sport": "basketball",
        "commence_day": expected_commence_time.strftime("%Y-%m-%d"),
        "min_profit": 0.1
    })
    assert response.status_code == 200
    data = response.json()
    assert data['surebetsCount'] == 1
    assert data['surebets'][0] == {
        "sport": "basketball",
        "tournament": "test-cup",
        "tournamentNice": "Test Cup",
        "teams": [
            "Testonia Basket",
            "Real Testing"
        ],
        "commenceTime": f"{expected_commence_time.isoformat()}Z",
        "url": '',
        "surebet": {
            "betType": "Winner",
            "betScope": "Full Time",
            "isBack": True,
            "profit": 0.133986928104575,
            "slug": "testonia-basket-real-testing-sport-basketball-test-cup-1597350600-test-365-testbet",
            "createdAt": "2020-08-11T20:25:58Z",
            "updatedAt": "2020-08-11T20:25:58Z",
            "outcomes": [
                {
                    "bookmaker": "test-365",
                    "bookmakerNice": "Test 365",
                    "url": "https://data.testingportal.com/feed/match/1-12-jRKgDPoT-2-12-abcd2.dat",
                    "odd": 1.7
                },
                {
                    "bookmaker": "testbet",
                    "bookmakerNice": "Test Bet",
                    "url": "https://data.testingportal.com/feed/match/1-12-jRKgDPoT-2-12-abcd1.dat",
                    "odd": 3.6
                }
            ]
        }
    }

    # Surebets without filters
    response = client.get("/api/matches/surebets/")
    assert response.status_code == 200
    data = response.json()
    assert data['surebetsCount'] == 2


def test_create_surebet(client, collection):
    match_slug = "testonia-basket-real-testing-sport-basketball-test-cup-1597350600"
    collection.insert_one(
        {
            "sport": "basketball",
            "tournament": "test-cup",
            "tournament_nice": "Test Cup",
            "teams": [
                "Testonia Basket",
                "Real Testing"
            ],
            "commence_time": datetime(2020, 8, 13, 20, 30, 00, tzinfo=timezone.utc),
            "url": '',
            "bets": [
                {
                    "bookmaker": "testbet",
                    "bookmaker_nice": "Test Bet",
                    "bet_type": "Winner",
                    "bet_scope": "Full Time",
                    "is_back": True,
                    "url": "https://data.testingportal.com/feed/match/1-12-jRKgDPoT-2-12-abcd1.dat",
                    "odds": [
                        1.6,
                        3.6,
                    ],
                    "slug": "testonia-basket-real-testing-sport-basketball-test-cup-1597350600-testbet-winner-full-time",
                    "feed": "testfeed_1"
                },
                {
                    "bookmaker": "test-365",
                    "bookmaker_nice": "Test 365",
                    "bet_type": "Winner",
                    "bet_scope": "Full Time",
                    "is_back": True,
                    "url": "https://data.testingportal.com/feed/match/1-12-jRKgDPoT-2-12-abcd2.dat",
                    "odds": [
                        1.7,
                        3.2,
                    ],
                    "slug": "testonia-basket-real-testing-sport-basketball-test-cup-1597350600-testbet-winner-full-time",
                    "feed": "testfeed_1"
                },
            ],
            "slug": match_slug,
            "feed": "testfeed_1"
        }
    )
    response = client.post(f"/api/matches/{match_slug}/surebets", data=json.dumps(
        [
            {
                "bet_type": "Winner",
                "bet_scope": "Full Time",
                "is_back": True,
                "profit": 0.0625,
                "slug": "testonia-basket-real-testing-sport-basketball-test-cup-1597350600-testbet-test-365",
                "outcomes": [
                    {
                        "bookmaker": "testbet",
                        "bookmaker_nice": "Test Bet",
                        "url": "https://data.testingportal.com/feed/match/1-12-jRKgDPoT-2-12-abcd1.dat",
                        "odd": 1.6
                    },
                    {
                        "bookmaker": "test-365",
                        "bookmaker_nice": "Test 365",
                        "url": "https://data.testingportal.com/feed/match/1-12-jRKgDPoT-2-12-abcd2.dat",
                        "odd": 3.2
                    },
                ],
            },
            {
                "bet_type": "Winner",
                "bet_scope": "Full Time",
                "is_back": True,
                "profit": 0.133986928104575,
                "slug": "testonia-basket-real-testing-sport-basketball-test-cup-1597350600-test-365-testbet",
                "outcomes": [
                    {
                        "bookmaker": "test-365",
                        "bookmaker_nice": "Test 365",
                        "url": "https://data.testingportal.com/feed/match/1-12-jRKgDPoT-2-12-abcd2.dat",
                        "odd": 1.7,
                    },
                    {
                        "bookmaker": "testbet",
                        "bookmaker_nice": "Test Bet",
                        "url": "https://data.testingportal.com/feed/match/1-12-jRKgDPoT-2-12-abcd1.dat",
                        "odd": 3.6
                    }
                ]
            }
        ]
    ))
    assert response.status_code == 200
    result = collection.find_one({'slug': match_slug}, {"surebets": 1})
    assert len(result['surebets']) == 2
    assert "created_at" in result["surebets"][0]
    assert "slug" in result["surebets"][0]
