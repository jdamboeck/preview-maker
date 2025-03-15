"""Unit tests for the event communication system."""

import threading
import time
import pytest
from dataclasses import dataclass

from preview_maker.core.events import EventManager, Event


@dataclass
class TestEvent(Event):
    """Test event data class."""

    message: str
    value: int = 0


@pytest.fixture
def event_manager():
    """Fixture providing a fresh EventManager instance."""
    # Reset singleton state for each test
    EventManager._reset_for_testing()
    return EventManager()


def test_singleton_pattern(event_manager):
    """Test that EventManager follows the singleton pattern."""
    another_manager = EventManager()
    assert event_manager is another_manager


def test_subscribe_and_publish():
    """Test basic event subscription and publication."""
    manager = EventManager()
    received_events = []

    def event_handler(event: TestEvent):
        received_events.append(event)

    # Subscribe to event
    manager.subscribe(TestEvent, event_handler)

    # Publish event
    test_event = TestEvent(message="Hello", value=42)
    manager.publish(test_event)

    # Check that the event was received
    assert len(received_events) == 1
    assert received_events[0] is test_event
    assert received_events[0].message == "Hello"
    assert received_events[0].value == 42


def test_unsubscribe():
    """Test event unsubscription."""
    manager = EventManager()
    received_events = []

    def event_handler(event: TestEvent):
        received_events.append(event)

    # Subscribe to event
    subscription = manager.subscribe(TestEvent, event_handler)

    # Publish event
    manager.publish(TestEvent(message="First event"))
    assert len(received_events) == 1

    # Unsubscribe
    manager.unsubscribe(subscription)

    # Publish another event
    manager.publish(TestEvent(message="Second event"))

    # The second event should not be received
    assert len(received_events) == 1
    assert received_events[0].message == "First event"


def test_multiple_subscribers():
    """Test that multiple subscribers receive events."""
    manager = EventManager()
    received_events_1 = []
    received_events_2 = []

    def event_handler_1(event: TestEvent):
        received_events_1.append(event)

    def event_handler_2(event: TestEvent):
        received_events_2.append(event)

    # Subscribe both handlers
    manager.subscribe(TestEvent, event_handler_1)
    manager.subscribe(TestEvent, event_handler_2)

    # Publish event
    test_event = TestEvent(message="Broadcast", value=100)
    manager.publish(test_event)

    # Check that both handlers received the event
    assert len(received_events_1) == 1
    assert len(received_events_2) == 1
    assert received_events_1[0] is test_event
    assert received_events_2[0] is test_event


def test_typed_events():
    """Test that events are delivered to the correct handlers based on type."""
    manager = EventManager()
    test_events = []
    other_events = []

    @dataclass
    class OtherEvent(Event):
        data: str

    def test_handler(event: TestEvent):
        test_events.append(event)

    def other_handler(event: OtherEvent):
        other_events.append(event)

    # Subscribe to different event types
    manager.subscribe(TestEvent, test_handler)
    manager.subscribe(OtherEvent, other_handler)

    # Publish both types of events
    manager.publish(TestEvent(message="Test message"))
    manager.publish(OtherEvent(data="Other data"))

    # Check that events were delivered to the correct handlers
    assert len(test_events) == 1
    assert len(other_events) == 1
    assert test_events[0].message == "Test message"
    assert other_events[0].data == "Other data"


def test_threaded_publication():
    """Test event publication from multiple threads."""
    manager = EventManager()
    received_events = []
    event_lock = threading.Lock()

    def event_handler(event: TestEvent):
        with event_lock:
            received_events.append(event)

    # Subscribe to events
    manager.subscribe(TestEvent, event_handler)

    # Define thread function
    def publisher_thread(thread_id):
        for i in range(10):
            manager.publish(TestEvent(message=f"Thread {thread_id}, Event {i}"))

    # Start multiple publisher threads
    threads = []
    for i in range(5):
        thread = threading.Thread(target=publisher_thread, args=(i,))
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    # Check that all events were received
    assert len(received_events) == 50  # 5 threads * 10 events each


def test_async_publication():
    """Test asynchronous event publication."""
    manager = EventManager()
    received_events = []
    processed_time = None

    def slow_handler(event: TestEvent):
        nonlocal processed_time
        # Simulate processing delay
        time.sleep(0.1)
        received_events.append(event)
        processed_time = time.time()

    # Subscribe to events
    manager.subscribe(TestEvent, slow_handler)

    # Publish event asynchronously
    published_time = time.time()
    manager.publish_async(TestEvent(message="Async event"))

    # Check that we returned immediately
    assert time.time() - published_time < 0.05  # Much less than the 0.1s sleep

    # Wait for processing to complete
    time.sleep(0.2)

    # Check that the event was processed
    assert len(received_events) == 1
    assert received_events[0].message == "Async event"
    assert processed_time is not None
    assert processed_time > published_time


def test_reset_for_testing():
    """Test that _reset_for_testing clears all subscriptions."""
    # Get a fresh instance
    EventManager._reset_for_testing()

    # Create a manager and subscribe to events
    manager = EventManager()
    received_events = []

    def event_handler(event: TestEvent):
        received_events.append(event)
        print(f"Event received: {event.message}")

    # Subscribe to events
    manager.subscribe(TestEvent, event_handler)

    # Reset the manager
    EventManager._reset_for_testing()

    # Create a new manager instance to ensure we're not using the old one
    new_manager = EventManager()

    # Publish event using the new instance
    new_manager.publish(TestEvent(message="After reset"))

    # Check that no events were received
    assert len(received_events) == 0, f"Received events: {received_events}"


def test_error_handling():
    """Test that errors in event handlers don't affect other handlers."""
    manager = EventManager()
    successful_calls = []

    def failing_handler(event: TestEvent):
        raise RuntimeError("Handler error")

    def successful_handler(event: TestEvent):
        successful_calls.append(event.message)

    # Subscribe both handlers
    manager.subscribe(TestEvent, failing_handler)
    manager.subscribe(TestEvent, successful_handler)

    # Publish event
    manager.publish(TestEvent(message="Test error handling"))

    # Check that the successful handler was still called
    assert len(successful_calls) == 1
    assert successful_calls[0] == "Test error handling"
