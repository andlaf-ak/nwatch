"""JsonFileRepository adapter for reading step files from the filesystem.

Implements the StepRepository port interface using JSON files as the data source.
"""

import json
import logging
from glob import glob
from pathlib import Path

from domain.step import Step

logger = logging.getLogger(__name__)


class JsonFileRepository:
    """Repository adapter that reads Step data from JSON files.

    This adapter implements the StepRepository protocol by reading step
    definitions from JSON files in a specified folder.

    Attributes:
        folder_path: Path to the folder containing JSON step files.
    """

    def __init__(self, folder_path: str | Path) -> None:
        """Initialize the repository with the folder containing step files.

        Args:
            folder_path: Path to the folder containing JSON step files.
        """
        self._folder_path = Path(folder_path)

    @property
    def folder_path(self) -> Path:
        """Return the folder path for step files."""
        return self._folder_path

    def get_all(self) -> list[Step]:
        """Retrieve all steps from JSON files in the folder.

        Reads all *.json files in the configured folder and parses them
        into Step objects. Malformed JSON files are skipped with a warning.

        Returns:
            List of all Step objects parsed from JSON files.
            Returns empty list if no valid steps are found.
        """
        steps: list[Step] = []
        pattern = str(self._folder_path / "*.json")

        for file_path in glob(pattern):
            step = self._read_step_file(file_path)
            if step is not None:
                steps.append(step)

        return steps

    def get_by_id(self, task_id: str) -> Step | None:
        """Retrieve a step by its task_id.

        Searches through all JSON files to find the step with the matching task_id.

        Args:
            task_id: The unique identifier for the task (e.g., '01-02')

        Returns:
            The Step with the matching task_id, or None if not found.
        """
        for step in self.get_all():
            if step.task_id == task_id:
                return step
        return None

    def refresh(self, task_id: str) -> Step | None:
        """Re-read and return the step data for a specific task.

        Forces a fresh read from the JSON file for the specified task_id.

        Args:
            task_id: The unique identifier for the task (e.g., '01-02')

        Returns:
            The refreshed Step with the matching task_id, or None if not found.
        """
        # Re-read all files to get fresh data
        return self.get_by_id(task_id)

    def _read_step_file(self, file_path: str) -> Step | None:
        """Read and parse a single JSON step file.

        Args:
            file_path: Path to the JSON file to read.

        Returns:
            Parsed Step object, or None if the file is malformed.
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return Step.from_dict(data)
        except json.JSONDecodeError as e:
            logger.warning(
                "Skipping malformed JSON file '%s': %s",
                file_path,
                str(e),
            )
            return None
        except (KeyError, ValueError) as e:
            logger.warning(
                "Skipping invalid step file '%s': %s",
                file_path,
                str(e),
            )
            return None
