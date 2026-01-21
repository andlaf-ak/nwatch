"""StepRepository port interface.

Defines the protocol for step data access following hexagonal architecture.
"""

from typing import Protocol

from domain.step import Step


class StepRepository(Protocol):
    """Protocol defining the interface for step data access.

    This port defines the contract that any step repository adapter must implement.
    Following hexagonal architecture, the domain depends on this protocol, not
    on concrete implementations.
    """

    def get_all(self) -> list[Step]:
        """Retrieve all steps from the repository.

        Returns:
            List of all Step objects in the repository.
            Returns empty list if no steps are found.
        """
        ...

    def get_by_id(self, task_id: str) -> Step | None:
        """Retrieve a step by its task_id.

        Args:
            task_id: The unique identifier for the task (e.g., '01-02')

        Returns:
            The Step with the matching task_id, or None if not found.
        """
        ...

    def refresh(self, task_id: str) -> Step | None:
        """Re-read and return the step data for a specific task.

        This method forces a fresh read from the underlying data source,
        bypassing any caching that may be in place.

        Args:
            task_id: The unique identifier for the task (e.g., '01-02')

        Returns:
            The refreshed Step with the matching task_id, or None if not found.
        """
        ...
