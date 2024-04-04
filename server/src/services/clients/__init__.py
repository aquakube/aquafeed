import time
import logging
import requests
import threading

from models.automation_event import AutomationEvent

from automation import stop as stop_automation
import clients.events as events
import clients.state as state
from clients import plc

from config import config


class ClientMonitorThread(threading.Thread):
    """
    Responsible for stopping an automation if a network partition occurs and an operator gets disconnected during a feed
    """

    def __init__(self):
        super().__init__(daemon=True, name=f"client monitor thread")
        self.stop_event = threading.Event()
        self.bomb_timer = None
        self.bombed = False

    def run(self):
        while not self.stop_event.is_set():
            try:
                time.sleep(config.client_monitor_polling_interval)
                number_of_connected_clients: int = state.get_number_of_connected_clients()

                if number_of_connected_clients == 0 and not self.bombed and state.automation_thread and state.automation_thread.is_alive() and self.bomb_timer is None:
                    logging.info('No connected clients, starting bomb timer')
                    self.bomb_timer = time.time()

                if self.bomb_timer is not None and time.time() - self.bomb_timer > config.client_monitor_bomb_threshold:
                    logging.info('BOMB! Stopping automation due to no connected clients')
                    stop_automation()
                    events.push(AutomationEvent(
                        event='no_connected_clients_warning',
                        automation_id=state.automation.automation_id,
                        message='Stopping automation due to no connected clients',
                        level='warning',
                        details={}
                    ))
                    self.bomb_timer = None
                    self.bombed = True

                if self.bomb_timer is not None and number_of_connected_clients > 0:
                    logging.info("Resetting bomb timer, clients are connected again")
                    self.bomb_timer = None

                if self.bombed and not (state.automation_thread and state.automation_thread.is_alive()):
                    logging.info('Resetting bombed flag')
                    self.bombed = False
            except:
                logging.exception('client monitor thread failed')

    def stop(self):
        self.stop_event.set()
