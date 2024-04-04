import time
import requests
import traceback
import threading
from dataclasses import asdict

from models.plc_reading import PLCReading
from models.automation_event import AutomationEvent

from automation.settings import update_settings

import clients.events as events
import clients.plc as plc
import clients.state as state
from config import config
import utility.plc_readings as plc_readings

stop_event = threading.Event()
""" stop flag initiated by operator """

def initialize():
    global stop_event

    if stop_event.is_set():
        return

    start_time = time.time()

    state.automation.phase_description = 'Confirming Emergency Power Off mode is not active'
    state.publish(state=state.automation)

    confirm_emergency_power_off_mode()
    state.automation.phase_percentage = 5
    state.automation.phase_elapsed_time = time.time() - start_time
    state.automation.phase_description = 'Confirming supply pump is off'
    state.publish(state=state.automation)

    if stop_event.is_set():
        return

    confirm_supply_pump_is_off()
    state.automation.phase_percentage = 10
    state.automation.phase_elapsed_time = time.time() - start_time
    state.automation.phase_description = 'Confirming delivery pump is off'
    state.publish(state=state.automation)

    if stop_event.is_set():
        return

    confirm_delivery_pump_is_off()
    state.automation.phase_percentage = 15
    state.automation.phase_elapsed_time = time.time() - start_time
    state.automation.phase_description = 'Confirming auger is off'
    state.publish(state=state.automation)

    if stop_event.is_set():
        return

    confirm_auger_is_off()
    state.automation.phase_percentage = 20
    state.automation.phase_elapsed_time = time.time() - start_time
    state.automation.phase_description = 'Turning generator on'
    state.publish(state=state.automation)

    turn_generator_on()
    wait_for_loadbus_to_come_online()

    state.automation.phase_percentage = 99
    state.automation.phase_elapsed_time = time.time() - start_time
    state.automation.phase_description = 'Confirming settings are updated'
    state.publish(state=state.automation)

    if stop_event.is_set():
        return

    confirm_settings_are_updated()
    state.automation.phase_percentage = 100
    state.automation.phase_elapsed_time = time.time() - start_time
    state.automation.phase_description = 'Preflight successfully complete'
    state.publish(state=state.automation)


def read_epo_status(retries=3, retry_timeout=1) -> bool:
        url =  config.controls_plc_url + '/userenableepo'

        response = None
        exception = None

        for _ in range(retries):
            try:
                response = requests.get(url=url, timeout=0.5)

                if response.status_code == 200:
                    return bool(response.json().get('value'))

            except Exception as e:
                exception = e
            
            time.sleep(retry_timeout)

        if exception is not None:
            raise exception
        
        return response.raise_for_status()

def confirm_emergency_power_off_mode():
    automation_id = state.automation.automation_id

    emergency_power_off = read_epo_status()

    details = {
        'plc_readings': [
            {
                "panel": config.controls_plc_url,
                "property": "userenableepo",
                "value": emergency_power_off,
            }
        ]
    }

    if emergency_power_off:
        events.push(AutomationEvent(
            event='preflight_failed',
            automation_id=automation_id,
            message='Preflight failed: The system is in Emergency Power Off mode',
            level='error',
            details=details
        ))
        raise Exception('Preflight failed: The system is in Emergency Power Off mode')

    events.push(AutomationEvent(
        event='preflight_succeeded',
        automation_id=automation_id,
        message='Preflight succeeded: The system is not in Emergency Power Off mode',
        level='info',
        details=details
    ))


def confirm_supply_pump_is_off():
    automation_id = state.automation.automation_id

    supply_pump_running = plc.read(property='userrunsupplypump')

    details = {
        'plc_readings': [
            {
                "panel": state.automation.settings.feed_string['plc']['settings']['href'],
                "property": "userrunsupplypump",
                "value": supply_pump_running,
            }
        ]
    }

    if supply_pump_running:
        events.push(AutomationEvent(
            event='preflight_failed',
            automation_id=automation_id,
            message='Preflight failed: The supply pump is already running. Please turn off the supply pump before running the automation.',
            level='error',
            details=details
        ))
        raise Exception('Preflight failed: The supply pump is already running. Please turn off the supply pump before running the automation.')
    
    events.push(AutomationEvent(
        event='preflight_succeeded',
        automation_id=automation_id,
        message='Preflight succeeded: The supply pump is not running',
        level='info',
        details=details
    ))


def confirm_delivery_pump_is_off():
    automation_id = state.automation.automation_id

    delivery_pump_running = plc.read(property='userrundeliverypump')

    details = {
        'plc_readings': [
            {
                "panel": state.automation.settings.feed_string['plc']['settings']['href'],
                "property": "userrundeliverypump",
                "value": delivery_pump_running,
            }
        ]
    }

    if delivery_pump_running:
        events.push(AutomationEvent(
            event='preflight_failed',
            automation_id=automation_id,
            message='Preflight failed: The delivery pump is already running. Please turn off the delivery pump before running the automation.',
            level='error',
            details=details
        ))
        raise Exception('Preflight failed: The delivery pump is already running. Please turn off the delivery pump before running the automation.')
    
    events.push(AutomationEvent(
        event='preflight_succeeded',
        automation_id=automation_id,
        message='Preflight succeeded: The delivery pump is not running',
        level='info',
        details=details
    ))


def confirm_auger_is_off():
    automation_id = state.automation.automation_id

    auger_running = plc.read(property='userrunaugermotor')

    details = {
        'plc_readings': [
            {
                "panel": state.automation.settings.feed_string['plc']['settings']['href'],
                "property": "userrunaugermotor",
                "value": auger_running,
            }
        ]
    }

    if auger_running:
        events.push(AutomationEvent(
            event='preflight_failed',
            automation_id=automation_id,
            message='Preflight failed: The auger is already running. Please ensure the auger is stopped before running the automation.',
            level='error',
            details=details
        ))
        raise Exception('Preflight failed: The auger is already running. Please ensure the auger is stopped before running the automation.')
    
    events.push(AutomationEvent(
        event='preflight_succeeded',
        automation_id=automation_id,
        message='Preflight succeeded: The auger is not running',
        level='info',
        details=details
    ))


def confirm_settings_are_updated():
    try:
        settings = state.automation.settings
        plc_readings = update_settings(settings)
        state.automation.settings.plc_readings = plc_readings
        state.publish(state=state.automation)

        events.push(AutomationEvent(
            event='preflight_succeeded',
            automation_id=state.automation.automation_id,
            message='Preflight succeeded: Settings are updated',
            level='info',
            details={
                "settings": asdict(state.automation.settings),
            }
        ))

    except Exception as e:
        events.push(AutomationEvent(
            event='preflight_failed',
            automation_id=state.automation.automation_id,
            message='Preflight failed: Settings could not be updated',
            level='error',
            details={
                "error": str(e),
                "traceback": traceback.format_exc(),
            }
        ))
        raise Exception('Preflight failed: Settings could not be updated')


def turn_generator_on():
    automation_id = state.automation.automation_id
    try:
        response = plc.write(
            panel=config.controls_plc_url,
            property='userenablegenerator',
            value=1,
            timeout=0.5
        )
        plc_readings.update(PLCReading(
            panel=config.controls_plc_url,
            property='userenablegenerator',
            value=1
        ))
        events.push(AutomationEvent(
            event='start_generator_succeeded',
            automation_id=automation_id,
            message='The generator has started',
            level='info',
            details=response
        ))
    except Exception as exception:
        events.push(AutomationEvent(
            event='start_generator_failed',
            automation_id=automation_id,
            message='The generator failed to start',
            level='error',
            details=exception
        ))
        raise Exception(f'The generator failed to start {exception}')


def wait_for_loadbus_to_come_online(timeout: int = 30):
    start_time = time.time()
    automation_id = state.automation.automation_id

    while time.time() - start_time < timeout:
        if stop_event.is_set():
            return
        
        loadbus_online = plc.read_from_controls_plc(property='genloadbusonline')
        if loadbus_online:
            details = {
                'plc_readings': [
                    {
                        "panel": config.controls_plc_url,
                        "property": "genloadbusonline",
                        "value": loadbus_online,
                    }
                ]
            }
            events.push(AutomationEvent(
                event='generator_loadbus_online_succeeded',
                automation_id=automation_id,
                message='The generator loadbus has come online',
                level='info',
                details=details
            ))
            return

        state.automation.phase_percentage = 20 + (time.time() - start_time) / 30 * 79
        state.automation.phase_elapsed_time = time.time() - start_time
        state.publish(state=state.automation)
        time.sleep(1)

    events.push(AutomationEvent(
        event='generator_loadbus_online_failed',
        automation_id=automation_id,
        message='The generator loadbus failed to come online',
        level='error',
        details='The load bus did not come online within the timeout period',
    ))
    raise Exception('The load bus did not come online within the timeout period')
