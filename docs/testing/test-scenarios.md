# nwwatch - Test Scenarios Document

**Project**: nwwatch (nWave Step Viewer)
**Version**: 1.0
**Date**: 2026-01-21
**Wave**: DISTILL

---

## 1. Test Strategy Overview

### 1.1 Testing Approach

**Outside-In TDD** with E2E acceptance tests as the outer loop:

```
┌─────────────────────────────────────────────────────────────────┐
│                    E2E Acceptance Tests                         │
│                    (Playwright + pytest-bdd)                    │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              Integration Tests                           │   │
│  │              (Backend + WebSocket)                       │   │
│  │  ┌─────────────────────────────────────────────────┐   │   │
│  │  │           Unit Tests                             │   │   │
│  │  │           (Domain, Components)                   │   │   │
│  │  └─────────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 Test Framework Stack

| Layer | Framework | Purpose |
|-------|-----------|---------|
| E2E/Acceptance | pytest-bdd + Playwright | Gherkin scenarios with real browser |
| Backend Integration | pytest + httpx | WebSocket and file watcher testing |
| Backend Unit | pytest | Domain logic, Step entity |
| Frontend Unit | Vitest + React Testing Library | Component behavior |

---

## 2. Acceptance Test Scenarios Summary

### 2.1 User Story Coverage Matrix

| User Story | Scenarios | Priority |
|------------|-----------|----------|
| US-01: View All Steps | 3 | Must |
| US-02: See Current Step | 3 | Must |
| US-03: Real-time Updates | 4 | Must |
| US-04: Toggle Theme | 3 | Must |
| US-05: Start Viewer | 2 | Must |
| Status Colors | 1 (5 examples) | Must |
| Reliability | 3 | Should |
| Performance | 2 | Should |

**Total: 21 scenarios**

### 2.2 Scenario Details by User Story

#### US-01: View All Steps

| Scenario | Description | Acceptance Criteria |
|----------|-------------|---------------------|
| Display all steps | Steps folder with 4 files shows 4 cards | FR-04, FR-09 |
| Phase grouping | Steps grouped into rows by major version | FR-10 |
| Step ordering | Steps ordered by minor version within phase | FR-10 |

#### US-02: See Current Step

| Scenario | Description | Acceptance Criteria |
|----------|-------------|---------------------|
| Pulse animation | in_progress step pulses | FR-13 |
| Single pulse | Only first in_progress pulses | FR-13 |
| No pulse when none in progress | No animation if no in_progress | FR-13 |

#### US-03: Real-time Updates

| Scenario | Description | Acceptance Criteria |
|----------|-------------|---------------------|
| File modification | Status change reflected in < 1s | FR-03, FR-06 |
| File creation | New step appears in < 1s | FR-03, FR-06 |
| File deletion | Step removed in < 1s | FR-03, FR-06 |
| No refresh required | Updates without page reload | NFR-08 |

#### US-04: Toggle Theme

| Scenario | Description | Acceptance Criteria |
|----------|-------------|---------------------|
| Theme toggle | Click toggles dark/light | FR-16 |
| Theme persistence | Preference saved in localStorage | FR-17 |
| Theme contrast | Colors visible in both themes | FR-14, FR-15 |

#### US-05: Start Viewer

| Scenario | Description | Acceptance Criteria |
|----------|-------------|---------------------|
| Server startup | CLI arg specifies folder | FR-02 |
| WebSocket connection | Browser connects successfully | FR-05 |

---

## 3. Test Implementation Plan

### 3.1 Implementation Order (Outside-In)

Following Outside-In TDD, implement tests in this order:

```
1. E2E: "Display all steps" (US-01) ────────────────┐
   │                                                 │
   ├─> Backend: WebSocket sends init message         │
   │   ├─> StepService.get_all_steps()              │
   │   │   └─> JsonFileRepository.get_all()         │
   │   └─> ConnectionManager.send()                  │
   │                                                 │
   ├─> Frontend: StepGrid renders steps             │
   │   ├─> useWebSocket receives init               │
   │   └─> StepCard displays data                   │
   │                                                 │
   └─> Domain: Step entity parsing                   │
                                                     │
2. E2E: "Pulse animation" (US-02) ──────────────────┤
   │                                                 │
   └─> Frontend: StepCard pulse logic               │
                                                     │
3. E2E: "File modification" (US-03) ────────────────┤
   │                                                 │
   ├─> Backend: WatchdogFileWatcher                 │
   │   └─> StepService.on_step_change()             │
   │                                                 │
   └─> Frontend: useWebSocket handles update         │
                                                     │
4. E2E: "Theme toggle" (US-04) ─────────────────────┤
   │                                                 │
   └─> Frontend: useTheme + ThemeToggle             │
                                                     │
5. E2E: "Server startup" (US-05) ───────────────────┘
```

### 3.2 Test File Structure

```
tests/
├── acceptance/
│   ├── step_viewer.feature          # Gherkin scenarios
│   ├── conftest.py                  # Pytest fixtures
│   └── step_defs/
│       ├── __init__.py
│       ├── test_view_steps.py       # US-01 step definitions
│       ├── test_current_step.py     # US-02 step definitions
│       ├── test_realtime.py         # US-03 step definitions
│       ├── test_theme.py            # US-04 step definitions
│       ├── test_startup.py          # US-05 step definitions
│       └── common_steps.py          # Shared Given/When/Then
├── integration/
│   ├── test_websocket.py            # WebSocket message flow
│   ├── test_file_watcher.py         # File change detection
│   └── test_step_repository.py      # JSON file parsing
└── unit/
    ├── backend/
    │   ├── test_step_entity.py      # Step domain object
    │   ├── test_step_service.py     # Application service
    │   └── test_connection_manager.py
    └── frontend/
        ├── StepCard.test.tsx        # Component tests
        ├── StepGrid.test.tsx
        ├── useWebSocket.test.ts     # Hook tests
        └── useTheme.test.ts
```

---

## 4. Step Definitions Structure

### 4.1 Common Fixtures (conftest.py)

```python
import pytest
from playwright.sync_api import Page, Browser
import tempfile
import json
import subprocess
import time

@pytest.fixture
def steps_folder():
    """Create a temporary steps folder for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir

@pytest.fixture
def backend_server(steps_folder):
    """Start the nwwatch backend server."""
    process = subprocess.Popen(
        ["python", "backend/main.py", steps_folder],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    time.sleep(1)  # Wait for server startup
    yield process
    process.terminate()

@pytest.fixture
def browser_page(browser: Browser, backend_server) -> Page:
    """Open browser connected to step viewer."""
    page = browser.new_page()
    page.goto("http://localhost:8000")
    page.wait_for_selector("[data-testid='step-grid']", timeout=5000)
    return page
```

### 4.2 Step Definition Examples

#### Given Steps

```python
from pytest_bdd import given, when, then, parsers
import json
import os

@given(parsers.parse('the steps folder contains the following step files:'))
def create_step_files(steps_folder, datatable):
    """Create step JSON files from datatable."""
    for row in datatable:
        step_data = {
            "task_id": row["task_id"],
            "project_id": row["project_id"],
            "phase": row["phase"],
            "description": f"Test step {row['task_id']}",
            "validation": {
                "status": row["status"]
            }
        }
        file_path = os.path.join(steps_folder, f"{row['task_id']}.json")
        with open(file_path, 'w') as f:
            json.dump(step_data, f)

@given('the nwwatch backend is running')
def backend_running(backend_server):
    """Ensure backend is running (uses fixture)."""
    assert backend_server.poll() is None, "Backend server not running"

@given('the browser is connected to the step viewer')
def browser_connected(browser_page):
    """Ensure browser has loaded the viewer."""
    assert browser_page.locator("[data-testid='connection-status']").text_content() == "connected"
```

#### When Steps

```python
@when('I open the step viewer')
def open_step_viewer(browser_page):
    """Navigate to step viewer (already done in fixture)."""
    pass  # browser_page fixture handles this

@when(parsers.parse('the step file "{filename}" is modified with status "{status}"'))
def modify_step_file(steps_folder, filename, status):
    """Modify a step file's status."""
    file_path = os.path.join(steps_folder, filename)
    with open(file_path, 'r') as f:
        data = json.load(f)
    data["validation"]["status"] = status
    with open(file_path, 'w') as f:
        json.dump(data, f)

@when('I click the theme toggle button')
def click_theme_toggle(browser_page):
    """Click the theme toggle button."""
    browser_page.click("[data-testid='theme-toggle']")
```

#### Then Steps

```python
@then(parsers.parse('I should see {count:d} step cards displayed'))
def verify_step_count(browser_page, count):
    """Verify number of step cards."""
    cards = browser_page.locator("[data-testid='step-card']")
    assert cards.count() == count

@then(parsers.parse('the step card "{task_id}" should have a pulse animation'))
def verify_pulse_animation(browser_page, task_id):
    """Verify step card has pulse animation."""
    card = browser_page.locator(f"[data-testid='step-card-{task_id}']")
    assert "pulse" in card.get_attribute("class")

@then(parsers.parse('within {seconds:d} second the step card "{task_id}" should show status "{status}"'))
def verify_status_update(browser_page, seconds, task_id, status):
    """Verify status updates within timeout."""
    card = browser_page.locator(f"[data-testid='step-card-{task_id}']")
    status_badge = card.locator("[data-testid='status-badge']")
    expect(status_badge).to_have_text(status, timeout=seconds * 1000)
```

---

## 5. Test Data Requirements

### 5.1 Step File Templates

**Valid Step File (template):**
```json
{
  "task_id": "XX-YY",
  "project_id": "test-project",
  "phase": "TestPhase",
  "description": "Test step description",
  "validation": {
    "status": "pending"
  }
}
```

**Malformed Step File (for error handling test):**
```json
{ "task_id": "01-01", invalid json here
```

### 5.2 Test Data Sets

| Test Set | Purpose | Steps |
|----------|---------|-------|
| minimal | Basic functionality | 1 step |
| multi-phase | Phase grouping | 5 steps across 3 phases |
| all-statuses | Color testing | 5 steps, one per status |
| large | Performance | 100 steps across 10 phases |

---

## 6. Test Environment Requirements

### 6.1 Dependencies

**Backend Testing:**
```
pytest>=7.0
pytest-bdd>=6.0
pytest-asyncio>=0.21
httpx>=0.24
```

**Frontend Testing:**
```
vitest
@testing-library/react
@testing-library/jest-dom
```

**E2E Testing:**
```
playwright
pytest-playwright
```

### 6.2 CI/CD Integration

```yaml
# .github/workflows/test.yml
test:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4

    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Setup Node
      uses: actions/setup-node@v4
      with:
        node-version: '20'

    - name: Install dependencies
      run: |
        pip install -r backend/requirements.txt
        pip install -r tests/requirements.txt
        cd frontend && npm install

    - name: Install Playwright
      run: playwright install chromium

    - name: Run unit tests
      run: |
        pytest tests/unit/backend -v
        cd frontend && npm test

    - name: Run integration tests
      run: pytest tests/integration -v

    - name: Run acceptance tests
      run: pytest tests/acceptance -v
```

---

## 7. Definition of Done for DISTILL Wave

- [x] All user stories have Gherkin acceptance tests
- [x] Test scenarios cover happy path and edge cases
- [x] Step definitions structure defined
- [x] Test data requirements documented
- [x] E2E test framework selected (pytest-bdd + Playwright)
- [ ] First acceptance test executable (deferred to DEVELOP)

---

## 8. Handoff to DEVELOP Wave

### 8.1 Implementation Sequence

The software-crafter should implement in this order:

1. **Walking Skeleton** (if needed): Minimal E2E slice
2. **US-01**: Display all steps (establishes core architecture)
3. **US-03**: Real-time updates (adds file watching)
4. **US-02**: Pulse animation (frontend enhancement)
5. **US-04**: Theme toggle (UI polish)
6. **US-05**: Server startup (CLI interface)

### 8.2 First Test to Make Pass

Start with: `@US-01 @initial-load` - "Display all steps from a steps folder"

This scenario drives implementation of:
- Backend: FastAPI + WebSocket endpoint
- Backend: JsonFileRepository
- Backend: StepService
- Frontend: React app structure
- Frontend: StepGrid + StepCard components
- Frontend: useWebSocket hook

### 8.3 Test-Driven Constraints

- Each component boundary (hexagonal architecture) should have tests at the port level
- Frontend components should have data-testid attributes for E2E selection
- WebSocket messages should match the API contract exactly
