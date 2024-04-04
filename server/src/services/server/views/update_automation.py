import logging
import time
import traceback
from dataclasses import asdict

from models.automation_event import AutomationEvent
import clients.events as events
import clients.state as state
from config import update_request_schema, feed_strings
from automation.settings import update_settings
from automation.main import reset_feed_completed_bits, turn_auger_on

import jsonschema
from flask import Response, Blueprint, request

mod = Blueprint('update_automation', __name__)

@mod.route("/api/automation/update", methods=['PUT'])
def update_automation():

    # if there is not automation thread, we can't stop it
    if state.automation_thread is None or not state.automation_thread.is_alive():
        return 'Automation not running', 400

    # if the automation is not in a state where it can be updated, return an error
    # NOTE: this is definetely a hack, because obviously you could update the automation
    # settings after this check but by then maybe the automation already went to teardown
    # or something. This is just a quick fix to prevent the user from updating the automation
    # :shrugh: oh well what you gonna do when I have to manage state
    if state.automation.phase != 'preflight' and state.automation.phase != 'setup' and state.automation.phase != 'main':
        return 'Automation phase must be "setup" or "main" to update settings', 400

    # validate the request body
    try:
        request_data = request.get_json()
        jsonschema.validate(instance=request_data, schema=update_request_schema)
    except jsonschema.exceptions.ValidationError:
        logging.exception('Invalid request')
        return "Invalid request body", 400

    try:
        prev_feed_limit = state.automation.settings.feed_limit
        prev_feed_rate = state.automation.settings.feed_rate
        settings = state.automation.settings
        settings.feed_limit = request_data.get('feed_limit')
        settings.time_limit = request_data.get('time_limit')
        settings.feed_rate = request_data.get('feed_rate')
        settings.plc_readings = request_data.get('plc_readings')

        settings.plc_readings = update_settings(settings, on_update=True)

        state.automation.settings = settings
        state.publish(state=state.automation)

        if state.automation.phase == 'main':
            logging.info(f"requested limit: {request_data.get('feed_limit')} prev limit: {prev_feed_limit}")
            if request_data.get('feed_limit') > prev_feed_limit:
                logging.info(f"Feed limit increased, resetting feed completed bits")
                reset_feed_completed_bits()
                if not state.automation.paused:
                    turn_auger_on()
            if  prev_feed_rate < state.automation.settings.feed_string['augers'][0]['settings']['feedRate']['pulseThreshold'] and request_data.get('feed_rate') >= state.automation.settings.feed_string['augers'][0]['settings']['feedRate']['pulseThreshold']:
                if not state.automation.paused:
                    logging.info(f"Feed rate increased beyond pulse range, turning auger on for continuous feeeding")
                    turn_auger_on()
            if prev_feed_rate != state.automation.settings.feed_rate:
                logging.info(f"Feed rate changed, reseting auger on time for offspeed detection")
                state.auger_on_time = time.time()


    except Exception as e:
        logging.exception('Failed to update automation settings')
    
        events.push(AutomationEvent(
            event='automation_update_failed',
            automation_id=state.automation.automation_id,
            message='Automation settings update failed',
            level='error',
            details={
                'settings': asdict(state.automation.settings),
                'error': str(e),
                'traceback': traceback.format_exc()
            }
        ))

        return Response(status=500)
    
    events.push(AutomationEvent(
        event='automation_updated',
        automation_id=state.automation.automation_id,
        message='Automation settings were updated',
        level='info',
        details={
            'settings': asdict(state.automation.settings),
        }
    ))

    return Response(status=202)