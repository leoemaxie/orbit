import asyncio
import inspect
import logging
from collections.abc import Callable, Coroutine
from typing import Any

from core.events.types import OrbitEvent

logger = logging.getLogger("core.events")

Subscriber = Callable[[OrbitEvent], Coroutine[Any, Any, None] | Any]


class EventBus:
    """In-process asynchronous event bus for pipeline and agent lifecycle events."""

    def __init__(self):
        self._subscribers: list[Subscriber] = []

    def subscribe(self, callback: Subscriber) -> None:
        self._subscribers.append(callback)

    async def publish(self, event: OrbitEvent) -> None:
        logger.debug(f"Event: {event.event_type} (run={event.run_id})")
        for sub in self._subscribers:
            try:
                if inspect.iscoroutinefunction(sub):
                    await sub(event)
                else:
                    res = sub(event)
                    if inspect.isawaitable(res):
                        await res
            except Exception as e:  # noqa: BLE001
                logger.error(f"Error in event subscriber for {event.event_type}: {e}")


# Global default event bus
event_bus = EventBus()
