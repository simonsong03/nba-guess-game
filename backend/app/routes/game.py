"""
Game Routes - API endpoints for NBA Wordle game
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict
from app.services.nba_data import NBADataService
from app.services.wordle_engine import WordleEngine

router = APIRouter()

# In-memory game storage (in production, use Redis or database)
games: Dict[str, WordleEngine] = {}
nba_service = NBADataService()


class StartGameResponse(BaseModel):
    game_id: str
    message: str


class PlayerSearchResult(BaseModel):
    id: int
    name: str
    team: str
    image_url: Optional[str] = None


class GuessRequest(BaseModel):
    game_id: str
    player_id: int


class ComparisonResult(BaseModel):
    team: str
    division: str
    conference: str
    age: str
    height: str
    position: str
    jersey_number: str
    ppg: str


class GuessResponse(BaseModel):
    guessed_player: Dict
    comparison: Dict
    is_correct: bool
    guess_number: int
    is_game_over: bool
    is_won: bool
    target_player: Optional[Dict] = None


@router.post("/start-game", response_model=StartGameResponse)
async def start_game():
    """Start a new game with a random NBA player from the 2025-26 season"""
    try:
        # Hardcode to 2025-26 season
        season = "2025-26"
        
        # Service will automatically fall back to cache if API fails
        target_player = nba_service.get_random_player(season)
        game_engine = WordleEngine(target_player, season)
        
        # Generate simple game ID (in production, use UUID)
        import uuid
        game_id = str(uuid.uuid4())
        
        games[game_id] = game_engine
        
        return StartGameResponse(
            game_id=game_id,
            message="Game started! Guess the NBA player."
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Failed to start game: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start game: {str(e)}")


@router.get("/player-search", response_model=List[PlayerSearchResult])
async def search_players(q: str, limit: int = 20):
    """Search for players by name"""
    if not q or len(q) < 2:
        return []
    
    try:
        # Hardcode to 2025-26 season
        season = "2025-26"
        results = nba_service.search_players(q, limit, season)
        return [PlayerSearchResult(**r) for r in results]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.post("/guess", response_model=GuessResponse)
async def make_guess(request: GuessRequest):
    """Make a guess in the game"""
    game_id = request.game_id
    
    if game_id not in games:
        raise HTTPException(status_code=404, detail="Game not found")
    
    game_engine = games[game_id]
    
    if game_engine.is_game_over():
        raise HTTPException(status_code=400, detail="Game is already over")
    
    try:
        # Get player details for the game's season
        # Service will handle timeouts and fallbacks automatically
        guessed_player = nba_service.get_player_details(request.player_id, game_engine.season)
        
        # Make guess
        result = game_engine.make_guess(guessed_player)
        
        # If game is over, get target player details for the overlay
        target_player_details = None
        if game_engine.is_game_over():
            target_player_details = nba_service.get_player_details(
                game_engine.target_player.get('id'), 
                game_engine.season
            )
        
        response_data = {
            'guessed_player': result['guessed_player'],
            'comparison': result['comparison'],
            'is_correct': result['is_correct'],
            'guess_number': result['guess_number'],
            'is_game_over': game_engine.is_game_over(),
            'is_won': result['is_correct']
        }
        
        # Add target player details if game is over
        if target_player_details:
            response_data['target_player'] = target_player_details
        
        return GuessResponse(**response_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Guess failed: {str(e)}")


@router.get("/game-state/{game_id}")
async def get_game_state(game_id: str):
    """Get current game state"""
    if game_id not in games:
        raise HTTPException(status_code=404, detail="Game not found")
    
    game_engine = games[game_id]
    return game_engine.get_game_state()
