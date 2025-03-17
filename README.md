# Quake Log Parser

A comprehensive log parser for Quake 3 Arena server logs, designed to analyze game sessions, player performance, and generate detailed statistics.

## Project Overview

This is a log parser specifically designed to analyze game logs from Quake 3 Arena servers. It's part of an AI-driven coding challenge that tests both technical skills and the ability to work with AI tools in real-time coding.

## Main Purpose

1. Parse and analyze Quake 3 Arena server logs
2. Extract meaningful statistics about games and players
3. Generate reports about player performance and game events

## How it Works

### 1. Log File Processing
- Reads a `qgames.log.txt` file that contains server logs
- The log file contains events like:
  - Game starts (`InitGame:`)
  - Player connections (`ClientConnect:`)
  - Player kills (`Kill: [killer] killed [victim] by [weapon]`)
  - Game ends (`Exit:`, `ShutdownGame:`)

### 2. Game Parsing
The `parseGame` function:
- Processes each game session separately
- Tracks:
  - Total number of kills
  - List of players who participated
  - Kill count per player
  - Types of deaths (weapons/means used)
- Special handling for:
  - `<world>` kills (environmental deaths)
  - Negative scores when players are killed by the world
- Marks games as "aborted" if they have no kills

### 3. Ranking Generation
The `generateRanking` function:
- Creates a player ranking across all games
- Aggregates kills from all completed games
- Excludes aborted games from rankings
- Sorts players by total kills

### 4. Output Format
The parser generates a JSON report with:
```json
{
  "games": {
    "game_1": {
      "total_kills": number,
      "players": ["player1", "player2", ...],
      "kills": {
        "player1": number,
        "player2": number,
        ...
      },
      "kills_by_means": {
        "MOD_WEAPON": number,
        ...
      },
      "status": "completed" | "aborted"
    },
    ...
  },
  "ranking": [
    "1. Player1 - X kills",
    "2. Player2 - Y kills",
    ...
  ]
}
```

## Technical Features

### 1. Error Handling
- Robust file reading with try-catch blocks
- Detailed error logging
- Graceful handling of malformed data

### 2. Data Processing
- Uses Sets for unique player tracking
- Efficient kill counting and aggregation
- Proper handling of special cases (world kills)

### 3. Game State Management
- Tracks game sessions separately
- Identifies and marks aborted games
- Maintains game boundaries using InitGame events

## Use Cases

### 1. Game Analysis
- Track player performance
- Analyze weapon usage
- Monitor game sessions

### 2. Statistics Generation
- Player rankings
- Kill/death ratios
- Weapon effectiveness

### 3. Server Monitoring
- Track game sessions
- Identify failed/aborted games
- Monitor player participation

## Project Significance

This project serves as a practical example of:
- Log parsing and analysis
- Data aggregation and reporting
- Game statistics processing
- Error handling and robust programming
- Working with structured data formats (JSON)

The challenge aspect of this project tests:
- Code organization and structure
- Problem-solving abilities
- Understanding of game mechanics
- Data processing capabilities
- Integration with AI tools for development
