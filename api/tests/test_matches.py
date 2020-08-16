from datetime import datetime, timezone
import json


def test_get_match_by_slug(client, collection):
    collection.insert_one(
        {
            "sport": "basketball",
            "tournament": "test-league",
            "tournament_nice": "Test League",
            "teams": [
                "Test FC",
                "AD Test"
            ],
            "commence_time": datetime(2020, 8, 12, 11, 30, 00, tzinfo=timezone.utc),
            "url": "https://www.test.com/basketball/country/test-league/test-test-jRKgDPoT/",
            "bets": [],
            "created_at": datetime(2020, 8, 11, 20, 25, 58),
            "updated_at": datetime(2020, 8, 11, 20, 25, 58),
            "slug": "test-fc-ad-test-basketball-test-league-1597231800",
            "feed": "test"
        }
    )
    response = client.get("/api/matches/test-fc-ad-test-basketball-test-league-1597231800")
    assert response.status_code == 200
    assert response.json() == {
        "sport": "basketball",
        "tournament": "test-league",
        "tournamentNice": "Test League",
        "teams": [
            "Test FC",
            "AD Test"
        ],
        "commenceTime": "2020-08-12T11:30:00Z",
        "url": "https://www.test.com/basketball/country/test-league/test-test-jRKgDPoT/",
        "bets": [],
        "createdAt": "2020-08-11T20:25:58Z",
        "updatedAt": "2020-08-11T20:25:58Z",
        "slug": "test-fc-ad-test-basketball-test-league-1597231800",
    }


def test_list_matches(client, collection):
    collection.insert_many([
        {
            "sport": "football",
            "tournament": "test-cup",
            "tournament_nice": "Test Cup",
            "teams": [
                "Test FC",
                "AD Test"
            ],
            "commence_time": datetime(2020, 8, 13, 20, 30, 00, tzinfo=timezone.utc),
            "url": '',
            "bets": [],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "slug": "test-fc-ad-test-football-test-cup-1597350600",
        },
        {
            "sport": "football",
            "tournament": "test-league",
            "tournament_nice": "Test League",
            "teams": [
                "U.D.Testing",
                "Atlético de Testeo"
            ],
            "commence_time": datetime(2020, 8, 13, 11, 30, 00, tzinfo=timezone.utc),
            "url": '',
            "bets": [],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "slug": "ud-testing-atletico-de-testeo-football-test-league-1597318200",
        },
        {
            "sport": "football",
            "tournament": "test-league",
            "tournament_nice": "Test League",
            "teams": [
                "Real Testing",
                "F.C. Testalona"
            ],
            "commence_time": datetime(2020, 8, 12, 11, 30, 00, tzinfo=timezone.utc),
            "url": '',
            "bets": [],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "slug": "real-testing-fc-testalona-football-test-league-1597231800",
        },
        {
            "sport": "basketball",
            "tournament": "test-tournament",
            "tournament_nice": "Test Tournament",
            "teams": [
                "Testing Basketball Club",
                "Basket Test"
            ],
            "commence_time": datetime(2020, 8, 12, 11, 30, 00, tzinfo=timezone.utc),
            "url": '',
            "bets": [],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "slug": "test-basketball-club-basket-test-basketball-test-tournament-1597231800",
        }
    ]
    )
    # By Commence Day, sport and tournament
    response = client.get("/api/matches/", params={
        'commence_day': '2020-08-13',
        'sport': 'football',
        'tournament': 'test-league'
    })
    assert response.status_code == 200
    data = response.json()
    assert data['matchesCount'] == 1
    assert data['matches'][0]['slug'] == "ud-testing-atletico-de-testeo-football-test-league-1597318200"

    # By Commence Time and sport
    response = client.get("/api/matches/", params={
        'commence_time': '2020-08-13T20:30:00Z',
        'sport': 'football',
    })
    assert response.status_code == 200
    data = response.json()
    assert data['matchesCount'] == 1
    assert data['matches'][0]['slug'] == "test-fc-ad-test-football-test-cup-1597350600"


def test_find_match(client, collection):
    collection.insert_many([
        {
            "sport": "football",
            "tournament": "test-cup",
            "tournament_nice": "Test Cup",
            "teams": [
                "Testeo F.C",
                "A.D. Testing"
            ],
            "commence_time": datetime(2020, 8, 13, 20, 30, 00, tzinfo=timezone.utc),
            "url": '',
            "bets": [],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "slug": "testeo-fc-ad-testing-football-test-cup-1597350600",
        },
        {
            "sport": "football",
            "tournament": "test-cup",
            "tournament_nice": "Test Cup",
            "teams": [
                "Testalona F.C",
                "Atlético de Testeo"
            ],
            "commence_time": datetime(2020, 8, 13, 20, 30, 00, tzinfo=timezone.utc),
            "url": '',
            "bets": [],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "slug": "testalona-fc-atletico-de-testeo-football-test-cup-1597350600",
        }]
    )

    # Match found
    response = client.get("/api/matches/find", params={
        'sport': 'football',
        'commence_day': '2020-08-13',
        'similarity': 85,
        'teams': [
            "Testeo FC",
            "AD Testing"
        ]
    })
    assert response.status_code == 200
    data = response.json()
    assert data['slug'] == "testeo-fc-ad-testing-football-test-cup-1597350600"

    # Match not found due to query filters
    response = client.get("/api/matches/find", params={
        'sport': 'football',
        'commence_day': '2020-08-14',
        'similarity': 85,
        'teams': [
            "U.D Testing City",
            "Real Testing"
        ]
    })
    assert response.status_code == 404

    # Match not found due to fuzzy search
    response = client.get("/api/matches/find", params={
        'sport': 'football',
        'commence_day': '2020-08-13',
        'similarity': 85,
        'teams': [
            "U.D Testing City",
            "Real Testing"
        ]
    })
    assert response.status_code == 404

    # Multiple matches due to low similarity
    response = client.get("/api/matches/find", params={
        'sport': 'football',
        'commence_day': '2020-08-13',
        'similarity': 40,
        'teams': [
            "Testeo F.C",
            "A.D. Testing"
        ]
    })
    assert response.status_code == 422


def test_upsert_match(client, collection):
    collection.insert_one(
        {
            "sport": "football",
            "tournament": "test-cup",
            "tournament_nice": "Test Cup",
            "teams": [
                "Testeo FC",
                "AD Testing"
            ],
            "commence_time": datetime(2020, 8, 13, 20, 30, 00, tzinfo=timezone.utc),
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
                    "slug": "testeo-fc-ad-testing-football-test-cup-1597350600-testbet-1-x-2-full-time-true",
                    "feed": "testfeed_1"
                },
            ],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "slug": "testeo-fc-ad-testing-football-test-cup-1597350600",
            "feed": "testfeed_1"
        }
    )

    # Create new Match
    response = client.put("/api/matches/", data=json.dumps({
        "sport": "football",
        "tournament": "test-cup",
        "tournament_nice": "Test Cup",
        "teams": [
            "Testalona FC",
            "Atlético de Testeo"
        ],
        "commence_time": "2020-08-13T20:30:00Z",
        "url": 'https://www.test.com/football/country/test-cup/testalona-fc-atletico-de-testeo-jRKgFPoT/',
        "bets": [
            {
                "bookmaker": "testfair",
                "bookmaker_nice": "Testfair",
                "bet_type": "1X2",
                "bet_scope": "Full Time",
                "is_back": True,
                "url": "https://data.testingportal.com/feed/match/1-12-jRKgDPdT-2-12-abcd1.dat",
                "odds": [
                    1.25,
                    3.1,
                    2.25
                ],
                "feed": "testfeed_1"
            },
        ],
        "feed": "testfeed_1"
    }))
    assert response.status_code == 200
    data = response.json()
    assert data['betsCount'] == 1
    assert data['match']['slug'] == 'testalona-fc-atletico-de-testeo-football-test-cup-1597350600'
    assert (data['match']['bets'][0]['slug'] ==
            'testalona-fc-atletico-de-testeo-football-test-cup-1597350600-testfair-1x2-full-time-true')

    # Update existing match
    response = client.put("/api/matches/", data=json.dumps({
        "sport": "football",
        "tournament": "test-cup",
        "tournament_nice": "Test Cup",
        "teams": [
            "Testeo FC",
            "AD Testing"
        ],
        "commence_time": "2020-08-13T20:30:00Z",
        "url": 'https://www.test.com/football/country/test-cup/testeo-fc-ad-testing-jRKgDPoT/',
        "bets": [
            {
                "bookmaker": "testfair",
                "bookmaker_nice": "Testfair",
                "bet_type": "1X2",
                "bet_scope": "Full Time",
                "is_back": True,
                "url": "https://data.testingportal.com/feed/match/1-12-jRKgDPoT-2-12-abcd2.dat",
                "odds": [
                    1.79,
                    1.95,
                    3.1
                ],
                "feed": "testfeed_2"
            },
        ],
        "feed": "testfeed_2"
    }))
    assert response.status_code == 200
    data = response.json()
    assert data['betsCount'] == 2
    assert data['match']['slug'] == 'testeo-fc-ad-testing-football-test-cup-1597350600'

