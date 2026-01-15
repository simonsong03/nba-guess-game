"""
Wordle Engine - Game logic for comparing guesses to target player
"""
from typing import Dict, List, Optional


class WordleEngine:
    """Engine for comparing player guesses to target player"""
    
    def __init__(self, target_player: Dict, season: Optional[str] = None):
        """
        Initialize engine with target player
        
        Args:
            target_player: Dict with player details (id, name, team, division, 
                         conference, age, height, position, jersey_number, ppg)
            season: NBA season string (e.g., '2023-24')
        """
        self.target_player = target_player
        self.season = season
        self.guesses = []
        self.max_guesses = 8
    
    def make_guess(self, guessed_player: Dict) -> Dict:
        """
        Compare guessed player to target player
        
        Args:
            guessed_player: Dict with player details to compare
            
        Returns:
            Dict with comparison results for each attribute
        """
        if len(self.guesses) >= self.max_guesses:
            raise ValueError("Maximum guesses reached")
        
        comparison = {
            'team': self._compare_team(guessed_player),
            'division': self._compare_division(guessed_player),
            'conference': self._compare_conference(guessed_player),
            'age': self._compare_age(guessed_player),
            'height': self._compare_height(guessed_player),
            'position': self._compare_position(guessed_player),
            'jersey_number': self._compare_jersey(guessed_player),
            'ppg': self._compare_ppg(guessed_player)
        }
        
        is_correct = guessed_player.get('id') == self.target_player.get('id')
        
        guess_result = {
            'guessed_player': {
                'id': guessed_player.get('id'),
                'name': guessed_player.get('name'),
                'team': guessed_player.get('team', ''),
                'division': guessed_player.get('division', ''),
                'conference': guessed_player.get('conference', ''),
                'age': guessed_player.get('age'),
                'height': guessed_player.get('height', ''),
                'position': guessed_player.get('position', ''),
                'jersey_number': guessed_player.get('jersey_number'),
                'ppg': guessed_player.get('ppg', 0.0)
            },
            'comparison': comparison,
            'is_correct': is_correct,
            'guess_number': len(self.guesses) + 1
        }
        
        self.guesses.append(guess_result)
        
        return guess_result
    
    def _compare_team(self, guessed: Dict) -> Dict:
        """Compare team - exact match only"""
        target_team = self.target_player.get('team', '')
        guessed_team = guessed.get('team', '')
        
        target_team_lower = target_team.lower() if target_team else ''
        guessed_team_lower = guessed_team.lower() if guessed_team else ''
        
        if not target_team_lower or not guessed_team_lower:
            return {
                'attribute': 'team',
                'guessed': guessed_team,
                'target': target_team,
                'status': 'incorrect'
            }
        
        if target_team_lower == guessed_team_lower:
            return {
                'attribute': 'team',
                'guessed': guessed_team,
                'target': target_team,
                'status': 'correct'
            }
        
        # Check abbreviation match
        target_abbrev = self.target_player.get('team_abbreviation', '').lower()
        guessed_abbrev = guessed.get('team_abbreviation', '').lower()
        
        if target_abbrev and guessed_abbrev and target_abbrev == guessed_abbrev:
            return {
                'attribute': 'team',
                'guessed': guessed_team,
                'target': target_team,
                'status': 'correct'
            }
        
        return {
            'attribute': 'team',
            'guessed': guessed_team,
            'target': target_team,
            'status': 'incorrect'
        }
    
    def _compare_division(self, guessed: Dict) -> Dict:
        """Compare division - exact match only"""
        target_div = self.target_player.get('division', '')
        guessed_div = guessed.get('division', '')
        
        target_div_lower = target_div.lower() if target_div else ''
        guessed_div_lower = guessed_div.lower() if guessed_div else ''
        
        if not target_div_lower or not guessed_div_lower:
            return {
                'attribute': 'division',
                'guessed': guessed_div,
                'target': target_div,
                'status': 'incorrect'
            }
        
        if target_div_lower == guessed_div_lower:
            return {
                'attribute': 'division',
                'guessed': guessed_div,
                'target': target_div,
                'status': 'correct'
            }
        
        return {
            'attribute': 'division',
            'guessed': guessed_div,
            'target': target_div,
            'status': 'incorrect'
        }
    
    def _compare_conference(self, guessed: Dict) -> Dict:
        """Compare conference - exact match only"""
        target_conf = self.target_player.get('conference', '')
        guessed_conf = guessed.get('conference', '')
        
        target_conf_lower = target_conf.lower() if target_conf else ''
        guessed_conf_lower = guessed_conf.lower() if guessed_conf else ''
        
        if not target_conf_lower or not guessed_conf_lower:
            return {
                'attribute': 'conference',
                'guessed': guessed_conf,
                'target': target_conf,
                'status': 'incorrect'
            }
        
        if target_conf_lower == guessed_conf_lower:
            return {
                'attribute': 'conference',
                'guessed': guessed_conf,
                'target': target_conf,
                'status': 'correct'
            }
        
        return {
            'attribute': 'conference',
            'guessed': guessed_conf,
            'target': target_conf,
            'status': 'incorrect'
        }
    
    def _compare_age(self, guessed: Dict) -> Dict:
        """Compare age - directional feedback (higher/lower/correct)"""
        target_age = self.target_player.get('age')
        guessed_age = guessed.get('age')
        
        if target_age is None or guessed_age is None:
            return {
                'attribute': 'age',
                'guessed': guessed_age,
                'target': target_age,
                'status': 'incorrect'
            }
        
        if target_age == guessed_age:
            return {
                'attribute': 'age',
                'guessed': guessed_age,
                'target': target_age,
                'status': 'correct'
            }
        
        if guessed_age < target_age:
            return {
                'attribute': 'age',
                'guessed': guessed_age,
                'target': target_age,
                'status': 'higher'
            }
        
        return {
            'attribute': 'age',
            'guessed': guessed_age,
            'target': target_age,
            'status': 'lower'
        }
    
    def _compare_height(self, guessed: Dict) -> Dict:
        """Compare height - directional feedback (higher/lower/correct)"""
        target_height = self.target_player.get('height', '')
        guessed_height = guessed.get('height', '')
        
        if not target_height or not guessed_height:
            return {
                'attribute': 'height',
                'guessed': guessed_height,
                'target': target_height,
                'status': 'incorrect'
            }
        
        if target_height == guessed_height:
            return {
                'attribute': 'height',
                'guessed': guessed_height,
                'target': target_height,
                'status': 'correct'
            }
        
        # Convert to inches for comparison
        target_inches = self._height_to_inches(target_height)
        guessed_inches = self._height_to_inches(guessed_height)
        
        if target_inches is None or guessed_inches is None:
            return {
                'attribute': 'height',
                'guessed': guessed_height,
                'target': target_height,
                'status': 'incorrect'
            }
        
        if guessed_inches == target_inches:
            return {
                'attribute': 'height',
                'guessed': guessed_height,
                'target': target_height,
                'status': 'correct'
            }
        
        if guessed_inches < target_inches:
            return {
                'attribute': 'height',
                'guessed': guessed_height,
                'target': target_height,
                'status': 'higher'
            }
        
        return {
            'attribute': 'height',
            'guessed': guessed_height,
            'target': target_height,
            'status': 'lower'
        }
    
    def _compare_position(self, guessed: Dict) -> Dict:
        """Compare position - exact match or partial (same position group)"""
        target_pos = self.target_player.get('position', '')
        guessed_pos = guessed.get('position', '')
        
        target_pos_upper = target_pos.upper() if target_pos else ''
        guessed_pos_upper = guessed_pos.upper() if guessed_pos else ''
        
        if not target_pos_upper or not guessed_pos_upper:
            return {
                'attribute': 'position',
                'guessed': guessed_pos,
                'target': target_pos,
                'status': 'incorrect'
            }
        
        if target_pos_upper == guessed_pos_upper:
            return {
                'attribute': 'position',
                'guessed': guessed_pos,
                'target': target_pos,
                'status': 'correct'
            }
        
        # Partial match: same position group
        # Guards: PG, SG, G
        # Forwards: SF, PF, F
        # Centers: C
        guard_positions = {'PG', 'SG', 'G'}
        forward_positions = {'SF', 'PF', 'F'}
        center_positions = {'C'}
        
        target_group = None
        guessed_group = None
        
        if any(pos in target_pos_upper for pos in guard_positions):
            target_group = 'guard'
        elif any(pos in target_pos_upper for pos in forward_positions):
            target_group = 'forward'
        elif 'C' in target_pos_upper:
            target_group = 'center'
        
        if any(pos in guessed_pos_upper for pos in guard_positions):
            guessed_group = 'guard'
        elif any(pos in guessed_pos_upper for pos in forward_positions):
            guessed_group = 'forward'
        elif 'C' in guessed_pos_upper:
            guessed_group = 'center'
        
        if target_group and guessed_group and target_group == guessed_group:
            return {
                'attribute': 'position',
                'guessed': guessed_pos,
                'target': target_pos,
                'status': 'partial'
            }
        
        return {
            'attribute': 'position',
            'guessed': guessed_pos,
            'target': target_pos,
            'status': 'incorrect'
        }
    
    def _compare_jersey(self, guessed: Dict) -> Dict:
        """Compare jersey number - directional feedback (higher/lower/correct)"""
        target_jersey = self.target_player.get('jersey_number')
        guessed_jersey = guessed.get('jersey_number')
        
        if target_jersey is None or guessed_jersey is None:
            return {
                'attribute': 'jersey_number',
                'guessed': guessed_jersey,
                'target': target_jersey,
                'status': 'incorrect'
            }
        
        if target_jersey == guessed_jersey:
            return {
                'attribute': 'jersey_number',
                'guessed': guessed_jersey,
                'target': target_jersey,
                'status': 'correct'
            }
        
        if guessed_jersey < target_jersey:
            return {
                'attribute': 'jersey_number',
                'guessed': guessed_jersey,
                'target': target_jersey,
                'status': 'higher'
            }
        
        return {
            'attribute': 'jersey_number',
            'guessed': guessed_jersey,
            'target': target_jersey,
            'status': 'lower'
        }
    
    def _compare_ppg(self, guessed: Dict) -> Dict:
        """Compare PPG - directional feedback (higher/lower/correct)"""
        target_ppg = self.target_player.get('ppg', 0.0)
        guessed_ppg = guessed.get('ppg', 0.0)
        
        if target_ppg == guessed_ppg:
            return {
                'attribute': 'ppg',
                'guessed': guessed_ppg,
                'target': target_ppg,
                'status': 'correct'
            }
        
        if guessed_ppg < target_ppg:
            return {
                'attribute': 'ppg',
                'guessed': guessed_ppg,
                'target': target_ppg,
                'status': 'higher'
            }
        
        return {
            'attribute': 'ppg',
            'guessed': guessed_ppg,
            'target': target_ppg,
            'status': 'lower'
        }
    
    def _height_to_inches(self, height_str: str) -> Optional[int]:
        """Convert height string (e.g., '6-8') to inches"""
        try:
            parts = height_str.split('-')
            if len(parts) == 2:
                feet = int(parts[0])
                inches = int(parts[1])
                return feet * 12 + inches
        except:
            pass
        return None
    
    def is_game_over(self) -> bool:
        """Check if game is over (won or max guesses reached)"""
        if self.guesses and self.guesses[-1]['is_correct']:
            return True
        return len(self.guesses) >= self.max_guesses
    
    def is_won(self) -> bool:
        """Check if game is won"""
        return self.guesses and self.guesses[-1]['is_correct'] if self.guesses else False
    
    def get_game_state(self) -> Dict:
        """Get current game state"""
        return {
            'target_player_id': self.target_player.get('id'),
            'target_player_name': self.target_player.get('name'),
            'season': self.season,
            'guesses': self.guesses,
            'guess_count': len(self.guesses),
            'max_guesses': self.max_guesses,
            'is_game_over': self.is_game_over(),
            'is_won': self.guesses and self.guesses[-1]['is_correct'] if self.guesses else False
        }
