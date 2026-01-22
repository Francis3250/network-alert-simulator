"""
Event types and event queue management for the simulation.
"""

import heapq
import itertools
from typing import Any


class EventQueue:
    """
    Manages scheduled events in the simulation using a priority queue.
    Events are processed in chronological order.
    """

    def __init__(self):
        self._queue = []
        self._counter = itertools.count()

    def schedule(self, time: int, event_type: str, data: Any, max_time: int) -> None:
        """
        Schedule an event to occur at a specific time.

        Args:
            time: The simulation time when the event should occur
            event_type: The type of event (e.g., 'ALERT_SEND', 'CANCEL_RECV')
            data: Additional data associated with the event
            max_time: Maximum simulation time (events beyond this are ignored)
        """
        if time > max_time:
            return
        count = next(self._counter)
        heapq.heappush(self._queue, (time, count, event_type, data))

    def pop(self) -> tuple[int, str, Any]:
        """
        Remove and return the next event from the queue.

        Returns:
            A tuple of (time, event_type, data)
        """
        time, _, event_type, data = heapq.heappop(self._queue)
        return time, event_type, data

    def is_empty(self) -> bool:
        """Check if the event queue is empty."""
        return len(self._queue) == 0
