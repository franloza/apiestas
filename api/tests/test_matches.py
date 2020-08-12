from datetime import datetime

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
            "commence_time": datetime(2020, 8, 12, 11, 30, 00),
            "url": "https://www.test.com/basketball/country/test-league/test-test-jRKgDPoT/",
            "bets": [],
            "created_at": datetime(2020, 8, 11, 20, 25, 58),
            "updated_at": datetime(2020, 8, 11, 20, 25, 58),
            "slug": "test-fc-ad-test-sport-basketball-test-league-1597231800",
            "feed": "test"
        }
    )
    response = client.get("/api/matches/test-fc-ad-test-sport-basketball-test-league-1597231800")
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
            "slug": "test-fc-ad-test-sport-basketball-test-league-1597231800",
        }


def test_list_matches(client, collection):
    collection.insert_many([
        {
            "sport": "soccer",
            "tournament": "test-cup",
            "tournament_nice": "Test Cup",
            "teams": [
                "Test FC",
                "AD Test"
            ],
            "commence_time": datetime(2020, 8, 13, 22, 30, 00),
            "url": '',
            "bets": [],
            "created_at": datetime(2020, 8, 11, 20, 25, 58),
            "updated_at": datetime(2020, 8, 11, 20, 25, 58),
            "slug": "test-fc-ad-test-sport-soccer-test-cup-1597357800",
        },
        {
            "sport": "soccer",
            "tournament": "test-league",
            "tournament_nice": "Test League",
            "teams": [
                "U.D.Testing",
                "Atlético de Testeo"
            ],
            "commence_time": datetime(2020, 8, 13, 11, 30, 00),
            "url": '',
            "bets": [],
            "created_at": datetime(2020, 8, 11, 20, 25, 58),
            "updated_at": datetime(2020, 8, 11, 20, 25, 58),
            "slug": "ud-testing-atletico-de-testeo-sport-soccer-test-league-1597318200",
        },
        {
            "sport": "soccer",
            "tournament": "test-league",
            "tournament_nice": "Test League",
            "teams": [
                "Real Testing",
                "F.C. Testalona"
            ],
            "commence_time": datetime(2020, 8, 12, 11, 30, 00),
            "url": '',
            "bets": [],
            "created_at": datetime(2020, 8, 11, 20, 25, 58),
            "updated_at": datetime(2020, 8, 11, 20, 25, 58),
            "slug": "real-testing-fc-testalona-sport-soccer-test-league-1597231800",
        },
        {
            "sport": "basketball",
            "tournament": "test-tournament",
            "tournament_nice": "Test Tournament",
            "teams": [
                "Testing Basketball Club",
                "Basket Test"
            ],
            "commence_time": datetime(2020, 8, 12, 11, 30, 00),
            "url": '',
            "bets": [],
            "created_at": datetime(2020, 8, 11, 20, 25, 58),
            "updated_at": datetime(2020, 8, 11, 20, 25, 58),
            "slug": "test-basketball-club-basket-test-basketball-test-tournament-1597231800",
        }
    ]
    )
    # By Commence Day, sport and tournament
    response = client.get("/api/matches/", params={
        'commence_day': '2020-08-13',
        'sport': 'soccer',
        'tournament': 'test-league'
    })
    assert response.status_code == 200
    data = response.json()
    assert data['matchesCount'] == 1
    assert data['matches'][0]['slug'] == "ud-testing-atletico-de-testeo-sport-soccer-test-league-1597318200"

    # By Commence Time and sport
    response = client.get("/api/matches/", params={
        'commence_time': '2020-08-13T22:30:00Z',
        'sport': 'soccer',
    })
    assert response.status_code == 200
    data = response.json()
    assert data['matchesCount'] == 1
    assert data['matches'][0]['slug'] == "test-fc-ad-test-sport-soccer-test-cup-1597357800"