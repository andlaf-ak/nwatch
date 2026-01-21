"""Step domain entity and StepStatus enum.

This module defines the core domain model for workflow steps in nwwatch.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class StepStatus(Enum):
    """Status values for a workflow step."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class Step:
    """Domain entity representing a workflow step.

    Attributes:
        task_id: Unique identifier for the task (e.g., '01-02')
        project_id: Identifier for the project this step belongs to
        phase: The phase of the workflow this step belongs to
        description: Human-readable description of the step
        status: Current status of the step
        major_version: Major version parsed from task_id
        minor_version: Minor version parsed from task_id
    """

    task_id: str
    project_id: str
    phase: str
    description: str
    status: StepStatus
    major_version: int = field(default=0)
    minor_version: int = field(default=0)

    def __post_init__(self) -> None:
        """Parse major_version and minor_version from task_id after initialization."""
        if self.major_version == 0 and self.minor_version == 0:
            self.major_version, self.minor_version = self._parse_version_from_task_id(
                self.task_id
            )

    @staticmethod
    def _parse_version_from_task_id(task_id: str) -> tuple[int, int]:
        """Parse major and minor version numbers from task_id.

        Args:
            task_id: Task identifier in format 'XX-YY' (e.g., '01-02')

        Returns:
            Tuple of (major_version, minor_version)

        Raises:
            ValueError: If task_id format is invalid
        """
        if not task_id or "-" not in task_id:
            raise ValueError(f"Invalid task_id format: '{task_id}'. Expected 'XX-YY'")

        parts = task_id.split("-")
        if len(parts) != 2:
            raise ValueError(f"Invalid task_id format: '{task_id}'. Expected 'XX-YY'")

        try:
            major = int(parts[0])
            minor = int(parts[1])
            return major, minor
        except ValueError as e:
            raise ValueError(
                f"Invalid task_id format: '{task_id}'. "
                f"Both parts must be integers. Error: {e}"
            ) from e

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Step":
        """Create a Step instance from a dictionary.

        Parses JSON structure with validation.status for the step status.

        Args:
            data: Dictionary containing step data with keys:
                - task_id: str
                - project_id: str
                - phase: str
                - description: str
                - validation: dict with 'status' key

        Returns:
            Step instance

        Raises:
            KeyError: If required keys are missing
            ValueError: If validation.status is not a valid StepStatus
        """
        validation = data.get("validation", {})
        status_str = validation.get("status", "pending")

        try:
            status = StepStatus(status_str)
        except ValueError:
            valid_statuses = [s.value for s in StepStatus]
            raise ValueError(
                f"Invalid status '{status_str}'. Must be one of: {valid_statuses}"
            )

        return cls(
            task_id=data["task_id"],
            project_id=data["project_id"],
            phase=data["phase"],
            description=data["description"],
            status=status,
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialize the Step to a JSON-compatible dictionary.

        Uses camelCase keys for frontend API compatibility.

        Returns:
            Dictionary representation of the Step
        """
        return {
            "taskId": self.task_id,
            "projectId": self.project_id,
            "phase": self.phase,
            "description": self.description,
            "status": self.status.value,
            "majorVersion": self.major_version,
            "minorVersion": self.minor_version,
        }
