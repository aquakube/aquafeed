from dataclasses import asdict
from uuid import uuid4
from datetime import datetime, timezone

import clients.state as state
from models.automation_state import AutomationState


def reset_automation_state() -> AutomationState:
    """
    Resets the automation state to the default values.
    """
    state.automation = AutomationState(
        automation_id=None,
        phase="ready",
        paused=False,
        start_time=None,
        end_time=None,
        elapsed_time=0,
        phase_elapsed_time=0,
        phase_percentage=0,
        phase_description='',
        feed_delivered=0,
        feed_rate=0,
        epo=False,
        settings={},
        readings={}
    )
    return state.automation


def get_cloudevent(state: AutomationState) -> dict:
    """
    Returns a cloudevent representation of the automation state.
    """
    timestamp = datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()
    cloudevent = {
        "context": {
            "version": "1.0.0",
            "id": str(uuid4()),
            "timestamp": timestamp,
            "type": "feed.automation.state",
            "source": "/feed/automation/state",
            "action": "create",
            "dataschema": "http://schema.foreveroceans.io/v1/feedAutomationEvent/feedAutomationState-1.0.0.json",
            "datacontenttype": "json",
        },
        "data": asdict(state) if state else None,
    }
    return cloudevent