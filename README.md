# 🏀 NBA Wordle

A Wordle-style guessing game where you try to identify a random NBA player from the 2025-26 season in 8 guesses. After each guess, receive directional feedback comparing attributes like team, conference, age, height, position, jersey number, and points per game.

## 🎮 How to Play

1. A new game automatically starts when you load the page (2025-26 season)
2. Search for an NBA player by name (with autocomplete)
3. Select a player and make your guess
4. Review the feedback for each attribute:
   - ✅ **Correct**: Attribute matches exactly
   - ⬆️ **Higher**: Your guess is too low (need to guess higher)
   - ⬇️ **Lower**: Your guess is too high (need to guess lower)
   - 🟨 **Partial**: Position is in the same group (Guards/Forwards/Centers)
   - ❌ **Incorrect**: Attribute doesn't match
5. Use the directional feedback to narrow down your next guess
6. Win by guessing correctly within 8 attempts!
7. You cannot guess the same player twice

## 🛠️ Tech Stack

### Backend
- **Python 3.11+**
- **FastAPI** - Modern, fast web framework
- **nba_api** - NBA statistics and player data
- **Uvicorn** - ASGI server
- **Pytest** - Testing framework

### Frontend
- **React 18** - UI library
- **Vite** - Build tool and dev server
- **Axios** - HTTP client
- **CSS3** - Styling (no frameworks)

## 📁 Project Structure

```
nba-wordle/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application
│   │   ├── routes/
│   │   │   └── game.py          # API routes
│   │   └── services/
│   │       ├── nba_data.py      # NBA data fetching
│   │       └── wordle_engine.py # Game logic
│   ├── tests/
│   │   ├── test_wordle_engine.py # Unit tests
│   │   └── test_api.py           # Integration/API tests
│   ├── requirements.txt
│   ├── run.py                    # Development server
│   └── Procfile                  # Production server
├── frontend/
│   ├── src/
│   │   ├── App.jsx              # Main component
│   │   ├── App.css              # Styles
│   │   ├── main.jsx             # Entry point
│   │   └── index.css            # Global styles
│   ├── package.json
│   └── vite.config.js
├── DESIGN.md                     # Design document
└── README.md                     # This file
```

## 🚀 Local Development

### Prerequisites

- Python 3.11+
- Node.js 18+
- npm or yarn

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
```

3. Activate virtual environment:
```bash
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Run development server:
```bash
python run.py
```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create `.env` file (optional, defaults to localhost):
```env
VITE_API_URL=http://localhost:8000
```

4. Run development server:
```bash
npm run dev
```

The app will be available at `http://localhost:3000`

## 🧪 Testing

### Backend Tests

Run all tests from the backend directory:

```bash
cd backend
pytest
```

Run only unit tests:

```bash
pytest tests/test_wordle_engine.py
```

Run only integration/API tests:

```bash
pytest tests/test_api.py
```

Run with coverage:

```bash
pytest --cov=app tests/
```

### Frontend Tests

Frontend testing can be added with React Testing Library or similar tools.

## 📦 Deployment

### Backend Deployment (Render)

1. Create account on [Render](https://render.com)
2. Create new Web Service
3. Connect your GitHub repository
4. Configure:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Environment**: Python 3
5. Deploy!

### Backend Deployment (Railway)

1. Create account on [Railway](https://railway.app)
2. Create new project from GitHub
3. Add Python service
4. Railway will auto-detect and deploy
5. Set start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Frontend Deployment (Vercel)

1. Create account on [Vercel](https://vercel.com)
2. Import GitHub repository
3. Configure:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
   - **Environment Variable**: `VITE_API_URL` = your backend URL
4. Deploy!

### Frontend Deployment (Netlify)

1. Create account on [Netlify](https://netlify.com)
2. Import GitHub repository
3. Configure:
   - **Base directory**: `frontend`
   - **Build command**: `npm run build`
   - **Publish directory**: `frontend/dist`
   - **Environment Variable**: `VITE_API_URL` = your backend URL
4. Deploy!

## 🔧 Environment Variables

### Backend
- `PORT` - Server port (automatically set by hosting platform)

### Frontend
- `VITE_API_URL` - Backend API URL (default: `http://localhost:8000`)

## 📊 API Endpoints

### `POST /api/start-game`
Start a new game with a random NBA player.

**Response:**
```json
{
  "game_id": "uuid-string",
  "message": "Game started! Guess the NBA player."
}
```

### `GET /api/player-search?q={query}&limit={limit}`
Search for players by name.

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

### `POST /api/guess`
Make a guess in the game.

**Request:**
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

## 🎯 Game Rules

- **Season**: 2025-26 NBA season (hardcoded)
- **Maximum Guesses**: 8 attempts
- **No Duplicate Guesses**: You cannot guess the same player twice
- **Comparison Attributes**: Team, Division, Conference, Age, Height, Position, Jersey Number, PPG

### Feedback Types

**Numeric Attributes (Age, Height, Jersey #, PPG):**
- ✅ **Correct**: Exact match
- ⬆️ **Higher**: Your guess is lower than target (need to guess higher)
- ⬇️ **Lower**: Your guess is higher than target (need to guess lower)

**Categorical Attributes (Team, Division, Conference):**
- ✅ **Correct**: Exact match
- ❌ **Incorrect**: No match

**Position:**
- ✅ **Correct**: Exact position match
- 🟨 **Partial**: Same position group (Guards: PG/SG/G, Forwards: SF/PF/F, Centers: C)
- ❌ **Incorrect**: Different position group

## 🐛 Troubleshooting

### Backend Issues

**nba_api errors:**
- The nba_api library may occasionally fail due to rate limits or API changes
- Check your internet connection
- Try restarting the server

**Port already in use:**
- Change port in `run.py` or use environment variable

### Frontend Issues

**Cannot connect to backend:**
- Verify `VITE_API_URL` is set correctly
- Check CORS settings in backend
- Ensure backend is running

**Build errors:**
- Clear `node_modules` and reinstall: `rm -rf node_modules && npm install`
- Check Node.js version (requires 18+)

## 📝 License

This project is open source and available for educational purposes.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Contact

For questions or issues, please open an issue on GitHub.

---

**Note**: This is a production-ready MVP. For production use, consider adding:
- Database persistence (Redis/PostgreSQL)
- Rate limiting
- Authentication (if multi-player)
- Error monitoring (Sentry)
- Analytics
