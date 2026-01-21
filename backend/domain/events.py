"""File event domain object.

Defines the FileEvent dataclass for file change events in nwwatch.
"""

from dataclasses import dataclass
from enum import Enum


class FileEventType(Enum):
    """Type of file system event."""

    CREATED = "created"
    MODIFIED = "modified"
    DELETED = "deleted"


@dataclass(frozen=True)
class FileEvent:
    """Domain object representing a file change event.

    This is an immutable value object that captures the details of a file
    system change event, used for real-time monitoring of step files.

    Attributes:
        event_type: The type of file event (created, modified, or deleted).
        file_path: The absolute path to the file that changed.
    """

    event_type: FileEventType
    file_path: str

    def __str__(self) -> str:
        """Return a human-readable string representation."""
        return f"FileEvent({self.event_type.value}, {self.file_path})"
