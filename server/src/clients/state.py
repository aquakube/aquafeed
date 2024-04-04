"""
This state is only to be manipulated by the automation thread.
Only the automation thread should be able to update the state.
Other threads should read the state as needed.
"""
import time
import threading

from multiprocessing import Queue
from threading import Thread
from models.automation_state import AutomationState

from utility import state as state_utility

automation_thread: Thread = None
automation: AutomationState = state_utility.reset_automation_state()
last_publish_time: float = time.time()
auger_on_time: float = None
supply_pump_on_time: float = None
delivery_pump_on_time: float = None
number_connected_clients: int = 0

_event_queue = Queue()
_event_lock = threading.Lock()
_clients_lock = threading.Lock()

def publish(state: AutomationState):

    # update the elapsed time whenever state gets published
    if not state.end_time and state.start_time:
        state.elapsed_time = time.time() - state.start_time

    global _event_queue

    with _event_lock:
        cloudevent = state_utility.get_cloudevent(state)
        _event_queue.put_nowait(cloudevent)


def listen() -> 'dict | None':
    """
    Listen to the event queue, timeout after 5 seconds and
    return None if no event is received.
    """
    global _event_queue

    try:
        return _event_queue.get(block=True, timeout=5)
    except:
        # normal in timeout when queue is empty
        return None


def increment_number_of_connected_clients():
    global number_connected_clients
    with _clients_lock:
        number_connected_clients += 1


def decrement_number_of_connected_clients():
    global number_connected_clients
    with _clients_lock:
        number_connected_clients -= 1


def get_number_of_connected_clients() -> int:
    global number_connected_clients
    with _clients_lock:
        return number_connected_clients