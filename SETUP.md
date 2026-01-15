# Quick Setup Guide

## Backend Setup (5 minutes)

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
python run.py
```

Backend runs on `http://localhost:8000`

## Frontend Setup (3 minutes)

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on `http://localhost:3000`

## Testing

```bash
cd backend
pytest                    # Run all tests
pytest tests/test_wordle_engine.py  # Unit tests only
pytest tests/test_api.py            # Integration tests only
pytest --cov=app tests/  # With coverage
```

## Project Structure

```
nba-wordle/
├── backend/           # FastAPI backend
│   ├── app/
│   │   ├── main.py   # FastAPI app
│   │   ├── routes/   # API endpoints
│   │   └── services/ # Business logic
│   └── tests/        # Unit tests
├── frontend/          # React frontend
│   └── src/          # React components
├── README.md         # Full documentation
├── DESIGN.md         # Design document
└── ARCHITECTURE.md   # Architecture diagrams
```

## Environment Variables

### Frontend
Create `frontend/.env`:
```
VITE_API_URL=http://localhost:8000
```

### Backend
No environment variables needed for local development.

## Common Issues

1. **nba_api errors**: The library may be slow or fail occasionally. This is normal.
2. **Port conflicts**: Change ports in `run.py` (backend) or `vite.config.js` (frontend)
3. **CORS errors**: Ensure backend CORS allows `http://localhost:3000`
4. **Player images not loading**: Some players may not have images on NBA.com CDN - this is expected
5. **Duplicate guess error**: You cannot guess the same player twice in one game

## Next Steps

1. Read `README.md` for full documentation
2. Check `DESIGN.md` for architecture details
3. Review `ARCHITECTURE.md` for system diagrams
4. Deploy using instructions in `README.md`
