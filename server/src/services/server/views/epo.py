import time
import requests
import logging
import traceback

from flask import Response, Blueprint

import clients.events as events
import clients.state as state

from models.automation_event import AutomationEvent
from config import config

mod = Blueprint('epo', __name__)


@mod.route("/api/automation/epo/on", methods=['PUT'])
def epo_on():
    """ turn emergency power off ON"""
    try:
        response = userenableepo(value=1)
        events.push(AutomationEvent(
            event='epo',
            automation_id=state.automation.automation_id if state and state.automation else '',
            message='EPO request was acknowledged',
            level='info',
            details=response
        ))
    except Exception as e:
        logging.exception('EPO request failed!')
        events.push(AutomationEvent(
            event='epo_request_failed',
            automation_id=state.automation.automation_id if state is not None else '',
            message='EPO request failed',
            level='error',
            details={
                "error": str(e),
                "traceback": traceback.format_exc(),
            }
        ))
        return Response(status=500)

    return Response(status=202)


@mod.route("/api/automation/epo/off", methods=['DELETE'])
def epo_off():
    """ emergency power off OFF"""
    try:
        response = userenableepo(value=0)
        events.push(AutomationEvent(
            event='clear_epo',
            automation_id=state.automation.automation_id if state and state.automation else '',
            message='clear EPO request was acknowledged',
            level='info',
            details=response
        ))
    except Exception as e:
        logging.exception('clear EPO request failed!')
        events.push(AutomationEvent(
            event='clear_epo_request_failed',
            automation_id=state.automation.automation_id if state is not None else '',
            message='clear EPO request failed',
            level='error',
            details={
                "error": str(e),
                "traceback": traceback.format_exc(),
            }
        ))
        return Response(status=500)

    return Response(status=202)


def userenableepo(value: int, retries=3, retry_timeout=1) -> str:
    url =  config.controls_plc_url + '/userenableepo'

    response = None
    exception = None

    for _ in range(retries):
        try:
            response = requests.put(
                url=url,
                json={'value': value},
                timeout=0.5
            )

            if response.status_code == 200:
                return response.content.decode('utf-8')

        except Exception as e:
            exception = e
            logging.exception(f'Request to {url} timed out')
        
        time.sleep(retry_timeout)

    if exception is not None:
        raise exception
    
    return response.raise_for_status()