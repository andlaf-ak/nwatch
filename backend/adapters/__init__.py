"""Adapters package for nwwatch.

Contains adapter implementations following hexagonal architecture principles.
Adapters implement the port interfaces to integrate with external systems.
"""

from .json_file_repository import JsonFileRepository
from .watchdog_file_watcher import WatchdogFileWatcher

__all__ = ["JsonFileRepository", "WatchdogFileWatcher"]
