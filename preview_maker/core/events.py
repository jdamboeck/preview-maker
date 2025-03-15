"""Event communication system for Preview Maker.

This module provides a publish-subscribe mechanism for communication between
different parts of the application, enabling loose coupling and facilitating
asynchronous operations.
"""

import logging
import threading
import concurrent.futures
import uuid
from typing import Callable, Dict, List, Optional, Type, TypeVar, cast
from dataclasses import dataclass

T = TypeVar("T", bound="Event")

# Set up module logger
logger = logging.getLogger(__name__)


class Event:
    """Base class for all events."""

    pass


@dataclass
class Subscription:
    """Represents an event subscription."""

    id: str
    event_type: Type[Event]
    callback: Callable[[Event], None]


class EventManager:
    """Manages event subscriptions and publications.

    This class follows the singleton pattern to provide a single, centralized
    event manager for the entire application.
    """

    # Class-level variables for singleton pattern
    _instance: Optional["EventManager"] = None
    _lock = threading.RLock()
    _initialized = False
    _subscriptions: Dict[Type[Event], List[Subscription]] = {}
    _executor: Optional[concurrent.futures.ThreadPoolExecutor] = None

    @classmethod
    def _reset_for_testing(cls) -> None:
        """Reset the singleton instance for testing purposes."""
        with cls._lock:
            # Store the existing instance
            old_instance = cls._instance

            # Set class variables to None before creating a new instance
            cls._instance = None
            cls._initialized = False

            # Clean up the executor if it exists
            if old_instance and old_instance._executor:
                try:
                    old_instance._executor.shutdown(wait=True)
                except Exception as e:
                    logger.error(f"Error shutting down executor: {e}")

            # Explicitly clear all subscriptions
            cls._subscriptions = {}

    def __new__(cls) -> "EventManager":
        """Ensure singleton pattern for event manager."""
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
            return cls._instance

    def __init__(self) -> None:
        """Initialize the event manager."""
        with self._lock:
            if not self._initialized:
                self._subscriptions = {}
                self._executor = concurrent.futures.ThreadPoolExecutor(
                    max_workers=10, thread_name_prefix="event_worker"
                )
                self._initialized = True

    def subscribe(
        self, event_type: Type[T], callback: Callable[[T], None]
    ) -> Subscription:
        """Subscribe to events of a specific type.

        Args:
            event_type: The type of event to subscribe to
            callback: The function to call when an event of this type is published

        Returns:
            A Subscription object that can be used to unsubscribe
        """
        with self._lock:
            # Create subscription ID
            subscription_id = str(uuid.uuid4())

            # Create a subscription object with type casting for callback
            subscription = Subscription(
                id=subscription_id,
                event_type=event_type,
                callback=cast(Callable[[Event], None], callback),
            )

            # Add to subscriptions dict
            if event_type not in self._subscriptions:
                self._subscriptions[event_type] = []

            self._subscriptions[event_type].append(subscription)

            logger.debug(
                f"Added subscription {subscription_id} for {event_type.__name__}"
            )
            return subscription

    def unsubscribe(self, subscription: Subscription) -> None:
        """Unsubscribe from events.

        Args:
            subscription: The Subscription object returned from subscribe()
        """
        with self._lock:
            event_type = subscription.event_type
            if event_type in self._subscriptions:
                self._subscriptions[event_type] = [
                    s
                    for s in self._subscriptions[event_type]
                    if s.id != subscription.id
                ]
                logger.debug(
                    f"Removed subscription {subscription.id} for {event_type.__name__}"
                )

    def publish(self, event: Event) -> None:
        """Publish an event to all subscribers.

        Args:
            event: The event to publish
        """
        event_type = type(event)
        logger.debug(f"Publishing event of type {event_type.__name__}")

        # Make a copy of the subscriptions to avoid issues if subscribers
        # add/remove subscriptions during callback execution
        with self._lock:
            if event_type not in self._subscriptions:
                return

            subscribers = self._subscriptions[event_type].copy()

        # Call all subscribers
        for subscription in subscribers:
            try:
                subscription.callback(event)
            except Exception as e:
                logger.error(f"Error in event handler: {e}")

    def publish_async(self, event: Event) -> concurrent.futures.Future:
        """Publish an event asynchronously.

        This method returns immediately and processes the event in a background thread.

        Args:
            event: The event to publish

        Returns:
            A Future object representing the asynchronous operation
        """
        if not self._executor:
            with self._lock:
                if not self._executor:
                    self._executor = concurrent.futures.ThreadPoolExecutor(
                        max_workers=10, thread_name_prefix="event_worker"
                    )

        return self._executor.submit(self.publish, event)


# Global event manager instance
event_manager = EventManager()
