# Two Flags Game

A strategic board game inspired by chess, focused on pawn movement and capture mechanics. Players compete to either reach the opposite side of the board with a pawn or capture all opponent's pieces.

## Game Overview

Two Flags Game offers three play modes:
- **Human vs Human** - Network play with two clients connecting to a server
- **Human vs AI** - Play against a computer opponent
- **AI vs External Agent** - Test the built-in AI against an external chess engine

## Getting Started

You can run the game either using the executable files (Windows) or directly with Python scripts.

### Requirements for Python Version
- Python 3.6 or higher
- Pygame (for graphics): `pip install pygame`

## Game Rules
- Each player controls 8 pawns
- Pawns move forward one square (or two on their first move)
- Pawns capture diagonally (including en passant)
- Win by reaching the opposite side of the board, capturing all opponent pieces, or leaving the opponent with no valid moves

## Game Modes

### Local Play (Human vs AI)

Using executables:
```
dist\play_local.exe --white human --black ai --time 5
```

Using Python:
```
python play_local.py --white human --black ai --time 5
```

This will start a game where you play as white against the AI with a 5-minute timer.

To play as black:

Using executables:
```
dist\play_local.exe --white ai --black human --time 5
```

Using Python:
```
python play_local.py --white ai --black human --time 5
```

### Network Play (Human vs Human)

#### Using executables:

1. Start the server:
   ```
   dist\server.exe
   ```
   
2. Then, each player runs a client:
   ```
   dist\client.exe
   ```

#### Using Python:

1. Start the server:
   ```
   python -m server.server
   ```
   
2. Then, each player runs a client:
   ```
   python -m client.client
   ```

For network play across different computers, use:

Using executables:
```
dist\client.exe --host [server-ip]
```

Using Python:
```
python -m client.client --host [server-ip]
```

### AI vs External Agent

Using executables:
```
dist\ai_vs_external.exe C:\path\to\external\agent.exe
```

Using Python:
```
python ai_vs_external.py C:\path\to\external\agent.exe
```

## Controls
- Use the mouse to select and move pieces
- The game highlights valid moves when a piece is selected

## Project Structure

```
TwoFlagsGame/               # Main project folder
├── assets/                 # Game resources
│   ├── white_pawn.png      # White pawn image
│   └── black_pawn.png      # Black pawn image
├── client/                 # Client code
│   ├── __init__.py         # Package initialization
│   ├── client.py           # Network client
│   ├── protocol.py         # Communication protocol
│   └── UserInterface.py    # Game UI
├── game/                   # Core game
│   ├── __init__.py         # Package initialization
│   ├── board.py            # Game board
│   ├── rules.py            # Game rules
│   ├── state.py            # Game state
│   └── timer.py            # Game timer
├── search/                 # AI components
│   ├── __init__.py         # Package initialization
│   ├── ai_agent.py         # AI implementation
│   ├── evaluation.py       # Board evaluation
│   └── minmax.py           # Minmax algorithm
├── server/                 # Server code
│   ├── __init__.py         # Package initialization
│   └── server.py           # Game server
├── dist/                   # Executable files
│   ├── play_local.exe      # Local play executable
│   ├── server.exe          # Game server executable
│   ├── client.exe          # Game client executable
│   └── ai_vs_external.exe  # AI vs External executable
├── ai_vs_external.py       # AI vs external agent script
├── play_local.py           # Local game script
└── README.md               # This file
```

## Troubleshooting

- If executables don't run, try running as administrator
- For network play, ensure your firewall isn't blocking the connection
- If using Python version, ensure all required packages are installed
- If the game runs slowly, close other applications to free up memory

## Credits

Two Flags Game was developed as a chess variant with simplified rules focusing on pawn movement strategies.