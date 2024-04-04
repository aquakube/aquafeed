import time
import logging
import requests
import threading

from models.automation_event import AutomationEvent

from automation import stop
import clients.events as events
import clients.state as state
from clients import plc

from config import config

class EPOThread(threading.Thread):

    def __init__(self):
        super().__init__(daemon=True, name=f'epo thread')
        self.stopped_automation: bool = False
        self.stop_event = threading.Event()

    def read_epo_status(self, retries=3, retry_timeout=1) -> bool:
        url =  config.controls_plc_url + '/userenableepo'

        response = None
        exception = None

        for _ in range(retries):
            try:
                response = requests.get(url=url, timeout=0.5)

                if response.status_code == 200:
                    return bool(response.json().get('value'))

            except Exception as e:
                exception = e
            
            time.sleep(retry_timeout)

        if exception is not None:
            raise exception
        
        return response.raise_for_status()


    def run(self):
        while not self.stop_event.is_set():
            try:
                time.sleep(config.epo_polling_interval)
                epo = self.read_epo_status()
                prev_epo_state = state.automation.epo
                state.automation.epo = epo
                if epo and state.automation_thread and state.automation_thread.is_alive() and not self.stopped_automation:
                    logging.info('Stopping automation due to EPO')
                    stop()
                    self.stopped_automation = True
                    events.push(AutomationEvent(
                        event='epo_on',
                        automation_id=state.automation.automation_id,
                        message='Stopping automation due to Emergency Power Off (EPO)',
                        level='info',
                        details={
                            'plc_readings': [
                                {
                                    "panel": config.controls_plc_url,
                                    "property": "userenableepo",
                                    "value": epo,
                                }
                            ]
                        }
                    ))

                if not epo:
                    self.stopped_automation = False
                
                if prev_epo_state != epo:
                    logging.warning(f"EPO status changed to {epo} from {prev_epo_state}")
                    state.publish(state.automation)

            except:
                # logging.exception('Failed to read EPO status')
                # requests.exceptions.ConnectionError: HTTPConnectionPool(host='controls.plc.svc.cluster.local', port=5000): Max retries exceeded with url: /api/plc/userenableepo
                # (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x105ab96d0>: Failed to establish a new connection: [Errno 8] nodename nor servname provided, or not known'))
                pass
    
    def stop(self):
        self.stop_event.set()