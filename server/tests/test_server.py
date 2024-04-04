import uuid
import time
from dataclasses import asdict

from unittest.mock import Mock, patch
import pytest

from models.automation_event import AutomationEvent
from models.automation_state import AutomationSettings
from models.automation_state import AutomationState
from services.server import app as flask_app
import clients.state as state
import clients.plc as plc
import clients.events as events


@pytest.fixture
def test_flask_app():
    """ Yields a flask test client """
    with flask_app.test_client() as client:
        yield client


@pytest.fixture
def test_automation_state(monkeypatch):
    automation = AutomationState(
        automation_id=str(uuid.uuid4()),
        phase='preflight',
        faulted=False,
        paused=False,
        start_time=time.time(),
        end_time=None,
        elapsed_time=0,
        phase_elapsed_time=0,
        phase_percentage=0,
        feed_delivered=0,
        feed_rate=0,
        settings=AutomationSettings(
            automation_type='double',
            feed_rate=60,
            feed_limit=100,
            time_limit=100,
            plc_readings=[]
        )
    )
    monkeypatch.setattr('clients.state.automation', automation)


@pytest.fixture
def test_plc_client(monkeypatch):
    plc_read = Mock()
    plc_read.return_value = None
    plc_write = Mock()
    plc_write.return_value = None
    monkeypatch.setattr('clients.plc.read', plc_read)
    monkeypatch.setattr('clients.plc.write', plc_write)
    monkeypatch.setattr(plc, 'requests', Mock())


@pytest.fixture
def test_automation_thread(monkeypatch):
    thread = Mock()
    thread.is_alive.return_value = True
    monkeypatch.setattr('clients.state.automation_thread', thread)


@pytest.fixture
def test_events_client(monkeypatch):
    push = Mock()
    push.return_value = None
    monkeypatch.setattr(events, 'push', Mock())



def test_unset_automation_state(test_flask_app):
    """
    The automation state should be unset by default
    """
    response = test_flask_app.get("/api/automation/state")
    assert response.status_code == 200
    assert response.json == {}


def test_set_automation_state(test_flask_app, test_automation_state):
    """
    The automation state should be the json representation of the state
    when set
    """
    response = test_flask_app.get("/api/automation/state")
    assert response.status_code == 200
    assert response.json == asdict(state.automation)
    assert response.json['automation_id'] != None


def test_pause_automation(test_flask_app, test_plc_client, test_automation_thread, test_automation_state, test_events_client):
    # send the request
    response = test_flask_app.put("/api/automation/pause")

    # assert the response
    assert response.status_code == 202
    assert events.push.called == True
    assert isinstance(events.push.call_args[0][0], AutomationEvent) == True
    assert plc.write.called == True
    assert plc.write.call_args[0][0] == 'mccp'
    assert plc.write.call_args[0][1] == 'feedpause'
    assert plc.write.call_args[0][2] == 1


def test_resume_automation(test_flask_app, test_plc_client, test_automation_thread, test_automation_state, test_events_client):
        # send the request
        response = test_flask_app.put("/api/automation/resume")
    
        # assert the response
        assert response.status_code == 202
        assert events.push.called == True
        assert isinstance(events.push.call_args[0][0], AutomationEvent) == True
        assert plc.write.called == True
        assert plc.write.call_args[0][0] == 'mccp'
        assert plc.write.call_args[0][1] == 'feedpause'
        assert plc.write.call_args[0][2] == 0


def test_stop_automation(test_flask_app, test_plc_client, test_automation_thread, test_automation_state, test_events_client):
        # send the request
        response = test_flask_app.put("/api/automation/stop")
    
        # assert the response
        assert response.status_code == 202
        assert events.push.called == True
        assert isinstance(events.push.call_args[0][0], AutomationEvent) == True
        assert plc.write.called == True
        assert plc.write.call_args[0][0] == 'mccp'
        assert plc.write.call_args[0][1] == 'feedstop'
        assert plc.write.call_args[0][2] == 1


def test_reset_automation(test_flask_app, test_plc_client, test_automation_thread, test_automation_state, test_events_client):
        # send the request
        response = test_flask_app.put("/api/automation/reset")
    
        # assert the response
        assert response.status_code == 200
        assert events.push.called == False
        assert plc.write.called == True
        assert plc.write.call_args[0][0] == 'mccp'
        assert plc.write.call_args[0][1] == 'feed2faultreset'
        assert plc.write.call_args[0][2] == 1