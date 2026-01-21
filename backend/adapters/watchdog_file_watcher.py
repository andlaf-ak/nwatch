"""WatchdogFileWatcher adapter for monitoring file changes.

Implements the FileWatcher port interface using the watchdog library
to monitor a folder for JSON file changes.
"""

import logging
from pathlib import Path
from threading import Timer
from typing import Callable

from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers.polling import PollingObserver

from domain.events import FileEvent, FileEventType

logger = logging.getLogger(__name__)


class _DebouncedEventHandler(FileSystemEventHandler):
    """Internal event handler that debounces rapid file changes.

    Implements debouncing to avoid firing multiple events for rapid
    successive changes to the same file (e.g., during a save operation
    that triggers multiple write events).

    Attributes:
        callback: The callback to invoke with debounced FileEvents.
        debounce_delay: Time in seconds to wait before firing the callback.
    """

    def __init__(
        self,
        callback: Callable[[FileEvent], None],
        debounce_delay: float = 0.1,
    ) -> None:
        """Initialize the debounced event handler.

        Args:
            callback: Function to call when a debounced file change is detected.
            debounce_delay: Time in seconds to wait before firing (default 0.1s).
        """
        super().__init__()
        self._callback = callback
        self._debounce_delay = debounce_delay
        self._pending_timers: dict[str, Timer] = {}

    def _is_json_file(self, path: str) -> bool:
        """Check if the file path is a JSON file.

        Args:
            path: The file path to check.

        Returns:
            True if the file has a .json extension, False otherwise.
        """
        return Path(path).suffix.lower() == ".json"

    def _cancel_pending_timer(self, file_path: str) -> None:
        """Cancel any pending timer for the given file path.

        Args:
            file_path: The file path whose timer should be cancelled.
        """
        if file_path in self._pending_timers:
            self._pending_timers[file_path].cancel()
            del self._pending_timers[file_path]

    def _schedule_callback(self, file_path: str, event_type: FileEventType) -> None:
        """Schedule a debounced callback for the given file event.

        Cancels any pending callback for the same file and schedules a new one.

        Args:
            file_path: The path of the changed file.
            event_type: The type of file event.
        """
        self._cancel_pending_timer(file_path)

        def fire_callback() -> None:
            if file_path in self._pending_timers:
                del self._pending_timers[file_path]
            file_event = FileEvent(event_type=event_type, file_path=file_path)
            logger.debug("Firing debounced callback for %s", file_event)
            self._callback(file_event)

        timer = Timer(self._debounce_delay, fire_callback)
        self._pending_timers[file_path] = timer
        timer.start()

    def on_created(self, event: FileSystemEvent) -> None:
        """Handle file creation events.

        Args:
            event: The file system event from watchdog.
        """
        logger.info("on_created event: %s (is_dir=%s)", event.src_path, event.is_directory)
        if event.is_directory:
            return
        if not self._is_json_file(event.src_path):
            return

        logger.info("File created: %s", event.src_path)
        self._schedule_callback(event.src_path, FileEventType.CREATED)

    def on_modified(self, event: FileSystemEvent) -> None:
        """Handle file modification events.

        Args:
            event: The file system event from watchdog.
        """
        if event.is_directory:
            return
        if not self._is_json_file(event.src_path):
            return

        logger.info("File modified detected: %s", event.src_path)
        self._schedule_callback(event.src_path, FileEventType.MODIFIED)

    def on_deleted(self, event: FileSystemEvent) -> None:
        """Handle file deletion events.

        Args:
            event: The file system event from watchdog.
        """
        if event.is_directory:
            return
        if not self._is_json_file(event.src_path):
            return

        logger.debug("File deleted: %s", event.src_path)
        self._schedule_callback(event.src_path, FileEventType.DELETED)

    def cancel_all_pending(self) -> None:
        """Cancel all pending debounce timers.

        Should be called when stopping the watcher to clean up resources.
        """
        for timer in list(self._pending_timers.values()):
            timer.cancel()
        self._pending_timers.clear()


class WatchdogFileWatcher:
    """File watcher adapter using the watchdog library.

    Monitors a folder for JSON file changes with debouncing support.
    Implements the FileWatcher protocol for integration with the domain.

    Attributes:
        folder_path: Path to the folder being monitored.
        debounce_delay: Time in seconds to wait before firing events.
    """

    def __init__(
        self,
        folder_path: str | Path,
        debounce_delay: float = 0.1,
    ) -> None:
        """Initialize the file watcher.

        Args:
            folder_path: Path to the folder to monitor for JSON file changes.
            debounce_delay: Time in seconds to debounce rapid changes (default 0.1s).
        """
        self._folder_path = Path(folder_path)
        self._debounce_delay = debounce_delay
        self._observer: PollingObserver | None = None
        self._handler: _DebouncedEventHandler | None = None

    @property
    def folder_path(self) -> Path:
        """Return the folder path being monitored."""
        return self._folder_path

    @property
    def is_running(self) -> bool:
        """Check if the watcher is currently running.

        Returns:
            True if the watcher is actively monitoring, False otherwise.
        """
        return self._observer is not None and self._observer.is_alive()

    def start(self, callback: Callable[[FileEvent], None]) -> None:
        """Start watching for file changes.

        Begins monitoring the configured folder for JSON file system events.
        When a change is detected (after debouncing), the callback is invoked.

        Args:
            callback: Function to call when a file change is detected.
                     Receives a FileEvent object as its only argument.

        Raises:
            RuntimeError: If the watcher is already running.
            FileNotFoundError: If the folder path does not exist.
        """
        if self.is_running:
            raise RuntimeError("File watcher is already running")

        if not self._folder_path.exists():
            raise FileNotFoundError(f"Folder does not exist: {self._folder_path}")

        if not self._folder_path.is_dir():
            raise NotADirectoryError(f"Path is not a directory: {self._folder_path}")

        logger.info("Starting file watcher on: %s", self._folder_path)

        self._handler = _DebouncedEventHandler(
            callback=callback,
            debounce_delay=self._debounce_delay,
        )

        self._observer = PollingObserver(timeout=1.0)
        self._observer.schedule(
            self._handler,
            str(self._folder_path),
            recursive=False,
        )
        self._observer.start()

        logger.info("File watcher started successfully")

    def stop(self) -> None:
        """Stop watching for file changes.

        Stops the file system monitoring and cancels any pending debounced
        callbacks. After calling stop(), no more callbacks will be invoked
        until start() is called again.
        """
        if not self.is_running:
            logger.debug("File watcher already stopped")
            return

        logger.info("Stopping file watcher")

        if self._handler is not None:
            self._handler.cancel_all_pending()

        if self._observer is not None:
            self._observer.stop()
            self._observer.join(timeout=5.0)
            self._observer = None

        self._handler = None

        logger.info("File watcher stopped successfully")
