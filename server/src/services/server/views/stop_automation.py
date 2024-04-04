import time
import uuid
import json
import threading
import logging
from dataclasses import asdict

from models.automation_state import AutomationState
from models.automation_event import AutomationEvent

from automation import stop

import clients.events as events
import clients.state as state
import clients.plc as plc

from flask import Response, Blueprint

mod = Blueprint('stop_automation', __name__)

@mod.route("/api/automation/stop", methods=['PUT'])
def stop_automation():

    # if there is not automation thread, we can't stop it
    if state.automation_thread is None or not state.automation_thread.is_alive():
        return 'Automation not running', 400

    try:
        stop()
    except:
        logging.exception('Failed to stop automation')
        return Response(status=500)

    events.push(AutomationEvent(
        event='requested_stop',
        automation_id=state.automation.automation_id,
        message='Automation request to stop was acknowledged',
        level='info',
        details={}
    ))

    return Response(status=202)