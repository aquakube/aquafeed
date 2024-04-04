import logging
import traceback
from dataclasses import asdict

from models.automation_state import AutomationState
from models.automation_event import AutomationEvent
from automation.main import turn_auger_on
import clients.events as events
import clients.state as state
import clients.plc as plc
from config import feed_strings

from flask import Flask, Response, Blueprint, jsonify, request, copy_current_request_context

mod = Blueprint('resume_automation', __name__)

@mod.route("/api/automation/resume", methods=['PUT'])
def resume_automation():

    try:
        # if there is not automation thread, we can't stop it
        if state.automation_thread is None or not state.automation_thread.is_alive():
            return 'Automation not running', 400
        
        if state.automation.phase != 'main':
            return 'Automation phase must be "main" to resume a feed', 400

        turn_auger_on()
        state.automation.paused = False
        state.publish(state=state.automation)

        events.push(AutomationEvent(
            event='automation_resumed',
            automation_id=state.automation.automation_id,
            message='Automation request to resume was acknowledged',
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
        logging.exception('Failed to resume automation')
        # send automation failed event
        events.push(AutomationEvent(
            event='automation_resume_failed',
            automation_id=state.automation.automation_id if state is not None else '',
            message='Automation failed',
            level='error',
            details={
                "error": str(e),
                "traceback": traceback.format_exc(),
            }
        ))
        return Response(status=500)