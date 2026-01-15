# Cache Population Script

## Purpose
This script populates BOTH the players list cache AND the full player details cache. This ensures the app has complete data available even when the NBA API is unavailable.

## Usage

```bash
cd backend
python scripts/populate_cache.py
```

This will:
1. Fetch all players for the 2025-26 season from the NBA API
2. Save the players list to `backend/app/data/players_cache.json`
3. Fetch FULL details (age, height, position, jersey, ppg, etc.) for each player
4. Save all player details to `backend/app/data/player_details_cache.json`

## Important Notes

⚠️ **This script takes 30-60 minutes to complete** because it fetches detailed data for 500+ players.

✅ **Run this once** before deploying to production, then commit both cache files to git.

✅ The app will use cached data immediately (no API calls) if cache is available, making it fast and reliable.

## When to Run
- **Before deploying to production** (required for full functionality)
- Periodically to update the cache with latest players/stats
- After the NBA season starts/ends

## Cache Files
- `players_cache.json` - List of all players (basic info)
- `player_details_cache.json` - Full details for all players (complete data)

Both files should be committed to git so they're available in production.
