"""
Integration/API tests for NBA Wordle API endpoints
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()
    assert response.json()["status"] == "running"


def test_health_endpoint():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_start_game():
    """Test starting a new game"""
    response = client.post("/api/start-game")
    assert response.status_code == 200
    data = response.json()
    assert "game_id" in data
    assert "message" in data
    assert len(data["game_id"]) > 0


def test_player_search():
    """Test player search endpoint"""
    # Test with valid query
    response = client.get("/api/player-search", params={"q": "James", "limit": 10})
    assert response.status_code == 200
    results = response.json()
    assert isinstance(results, list)
    
    # Test with short query (should return empty)
    response = client.get("/api/player-search", params={"q": "J"})
    assert response.status_code == 200
    assert response.json() == []


def test_player_search_results_format():
    """Test player search returns correct format"""
    response = client.get("/api/player-search", params={"q": "Curry", "limit": 5})
    assert response.status_code == 200
    results = response.json()
    
    if len(results) > 0:
        player = results[0]
        assert "id" in player
        assert "name" in player
        assert "team" in player
        assert isinstance(player["id"], int)
        assert isinstance(player["name"], str)


def test_make_guess_flow():
    """Test complete game flow: start game, search, make guess"""
    # Start a game
    start_response = client.post("/api/start-game")
    assert start_response.status_code == 200
    game_id = start_response.json()["game_id"]
    
    # Search for a player
    search_response = client.get("/api/player-search", params={"q": "James", "limit": 1})
    assert search_response.status_code == 200
    players = search_response.json()
    
    if len(players) > 0:
        player_id = players[0]["id"]
        
        # Make a guess
        guess_response = client.post(
            "/api/guess",
            json={"game_id": game_id, "player_id": player_id}
        )
        assert guess_response.status_code == 200
        guess_data = guess_response.json()
        
        assert "guessed_player" in guess_data
        assert "comparison" in guess_data
        assert "is_correct" in guess_data
        assert "guess_number" in guess_data
        assert "is_game_over" in guess_data
        assert "is_won" in guess_data
        
        # Verify comparison structure
        comparison = guess_data["comparison"]
        assert "team" in comparison
        assert "division" in comparison
        assert "conference" in comparison
        assert "age" in comparison
        assert "height" in comparison
        assert "position" in comparison
        assert "jersey_number" in comparison
        assert "ppg" in comparison


def test_make_guess_invalid_game():
    """Test making a guess with invalid game ID"""
    response = client.post(
        "/api/guess",
        json={"game_id": "invalid-id", "player_id": 123}
    )
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_make_guess_invalid_player():
    """Test making a guess with invalid player ID"""
    # Start a game first
    start_response = client.post("/api/start-game")
    game_id = start_response.json()["game_id"]
    
    # Try to guess with invalid player ID
    response = client.post(
        "/api/guess",
        json={"game_id": game_id, "player_id": 999999999}
    )
    # Should either return 400 or 500 depending on how nba_api handles it
    assert response.status_code in [400, 500]


def test_game_state():
    """Test getting game state"""
    # Start a game
    start_response = client.post("/api/start-game")
    game_id = start_response.json()["game_id"]
    
    # Get game state
    response = client.get(f"/api/game-state/{game_id}")
    assert response.status_code == 200
    state = response.json()
    
    assert "target_player_id" in state
    assert "guess_count" in state
    assert "max_guesses" in state
    assert "is_game_over" in state


def test_game_state_invalid():
    """Test getting game state with invalid game ID"""
    response = client.get("/api/game-state/invalid-id")
    assert response.status_code == 404


def test_multiple_guesses():
    """Test making multiple guesses in a game"""
    # Start a game
    start_response = client.post("/api/start-game")
    game_id = start_response.json()["game_id"]
    
    # Search for players
    search_response = client.get("/api/player-search", params={"q": "James", "limit": 3})
    players = search_response.json()
    
    if len(players) >= 2:
        # Make first guess
        guess1 = client.post(
            "/api/guess",
            json={"game_id": game_id, "player_id": players[0]["id"]}
        )
        assert guess1.status_code == 200
        assert guess1.json()["guess_number"] == 1
        
        # Make second guess
        guess2 = client.post(
            "/api/guess",
            json={"game_id": game_id, "player_id": players[1]["id"]}
        )
        assert guess2.status_code == 200
        assert guess2.json()["guess_number"] == 2


def test_max_guesses():
    """Test that game ends after maximum guesses"""
    # Start a game
    start_response = client.post("/api/start-game")
    game_id = start_response.json()["game_id"]
    
    # Search for enough players
    search_response = client.get("/api/player-search", params={"q": "a", "limit": 10})
    players = search_response.json()
    
    if len(players) >= 8:
        # Make 8 guesses
        for i in range(8):
            guess_response = client.post(
                "/api/guess",
                json={"game_id": game_id, "player_id": players[i]["id"]}
            )
            assert guess_response.status_code == 200
        
        # Try to make a 9th guess (should fail)
        guess_response = client.post(
            "/api/guess",
            json={"game_id": game_id, "player_id": players[8]["id"]}
        )
        assert guess_response.status_code == 400
        assert "already over" in guess_response.json()["detail"].lower()


def test_correct_guess():
    """Test winning the game with correct guess"""
    # Start a game
    start_response = client.post("/api/start-game")
    game_id = start_response.json()["game_id"]
    
    # Get game state to find target player
    state_response = client.get(f"/api/game-state/{game_id}")
    target_player_id = state_response.json()["target_player_id"]
    
    # Make correct guess
    guess_response = client.post(
        "/api/guess",
        json={"game_id": game_id, "player_id": target_player_id}
    )
    assert guess_response.status_code == 200
    guess_data = guess_response.json()
    
    assert guess_data["is_correct"] is True
    assert guess_data["is_won"] is True
    assert guess_data["is_game_over"] is True
    
    # Try to make another guess (should fail)
    guess_response2 = client.post(
        "/api/guess",
        json={"game_id": game_id, "player_id": target_player_id}
    )
    assert guess_response2.status_code == 400


def test_duplicate_guess_prevention():
    """Test that you cannot guess the same player multiple times"""
    # Start a game
    start_response = client.post("/api/start-game")
    game_id = start_response.json()["game_id"]
    
    # Search for a player
    search_response = client.get("/api/player-search", params={"q": "James", "limit": 1})
    players = search_response.json()
    
    if len(players) > 0:
        player_id = players[0]["id"]
        player_name = players[0]["name"]
        
        # Make first guess
        guess1 = client.post(
            "/api/guess",
            json={"game_id": game_id, "player_id": player_id}
        )
        assert guess1.status_code == 200
        assert guess1.json()["guess_number"] == 1
        
        # Try to guess the same player again (should fail)
        guess2 = client.post(
            "/api/guess",
            json={"game_id": game_id, "player_id": player_id}
        )
        assert guess2.status_code == 400
        assert "already guessed" in guess2.json()["detail"].lower()
        
        # Verify we can still make other guesses
        search_response2 = client.get("/api/player-search", params={"q": "Curry", "limit": 1})
        other_players = search_response2.json()
        
        if len(other_players) > 0:
            other_player_id = other_players[0]["id"]
            guess3 = client.post(
                "/api/guess",
                json={"game_id": game_id, "player_id": other_player_id}
            )
            assert guess3.status_code == 200
            assert guess3.json()["guess_number"] == 2
