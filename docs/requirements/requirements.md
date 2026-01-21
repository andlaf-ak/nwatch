# nWave Step Viewer - Requirements Document

**Project**: nwwatch
**Version**: 1.0
**Date**: 2026-01-21
**Status**: DISCUSS wave complete

---

## 1. Overview

### 1.1 Purpose
A real-time web application that visualizes nWave development steps. The viewer displays steps as connected colored rectangles in a grid layout, with the current in-progress step pulsing to indicate active work.

### 1.2 Problem Statement
During nWave-driven development, steps are created as JSON files in a `steps/` folder. Developers need visual feedback on:
- Which steps exist and their states
- Which step is currently being executed
- Overall progress through the development phases

### 1.3 Target Users
- Developers using the nWave agentic framework
- Team leads monitoring development progress

---

## 2. Functional Requirements

### 2.1 Step File Monitoring

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-01 | Backend watches a specified steps folder for JSON file changes | Must |
| FR-02 | Folder path specified via command line argument | Must |
| FR-03 | Detect file creation, modification, and deletion | Must |
| FR-04 | Parse step JSON files to extract: task_id, project_id, phase, description, validation.status | Must |

### 2.2 Real-time Communication

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-05 | WebSocket connection between backend and frontend | Must |
| FR-06 | Push updates to frontend when step files change | Must |
| FR-07 | Initial load sends all current steps to frontend | Must |
| FR-08 | Handle reconnection gracefully if WebSocket disconnects | Should |

### 2.3 Step Visualization

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-09 | Display steps as rectangles in a grid layout | Must |
| FR-10 | Group steps by phase (rows based on major version: 01-xx, 02-xx, etc.) | Must |
| FR-11 | Connect rectangles with lines showing flow/dependencies | Should |
| FR-12 | Each rectangle displays: task_id, phase name, status | Must |
| FR-13 | Current step (first with status "in_progress") pulses | Must |

### 2.4 Step States and Colors (Traffic Light Style)

| State | Color | Description |
|-------|-------|-------------|
| pending | Gray | Step not yet started |
| in_progress | Yellow/Amber | Step currently executing (pulses) |
| completed | Green | Step finished successfully |
| failed | Red | Step encountered an error |
| skipped | Blue | Step was skipped |

### 2.5 Theme Support

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-14 | Support dark mode theme | Must |
| FR-15 | Support light mode theme | Must |
| FR-16 | User toggle to switch between themes | Must |
| FR-17 | Persist theme preference (localStorage) | Should |

---

## 3. Non-Functional Requirements

### 3.1 Performance

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-01 | File change detection latency | < 500ms |
| NFR-02 | WebSocket message delivery | < 100ms |
| NFR-03 | UI update after receiving message | < 50ms |
| NFR-04 | Support up to 100 steps without performance degradation | Must |

### 3.2 Reliability

| ID | Requirement |
|----|-------------|
| NFR-05 | Backend handles missing or malformed JSON files gracefully |
| NFR-06 | Frontend displays error state if WebSocket connection lost |
| NFR-07 | Auto-reconnect WebSocket after disconnection |

### 3.3 Usability

| ID | Requirement |
|----|-------------|
| NFR-08 | No manual refresh required - updates appear automatically |
| NFR-09 | Visual indication when a step state changes (brief highlight) |
| NFR-10 | Responsive layout for different screen sizes |

---

## 4. Technical Architecture

### 4.1 Technology Stack

| Layer | Technology |
|-------|------------|
| Backend | Python + FastAPI |
| Real-time | WebSocket (fastapi-websocket) |
| File Watching | watchdog library |
| Frontend | React |
| Styling | CSS with CSS variables for theming |

### 4.2 Data Flow

```
[Steps Folder] --> [File Watcher] --> [FastAPI Backend] --> [WebSocket] --> [React Frontend]
       |                                      |
       |                                      v
       +--- JSON files ---------> Parse & transform to step objects
```

### 4.3 Step JSON Structure (Input)

Based on analysis of existing step files:

```json
{
  "task_id": "01-01",
  "project_id": "arkanoid-game",
  "phase": "Foundation",
  "description": "Create Makefile with engine submodule integration",
  "validation": {
    "status": "pending"
  }
}
```

### 4.4 Step Object (Internal)

```typescript
interface Step {
  taskId: string;        // e.g., "01-01"
  projectId: string;     // e.g., "arkanoid-game"
  phase: string;         // e.g., "Foundation"
  description: string;
  status: "pending" | "in_progress" | "completed" | "failed" | "skipped";
  majorVersion: number;  // Parsed from taskId (01, 02, etc.) for grid row grouping
  minorVersion: number;  // Parsed from taskId for ordering within row
}
```

---

## 5. User Interface Specification

### 5.1 Layout

```
+------------------------------------------------------------------+
|  nWave Step Viewer                           [Dark/Light Toggle]  |
+------------------------------------------------------------------+
|                                                                   |
|  Phase: Foundation (01-xx)                                        |
|  +-------+     +-------+     +-------+     +-------+              |
|  | 01-01 | --> | 01-02 | --> | 01-03 | --> | 01-04 |              |
|  | Found | --> | Found | --> | Found | --> | Found |              |
|  +-------+     +-------+     +-------+     +-------+              |
|                                                                   |
|  Phase: Entities (02-xx)                                          |
|  +-------+     +-------+     +-------+     +-------+     +-------+|
|  | 02-01 | --> | 02-02 | --> | 02-03 | --> | 02-04 | --> | 02-05 ||
|  | Entit | --> | Entit | --> | Entit | --> | Entit | --> | Entit ||
|  +-------+     +-------+     +-------+     +-------+     +-------+|
|                                                                   |
|  ...                                                              |
+------------------------------------------------------------------+
```

### 5.2 Step Rectangle Content

```
+---------------+
|    01-01      |  <- task_id (bold)
|  Foundation   |  <- phase name
|   [STATUS]    |  <- colored status badge
+---------------+
```

### 5.3 Pulse Animation

The current in-progress step should have a subtle pulsing animation:
- Opacity oscillates between 1.0 and 0.7
- Animation duration: 1.5 seconds
- Easing: ease-in-out

---

## 6. API Specification

### 6.1 WebSocket Endpoint

**URL**: `ws://localhost:8000/ws`

### 6.2 Message Types

#### Server -> Client: Initial State
```json
{
  "type": "init",
  "steps": [Step, Step, ...]
}
```

#### Server -> Client: Step Update
```json
{
  "type": "update",
  "step": Step
}
```

#### Server -> Client: Step Removed
```json
{
  "type": "remove",
  "taskId": "01-01"
}
```

---

## 7. User Stories

### US-01: View All Steps
**As a** developer
**I want to** see all steps in my project displayed visually
**So that** I can understand the overall development structure

**Acceptance Criteria:**
- All JSON files in the steps folder are parsed and displayed
- Steps are grouped by phase (major version number)
- Each step shows task_id, phase, and status

### US-02: See Current Step
**As a** developer
**I want to** immediately identify which step is currently being executed
**So that** I can track real-time progress

**Acceptance Criteria:**
- The first step with "in_progress" status pulses
- Pulse animation is visible but not distracting
- Only one step pulses at a time

### US-03: Real-time Updates
**As a** developer
**I want to** see step status changes automatically
**So that** I don't need to manually refresh the page

**Acceptance Criteria:**
- Status changes appear within 1 second of file modification
- No page refresh required
- Brief visual highlight on changed steps

### US-04: Toggle Theme
**As a** developer
**I want to** switch between dark and light themes
**So that** I can use the viewer comfortably in different environments

**Acceptance Criteria:**
- Toggle button switches theme immediately
- Theme preference persists across browser sessions
- Both themes have good contrast for step colors

### US-05: Start Viewer
**As a** developer
**I want to** start the viewer with a simple command
**So that** I can quickly monitor any project's steps

**Acceptance Criteria:**
- Run: `python main.py /path/to/steps`
- Server starts and begins watching folder
- Browser can connect to view steps

---

## 8. Constraints

### 8.1 Technical Constraints
- Single folder monitoring at a time
- Step files must be valid JSON
- Step files must contain `task_id` and `validation.status` fields

### 8.2 Assumptions
- Steps folder already exists when server starts
- Task IDs follow the pattern `XX-YY` where XX is major version and YY is minor
- Status is stored in `validation.status` field of JSON

---

## 9. Out of Scope (Version 1.0)

- Multi-project monitoring
- Step editing from the UI
- Historical progress tracking
- Authentication/authorization
- Mobile-specific layout
- Step dependency visualization (beyond linear connection)

---

## 10. Glossary

| Term | Definition |
|------|------------|
| nWave | An agentic framework for software development |
| Step | A discrete unit of work in the nWave process, stored as a JSON file |
| Phase | A grouping of related steps (e.g., Foundation, Entities, Managers) |
| Task ID | Unique identifier for a step in format "XX-YY" |
