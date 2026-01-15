import React, { useState, useEffect } from 'react'
import axios from 'axios'
import './App.css'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function App() {
  const [gameId, setGameId] = useState(null)
  const [guesses, setGuesses] = useState([])
  const [isGameOver, setIsGameOver] = useState(false)
  const [isWon, setIsWon] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [searchResults, setSearchResults] = useState([])
  const [selectedPlayer, setSelectedPlayer] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    startNewGame()
  }, [])

  const startNewGame = async () => {
    try {
      setIsLoading(true)
      setError(null)
      const response = await axios.post(`${API_BASE_URL}/api/start-game`)
      setGameId(response.data.game_id)
      setGuesses([])
      setIsGameOver(false)
      setIsWon(false)
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
      setSelectedPlayer(null)
      setSearchQuery('')
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to make guess. Please try again.')
      console.error(err)
    } finally {
      setIsLoading(false)
    }
  }

  const getMatchIcon = (comparison) => {
    // Handle both old format (string) and new format (object)
    if (typeof comparison === 'string') {
      // Legacy format support
      switch (comparison) {
        case 'exact':
        case 'correct':
          return '✅'
        case 'partial':
          return '🟨'
        case 'none':
        case 'incorrect':
          return '❌'
        default:
          return '❌'
      }
    }
    
    // New format: object with status field
    if (comparison && comparison.status) {
      switch (comparison.status) {
        case 'correct':
          return '✅'
        case 'partial':
          return '🟨'
        case 'higher':
          return '⬆️'
        case 'lower':
          return '⬇️'
        case 'incorrect':
        default:
          return '❌'
      }
    }
    
    return '❌'
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
      <header className="header">
        <h1>🏀 NBA Wordle</h1>
        <p>Guess the NBA player in 8 tries!</p>
        <p className="season-display">Season: 2025-26</p>
      </header>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {isGameOver && (
        <div className={`game-over ${isWon ? 'won' : 'lost'}`}>
          <h2>{isWon ? '🎉 Congratulations! You guessed it!' : '😔 Game Over!'}</h2>
          <button onClick={startNewGame} className="new-game-btn">
            New Game
          </button>
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
          <div key={index} className="guess-card">
            <div className="guess-header">
              <div className="player-header-info">
                {guess.guessed_player.image_url && (
                  <img 
                    src={guess.guessed_player.image_url} 
                    alt={guess.guessed_player.name}
                    className="player-image"
                    onError={(e) => {
                      // Hide image if it fails to load
                      e.target.style.display = 'none'
                    }}
                  />
                )}
                <h3>{guess.guessed_player.name}</h3>
              </div>
              <span className="guess-number">Guess #{guess.guess_number}</span>
            </div>
            <div className="guess-comparison">
              {attributes.map((attr) => {
                const comparison = guess.comparison[attr.key]
                const guessedValue = guess.guessed_player[attr.key]
                return (
                  <div key={attr.key} className="comparison-item">
                    <span className="attr-label">{attr.label}:</span>
                    <span className="attr-value">
                      {getComparisonValue(comparison, guessedValue)}
                    </span>
                    <span className="match-icon" title={comparison?.status || ''}>
                      {getMatchIcon(comparison)}
                    </span>
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
