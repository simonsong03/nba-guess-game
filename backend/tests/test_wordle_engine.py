"""
Unit tests for Wordle Engine game logic
"""
import pytest
from app.services.wordle_engine import WordleEngine


@pytest.fixture
def sample_target_player():
    """Sample target player for testing"""
    return {
        'id': 1,
        'name': 'LeBron James',
        'team': 'Los Angeles Lakers',
        'team_abbreviation': 'LAL',
        'division': 'Pacific',
        'conference': 'West',
        'age': 39,
        'height': '6-9',
        'position': 'SF',
        'jersey_number': 23,
        'ppg': 25.0
    }


@pytest.fixture
def sample_guessed_player():
    """Sample guessed player for testing"""
    return {
        'id': 2,
        'name': 'Stephen Curry',
        'team': 'Golden State Warriors',
        'team_abbreviation': 'GSW',
        'division': 'Pacific',
        'conference': 'West',
        'age': 35,
        'height': '6-2',
        'position': 'PG',
        'jersey_number': 30,
        'ppg': 26.0
    }


def test_exact_match_team(sample_target_player, sample_guessed_player):
    """Test exact team match"""
    engine = WordleEngine(sample_target_player)
    
    # Same team
    guessed = sample_guessed_player.copy()
    guessed['team'] = 'Los Angeles Lakers'
    guessed['team_abbreviation'] = 'LAL'
    
    result = engine.make_guess(guessed)
    team_comp = result['comparison']['team']
    assert team_comp['status'] == 'correct'
    assert team_comp['guessed'] == 'Los Angeles Lakers'
    assert team_comp['target'] == 'Los Angeles Lakers'


def test_incorrect_match_team(sample_target_player, sample_guessed_player):
    """Test incorrect team match"""
    engine = WordleEngine(sample_target_player)
    
    result = engine.make_guess(sample_guessed_player)
    team_comp = result['comparison']['team']
    assert team_comp['status'] == 'incorrect'
    assert team_comp['guessed'] == 'Golden State Warriors'
    assert team_comp['target'] == 'Los Angeles Lakers'


def test_exact_match_conference(sample_target_player, sample_guessed_player):
    """Test exact conference match"""
    engine = WordleEngine(sample_target_player)
    
    result = engine.make_guess(sample_guessed_player)
    conf_comp = result['comparison']['conference']
    assert conf_comp['status'] == 'correct'
    assert conf_comp['guessed'] == 'West'
    assert conf_comp['target'] == 'West'


def test_exact_match_division(sample_target_player, sample_guessed_player):
    """Test exact division match"""
    engine = WordleEngine(sample_target_player)
    
    result = engine.make_guess(sample_guessed_player)
    div_comp = result['comparison']['division']
    assert div_comp['status'] == 'correct'
    assert div_comp['guessed'] == 'Pacific'
    assert div_comp['target'] == 'Pacific'


def test_age_higher(sample_target_player, sample_guessed_player):
    """Test age - guessed is lower, need higher"""
    engine = WordleEngine(sample_target_player)
    
    # Age 35 < 39, should return "higher"
    result = engine.make_guess(sample_guessed_player)
    age_comp = result['comparison']['age']
    assert age_comp['status'] == 'higher'
    assert age_comp['guessed'] == 35
    assert age_comp['target'] == 39


def test_age_lower(sample_target_player):
    """Test age - guessed is higher, need lower"""
    engine = WordleEngine(sample_target_player)
    
    guessed = {
        'id': 2,
        'name': 'Test Player',
        'age': 42,  # Higher than target 39
        'team': 'Test Team',
        'division': '',
        'conference': '',
        'height': '',
        'position': '',
        'jersey_number': 0,
        'ppg': 0.0
    }
    
    result = engine.make_guess(guessed)
    age_comp = result['comparison']['age']
    assert age_comp['status'] == 'lower'
    assert age_comp['guessed'] == 42
    assert age_comp['target'] == 39


def test_age_correct(sample_target_player):
    """Test age - exact match"""
    engine = WordleEngine(sample_target_player)
    
    guessed = {
        'id': 2,
        'name': 'Test Player',
        'age': 39,
        'team': 'Test Team',
        'division': '',
        'conference': '',
        'height': '',
        'position': '',
        'jersey_number': 0,
        'ppg': 0.0
    }
    
    result = engine.make_guess(guessed)
    age_comp = result['comparison']['age']
    assert age_comp['status'] == 'correct'
    assert age_comp['guessed'] == 39
    assert age_comp['target'] == 39


def test_height_higher(sample_target_player, sample_guessed_player):
    """Test height - guessed is shorter, need taller"""
    engine = WordleEngine(sample_target_player)
    
    # 6-2 (74 inches) < 6-9 (81 inches), should return "higher"
    result = engine.make_guess(sample_guessed_player)
    height_comp = result['comparison']['height']
    assert height_comp['status'] == 'higher'
    assert height_comp['guessed'] == '6-2'
    assert height_comp['target'] == '6-9'


def test_height_lower(sample_target_player):
    """Test height - guessed is taller, need shorter"""
    engine = WordleEngine(sample_target_player)
    
    guessed = {
        'id': 2,
        'name': 'Test Player',
        'height': '7-0',  # Taller than 6-9
        'team': 'Test Team',
        'division': '',
        'conference': '',
        'age': 0,
        'position': '',
        'jersey_number': 0,
        'ppg': 0.0
    }
    
    result = engine.make_guess(guessed)
    height_comp = result['comparison']['height']
    assert height_comp['status'] == 'lower'
    assert height_comp['guessed'] == '7-0'
    assert height_comp['target'] == '6-9'


def test_height_correct(sample_target_player):
    """Test height - exact match"""
    engine = WordleEngine(sample_target_player)
    
    guessed = {
        'id': 2,
        'name': 'Test Player',
        'height': '6-9',
        'team': 'Test Team',
        'division': '',
        'conference': '',
        'age': 0,
        'position': '',
        'jersey_number': 0,
        'ppg': 0.0
    }
    
    result = engine.make_guess(guessed)
    height_comp = result['comparison']['height']
    assert height_comp['status'] == 'correct'
    assert height_comp['guessed'] == '6-9'
    assert height_comp['target'] == '6-9'


def test_position_correct(sample_target_player):
    """Test position - exact match"""
    engine = WordleEngine(sample_target_player)
    
    guessed = {
        'id': 2,
        'name': 'Test Player',
        'position': 'SF',
        'team': 'Test Team',
        'division': '',
        'conference': '',
        'age': 0,
        'height': '',
        'jersey_number': 0,
        'ppg': 0.0
    }
    
    result = engine.make_guess(guessed)
    pos_comp = result['comparison']['position']
    assert pos_comp['status'] == 'correct'
    assert pos_comp['guessed'] == 'SF'
    assert pos_comp['target'] == 'SF'


def test_position_partial(sample_target_player, sample_guessed_player):
    """Test position - partial match (same position group)"""
    engine = WordleEngine(sample_target_player)
    
    # SF vs PG - different groups, should be incorrect
    result = engine.make_guess(sample_guessed_player)
    pos_comp = result['comparison']['position']
    assert pos_comp['status'] == 'incorrect'
    
    # SF vs PF - same group (forward), should be partial
    guessed = sample_guessed_player.copy()
    guessed['position'] = 'PF'
    result2 = engine.make_guess(guessed)
    pos_comp2 = result2['comparison']['position']
    assert pos_comp2['status'] == 'partial'
    assert pos_comp2['guessed'] == 'PF'
    assert pos_comp2['target'] == 'SF'


def test_position_partial_guards(sample_target_player):
    """Test position - partial match between guards"""
    engine = WordleEngine(sample_target_player)
    
    # Change target to PG
    target = sample_target_player.copy()
    target['position'] = 'PG'
    engine = WordleEngine(target)
    
    # PG vs SG - same group (guard), should be partial
    guessed = {
        'id': 2,
        'name': 'Test Player',
        'position': 'SG',
        'team': 'Test Team',
        'division': '',
        'conference': '',
        'age': 0,
        'height': '',
        'jersey_number': 0,
        'ppg': 0.0
    }
    
    result = engine.make_guess(guessed)
    pos_comp = result['comparison']['position']
    assert pos_comp['status'] == 'partial'
    assert pos_comp['guessed'] == 'SG'
    assert pos_comp['target'] == 'PG'


def test_jersey_higher(sample_target_player, sample_guessed_player):
    """Test jersey number - guessed is lower, need higher"""
    engine = WordleEngine(sample_target_player)
    
    # Jersey 30 > 23, should return "lower"
    result = engine.make_guess(sample_guessed_player)
    jersey_comp = result['comparison']['jersey_number']
    assert jersey_comp['status'] == 'lower'
    assert jersey_comp['guessed'] == 30
    assert jersey_comp['target'] == 23


def test_jersey_lower(sample_target_player):
    """Test jersey number - guessed is higher, need lower"""
    engine = WordleEngine(sample_target_player)
    
    guessed = {
        'id': 2,
        'name': 'Test Player',
        'jersey_number': 15,  # Lower than 23
        'team': 'Test Team',
        'division': '',
        'conference': '',
        'age': 0,
        'height': '',
        'position': '',
        'ppg': 0.0
    }
    
    result = engine.make_guess(guessed)
    jersey_comp = result['comparison']['jersey_number']
    assert jersey_comp['status'] == 'higher'
    assert jersey_comp['guessed'] == 15
    assert jersey_comp['target'] == 23


def test_jersey_correct(sample_target_player):
    """Test jersey number - exact match"""
    engine = WordleEngine(sample_target_player)
    
    guessed = {
        'id': 2,
        'name': 'Test Player',
        'jersey_number': 23,
        'team': 'Test Team',
        'division': '',
        'conference': '',
        'age': 0,
        'height': '',
        'position': '',
        'ppg': 0.0
    }
    
    result = engine.make_guess(guessed)
    jersey_comp = result['comparison']['jersey_number']
    assert jersey_comp['status'] == 'correct'
    assert jersey_comp['guessed'] == 23
    assert jersey_comp['target'] == 23


def test_ppg_higher(sample_target_player, sample_guessed_player):
    """Test PPG - guessed is lower, need higher"""
    engine = WordleEngine(sample_target_player)
    
    # PPG 26.0 > 25.0, should return "lower" (need to guess lower)
    result = engine.make_guess(sample_guessed_player)
    ppg_comp = result['comparison']['ppg']
    assert ppg_comp['status'] == 'lower'
    assert ppg_comp['guessed'] == 26.0
    assert ppg_comp['target'] == 25.0


def test_ppg_lower(sample_target_player):
    """Test PPG - guessed is higher, need lower"""
    engine = WordleEngine(sample_target_player)
    
    guessed = {
        'id': 2,
        'name': 'Test Player',
        'ppg': 20.0,  # Lower than 25.0
        'team': 'Test Team',
        'division': '',
        'conference': '',
        'age': 0,
        'height': '',
        'position': '',
        'jersey_number': 0
    }
    
    result = engine.make_guess(guessed)
    ppg_comp = result['comparison']['ppg']
    assert ppg_comp['status'] == 'higher'
    assert ppg_comp['guessed'] == 20.0
    assert ppg_comp['target'] == 25.0


def test_ppg_correct(sample_target_player):
    """Test PPG - exact match"""
    engine = WordleEngine(sample_target_player)
    
    guessed = {
        'id': 2,
        'name': 'Test Player',
        'ppg': 25.0,
        'team': 'Test Team',
        'division': '',
        'conference': '',
        'age': 0,
        'height': '',
        'position': '',
        'jersey_number': 0
    }
    
    result = engine.make_guess(guessed)
    ppg_comp = result['comparison']['ppg']
    assert ppg_comp['status'] == 'correct'
    assert ppg_comp['guessed'] == 25.0
    assert ppg_comp['target'] == 25.0


def test_correct_guess(sample_target_player):
    """Test correct player guess"""
    engine = WordleEngine(sample_target_player)
    
    result = engine.make_guess(sample_target_player)
    assert result['is_correct'] is True
    assert engine.is_game_over() is True
    assert engine.is_won() is True


def test_max_guesses(sample_target_player, sample_guessed_player):
    """Test maximum guesses limit"""
    engine = WordleEngine(sample_target_player)
    
    # Make 8 guesses
    for i in range(8):
        guessed = sample_guessed_player.copy()
        guessed['id'] = i + 10
        engine.make_guess(guessed)
    
    assert engine.is_game_over() is True
    assert len(engine.guesses) == 8
    
    # Should raise error on 9th guess
    with pytest.raises(ValueError):
        engine.make_guess(sample_guessed_player)


def test_game_state(sample_target_player, sample_guessed_player):
    """Test game state retrieval"""
    engine = WordleEngine(sample_target_player)
    
    state = engine.get_game_state()
    assert state['target_player_id'] == sample_target_player['id']
    assert state['guess_count'] == 0
    assert state['max_guesses'] == 8
    assert state['is_game_over'] is False
    
    engine.make_guess(sample_guessed_player)
    state = engine.get_game_state()
    assert state['guess_count'] == 1


def test_duplicate_guess_prevention(sample_target_player, sample_guessed_player):
    """Test that you cannot guess the same player twice"""
    engine = WordleEngine(sample_target_player)
    
    # Make first guess
    result1 = engine.make_guess(sample_guessed_player)
    assert result1['guess_number'] == 1
    
    # Try to guess the same player again (should raise error)
    with pytest.raises(ValueError, match="already guessed"):
        engine.make_guess(sample_guessed_player)
    
    # Verify we can still make other guesses
    different_player = sample_guessed_player.copy()
    different_player['id'] = 999
    different_player['name'] = 'Different Player'
    result2 = engine.make_guess(different_player)
    assert result2['guess_number'] == 2
