"""FileWatcher port interface.

Defines the protocol for file system monitoring following hexagonal architecture.
"""

from typing import Callable, Protocol

from domain.events import FileEvent


class FileWatcher(Protocol):
    """Protocol defining the interface for file system monitoring.

    This port defines the contract that any file watcher adapter must implement.
    Following hexagonal architecture, the domain depends on this protocol, not
    on concrete implementations.

    The watcher monitors a folder for file changes and invokes a callback
    when changes are detected.
    """

    def start(self, callback: Callable[[FileEvent], None]) -> None:
        """Start watching for file changes.

        Begins monitoring the configured folder for file system events.
        When a change is detected, the callback is invoked with a FileEvent.

        Args:
            callback: Function to call when a file change is detected.
                     Receives a FileEvent object as its only argument.
        """
        ...

    def stop(self) -> None:
        """Stop watching for file changes.

        Stops the file system monitoring. After calling stop(), no more
        callbacks will be invoked until start() is called again.
        """
        ...
