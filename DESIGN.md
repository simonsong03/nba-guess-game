# NBA Wordle - Design Document

## Overview

NBA Wordle is a web-based guessing game where players attempt to identify a randomly selected NBA player from the **2025-26 season** within 8 guesses. After each guess, players receive directional feedback comparing various attributes of their guessed player to the target player. The game features player images, prevents duplicate guesses, and provides clear directional hints for numeric attributes.

## Architecture

### High-Level Architecture

```
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│                 │         │                 │         │                 │
│   React Frontend│────────▶│  FastAPI Backend│────────▶│   nba_api       │
│   (Vite)        │  HTTP   │   (Python)      │  HTTP   │   (External)    │
│                 │         │                 │         │                 │
└─────────────────┘         └─────────────────┘         └─────────────────┘
       │                             │
       │                             │
       │                             │
       ▼                             ▼
┌─────────────────┐         ┌─────────────────┐
│                 │         │                 │
│   Vercel/       │         │   Render/       │
│   Netlify       │         │   Railway       │
│   (CDN)         │         │   (Server)      │
│                 │         │                 │
└─────────────────┘         └─────────────────┘
```

## Data Flow

### 1. Game Initialization Flow

```
User → Frontend → POST /api/start-game → Backend
                                      ↓
                              NBA Data Service
                                      ↓
                              Get Random Player
                                      ↓
                              Create Game Engine
                                      ↓
                              Return game_id
                                      ↓
                              Frontend stores game_id
```

### 2. Player Search Flow

```
User types query → Frontend → GET /api/player-search?q=query → Backend
                                                              ↓
                                                      NBA Data Service
                                                              ↓
                                                      Search Players
                                                              ↓
                                                      Return Results
                                                              ↓
                                                      Frontend displays dropdown
```

### 3. Guess Flow

```
User selects player → Frontend → POST /api/guess {game_id, player_id} → Backend
                                                                        ↓
                                                                Get Player Details
                                                                        ↓
                                                                Wordle Engine
                                                                        ↓
                                                                Compare Attributes
                                                                        ↓
                                                                Return Comparison
                                                                        ↓
                                                                Frontend displays feedback
```

## Game Logic

### Comparison Attributes

The game compares 8 attributes between the guessed player and target player from the **2025-26 NBA season**:

1. **Team** - Exact match only (✅ or ❌)
2. **Division** - Exact match only (✅ or ❌)
3. **Conference** - Exact match only (✅ or ❌)
4. **Age** - Directional feedback (✅ correct, ⬆️ higher, ⬇️ lower)
5. **Height** - Directional feedback (✅ correct, ⬆️ higher, ⬇️ lower)
6. **Position** - Exact match (✅), same position group (🟨), or incorrect (❌)
   - Position groups: Guards (PG, SG, G), Forwards (SF, PF, F), Centers (C)
7. **Jersey Number** - Directional feedback (✅ correct, ⬆️ higher, ⬇️ lower)
8. **Points Per Game (PPG)** - Directional feedback (✅ correct, ⬆️ higher, ⬇️ lower)

### Match Types

- **✅ Correct**: Attribute values are identical
- **⬆️ Higher**: For numeric attributes, guessed value is lower than target (need to guess higher)
- **⬇️ Lower**: For numeric attributes, guessed value is higher than target (need to guess lower)
- **🟨 Partial**: Position is in the same group (only for position attribute)
- **❌ Incorrect**: Attribute values don't match (for categorical attributes) or wrong direction (for numeric attributes)

### Game State

- **Active**: Game in progress, guesses remaining
- **Won**: Correct player guessed
- **Lost**: Maximum guesses (8) reached without correct guess
- **Duplicate Prevention**: Cannot guess the same player twice

## API Design

### Endpoints

#### POST /api/start-game
Start a new game with a random player from the 2025-26 season.

**Response:**
```json
{
  "game_id": "uuid-string",
  "message": "Game started! Guess the NBA player."
}
```

#### GET /api/player-search
Search for players by name from the 2025-26 season.

**Query Parameters:**
- `q` (string, required): Search query (min 2 characters)
- `limit` (int, optional): Max results (default: 20)

**Response:**
```json
[
  {
    "id": 123,
    "name": "LeBron James",
    "team": "LAL",
    "image_url": "https://cdn.nba.com/headshots/nba/latest/1040x760/123.png"
  }
]
```

#### POST /api/guess
Make a guess in the game.

**Request Body:**
```json
{
  "game_id": "uuid-string",
  "player_id": 123
}
```

**Response:**
```json
{
  "guessed_player": {
    "id": 123,
    "name": "LeBron James",
    "team": "Los Angeles Lakers",
    "division": "Pacific",
    "conference": "West",
    "age": 39,
    "height": "6-9",
    "position": "SF",
    "jersey_number": 23,
    "ppg": 25.0,
    "image_url": "https://cdn.nba.com/headshots/nba/latest/1040x760/123.png"
  },
  "comparison": {
    "team": {
      "attribute": "team",
      "guessed": "Los Angeles Lakers",
      "target": "Los Angeles Lakers",
      "status": "correct"
    },
    "age": {
      "attribute": "age",
      "guessed": 35,
      "target": 39,
      "status": "higher"
    },
    "position": {
      "attribute": "position",
      "guessed": "PG",
      "target": "SF",
      "status": "incorrect"
    }
  },
  "is_correct": false,
  "guess_number": 1,
  "is_game_over": false,
  "is_won": false
}
```

#### GET /api/game-state/{game_id}
Get current game state (optional endpoint for debugging).

## Frontend Architecture

### Component Structure

```
App
├── Header (Season: 2025-26)
├── Game Controls
│   ├── Player Search (Autocomplete with images)
│   └── Guess Button
├── Game Over Banner (conditional)
└── Guesses List
    └── Guess Card (for each guess)
        ├── Player Image & Name
        └── Comparison Results (single row)
            └── Attributes with icons (✅⬆️⬇️🟨❌)
```

### State Management

- `gameId`: Current game identifier
- `guesses`: Array of guess results (with player images)
- `isGameOver`: Boolean flag for game completion
- `isWon`: Boolean flag for win state
- `searchQuery`: Current search input
- `searchResults`: Array of search results (with images)
- `selectedPlayer`: Currently selected player for guess

### User Interactions

1. **Start Game**: Automatically on page load (2025-26 season)
2. **Search Players**: Type in search box, see autocomplete dropdown with player images
3. **Select Player**: Click on search result (shows player image and name)
4. **Make Guess**: Click "Guess" button
5. **View Feedback**: See comparison results in single row with directional indicators
6. **New Game**: Start fresh game with new random player
7. **Duplicate Prevention**: Cannot select the same player twice in one game

## Deployment Architecture

### Backend Deployment (Render/Railway)

- **Platform**: Render or Railway
- **Runtime**: Python 3.11
- **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Environment**: Production Python environment
- **Scaling**: Single instance (sufficient for MVP)

### Frontend Deployment (Vercel/Netlify)

- **Platform**: Vercel or Netlify
- **Build Command**: `npm run build`
- **Output Directory**: `dist`
- **Environment Variables**: `VITE_API_URL` (backend URL)
- **CDN**: Automatic via platform

## Error Handling

### Backend Errors

- **400 Bad Request**: Invalid game state, invalid player ID, duplicate guess, game already over
- **404 Not Found**: Game not found
- **500 Internal Server Error**: NBA API failures, unexpected errors

### Frontend Errors

- Display error messages in UI
- Retry mechanisms for failed requests
- Graceful degradation if backend unavailable

## Performance Considerations

### Caching

- Player search results cached in memory
- Active players list cached after first fetch
- Team information cached

### API Rate Limiting

- nba_api may have rate limits
- Consider implementing request throttling if needed
- Cache frequently accessed data

### Optimization

- Frontend: Lazy loading, code splitting
- Backend: Async endpoints, connection pooling
- Database: Not required for MVP (in-memory storage)

## Security Considerations

### Current Implementation

- CORS configured for frontend origin
- Input validation on API endpoints
- No authentication required (single-player game)

### Future Enhancements

- Rate limiting per IP
- Input sanitization
- HTTPS enforcement
- Environment variable security

## Testing Strategy

### Unit Tests

- Wordle engine comparison logic
- NBA data service methods
- Edge cases (missing data, invalid inputs)

### Integration Tests

- API endpoint testing
- End-to-end game flow
- Error handling scenarios

### Manual Testing

- UI/UX testing
- Cross-browser compatibility
- Mobile responsiveness

### Test Coverage

- **Unit Tests** (`test_wordle_engine.py`): Test game logic in isolation
  - Comparison functions for all attributes
  - Directional feedback (higher/lower/correct)
  - Position partial matching
  - Duplicate guess prevention
  - Game state management

- **Integration/API Tests** (`test_api.py`): Test full API endpoints
  - Game start flow
  - Player search
  - Making guesses
  - Error handling
  - Complete game flows
  - Duplicate guess prevention via API

## Future Enhancements

1. **Persistence**: Store games in database (Redis/PostgreSQL)
2. **Statistics**: Track win rates, average guesses
3. **Leaderboards**: Compare scores with other players
4. **Daily Challenge**: Same player for all users each day
5. **Difficulty Levels**: Filter players by popularity
6. **Hints System**: Unlock hints after certain guesses
7. **Share Results**: Share game results on social media
8. **Season Selection**: Allow users to choose different NBA seasons (currently hardcoded to 2025-26)
