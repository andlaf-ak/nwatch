# nwwatch - Architecture Design Document

**Project**: nwwatch (nWave Step Viewer)
**Version**: 1.0
**Date**: 2026-01-21
**Wave**: DESIGN

---

## 1. Architecture Overview

### 1.1 Architecture Style

**Hexagonal Architecture (Ports & Adapters)** for the backend, with a **Component-Based** React frontend.

This architecture provides:
- Clear separation between domain logic and infrastructure
- Easy testability through port interfaces
- Flexibility to swap adapters (e.g., different file watchers, communication protocols)

### 1.2 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              NWWATCH SYSTEM                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                         FRONTEND (React SPA)                         │    │
│  │  ┌───────────────┐  ┌───────────────┐  ┌───────────────────────┐   │    │
│  │  │  StepGrid     │  │  ThemeToggle  │  │  WebSocketClient      │   │    │
│  │  │  Component    │  │  Component    │  │  (useWebSocket hook)  │   │    │
│  │  └───────────────┘  └───────────────┘  └───────────────────────┘   │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                    │                                         │
│                                    │ WebSocket (ws://localhost:8000/ws)      │
│                                    ▼                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                      BACKEND (FastAPI + Python)                      │    │
│  │                                                                      │    │
│  │   ┌─────────────────────────────────────────────────────────────┐   │    │
│  │   │                    APPLICATION LAYER                         │   │    │
│  │   │  ┌─────────────────────┐  ┌─────────────────────────────┐   │   │    │
│  │   │  │  StepService        │  │  ConnectionManager           │   │   │    │
│  │   │  │  - get_all_steps()  │  │  - broadcast()               │   │   │    │
│  │   │  │  - on_step_change() │  │  - add/remove_connection()   │   │   │    │
│  │   │  └─────────────────────┘  └─────────────────────────────┘   │   │    │
│  │   └─────────────────────────────────────────────────────────────┘   │    │
│  │                              │                                       │    │
│  │   ┌─────────────────────────────────────────────────────────────┐   │    │
│  │   │                      DOMAIN LAYER                            │   │    │
│  │   │  ┌─────────────────┐  ┌─────────────────────────────────┐   │   │    │
│  │   │  │  Step (Entity)  │  │  StepStatus (Value Object)      │   │   │    │
│  │   │  │  - task_id      │  │  - PENDING, IN_PROGRESS,        │   │   │    │
│  │   │  │  - phase        │  │    COMPLETED, FAILED, SKIPPED   │   │   │    │
│  │   │  │  - status       │  │                                  │   │   │    │
│  │   │  └─────────────────┘  └─────────────────────────────────┘   │   │    │
│  │   └─────────────────────────────────────────────────────────────┘   │    │
│  │                              │                                       │    │
│  │   ┌─────────────────────────────────────────────────────────────┐   │    │
│  │   │                 PORTS (Interfaces)                           │   │    │
│  │   │  ┌─────────────────────┐  ┌─────────────────────────────┐   │   │    │
│  │   │  │  StepRepository     │  │  FileWatcher                 │   │   │    │
│  │   │  │  (Port - Driven)    │  │  (Port - Driving)            │   │   │    │
│  │   │  └─────────────────────┘  └─────────────────────────────┘   │   │    │
│  │   └─────────────────────────────────────────────────────────────┘   │    │
│  │                              │                                       │    │
│  │   ┌─────────────────────────────────────────────────────────────┐   │    │
│  │   │                 ADAPTERS (Infrastructure)                    │   │    │
│  │   │  ┌─────────────────────┐  ┌─────────────────────────────┐   │   │    │
│  │   │  │  JsonFileRepository │  │  WatchdogFileWatcher         │   │   │    │
│  │   │  │  (reads JSON files) │  │  (watchdog library)          │   │   │    │
│  │   │  └─────────────────────┘  └─────────────────────────────┘   │   │    │
│  │   │  ┌─────────────────────┐                                    │   │    │
│  │   │  │  WebSocketAdapter   │                                    │   │    │
│  │   │  │  (FastAPI WS)       │                                    │   │    │
│  │   │  └─────────────────────┘                                    │   │    │
│  │   └─────────────────────────────────────────────────────────────┘   │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                    │                                         │
│                                    ▼                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                         FILE SYSTEM                                  │    │
│  │                    /path/to/steps/*.json                            │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Component Architecture

### 2.1 Backend Components

#### 2.1.1 Domain Layer

**Step Entity**
```python
@dataclass
class Step:
    task_id: str           # "01-01"
    project_id: str        # "arkanoid-game"
    phase: str             # "Foundation"
    description: str
    status: StepStatus
    major_version: int     # 1 (parsed from task_id)
    minor_version: int     # 1 (parsed from task_id)
```

**StepStatus Value Object**
```python
class StepStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
```

#### 2.1.2 Ports (Interfaces)

**StepRepository Port** (Driven/Secondary)
```python
class StepRepository(Protocol):
    def get_all(self) -> list[Step]: ...
    def get_by_id(self, task_id: str) -> Step | None: ...
    def refresh(self, task_id: str) -> Step | None: ...
```

**FileWatcher Port** (Driving/Primary)
```python
class FileWatcher(Protocol):
    def start(self, callback: Callable[[FileEvent], None]) -> None: ...
    def stop(self) -> None: ...

@dataclass
class FileEvent:
    event_type: Literal["created", "modified", "deleted"]
    file_path: str
```

#### 2.1.3 Adapters (Infrastructure)

**JsonFileRepository**
- Reads step JSON files from the configured folder
- Parses JSON and transforms to Step domain objects
- Handles malformed JSON gracefully (logs error, skips file)

**WatchdogFileWatcher**
- Uses `watchdog` library for filesystem monitoring
- Filters for `.json` files only
- Debounces rapid file changes (100ms)

**WebSocketAdapter**
- FastAPI WebSocket endpoint at `/ws`
- Manages connection lifecycle
- Serializes Step objects to JSON messages

#### 2.1.4 Application Layer

**StepService**
- Orchestrates step retrieval and change notifications
- Maintains in-memory cache of steps for fast access
- Coordinates between FileWatcher events and WebSocket broadcasts

**ConnectionManager**
- Manages active WebSocket connections
- Broadcasts messages to all connected clients
- Handles connection/disconnection lifecycle

### 2.2 Frontend Components

#### 2.2.1 Component Hierarchy

```
App
├── Header
│   ├── Logo/Title
│   └── ThemeToggle
├── StepGrid
│   └── PhaseRow (for each phase)
│       └── StepCard (for each step)
│           ├── TaskId
│           ├── PhaseName
│           └── StatusBadge
└── ConnectionStatus
```

#### 2.2.2 Component Responsibilities

**App**
- Root component
- Provides theme context
- Manages WebSocket connection via custom hook

**ThemeToggle**
- Toggle button for dark/light mode
- Persists preference to localStorage
- Updates CSS variables on document root

**StepGrid**
- Receives steps array from WebSocket
- Groups steps by major_version (phase)
- Renders PhaseRow components

**PhaseRow**
- Displays phase label
- Renders StepCard components horizontally
- Draws connecting lines between cards

**StepCard**
- Displays step information (task_id, phase, status)
- Applies color based on status
- Applies pulse animation if status is "in_progress" AND is first in_progress step

**ConnectionStatus**
- Shows WebSocket connection state
- Displays reconnecting indicator when disconnected

#### 2.2.3 Custom Hooks

**useWebSocket**
```typescript
function useWebSocket(url: string): {
  steps: Step[];
  connectionStatus: 'connecting' | 'connected' | 'disconnected';
}
```
- Manages WebSocket lifecycle
- Handles reconnection with exponential backoff
- Processes incoming messages and updates step state

**useTheme**
```typescript
function useTheme(): {
  theme: 'dark' | 'light';
  toggleTheme: () => void;
}
```
- Manages theme state
- Persists to localStorage
- Updates CSS variables

---

## 3. Data Flow

### 3.1 Initial Load Sequence

```
┌──────────┐     ┌──────────┐     ┌─────────────┐     ┌──────────────┐
│  Browser │     │  FastAPI │     │ StepService │     │ JsonFileRepo │
└────┬─────┘     └────┬─────┘     └──────┬──────┘     └──────┬───────┘
     │                │                   │                   │
     │  WS Connect    │                   │                   │
     │───────────────>│                   │                   │
     │                │                   │                   │
     │                │  get_all_steps()  │                   │
     │                │──────────────────>│                   │
     │                │                   │                   │
     │                │                   │    get_all()      │
     │                │                   │──────────────────>│
     │                │                   │                   │
     │                │                   │   [Step, Step...] │
     │                │                   │<──────────────────│
     │                │                   │                   │
     │                │  [Step, Step...]  │                   │
     │                │<──────────────────│                   │
     │                │                   │                   │
     │  {type: init}  │                   │                   │
     │<───────────────│                   │                   │
     │                │                   │                   │
```

### 3.2 File Change Sequence

```
┌────────────┐  ┌───────────────┐  ┌─────────────┐  ┌─────────────┐  ┌──────────┐
│ FileSystem │  │ FileWatcher   │  │ StepService │  │ ConnManager │  │ Browser  │
└─────┬──────┘  └──────┬────────┘  └──────┬──────┘  └──────┬──────┘  └────┬─────┘
      │                │                   │                │              │
      │  file modified │                   │                │              │
      │───────────────>│                   │                │              │
      │                │                   │                │              │
      │                │  FileEvent        │                │              │
      │                │──────────────────>│                │              │
      │                │                   │                │              │
      │                │                   │  refresh(id)   │              │
      │                │                   │───────────────>│              │
      │                │                   │                │              │
      │                │                   │  broadcast()   │              │
      │                │                   │───────────────>│              │
      │                │                   │                │              │
      │                │                   │                │ {type:update}│
      │                │                   │                │─────────────>│
      │                │                   │                │              │
```

---

## 4. Directory Structure

```
nwwatch/
├── backend/
│   ├── main.py                    # FastAPI app entry point
│   ├── domain/
│   │   ├── __init__.py
│   │   ├── step.py               # Step entity, StepStatus enum
│   │   └── events.py             # FileEvent dataclass
│   ├── ports/
│   │   ├── __init__.py
│   │   ├── step_repository.py    # StepRepository protocol
│   │   └── file_watcher.py       # FileWatcher protocol
│   ├── adapters/
│   │   ├── __init__.py
│   │   ├── json_file_repository.py
│   │   ├── watchdog_file_watcher.py
│   │   └── websocket_adapter.py
│   ├── application/
│   │   ├── __init__.py
│   │   ├── step_service.py
│   │   └── connection_manager.py
│   └── requirements.txt
├── frontend/
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── App.tsx
│   │   ├── App.css
│   │   ├── index.tsx
│   │   ├── components/
│   │   │   ├── Header.tsx
│   │   │   ├── ThemeToggle.tsx
│   │   │   ├── StepGrid.tsx
│   │   │   ├── PhaseRow.tsx
│   │   │   ├── StepCard.tsx
│   │   │   └── ConnectionStatus.tsx
│   │   ├── hooks/
│   │   │   ├── useWebSocket.ts
│   │   │   └── useTheme.ts
│   │   ├── types/
│   │   │   └── step.ts
│   │   └── styles/
│   │       ├── variables.css     # CSS custom properties for theming
│   │       └── animations.css    # Pulse animation
│   ├── package.json
│   └── tsconfig.json
└── docs/
    ├── requirements/
    │   └── requirements.md
    └── architecture/
        ├── architecture-design.md
        └── diagrams/
            └── *.mmd
```

---

## 5. Technology Stack Rationale

### 5.1 Backend

| Technology | Rationale |
|------------|-----------|
| **Python 3.11+** | Modern async support, type hints, excellent ecosystem |
| **FastAPI** | Native WebSocket support, automatic OpenAPI docs, high performance with uvicorn |
| **watchdog** | Mature file system monitoring library, cross-platform support |
| **uvicorn** | ASGI server with WebSocket support, production-ready |

### 5.2 Frontend

| Technology | Rationale |
|------------|-----------|
| **React 18** | Component model suits the UI structure, large ecosystem, hooks for state management |
| **TypeScript** | Type safety for Step interfaces, better IDE support |
| **CSS Variables** | Native theming without CSS-in-JS overhead, simple implementation |
| **Vite** | Fast development server, efficient builds |

### 5.3 Alternatives Considered

| Decision | Alternative | Why Not Chosen |
|----------|-------------|----------------|
| FastAPI | Flask | Flask lacks native async/WebSocket support |
| watchdog | inotify directly | watchdog provides cross-platform abstraction |
| React | Vue.js | Both viable; React has larger ecosystem |
| CSS Variables | Styled Components | Simpler, no runtime overhead |

---

## 6. API Contract

### 6.1 WebSocket Endpoint

**URL**: `ws://localhost:8000/ws`

### 6.2 Message Schema

#### InitMessage (Server → Client)
```json
{
  "type": "init",
  "steps": [
    {
      "taskId": "01-01",
      "projectId": "arkanoid-game",
      "phase": "Foundation",
      "description": "Create Makefile...",
      "status": "completed",
      "majorVersion": 1,
      "minorVersion": 1
    }
  ]
}
```

#### UpdateMessage (Server → Client)
```json
{
  "type": "update",
  "step": {
    "taskId": "02-03",
    "projectId": "arkanoid-game",
    "phase": "Entities",
    "description": "Create paddle entity...",
    "status": "in_progress",
    "majorVersion": 2,
    "minorVersion": 3
  }
}
```

#### RemoveMessage (Server → Client)
```json
{
  "type": "remove",
  "taskId": "01-01"
}
```

### 6.3 REST Endpoints (Optional/Future)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check endpoint |
| GET | `/api/steps` | Get all steps (HTTP fallback) |

---

## 7. Quality Attributes

### 7.1 Performance

| Attribute | Target | Implementation |
|-----------|--------|----------------|
| File change detection | < 500ms | watchdog with 100ms debounce |
| Message delivery | < 100ms | Direct WebSocket push |
| UI update | < 50ms | React state update, no virtual DOM diffing overhead for single step |
| Memory (100 steps) | < 50MB | In-memory step cache, no database |

### 7.2 Reliability

| Attribute | Implementation |
|-----------|----------------|
| Malformed JSON | Log error, skip file, continue processing |
| WebSocket disconnect | Auto-reconnect with exponential backoff (1s, 2s, 4s, max 30s) |
| File watcher crash | Restart watcher, log incident |

### 7.3 Testability

| Layer | Testing Strategy |
|-------|------------------|
| Domain | Unit tests (no dependencies) |
| Ports | Interface contracts |
| Adapters | Integration tests with real files/WebSocket |
| Frontend | Component tests with React Testing Library |

---

## 8. Security Considerations

| Risk | Mitigation |
|------|------------|
| Path traversal | Validate folder path is absolute, no `..` allowed |
| WebSocket hijacking | Same-origin policy (browser enforced) |
| Malicious JSON | JSON parsing in try/catch, no code execution |

---

## 9. Deployment

### 9.1 Development

```bash
# Backend
cd backend
pip install -r requirements.txt
python main.py /path/to/steps

# Frontend
cd frontend
npm install
npm run dev
```

### 9.2 Production (Single Command)

```bash
# Start backend (serves frontend static files)
python main.py /path/to/steps --port 8000
```

The backend serves:
- WebSocket at `ws://localhost:8000/ws`
- Static frontend files at `http://localhost:8000/`

---

## 10. Open Questions / Future Considerations

| Item | Status |
|------|--------|
| Multi-folder support | Out of scope v1.0 |
| Authentication | Out of scope v1.0 |
| Step history/timeline | Out of scope v1.0 |
| Docker deployment | Consider for v1.1 |
