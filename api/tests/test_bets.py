import json
from datetime import datetime, timezone


def test_get_bet(client, collection):
    collection.insert_one(
        {
            "sport": "basketball",
            "tournament": "test-league",
            "tournament_nice": "Test League",
            "teams": [
                "Testeo Basket",
                "Real Basketball"
            ],
            "commence_time": datetime(2020, 8, 13, 22, 30, 00, tzinfo=timezone.utc),
            "url": '',
            "bets": [
                {
                    "bookmaker": "test-365",
                    "bookmaker_nice": "Test 365",
                    "bet_type": "1X2",
                    "bet_scope": "Over/Under",
                    "is_back": True,
                    "url": "https://data.testingportal.com/feed/match/1-12-xRKgDPoT-2-12-abcd1.dat",
                    "odds": [
                        1.81,
                        3.97,
                    ],
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow(),
                    "slug": "testeo-basket-real-basketball-basketball-test-league-1597231800-test-365-over-under-full-time-true",
                    "feed": "testfeed_1"
                }
            ]
        }
    )
    # Existing betdocker-co
    response = client.get("/api/matches/bets/testeo-basket-real-basketball-basketball-test-league-1597231800-test-365-over-under-full-time-true")
    assert response.status_code == 200
    data = response.json()
    assert data['slug'] == f'testeo-basket-real-basketball-basketball-test-league-1597231800-test-365-over-under-full-time-true'

    # Non-existing bet
    response = client.get("/api/matches/bets/testeo-basket-real-basketball-basketball-test-league-1597231800-test-365-over-under-1st-half-true")
    assert response.status_code == 404


def test_upsert_bet(client, collection):
    match_slug = 'testeo-fc-ad-testing-football-test-cup-1597357800'
    collection.insert_one(
        {
            "sport": "football",
            "tournament": "test-cup",
            "tournament_nice": "Test Cup",
            "teams": [
                "Testeo FC",
                "AD Testing"
            ],
            "commence_time": datetime(2020, 8, 13, 22, 30, 00, tzinfo=timezone.utc),
            "url": '',
            "bets": [
                {
                    "bookmaker": "testbet",
                    "bookmaker_nice": "Test Bet",
                    "bet_type": "1X2",
                    "bet_scope": "Full Time",
                    "is_back": True,
                    "url": "https://data.testingportal.com/feed/match/1-12-jRKgDPoT-2-12-abcd1.dat",
                    "odds": [
                        1.81,
                        1.97,
                        3.2
                    ],
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow(),
                    "slug": f"{match_slug}-testbet-1x2-full-time-true",
                    "feed": "testfeed_1"
                },
            ],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "slug": match_slug,
            "feed": "testfeed_1"
        }
    )
    # Create new bet
    response = client.put(
        f"/api/matches/{match_slug}/bets",
        data=json.dumps({
            "bookmaker": "testfair",
            "bookmaker_nice": "Testfair",
            "bet_type": "Over/Under",
            "bet_scope": "Full Time",
            "is_back": True,
            "url": "https://data.testingportal.com/feed/match/1-12-jRKgDPoT-2-12-abcd2.dat",
            "odds": [
                1.79,
                1.95,
            ],
            "feed": "testfeed_2",
            "handicap": 1.00
        }
        ))
    assert response.status_code == 200
    data = response.json()
    assert data['slug'] == f'{match_slug}-testfair-over-under-full-time-true-1-0'

    # Update existing bet
    response = client.put(
        f"/api/matches/{match_slug}/bets",
        data=json.dumps({
            "bookmaker": "testbet",
            "bookmaker_nice": "Test Bet",
            "bet_type": "1X2",
            "bet_scope": "Full Time",
            "is_back": True,
            "url": "https://data.testingportal.com/feed/match/1-12-jRKgDPoT-2-12-abcd2.dat",
            "odds": [
                1.85,
                1.9,
                2.9
            ],
            "feed": "testfeed_2"
        }
        ))
    assert response.status_code == 200
    data = response.json()
    assert data['slug'] == f'{match_slug}-testbet-1x2-full-time-true'

    # Check that DB is updated correctly
    bets_in_db = collection.find_one({'slug': match_slug}, {'bets': 1})['bets']
    assert len(bets_in_db) == 2
    odds = {d["bookmaker"]: d['odds'] for d in bets_in_db}
    assert odds['testbet'] == [1.85, 1.9, 2.9]
    assert odds['testfair'] == [1.79, 1.95]
