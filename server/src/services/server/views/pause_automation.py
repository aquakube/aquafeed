import logging
import traceback

from models.automation_event import AutomationEvent
from automation.main import turn_auger_off
from config import feed_strings

import clients.events as events
import clients.state as state
import clients.plc as plc

from flask import Response, Blueprint

mod = Blueprint('pause_automation', __name__)

@mod.route("/api/automation/pause", methods=['PUT'])
def pause_automation():

    try:
        if state.automation_thread is None or not state.automation_thread.is_alive():
            return 'Automation not running', 400

        if state.automation.phase != 'main':
            return 'Automation phase must be "main" to pause a feed', 400

        turn_auger_off()
        state.automation.paused = True
        state.publish(state=state.automation)

        events.push(AutomationEvent(
            event='automation_paused',
            automation_id=state.automation.automation_id,
            message='Automation request to pause was acknowledged',
            level='info',
            details={
                'plc_readings': [{
                    'panel': state.automation.settings.feed_string['plc']['settings']['href'],
                    'property': 'userrunaugermotor',
                    'value': plc.read(property='userrunaugermotor')
                }]
            }
        ))

        return Response(status=202)

    except Exception as e:
        logging.exception('Failed to pause automation')
        events.push(AutomationEvent(
            event='automation_pause_failed',
            automation_id=state.automation.automation_id if state is not None else '',
            message='Automation pause failed',
            level='error',
            details={
                "error": str(e),
                "traceback": traceback.format_exc(),
            }
        ))
        return Response(status=500)