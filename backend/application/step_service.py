"""StepService application service.

Orchestrates step operations by coordinating between the StepRepository and
FileWatcher ports, translating file events into step updates.
"""

import logging
import re
from typing import Callable

from domain.events import FileEvent, FileEventType
from domain.step import Step
from ports.file_watcher import FileWatcher
from ports.step_repository import StepRepository

logger = logging.getLogger(__name__)

# Type alias for the step update callback
StepUpdateCallback = Callable[[str, Step | None], None]


class StepService:
    """Application service for managing workflow steps.

    Orchestrates step operations by coordinating between the repository for
    data access and the file watcher for real-time updates. Maintains an
    in-memory cache of steps for fast access.

    Attributes:
        repository: The step repository for data access.
        file_watcher: The file watcher for monitoring changes.
    """

    def __init__(
        self,
        repository: StepRepository,
        file_watcher: FileWatcher,
    ) -> None:
        """Initialize the StepService.

        Args:
            repository: StepRepository implementation for data access.
            file_watcher: FileWatcher implementation for monitoring changes.
        """
        self._repository = repository
        self._file_watcher = file_watcher
        self._steps_cache: dict[str, Step] = {}
        self._callback: StepUpdateCallback | None = None
        self._watching = False

    @property
    def repository(self) -> StepRepository:
        """Return the step repository."""
        return self._repository

    @property
    def file_watcher(self) -> FileWatcher:
        """Return the file watcher."""
        return self._file_watcher

    @property
    def is_watching(self) -> bool:
        """Check if the service is currently watching for file changes.

        Returns:
            True if watching is active, False otherwise.
        """
        return self._watching

    def get_all_steps(self) -> list[Step]:
        """Retrieve all steps, using cache if available.

        On first call, loads all steps from the repository into cache.
        Subsequent calls return cached data.

        Returns:
            List of all Step objects.
        """
        if not self._steps_cache:
            self._load_steps_into_cache()

        return list(self._steps_cache.values())

    def _load_steps_into_cache(self) -> None:
        """Load all steps from repository into the in-memory cache."""
        steps = self._repository.get_all()
        self._steps_cache = {step.task_id: step for step in steps}
        logger.debug("Loaded %d steps into cache", len(self._steps_cache))

    def start_watching(self, callback: StepUpdateCallback) -> None:
        """Start watching for file changes and translating them to step updates.

        Begins monitoring for file changes. When a change is detected,
        refreshes the affected step from the repository and invokes the
        callback with the event type and updated step.

        Args:
            callback: Function to call when a step is updated.
                     Receives (event_type: str, step: Step | None).
                     event_type is one of: 'created', 'modified', 'deleted'.
                     step is the updated Step object, or None for deletions.

        Raises:
            RuntimeError: If already watching.
        """
        if self._watching:
            raise RuntimeError("StepService is already watching for changes")

        # Ensure cache is populated before starting to watch
        if not self._steps_cache:
            self._load_steps_into_cache()

        self._callback = callback
        self._file_watcher.start(self._handle_file_event)
        self._watching = True

        logger.info("StepService started watching for file changes")

    def stop_watching(self) -> None:
        """Stop watching for file changes.

        Stops the file watcher and cleans up resources. After calling
        stop_watching(), no more callbacks will be invoked until
        start_watching() is called again.
        """
        if not self._watching:
            logger.debug("StepService already stopped watching")
            return

        self._file_watcher.stop()
        self._watching = False
        self._callback = None

        logger.info("StepService stopped watching for file changes")

    def _handle_file_event(self, file_event: FileEvent) -> None:
        """Handle a file event from the file watcher.

        Translates the file event to a step update by extracting the task_id
        from the file path, refreshing the step from the repository, and
        invoking the callback.

        Args:
            file_event: The file event received from the watcher.
        """
        task_id = self._extract_task_id_from_path(file_event.file_path)
        if task_id is None:
            logger.warning(
                "Could not extract task_id from file path: %s",
                file_event.file_path,
            )
            return

        event_type = file_event.event_type.value
        step: Step | None = None

        if file_event.event_type == FileEventType.DELETED:
            # For deletions, remove from cache and pass None
            step = self._steps_cache.pop(task_id, None)
            logger.debug("Step deleted: %s", task_id)
        else:
            # For created or modified, refresh from repository
            step = self._repository.refresh(task_id)
            if step is not None:
                self._steps_cache[task_id] = step
                logger.debug("Step %s: %s", event_type, task_id)
            else:
                logger.warning(
                    "Could not refresh step for task_id '%s' after %s event",
                    task_id,
                    event_type,
                )

        # Invoke callback with event type and step
        if self._callback is not None:
            self._callback(event_type, step)

    @staticmethod
    def _extract_task_id_from_path(file_path: str) -> str | None:
        """Extract task_id from a file path.

        Assumes the file is named with the task_id pattern (e.g., '01-02.json').

        Args:
            file_path: The full path to the step file.

        Returns:
            The extracted task_id (e.g., '01-02'), or None if extraction fails.
        """
        # Extract filename from path
        import os

        filename = os.path.basename(file_path)

        # Remove .json extension if present
        if filename.endswith(".json"):
            filename = filename[:-5]

        # Validate task_id format (XX-YY where X and Y are digits)
        pattern = r"^\d{2}-\d{2}$"
        if re.match(pattern, filename):
            return filename

        return None
