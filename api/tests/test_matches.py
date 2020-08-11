def test_read_main(client, collection):
    collection.insert_one(
        {
            "sport": "basketball",
            "tournament": "test-league",
            "tournament_nice": "Test League",
            "teams": [
                "Test FC",
                "AD Test"
            ],
            "commence_time": "2020-08-12T11:30:00.000Z",
            "url": "https://www.test.com/basketball/country/test-league/test-test-jRKgDPoT/",
            "bets": [],
            "created_at": "2020-08-11T20:25:58.000Z",
            "updated_at": "2020-08-11T20:25:58.000Z",
            "slug": "test-fc-ad-test-sport-basketball-test-league-women-1597231800",
            "feed": "test"
        }
    )
    response = client.get("/api/matches/test-fc-ad-test-sport-basketball-test-league-women-1597231800")
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
            "slug": "test-fc-ad-test-sport-basketball-test-league-women-1597231800",
        }
