"""FastAPI main application with WebSocket endpoint for nwwatch.

Entry point for the backend server that provides real-time step updates
via WebSocket and serves the frontend static files.
"""

import asyncio
import logging
import sys
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from adapters.json_file_repository import JsonFileRepository
from adapters.watchdog_file_watcher import WatchdogFileWatcher
from application.connection_manager import ConnectionManager
from application.step_service import StepService
from domain.step import Step

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Global instances
connection_manager = ConnectionManager()
step_service: StepService | None = None
main_event_loop: asyncio.AbstractEventLoop | None = None


def get_steps_folder_path() -> str:
    """Get the steps folder path from command line arguments.

    Returns:
        The path to the steps folder.

    Raises:
        SystemExit: If no path argument is provided.
    """
    if len(sys.argv) < 2:
        logger.error("Usage: python main.py <steps_folder_path>")
        sys.exit(1)
    return sys.argv[1]


def create_step_service(steps_folder: str) -> StepService:
    """Create and configure the StepService with repository and file watcher.

    Args:
        steps_folder: Path to the folder containing step JSON files.

    Returns:
        Configured StepService instance.
    """
    repository = JsonFileRepository(steps_folder)
    file_watcher = WatchdogFileWatcher(steps_folder)
    return StepService(repository, file_watcher)


async def handle_step_update(event_type: str, step: Step | None) -> None:
    """Handle step update events from the file watcher.

    Broadcasts updates to all connected WebSocket clients.

    Args:
        event_type: Type of event ('created', 'modified', 'deleted').
        step: The updated Step object, or None for deletions.
    """
    if event_type == "deleted" and step is not None:
        # For deletions, send remove message with task_id
        message = {"type": "remove", "taskId": step.task_id}
        logger.info("Broadcasting step removal: %s", step.task_id)
    elif step is not None:
        # For created or modified, send update message with step data
        message = {"type": "update", "step": step.to_dict()}
        logger.info("Broadcasting step update: %s (%s)", step.task_id, event_type)
    else:
        # Skip if step is None and not a deletion
        logger.warning("Received %s event with None step", event_type)
        return

    await connection_manager.broadcast(message)


def on_file_change(event_type: str, step: Step | None) -> None:
    """Callback for file changes that schedules async broadcast.

    This callback is called from the watchdog thread, so it schedules
    the async broadcast operation on the main event loop.

    Args:
        event_type: Type of event ('created', 'modified', 'deleted').
        step: The updated Step object, or None for deletions.
    """
    global main_event_loop

    logger.info("File change detected: %s, step: %s", event_type, step.task_id if step else None)

    if main_event_loop is not None and main_event_loop.is_running():
        asyncio.run_coroutine_threadsafe(
            handle_step_update(event_type, step), main_event_loop
        )
    else:
        logger.warning("Event loop not available for broadcasting update")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage application lifespan events.

    Starts the file watcher on startup and stops it on shutdown.

    Args:
        app: The FastAPI application instance.

    Yields:
        None during the application lifetime.
    """
    global step_service, main_event_loop

    # Store the event loop for use in the file watcher callback
    main_event_loop = asyncio.get_running_loop()

    steps_folder = get_steps_folder_path()
    logger.info("Starting nwwatch with steps folder: %s", steps_folder)

    # Validate folder exists
    if not Path(steps_folder).exists():
        logger.error("Steps folder does not exist: %s", steps_folder)
        sys.exit(1)

    # Create and start the step service
    step_service = create_step_service(steps_folder)
    step_service.start_watching(on_file_change)
    logger.info("File watcher started")

    yield

    # Shutdown: stop the file watcher
    if step_service is not None:
        step_service.stop_watching()
        logger.info("File watcher stopped")
    main_event_loop = None


# Create FastAPI application
app = FastAPI(
    title="nwwatch",
    description="Real-time workflow step monitoring",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint.

    Returns:
        Dictionary with status indicating the server is healthy.
    """
    return {"status": "healthy"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    """WebSocket endpoint for real-time step updates.

    On connection, sends an init message with all current steps.
    Then keeps the connection open to receive updates.

    Args:
        websocket: The WebSocket connection.
    """
    await connection_manager.connect(websocket)

    try:
        # Send init message with all steps
        if step_service is not None:
            steps = step_service.get_all_steps()
            init_message = {
                "type": "init",
                "steps": [step.to_dict() for step in steps],
            }
            await connection_manager.send_personal(websocket, init_message)
            logger.info("Sent init message with %d steps", len(steps))

        # Keep connection open and handle incoming messages
        while True:
            # We don't expect messages from client, but need to keep
            # the connection alive and detect disconnections
            await websocket.receive_text()

    except WebSocketDisconnect:
        connection_manager.disconnect(websocket)
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.error("WebSocket error: %s", str(e))
        connection_manager.disconnect(websocket)


# Mount static files for frontend (must be last to avoid catching API routes)
# Only mount if frontend/dist exists
frontend_dist = Path(__file__).parent.parent / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="static")
    logger.info("Serving static files from: %s", frontend_dist)
else:
    logger.warning("Frontend dist folder not found at: %s", frontend_dist)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
