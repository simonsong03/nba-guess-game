"""
NBA Data Service - Fetches player data and statistics using nba_api
"""
from typing import List, Dict, Optional
from nba_api.stats.endpoints import commonplayerinfo, playergamelog, commonallplayers, teaminfocommon
from nba_api.stats.static import players, teams
import random
from datetime import datetime, date


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
    
    def get_all_active_players(self, season: Optional[str] = None) -> List[Dict]:
        """Get all NBA players for a given season"""
        # Use current season if not specified
        if season is None:
            season = self._get_current_season()
        
        # Cache key includes season
        cache_key = season
        
        if cache_key not in self._all_players_cache:
            try:
                # For historical seasons, get all players from that season
                if season == self._get_current_season():
                    all_players = commonallplayers.CommonAllPlayers(
                        is_only_current_season=1,
                        league_id='00'
                    )
                else:
                    # For historical seasons, get all players (not just current)
                    all_players = commonallplayers.CommonAllPlayers(
                        is_only_current_season=0,
                        league_id='00',
                        season=season
                    )
                
                players_data = all_players.get_data_frames()[0]
                
                # Filter by season if needed (for historical seasons)
                if season != self._get_current_season():
                    # Filter players who played in that season
                    # This is a simplified approach - in production, you might want
                    # to check player game logs for that season
                    pass
                
                self._all_players_cache[cache_key] = players_data.to_dict('records')
            except Exception as e:
                # Fallback to static players list
                print(f"Error fetching players for season {season}: {e}")
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
        return self.get_player_details(player['PERSON_ID'], season)
    
    def get_player_details(self, player_id: int, season: Optional[str] = None) -> Dict:
        """Get detailed information about a specific player for a given season"""
        if season is None:
            season = self._get_current_season()
        
        try:
            # Get player info (this is general info, not season-specific)
            player_info = commonplayerinfo.CommonPlayerInfo(player_id=player_id)
            info_df = player_info.get_data_frames()[0]
            
            if info_df.empty:
                raise ValueError(f"Player {player_id} not found")
            
            player_data = info_df.iloc[0].to_dict()
            
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
            try:
                game_log = playergamelog.PlayerGameLog(
                    player_id=player_id,
                    season=season
                )
                stats_df = game_log.get_data_frames()[0]
                
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
                    team_info = teaminfocommon.TeamInfoCommon(team_id=team_id)
                    team_df = team_info.team_info_common.get_data_frame()
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
            print(f"Error fetching player details for {player_id}: {e}")
            raise ValueError(f"Failed to fetch player details: {e}")
    
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
