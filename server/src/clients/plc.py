import time
import logging

import requests
import clients.state as state

from config import config


def read(property: str, retries=3, retry_timeout=1) -> int:
    url = state.automation.settings.feed_string['plc']['settings']['href'] + '/' + property
    timeout = state.automation.settings.feed_string['plc']['settings']['timeout']

    response = None
    exception = None

    for _ in range(retries):
        try:
            response = requests.get(url=url, timeout=timeout)

            if response.status_code == 200:
                return response.json().get('value')

        except Exception as e:
            exception = e
            logging.exception(f'Request to {url} failed!')
        
        time.sleep(retry_timeout)

    if exception is not None:
        raise exception
    
    return response.raise_for_status()


def write(panel: str, property: str, value: int, timeout: float, retries: float = 3, retry_timeout: float = 1):
    response = None
    exception = None

    for _ in range(retries):
        try:
            response = requests.put(
                url=panel + '/' + property,
                json={'value': value},
                timeout=timeout
            )

            if response.status_code == 200:
                return response.content.decode('utf-8')

        except Exception as e:
            exception = e
            logging.exception(f'Request to {panel + "/" + property} timed out')
        
        time.sleep(retry_timeout)

    if exception is not None:
        raise exception
    
    return response.raise_for_status()


def read_from_controls_plc(property: str, retries=3, retry_timeout=1) -> int:
        url =  config.controls_plc_url + '/' + property

        response = None
        exception = None

        for _ in range(retries):
            try:
                response = requests.get(url=url, timeout=0.5)

                if response.status_code == 200:
                    return response.json().get('value')

            except Exception as e:
                exception = e
                logging.exception(f'Request to {url} failed!')
            
            time.sleep(retry_timeout)

        if exception is not None:
            raise exception
        
        return response.raise_for_status()
