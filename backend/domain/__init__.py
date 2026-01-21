"""Domain package for nwwatch.

Contains domain entities and value objects following hexagonal architecture principles.
"""

from .events import FileEvent, FileEventType
from .step import Step, StepStatus

__all__ = ["FileEvent", "FileEventType", "Step", "StepStatus"]
