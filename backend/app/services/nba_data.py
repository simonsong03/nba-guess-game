"""
NBA Data Service - Fetches player data and statistics using nba_api
"""
from typing import List, Dict, Optional
from nba_api.stats.endpoints import commonplayerinfo, playergamelog, commonallplayers, teaminfocommon
from nba_api.stats.static import players, teams
import random
import time
import json
import os
from pathlib import Path
from datetime import datetime, date
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


def get_available_seasons() -> List[str]:
    """Get list of available NBA seasons in format 'YYYY-YY'"""
    seasons = []
    # NBA started in 1946-47
    start_year = 1946
    
    # Get current season (NBA season starts in October)
    current_date = datetime.now()
    current_year = current_date.year
    current_month = current_date.month
    
    # NBA season starts in October, so if we're before October, use previous year
    if current_month < 10:
        end_year = current_year - 1
    else:
        end_year = current_year
    
    # Generate seasons from 1946-47 to current season (not future seasons)
    for year in range(start_year, end_year + 1):
        # Format: "YYYY-YY" (e.g., "2023-24")
        next_year_short = str(year + 1)[-2:]
        season_str = f"{year}-{next_year_short}"
        seasons.append(season_str)
    
    # Reverse to show most recent first
    return list(reversed(seasons))


class NBADataService:
    """Service for fetching NBA player data and statistics"""
    
    def __init__(self):
        self._all_players_cache = {}
        self._teams_cache = None
        self._setup_retry_session()
        self._cache_file = Path(__file__).parent.parent / "data" / "players_cache.json"
    
    def _setup_retry_session(self):
        """Setup requests session with retry logic for NBA API calls"""
        # Configure retry strategy
        retry_strategy = Retry(
            total=3,  # Total number of retries
            backoff_factor=2,  # Wait 2, 4, 8 seconds between retries
            status_forcelist=[429, 500, 502, 503, 504],  # Retry on these status codes
            allowed_methods=["GET", "POST"],
            raise_on_status=False
        )
        
        # Create adapter with retry strategy
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=10,
            pool_maxsize=10
        )
        
        # Create session and mount adapter
        self.session = requests.Session()
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Set longer timeout
        self.session.timeout = 60  # 60 seconds timeout
        
        # Default headers to mimic browser (helps avoid blocking)
        self.default_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.nba.com/',
            'Origin': 'https://www.nba.com'
        }
    
    def _load_cached_players(self, season: str) -> Optional[List[Dict]]:
        """Load players from cached JSON file"""
        try:
            if not self._cache_file.exists():
                return None
            
            with open(self._cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            # Check if cache is for the right season
            if cache_data.get('season') == season:
                print(f"✅ Loaded {len(cache_data.get('players', []))} players from cache")
                return cache_data.get('players', [])
            
            return None
        except Exception as e:
            print(f"⚠️ Error loading cache: {e}")
            return None
    
    def _retry_api_call(self, func, *args, max_retries=3, delay=2, **kwargs):
        """Wrapper to retry API calls with exponential backoff"""
        last_exception = None
        for attempt in range(max_retries):
            try:
                # Add delay between retries (except first attempt)
                if attempt > 0:
                    wait_time = delay * (2 ** (attempt - 1))  # Exponential backoff
                    print(f"Retrying after {wait_time} seconds...")
                    time.sleep(wait_time)
                
                return func(*args, **kwargs)
            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError, 
                    requests.exceptions.ReadTimeout, Exception) as e:
                last_exception = e
                error_msg = str(e)
                print(f"API call attempt {attempt + 1}/{max_retries} failed: {error_msg}")
                
                # If it's the last attempt, raise the exception
                if attempt == max_retries - 1:
                    print(f"All {max_retries} attempts failed. Raising exception.")
                    raise
                
                # Continue to next retry
        raise last_exception if last_exception else Exception("Unknown error in retry logic")
    
    def get_all_active_players(self, season: Optional[str] = None) -> List[Dict]:
        """Get all NBA players for a given season"""
        # Use current season if not specified
        if season is None:
            season = self._get_current_season()
        
        # Cache key includes season
        cache_key = season
        
        if cache_key not in self._all_players_cache:
            try:
                def fetch_players():
                    # For historical seasons, get all players from that season
                    if season == self._get_current_season():
                        all_players = commonallplayers.CommonAllPlayers(
                            is_only_current_season=1,
                            league_id='00',
                            timeout=10,  # Shorter timeout - we'll fallback quickly
                            headers=self.default_headers
                        )
                    else:
                        # For historical seasons, get all players (not just current)
                        all_players = commonallplayers.CommonAllPlayers(
                            is_only_current_season=0,
                            league_id='00',
                            season=season,
                            timeout=10,  # Shorter timeout - we'll fallback quickly
                            headers=self.default_headers
                        )
                    return all_players.get_data_frames()[0]
                
                # Try API with shorter timeout and fewer retries
                players_data = self._retry_api_call(fetch_players, max_retries=2, delay=1)
                
                # Filter by season if needed (for historical seasons)
                if season != self._get_current_season():
                    # Filter players who played in that season
                    # This is a simplified approach - in production, you might want
                    # to check player game logs for that season
                    pass
                
                self._all_players_cache[cache_key] = players_data.to_dict('records')
                print(f"✅ Fetched {len(self._all_players_cache[cache_key])} players from NBA API")
            except Exception as e:
                # Fallback to cached JSON file
                print(f"⚠️ NBA API failed for season {season}: {e}")
                print("🔄 Attempting to load from cache...")
                
                cached_players = self._load_cached_players(season)
                if cached_players:
                    self._all_players_cache[cache_key] = cached_players
                    print(f"✅ Using cached players (fallback mode)")
                else:
                    # Last resort: static players list
                    print("⚠️ Cache not available, using static players list...")
                    try:
                        all_players = players.get_players()
                        self._all_players_cache[cache_key] = [
                            {
                                'PERSON_ID': p['id'],
                                'DISPLAY_FIRST_LAST': p['full_name'],
                                'TEAM_ID': None,
                                'TEAM_ABBREVIATION': None
                            }
                            for p in all_players
                        ]
                        print(f"✅ Using static players list ({len(self._all_players_cache[cache_key])} players)")
                    except Exception as fallback_error:
                        print(f"❌ All fallbacks failed: {fallback_error}")
                        raise ValueError(f"Failed to fetch players for season {season} - API, cache, and static list all failed")
        
        return self._all_players_cache[cache_key]
    
    def _get_current_season(self) -> str:
        """Get current NBA season string"""
        current_year = datetime.now().year
        current_month = datetime.now().month
        
        # NBA season starts in October, so if we're before October, use previous year
        if current_month < 10:
            year = current_year - 1
        else:
            year = current_year
        
        next_year_short = str(year + 1)[-2:]
        return f"{year}-{next_year_short}"
    
    def get_random_player(self, season: Optional[str] = None) -> Dict:
        """Get a random NBA player from a given season"""
        if season is None:
            season = self._get_current_season()
        
        active_players = self.get_all_active_players(season)
        if not active_players:
            raise ValueError(f"No players found for season {season}")
        
        player = random.choice(active_players)
        # Small delay to avoid rate limiting
        time.sleep(0.5)
        return self.get_player_details(player['PERSON_ID'], season)
    
    def get_player_details(self, player_id: int, season: Optional[str] = None) -> Dict:
        """Get detailed information about a specific player for a given season"""
        if season is None:
            season = self._get_current_season()
        
        try:
            # Get player info (this is general info, not season-specific)
            def fetch_player_info():
                player_info = commonplayerinfo.CommonPlayerInfo(
                    player_id=player_id,
                    timeout=10,  # Shorter timeout - fail fast and use cached players
                    headers=self.default_headers
                )
                return player_info.get_data_frames()[0]
            
            # Retry with exponential backoff (fewer retries for faster fallback)
            info_df = self._retry_api_call(fetch_player_info, max_retries=2, delay=1)
            
            if info_df.empty:
                raise ValueError(f"Player {player_id} not found")
            
            player_data = info_df.iloc[0].to_dict()
            
            # Small delay between API calls to avoid rate limiting
            time.sleep(0.3)
            
            # Calculate age from birthdate
            age = None
            birthdate_str = player_data.get('BIRTHDATE')
            if birthdate_str:
                try:
                    # Parse birthdate (format: "YYYY-MM-DDT00:00:00")
                    birth_date = datetime.strptime(birthdate_str.split("T")[0], "%Y-%m-%d").date()
                    today = date.today()
                    age = today.year - birth_date.year
                    # Adjust if birthday hasn't occurred yet this year
                    if (today.month, today.day) < (birth_date.month, birth_date.day):
                        age -= 1
                except Exception as e:
                    print(f"Error calculating age from birthdate {birthdate_str}: {e}")
                    age = None
            
            # Get stats for the specified season
            ppg = 0.0
            try:
                def fetch_player_stats():
                    game_log = playergamelog.PlayerGameLog(
                        player_id=player_id,
                        season=season,
                        timeout=10,  # Shorter timeout
                        headers=self.default_headers
                    )
                    return game_log.get_data_frames()[0]
                
                # Retry with exponential backoff (fewer retries)
                stats_df = self._retry_api_call(fetch_player_stats, max_retries=2, delay=1)
                
                # Small delay after stats call
                time.sleep(0.3)
                
                if not stats_df.empty:
                    # Calculate PPG from the specified season
                    ppg = stats_df['PTS'].mean()
                else:
                    # Player didn't play in this season
                    ppg = 0.0
            except Exception as e:
                print(f"Error fetching stats for player {player_id} in season {season}: {e}")
                ppg = 0.0
            
            # Get team info
            team_id = player_data.get('TEAM_ID')
            team_abbrev = player_data.get('TEAM_ABBREVIATION', '')
            team_name = player_data.get('TEAM_NAME', '')
            
            # Get division and conference
            division = None
            conference = None
            if team_id:
                try:
                    def fetch_team_info():
                        team_info = teaminfocommon.TeamInfoCommon(
                            team_id=team_id,
                            timeout=10,  # Shorter timeout
                            headers=self.default_headers
                        )
                        return team_info.team_info_common.get_data_frame()
                    
                    # Retry with exponential backoff (fewer retries for team info as it's less critical)
                    team_df = self._retry_api_call(fetch_team_info, max_retries=1, delay=1)
                    
                    if not team_df.empty:
                        division = team_df.iloc[0].get('TEAM_DIVISION', '')
                        conference = team_df.iloc[0].get('TEAM_CONFERENCE', '')
                except Exception as e:
                    print(f"Error fetching team info for team_id {team_id}: {e}")
                    pass
            
            # Generate player image URL (NBA.com format)
            player_id_str = str(player_data.get('PERSON_ID', player_id))
            # NBA.com uses format: https://cdn.nba.com/headshots/nba/latest/1040x760/{player_id}.png
            image_url = f"https://cdn.nba.com/headshots/nba/latest/1040x760/{player_id_str}.png"
            
            return {
                'id': int(player_data.get('PERSON_ID', player_id)),
                'name': player_data.get('DISPLAY_FIRST_LAST', 'Unknown'),
                'team': team_name or team_abbrev or 'Free Agent',
                'team_abbreviation': team_abbrev or '',
                'division': division or '',
                'conference': conference or '',
                'age': age,
                'height': player_data.get('HEIGHT', ''),
                'position': player_data.get('POSITION', ''),
                'jersey_number': int(player_data.get('JERSEY', 0)) if player_data.get('JERSEY') else None,
                'ppg': round(float(ppg), 1) if ppg else 0.0,
                'image_url': image_url
            }
        except Exception as e:
            error_msg = str(e)
            print(f"Error fetching player details for {player_id}: {error_msg}")
            # Provide more helpful error message
            if "timeout" in error_msg.lower() or "timed out" in error_msg.lower():
                raise ValueError(f"NBA API request timed out for player {player_id}. Please try again.")
            elif "connection" in error_msg.lower():
                raise ValueError(f"Failed to connect to NBA API for player {player_id}. Please try again.")
            else:
                raise ValueError(f"Failed to fetch player details for {player_id}: {error_msg}")
    
    def search_players(self, query: str, limit: int = 20, season: Optional[str] = None) -> List[Dict]:
        """Search for players by name for a given season"""
        if not query or len(query) < 2:
            return []
        
        query_lower = query.lower()
        active_players = self.get_all_active_players(season)
        
        matches = []
        for player in active_players:
            name = player.get('DISPLAY_FIRST_LAST', '')
            if query_lower in name.lower():
                player_id_str = str(player['PERSON_ID'])
                image_url = f"https://cdn.nba.com/headshots/nba/latest/1040x760/{player_id_str}.png"
                matches.append({
                    'id': player['PERSON_ID'],
                    'name': name,
                    'team': player.get('TEAM_ABBREVIATION', ''),
                    'image_url': image_url
                })
                if len(matches) >= limit:
                    break
        
        return matches
    
    def get_teams_info(self) -> Dict:
        """Get teams information for division/conference lookup"""
        if self._teams_cache is None:
            try:
                all_teams = teams.get_teams()
                self._teams_cache = {team['abbreviation']: team for team in all_teams}
            except:
                self._teams_cache = {}
        return self._teams_cache
