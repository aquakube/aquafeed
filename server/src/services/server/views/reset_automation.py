import logging
import traceback

import clients.plc as plc
import clients.state as state
import clients.events as events
from models.automation_event import AutomationEvent
from utility import state as state_utility

from flask import Response, Blueprint

from automation import reset, feed_system_reset, shutdown_all_pumps

mod = Blueprint('reset_automation', __name__)

@mod.route("/api/automation/reset", methods=['PUT'])
def reset_automation():
    """ reset automation """
    try:
        if state.automation_thread is not None and state.automation_thread.is_alive():
            return Response(response="can't reset when an automation is running", status=400)

        state.automation = state_utility.reset_automation_state()
        state.publish(state=state.automation)

        events.push(AutomationEvent(
            event='automation_reset',
            automation_id=state.automation.automation_id,
            message='Automation reset',
            level='info',
            details={}
        ))

        return Response(status=200)

    except Exception as e:
        logging.exception('Failed to reset automation')
        events.push(AutomationEvent(
            event='automation_reset_failed',
            automation_id=state.automation.automation_id if state is not None else '',
            message='Automation reset failed',
            level='error',
            details={
                "error": str(e),
                "traceback": traceback.format_exc(),
            }
        ))
        return Response(status=500)