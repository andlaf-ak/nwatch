# nwwatch

Real-time workflow step viewer for the nWave agentic framework. Displays development steps as connected cards in a grid layout, with real-time updates via WebSocket.

## Features

- Real-time step monitoring via WebSocket
- Steps displayed in a grid layout grouped by phase
- Color-coded status indicators (pending, in_progress, completed, failed, skipped)
- Pulsing glow effect on the current in-progress step
- Dark/light theme toggle with persistence
- File watcher for automatic updates when step files change

## Prerequisites

- Python 3.11+
- Node.js 18+
- npm

## Installation

### Backend

```bash
cd /path/to/nwwatch

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install fastapi uvicorn watchdog websockets
```

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Build for production
npm run build
```

## Usage

### Running the Server

```bash
source venv/bin/activate
python backend/main.py /path/to/steps/folder
```

The server starts at `http://localhost:8000`.

**Arguments:**
- `steps_folder` (required): Path to the folder containing step JSON files

### Step File Format

Each step is a JSON file named with the pattern `XX-YY.json` (e.g., `01-02.json`):

```json
{
  "task_id": "01-02",
  "project_id": "my-project",
  "phase": "implement",
  "description": "Implement core functionality",
  "validation": {
    "status": "pending"
  }
}
```

**Status values:** `pending`, `in_progress`, `completed`, `failed`, `skipped`

## Emulator

A step emulator is included for testing the UI without a real nWave workflow.

### Interactive Mode

```bash
python backend/emulator.py /tmp/test-steps --interactive
```

**Commands:**
| Command | Description |
|---------|-------------|
| `n` / `next` | Complete current step, start next |
| `f` / `fail` | Fail current step |
| `s` / `skip` | Skip current step |
| `a` / `auto` | Switch to automatic mode |
| `r` / `restart` | Restart simulation |
| `q` / `quit` | Exit |

### Automatic Mode

```bash
python backend/emulator.py /tmp/test-steps --delay 2 --failure-rate 0.1
```

**Options:**
| Option | Description | Default |
|--------|-------------|---------|
| `--steps`, `-n` | Number of steps to create | 15 |
| `--delay`, `-d` | Seconds between transitions | 2.0 |
| `--failure-rate`, `-f` | Probability of step failure (0.0-1.0) | 0.1 |
| `--project`, `-p` | Project ID | test-project |
| `--interactive`, `-i` | Enable interactive mode | false |

## Architecture

The project follows hexagonal architecture:

```
backend/
├── domain/           # Core business logic
│   ├── step.py       # Step entity and StepStatus enum
│   └── events.py     # FileEvent domain events
├── ports/            # Interface definitions
│   ├── file_watcher.py
│   └── step_repository.py
├── adapters/         # External implementations
│   ├── json_file_repository.py
│   └── watchdog_file_watcher.py
├── application/      # Application services
│   ├── step_service.py
│   └── connection_manager.py
├── main.py           # FastAPI entry point
└── emulator.py       # Test emulator

frontend/
├── src/
│   ├── components/   # React components
│   ├── hooks/        # Custom React hooks
│   ├── styles/       # CSS files
│   └── types/        # TypeScript types
└── dist/             # Production build
```

## Development

### Frontend Development

```bash
cd frontend
npm run dev
```

This starts a development server with hot reload at `http://localhost:5173`.

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## License

MIT
