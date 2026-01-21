"""Ports package for nwwatch.

Contains protocol interfaces (ports) following hexagonal architecture principles.
Ports define the contracts for external adapters to implement.
"""

from .file_watcher import FileWatcher
from .step_repository import StepRepository

__all__ = ["FileWatcher", "StepRepository"]
