"""
Script to populate the players cache from NBA API.
Run this locally to generate backend/app/data/players_cache.json
"""
import sys
import json
import time
from pathlib import Path
from datetime import datetime

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from nba_api.stats.endpoints import commonallplayers

def populate_cache():
    """Fetch all players for 2025-26 season and save to cache"""
    print("Fetching players from NBA API (this may take a minute)...")
    
    try:
        season = "2025-26"
        
        # Direct API call with longer timeout for cache population
        print("Calling NBA API...")
        all_players = commonallplayers.CommonAllPlayers(
            is_only_current_season=1,
            league_id='00',
            timeout=120  # Longer timeout for cache population
        )
        
        players_df = all_players.get_data_frames()[0]
        players = players_df.to_dict('records')
        
        print(f"✅ Fetched {len(players)} players from NBA API")
        
        # Convert to cache format
        cache_data = {
            "season": season,
            "players": players,
            "last_updated": datetime.now().isoformat()
        }
        
        # Save to cache file
        cache_dir = Path(__file__).parent.parent / "app" / "data"
        cache_dir.mkdir(parents=True, exist_ok=True)
        cache_file = cache_dir / "players_cache.json"
        
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Successfully cached {len(players)} players to {cache_file}")
        return True
        
    except Exception as e:
        print(f"❌ Error populating cache: {e}")
        return False

if __name__ == "__main__":
    success = populate_cache()
    sys.exit(0 if success else 1)
