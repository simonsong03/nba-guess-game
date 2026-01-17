import React, { useState, useEffect } from 'react'
import axios from 'axios'
import './App.css'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// NBA Logo Component - Using official NBA logo from NBA CDN
const NBALogo = ({ className }) => {
  return (
    <img 
      src="https://cdn.nba.com/logos/nba/nba-logoman-word-white.svg" 
      alt="NBA Logo" 
      className={className}
    />
  )
}

// Icon components
const CheckIcon = ({ className }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" />
  </svg>
)

const XIcon = ({ className }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
  </svg>
)

const ArrowUpIcon = ({ className }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
  </svg>
)

const ArrowDownIcon = ({ className }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
  </svg>
)

const WaveIcon = ({ className }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 12c2.5-2.5 5-2.5 7.5 0s5 2.5 7.5 0M5 12c2.5 2.5 5 2.5 7.5 0s5-2.5 7.5 0" />
  </svg>
)

function App() {
  const [gameId, setGameId] = useState(null)
  const [guesses, setGuesses] = useState([])
  const [isGameOver, setIsGameOver] = useState(false)
  const [isWon, setIsWon] = useState(false)
  const [targetPlayer, setTargetPlayer] = useState(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [searchResults, setSearchResults] = useState([])
  const [selectedPlayer, setSelectedPlayer] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)
  const [showOverlay, setShowOverlay] = useState(false)

  useEffect(() => {
    startNewGame()
  }, [])

  const startNewGame = async () => {
    try {
      setIsLoading(true)
      setError(null)
      setShowOverlay(false)
      const response = await axios.post(`${API_BASE_URL}/api/start-game`)
      setGameId(response.data.game_id)
      setGuesses([])
      setIsGameOver(false)
      setIsWon(false)
      setTargetPlayer(null)
      setSelectedPlayer(null)
      setSearchQuery('')
      setSearchResults([])
    } catch (err) {
      setError('Failed to start game. Please try again.')
      console.error(err)
    } finally {
      setIsLoading(false)
    }
  }

  const handleSearch = async (query) => {
    setSearchQuery(query)
    if (query.length < 2) {
      setSearchResults([])
      return
    }

    try {
      const response = await axios.get(`${API_BASE_URL}/api/player-search`, {
        params: { 
          q: query, 
          limit: 10
        }
      })
      setSearchResults(response.data)
    } catch (err) {
      console.error(err)
      setSearchResults([])
    }
  }

  const handleSelectPlayer = (player) => {
    setSelectedPlayer(player)
    setSearchQuery(player.name)
    setSearchResults([])
  }

  const handleGuess = async () => {
    if (!selectedPlayer || !gameId || isGameOver) return

    try {
      setIsLoading(true)
      setError(null)
      const response = await axios.post(`${API_BASE_URL}/api/guess`, {
        game_id: gameId,
        player_id: selectedPlayer.id
      })

      const newGuess = response.data
      setGuesses([...guesses, newGuess])
      setIsGameOver(newGuess.is_game_over)
      setIsWon(newGuess.is_won)
      
      // If game is over, show overlay with target player
      if (newGuess.is_game_over && newGuess.target_player) {
        setTargetPlayer(newGuess.target_player)
        // Small delay to allow guess animation to complete
        setTimeout(() => {
          setShowOverlay(true)
        }, 500)
      }
      
      setSelectedPlayer(null)
      setSearchQuery('')
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to make guess. Please try again.')
      console.error(err)
    } finally {
      setIsLoading(false)
    }
  }

  const getStatusIcon = (comparison) => {
    // Handle both old format (string) and new format (object)
    let status = 'incorrect'
    if (typeof comparison === 'string') {
      status = comparison === 'exact' || comparison === 'correct' ? 'correct' : 
               comparison === 'partial' ? 'partial' : 'incorrect'
    } else if (comparison && comparison.status) {
      status = comparison.status
    }
    
    switch (status) {
      case 'correct':
        return <CheckIcon className="status-icon status-icon-correct" />
      case 'partial':
        return <WaveIcon className="status-icon status-icon-partial" />
      case 'higher':
        return <ArrowUpIcon className="status-icon status-icon-higher" />
      case 'lower':
        return <ArrowDownIcon className="status-icon status-icon-lower" />
      case 'incorrect':
      default:
        return <XIcon className="status-icon status-icon-incorrect" />
    }
  }
  
  const getComparisonValue = (comparison, guessedValue) => {
    // Handle both old format (string) and new format (object)
    if (typeof comparison === 'string') {
      return guessedValue ?? 'N/A'
    }
    
    // New format: show guessed value
    if (comparison && comparison.guessed !== undefined) {
      return comparison.guessed ?? 'N/A'
    }
    
    return guessedValue ?? 'N/A'
  }

  const attributes = [
    { key: 'team', label: 'Team' },
    { key: 'division', label: 'Division' },
    { key: 'conference', label: 'Conference' },
    { key: 'age', label: 'Age' },
    { key: 'height', label: 'Height' },
    { key: 'position', label: 'Position' },
    { key: 'jersey_number', label: 'Jersey #' },
    { key: 'ppg', label: 'PPG' }
  ]

  return (
    <div className="app">
      {/* Win/Loss Overlay */}
      {showOverlay && targetPlayer && (
        <div className={`game-overlay ${isWon ? 'won' : 'lost'}`}>
          <div className="overlay-content">
            <div className="overlay-header">
              <h2 className="overlay-title">
                {isWon ? '🎉 YOU GOT IT!' : 'GAME OVER'}
              </h2>
              <p className="overlay-subtitle">
                {isWon ? 'Congratulations!' : 'Better luck next time!'}
              </p>
            </div>
            
            <div className="target-player-card">
              <div className="target-player-image-wrapper">
                <img 
                  src={targetPlayer.image_url || ''} 
                  alt={targetPlayer.name || 'Player'}
                  className="target-player-image"
                  onError={(e) => {
                    e.target.style.display = 'none'
                    const placeholder = e.target.parentElement.querySelector('.target-player-placeholder')
                    if (placeholder) placeholder.classList.remove('hidden')
                  }}
                />
                <div className={`target-player-placeholder ${targetPlayer.image_url ? 'hidden' : ''}`}>
                  <span>?</span>
                </div>
              </div>
              <h3 className="target-player-name">{targetPlayer.name}</h3>
              <p className="target-player-team">{targetPlayer.team}</p>
              
              <div className="target-player-stats">
                {attributes.map((attr) => {
                  const value = targetPlayer[attr.key]
                  return (
                    <div key={attr.key} className="target-stat-badge">
                      <span className="target-stat-label">{attr.label}</span>
                      <span className="target-stat-value">{value || 'N/A'}</span>
                      <CheckIcon className="target-stat-check" />
                    </div>
                  )
                })}
              </div>
            </div>
            
            <button onClick={startNewGame} className="play-again-btn">
              Play Again
            </button>
          </div>
        </div>
      )}

      <header className="header">
        <div className="header-banner">
          <div className="header-logo-wrapper">
            <NBALogo className="nba-logo" />
          </div>
          <div className="header-title-section">
            <h1 className="header-title">NBA WORDLE</h1>
            <p className="header-subtitle">Guess the NBA player in 8 tries!</p>
            <p className="season-display">Season: 2025-26</p>
          </div>
        </div>
      </header>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {!isGameOver && (
        <div className="game-controls">
          <div className="search-container">
            <input
              type="text"
              placeholder="Search for a player..."
              value={searchQuery}
              onChange={(e) => handleSearch(e.target.value)}
              className="search-input"
              disabled={isLoading}
            />
            {searchResults.length > 0 && (
              <div className="search-results">
                {searchResults.map((player) => (
                  <div
                    key={player.id}
                    className="search-result-item"
                    onClick={() => handleSelectPlayer(player)}
                  >
                    {player.image_url && (
                      <img 
                        src={player.image_url} 
                        alt={player.name}
                        className="search-result-image"
                        onError={(e) => {
                          e.target.style.display = 'none'
                        }}
                      />
                    )}
                    <span className="player-name">{player.name}</span>
                    <span className="player-team">{player.team}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
          <button
            onClick={handleGuess}
            disabled={!selectedPlayer || isLoading}
            className="guess-btn"
          >
            {isLoading ? 'Guessing...' : 'Guess'}
          </button>
        </div>
      )}

      <div className="guesses-container">
        <h2>Guesses ({guesses.length}/8)</h2>
        {guesses.length === 0 && (
          <p className="no-guesses">No guesses yet. Start guessing!</p>
        )}
        {guesses.map((guess, index) => (
          <div key={index} className={`guess-row guess-row-${index + 1}`}>
            <div className="guess-player-section">
              <div className="player-image-wrapper">
                <img 
                  src={guess.guessed_player?.image_url || ''} 
                  alt={guess.guessed_player?.name || 'Player'}
                  className="player-headshot"
                  onError={(e) => {
                    e.target.style.display = 'none'
                    const placeholder = e.target.parentElement.querySelector('.player-image-placeholder')
                    if (placeholder) {
                      placeholder.classList.remove('hidden')
                    }
                  }}
                  onLoad={(e) => {
                    const placeholder = e.target.parentElement.querySelector('.player-image-placeholder')
                    if (placeholder) {
                      placeholder.classList.add('hidden')
                    }
                  }}
                  style={{ display: guess.guessed_player?.image_url ? 'block' : 'none' }}
                />
                <div className={`player-image-placeholder ${guess.guessed_player?.image_url ? 'hidden' : ''}`}>
                  <span className="placeholder-text">?</span>
                </div>
              </div>
              <div className="player-info">
                <h3 className="player-name-large">{guess.guessed_player.name}</h3>
                <span className="guess-number-badge">Guess #{guess.guess_number}</span>
              </div>
            </div>
            <div className="guess-attributes-grid">
              {attributes.map((attr) => {
                const comparison = guess.comparison[attr.key]
                const guessedValue = getComparisonValue(comparison, guess.guessed_player[attr.key])
                const status = typeof comparison === 'object' && comparison?.status 
                  ? comparison.status 
                  : typeof comparison === 'string' 
                    ? (comparison === 'exact' || comparison === 'correct' ? 'correct' : comparison === 'partial' ? 'partial' : 'incorrect')
                    : 'incorrect'
                
                return (
                  <div key={attr.key} className={`stat-badge stat-badge-${status}`}>
                    <div className="stat-badge-header">
                      <span className="stat-badge-label">{attr.label}</span>
                      <div className="stat-badge-icon">
                        {getStatusIcon(comparison)}
                      </div>
                    </div>
                    <div className="stat-badge-value">{guessedValue}</div>
                  </div>
                )
              })}
            </div>
          </div>
        ))}
      </div>

      {guesses.length > 0 && !isGameOver && (
        <button onClick={startNewGame} className="new-game-btn">
          Start New Game
        </button>
      )}
    </div>
  )
}

export default App
