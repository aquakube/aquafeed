import time
import uuid
import json
import threading
import logging
from dataclasses import asdict

from models.automation_state import AutomationState, AutomationSettings
from models.automation_event import AutomationEvent
import clients.events as events
import clients.state as state
from config import start_request_schema, feed_strings
import automation

import jsonschema
from flask import Flask, Response, Blueprint, request

mod = Blueprint('start_automation', __name__)

@mod.route("/api/automation/start", methods=['PUT'])
def start_automation():

    # check that no automation is running
    if state.automation_thread is not None and state.automation_thread.is_alive():
        return Response(response="An automation is already running!", status=400)

    # validate the request body
    try:
        request_data = request.get_json()
        jsonschema.validate(instance=request_data, schema=start_request_schema)
    except jsonschema.exceptions.ValidationError as e:
        logging.exception('Invalid request')
        return Response(response=str(e), status=400)

    # validate the feed string
    if request_data.get('feed_string') not in feed_strings.keys():
        return Response(response=f"Could not find a feed string called {state.automation.settings.feed_string}. Must be one of these {feed_strings.keys()}", status=404)

    # initialize the automation state
    state.automation = AutomationState(
        automation_id=str(uuid.uuid4()),
        phase='preflight',
        paused=False,
        start_time=time.time(),
        end_time=None,
        elapsed_time=0,
        phase_elapsed_time=0,
        phase_percentage=0,
        phase_description='',
        feed_delivered=0,
        feed_rate=0,
        epo=state.automation.epo,
        settings=AutomationSettings(
            feed_string=feed_strings[request_data.get('feed_string')],
            feed_rate=request_data.get('feed_rate'),
            feed_limit=request_data.get('feed_limit'),
            time_limit=request_data.get('time_limit'),
            plc_readings=request_data.get('plc_readings'),
        ),
        readings={}
    )

    # start the automation thread!
    automation_thread = threading.Thread(target=automation.initialize)
    automation_thread.start()
    state.automation_thread = automation_thread

    # send acknowledgement event
    events.push(AutomationEvent(
        event='automation_started',
        automation_id=state.automation.automation_id,
        message='Automation acknowledged request to start',
        level='info',
        details={
            "automation": asdict(state.automation)
        }
    ))
    # publish the state
    state.publish(state=state.automation)

    # send event that phase has changed. This is a special case, since
    events.push(AutomationEvent(
        event='automation_phase_changed',
        automation_id=state.automation.automation_id,
        message=f'Automation phase changed from "ready" to "{state.automation.phase}"',
        level='info',
        details={
            'previous_phase': 'ready',
            'current_phase': state.automation.phase,
        }
    ))

    return Response(
        response=json.dumps(asdict(state.automation)),
        mimetype="application/json",
        status=202
    )