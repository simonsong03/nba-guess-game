# Cache Population Script

## Purpose
This script populates the players cache JSON file that serves as a fallback when the NBA API is unavailable.

## Usage

```bash
cd backend
python scripts/populate_cache.py
```

This will:
1. Fetch all players for the 2025-26 season from the NBA API
2. Save them to `backend/app/data/players_cache.json`
3. The service will automatically use this cache if the API times out

## When to Run
- Before deploying to production
- Periodically to update the cache with latest players
- After the NBA season starts/ends

## Note
The cache file should be committed to git so it's available in production as a fallback.
