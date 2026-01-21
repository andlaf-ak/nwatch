"""
Pytest fixtures for nwwatch acceptance tests.

Provides test infrastructure for E2E testing with:
- Temporary steps folder management
- Backend server lifecycle
- Browser automation via Playwright
"""

import pytest
import tempfile
import subprocess
import time
import json
import os
from pathlib import Path

# Playwright imports (installed via pytest-playwright)
pytest_plugins = ["pytest_bdd"]


@pytest.fixture(scope="function")
def steps_folder():
    """
    Create a temporary steps folder for testing.

    Yields the folder path and cleans up after test.
    """
    with tempfile.TemporaryDirectory(prefix="nwwatch_test_") as tmpdir:
        yield tmpdir


@pytest.fixture(scope="function")
def backend_server(steps_folder):
    """
    Start the nwwatch backend server pointing to the test steps folder.

    Waits for server to be ready before yielding.
    Terminates server after test completes.
    """
    backend_path = Path(__file__).parent.parent.parent / "backend" / "main.py"

    process = subprocess.Popen(
        ["python", str(backend_path), steps_folder],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env={**os.environ, "PYTHONUNBUFFERED": "1"}
    )

    # Wait for server to start (check if port 8000 is listening)
    max_wait = 5
    start_time = time.time()
    while time.time() - start_time < max_wait:
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', 8000))
            sock.close()
            if result == 0:
                break
        except Exception:
            pass
        time.sleep(0.1)

    yield process

    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()


@pytest.fixture(scope="function")
def browser_page(page, backend_server):
    """
    Open browser page connected to the step viewer.

    Uses Playwright's page fixture (from pytest-playwright).
    Waits for the step grid to be visible before returning.
    """
    page.goto("http://localhost:8000")

    # Wait for the app to load
    page.wait_for_selector("[data-testid='step-grid']", timeout=5000)

    return page


# ============================================================================
# Helper functions for step definitions
# ============================================================================

def create_step_file(folder: str, task_id: str, project_id: str,
                     phase: str, status: str, description: str = None):
    """
    Create a step JSON file in the given folder.

    Args:
        folder: Path to the steps folder
        task_id: Step task ID (e.g., "01-01")
        project_id: Project identifier
        phase: Phase name
        status: Step status (pending, in_progress, completed, failed, skipped)
        description: Optional description (defaults to auto-generated)
    """
    step_data = {
        "task_id": task_id,
        "project_id": project_id,
        "phase": phase,
        "description": description or f"Test step {task_id}",
        "validation": {
            "status": status
        }
    }

    file_path = os.path.join(folder, f"{task_id}.json")
    with open(file_path, 'w') as f:
        json.dump(step_data, f, indent=2)

    return file_path


def modify_step_status(folder: str, task_id: str, new_status: str):
    """
    Modify the status of an existing step file.

    Args:
        folder: Path to the steps folder
        task_id: Step task ID (e.g., "01-01")
        new_status: New status value
    """
    file_path = os.path.join(folder, f"{task_id}.json")

    with open(file_path, 'r') as f:
        data = json.load(f)

    data["validation"]["status"] = new_status

    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)


def delete_step_file(folder: str, task_id: str):
    """
    Delete a step file from the folder.

    Args:
        folder: Path to the steps folder
        task_id: Step task ID (e.g., "01-01")
    """
    file_path = os.path.join(folder, f"{task_id}.json")
    os.remove(file_path)


def create_malformed_json(folder: str, filename: str):
    """
    Create a malformed JSON file for error handling tests.

    Args:
        folder: Path to the steps folder
        filename: Name of the file to create
    """
    file_path = os.path.join(folder, filename)
    with open(file_path, 'w') as f:
        f.write('{ "task_id": "bad", invalid json here }')


# ============================================================================
# Pytest-BDD step parsers registration
# ============================================================================

def pytest_configure(config):
    """Register custom markers for test categorization."""
    config.addinivalue_line("markers", "US01: User Story 01 - View All Steps")
    config.addinivalue_line("markers", "US02: User Story 02 - See Current Step")
    config.addinivalue_line("markers", "US03: User Story 03 - Real-time Updates")
    config.addinivalue_line("markers", "US04: User Story 04 - Toggle Theme")
    config.addinivalue_line("markers", "US05: User Story 05 - Start Viewer")
    config.addinivalue_line("markers", "reliability: Reliability tests")
    config.addinivalue_line("markers", "performance: Performance tests")
