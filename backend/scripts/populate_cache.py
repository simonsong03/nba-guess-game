"""
Script to populate the players cache and player details cache from NBA API.
Run this locally to generate backend/app/data/players_cache.json and player_details_cache.json

This will fetch ALL player details - it may take 30-60 minutes depending on API speed.
"""
import sys
import json
import time
from pathlib import Path
from datetime import datetime, date

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from nba_api.stats.endpoints import commonallplayers, commonplayerinfo, playergamelog, teaminfocommon

def populate_cache():
    """Fetch all players and their full details for 2025-26 season and save to cache"""
    season = "2025-26"
    
    print("=" * 60)
    print("NBA Wordle Cache Population Script")
    print("=" * 60)
    print(f"Season: {season}")
    print("This will fetch ALL player details - may take 30-60 minutes")
    print("=" * 60)
    
    try:
        # Step 1: Fetch players list
        print("\nStep 1: Fetching players list...")
        all_players = commonallplayers.CommonAllPlayers(
            is_only_current_season=1,
            league_id='00',
            timeout=120
        )
        players_df = all_players.get_data_frames()[0]
        players = players_df.to_dict('records')
        print(f"✅ Fetched {len(players)} players")
        
        # Save players list cache
        cache_dir = Path(__file__).parent.parent / "app" / "data"
        cache_dir.mkdir(parents=True, exist_ok=True)
        players_cache_file = cache_dir / "players_cache.json"
        
        players_cache_data = {
            "season": season,
            "players": players,
            "last_updated": datetime.now().isoformat()
        }
        
        with open(players_cache_file, 'w', encoding='utf-8') as f:
            json.dump(players_cache_data, f, indent=2, ensure_ascii=False)
        print(f"✅ Saved players list to {players_cache_file}")
        
        # Step 2: Fetch full details for each player
        print(f"\n📊 Step 2: Fetching full details for {len(players)} players...")
        print("This will take a while - please be patient...")
        
        player_details_cache = {}
        teams_info_cache = {}  # Cache team_id -> (division, conference)
        
        successful = 0
        failed = 0
        
        for i, player in enumerate(players, 1):
            player_id = player.get('PERSON_ID')
            player_name = player.get('DISPLAY_FIRST_LAST', 'Unknown')
            
            if not player_id:
                continue
            
            try:
                # Fetch player info
                player_info = commonplayerinfo.CommonPlayerInfo(
                    player_id=player_id,
                    timeout=30
                )
                info_df = player_info.get_data_frames()[0]
                
                if info_df.empty:
                    print(f"  ⚠️ [{i}/{len(players)}] {player_name}: No info found")
                    failed += 1
                    continue
                
                player_data = info_df.iloc[0].to_dict()
                
                # Calculate age
                age = None
                birthdate_str = player_data.get('BIRTHDATE')
                if birthdate_str:
                    try:
                        birth_date = datetime.strptime(birthdate_str.split("T")[0], "%Y-%m-%d").date()
                        today = date.today()
                        age = today.year - birth_date.year
                        if (today.month, today.day) < (birth_date.month, birth_date.day):
                            age -= 1
                    except:
                        pass
                
                # Fetch stats
                ppg = 0.0
                try:
                    game_log = playergamelog.PlayerGameLog(
                        player_id=player_id,
                        season=season,
                        timeout=30
                    )
                    stats_df = game_log.get_data_frames()[0]
                    if not stats_df.empty:
                        ppg = stats_df['PTS'].mean()
                except:
                    pass
                
                # Get team info
                team_id = player_data.get('TEAM_ID')
                team_abbrev = player_data.get('TEAM_ABBREVIATION', '')
                team_name = player_data.get('TEAM_NAME', '')
                
                # Get division and conference from API
                division = ''
                conference = ''
                if team_id:
                    # Check cache first
                    if team_id in teams_info_cache:
                        division, conference = teams_info_cache[team_id]
                    else:
                        # Fetch from API
                        try:
                            team_info = teaminfocommon.TeamInfoCommon(
                                team_id=team_id,
                                timeout=30
                            )
                            team_df = team_info.team_info_common.get_data_frame()
                            if not team_df.empty:
                                division = team_df.iloc[0].get('TEAM_DIVISION', '')
                                conference = team_df.iloc[0].get('TEAM_CONFERENCE', '')
                                # Cache it
                                teams_info_cache[team_id] = (division, conference)
                        except Exception as e:
                            # If it fails, cache empty values to avoid retrying
                            teams_info_cache[team_id] = ('', '')
                            if i <= 5:  # Only show first few errors
                                print(f"    ⚠️ Could not fetch team info for {team_name}: {e}")
                
                # Build player details
                player_id_str = str(player_id)
                image_url = f"https://cdn.nba.com/headshots/nba/latest/1040x760/{player_id_str}.png"
                
                player_details = {
                    'id': player_id,
                    'name': player_data.get('DISPLAY_FIRST_LAST', player_name),
                    'team': team_name or team_abbrev or 'Free Agent',
                    'team_abbreviation': team_abbrev or '',
                    'division': division,
                    'conference': conference,
                    'age': age,
                    'height': player_data.get('HEIGHT', ''),
                    'position': player_data.get('POSITION', ''),
                    'jersey_number': int(player_data.get('JERSEY', 0)) if player_data.get('JERSEY') else None,
                    'ppg': round(float(ppg), 1) if ppg else 0.0,
                    'image_url': image_url,
                    'season': season
                }
                
                player_details_cache[player_id_str] = player_details
                successful += 1
                
                # Progress update every 10 players
                if i % 10 == 0:
                    print(f"  ✅ [{i}/{len(players)}] {player_name} - Progress: {successful} successful, {failed} failed")
                
                # Small delay to avoid rate limiting
                time.sleep(0.5)
                
            except Exception as e:
                failed += 1
                if i % 10 == 0 or failed <= 5:  # Show first few failures
                    print(f"  ❌ [{i}/{len(players)}] {player_name}: {str(e)[:50]}")
                continue
        
        # Save player details cache
        details_cache_file = cache_dir / "player_details_cache.json"
        details_cache_data = {
            'last_updated': datetime.now().isoformat(),
            'players': player_details_cache
        }
        
        with open(details_cache_file, 'w', encoding='utf-8') as f:
            json.dump(details_cache_data, f, indent=2, ensure_ascii=False)
        
        print("\n" + "=" * 60)
        print("✅ Cache Population Complete!")
        print(f"   Players list: {len(players)} players")
        print(f"   Player details: {successful} successful, {failed} failed")
        print(f"   Saved to: {details_cache_file}")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error populating cache: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = populate_cache()
    sys.exit(0 if success else 1)
