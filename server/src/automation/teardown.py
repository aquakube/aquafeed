import time
import math
import threading

from models.automation_event import AutomationEvent

from config import config
from models.plc_reading import PLCReading

import clients.events as events
import clients.plc as plc
import clients.state as state
import utility.plc_readings as plc_readings

stop_event = threading.Event()
start_time = None

def initialize():
    global start_time, stop_event

    start_time = time.time()

    automation_id = state.automation.automation_id

    # send event that phase has changed
    events.push(AutomationEvent(
        event='automation_phase_changed',
        automation_id=state.automation.automation_id,
        message=f'Automation phase changed from "{state.automation.phase}" to "teardown"',
        level='info',
        details={
            'previous_phase': state.automation.phase,
            'current_phase': 'teardown',
        }
    ))
    state.automation.phase = 'teardown'
    state.automation.phase_description = ''
    state.automation.phase_percentage = 0
    state.publish(state=state.automation)

    if state.automation.epo:
        state.automation.phase_description = 'Detected EPO in teardown state. Turning pumps off and exiting'
        state.publish(state=state.automation)
        stop_supply_pump()
        stop_delivery_pump()
        turn_generator_off()
        return

    # get system state
    supply_pump_running = plc.read(property='userrunsupplypump')
    delivery_pump_running = plc.read(property='userrundeliverypump')
    auger_running = plc.read(property='userrunaugermotor')
    details = {
        'plc_readings': [
            {
                "panel": state.automation.settings.feed_string['plc']['settings']['href'],
                "property": "userrunsupplypump",
                "value": supply_pump_running,
            },
            {
                "panel": state.automation.settings.feed_string['plc']['settings']['href'],
                "property": "userrundeliverypump",
                "value": delivery_pump_running,
            },
            {
                "panel": state.automation.settings.feed_string['plc']['settings']['href'],
                "property": "userrundeliverypump",
                "value": auger_running,
            }
        ]
    }

    # check for abnoraml teardown state
    if not supply_pump_running or not delivery_pump_running:
        events.push(AutomationEvent(
            event='teardown_warning',
            automation_id=automation_id,
            message='Teardown warning: Detected abnormal teardown state. Supply and/or delivery pumps were off when they should be on at this point.',
            level='warning',
            details=details
        ))
        state.automation.phase_description = 'Detected abnormal teardown state. Turning pumps off to be safe.'
        state.publish(state=state.automation)
        stop_supply_pump()
        stop_delivery_pump()
        turn_generator_off()
        return


    # Allow pumps to flush for X seconds (determined by length of output hose)
    while time.time() - start_time < state.automation.settings.feed_string['mixingBowl']['settings']['flushTimeout'] and not stop_event.is_set():
        update_automation_phase_times(phase_description=f"Flushing the system for {int(state.automation.settings.feed_string['mixingBowl']['settings']['flushTimeout'] - (time.time() - start_time))} seconds")
        time.sleep(1)
    
    # Stop the supply pump
    state.automation.phase_description = 'Stopping the supply pump'
    state.publish(state=state.automation)
    stop_supply_pump()

    # # Wait for the delivery pump to reach 0 PSI
    # # Deprecating this in favor of time based flushing because there is no penalty for running delivery pump when supply pump is off.
    # # This is more consistent than waiting for the delivery pump to reach 0 PSI. Sensor variation caused problems during testing
    # wait_for_delivery_pump_pressure(timeout=state.automation.settings.feed_string['deliveryPump']['settings']['shutoffPressureTimeout'])

    # Allow the delivery pump time to flush the mixing bowl dry
    _clear_mixing_start_time = time.time()
    while time.time() - _clear_mixing_start_time < state.automation.settings.feed_string['mixingBowl']['settings']['emptyBowlTimeout'] and not stop_event.is_set():
        update_automation_phase_times(phase_description=f"Emptying the mixing bowl. This will be done in {int(state.automation.settings.feed_string['mixingBowl']['settings']['emptyBowlTimeout'] - (time.time() - _clear_mixing_start_time))} seconds")
        time.sleep(1)

    # Stop the delivery pump
    state.automation.phase_description = 'Stopping the delivery pump'
    state.publish(state=state.automation)
    stop_delivery_pump()

    state.automation.phase_description = 'Turning off the generator'
    state.publish(state=state.automation)
    turn_generator_off()
    wait_for_loadbus_to_go_offline()

    state.automation.phase_percentage = 100

    # setup phase succeeded
    events.push(AutomationEvent(
        event='teardown_succeeded',
        automation_id=state.automation.automation_id,
        message=f'Teardown succeeded: The system has been shutoff',
        level='info',
        details={}
    ))


def update_automation_phase_times(phase_description: str = ''):
    global start_time
    phase_elapsed_time = time.time() - start_time
    phase_projected_time = state.automation.settings.feed_string['mixingBowl']['settings']['flushTimeout'] + state.automation.settings.feed_string['deliveryPump']['settings']['shutoffPressureTimeout'] + 30

    # prevent divide by zero
    phase_percentage = 0
    if phase_projected_time is not None and phase_projected_time > 0:
        phase_percentage = math.floor((phase_elapsed_time / phase_projected_time) * 100)

    state.automation.phase_elapsed_time = phase_elapsed_time
    state.automation.phase_projected_time = phase_projected_time
    state.automation.phase_percentage = phase_percentage
    state.automation.phase_description = phase_description

    if time.time() - state.last_publish_time > config.state_publish_interval:
        state.publish(state=state.automation)
        state.last_publish_time = time.time()


def stop_supply_pump():
    automation_id = state.automation.automation_id
    try:
        response = plc.write(
            panel = state.automation.settings.feed_string['plc']['settings']['href'],
            property='userrunsupplypump',
            value=0,
            timeout = state.automation.settings.feed_string['plc']['settings']['timeout']
        )
        plc_readings.update(PLCReading(
            panel=state.automation.settings.feed_string['plc']['settings']['href'],
            property='userrunsupplypump',
            value=0
        ))
        events.push(AutomationEvent(
            event='stop_supply_pump_succeeded',
            automation_id=automation_id,
            message='The supply pump has stopped',
            level='info',
            details=response
        ))
    except Exception as exception:
        events.push(AutomationEvent(
            event='stop_supply_pump_failed',
            automation_id=automation_id,
            message='The supply pump failed to stop',
            level='error',
            details=exception
        ))
        raise Exception(f'The supply pump failed to stop {exception}')


def stop_delivery_pump():
    automation_id = state.automation.automation_id
    try:
        response = plc.write(
            panel = state.automation.settings.feed_string['plc']['settings']['href'],
            property='userrundeliverypump',
            value=0,
            timeout = state.automation.settings.feed_string['plc']['settings']['timeout']
        )
        plc_readings.update(PLCReading(
            panel=state.automation.settings.feed_string['plc']['settings']['href'],
            property='userrundeliverypump',
            value=0
        ))
        events.push(AutomationEvent(
            event='stop_delivery_pump_succeeded',
            automation_id=automation_id,
            message='The delivery pump has stopped',
            level='info',
            details=response
        ))
    except Exception as exception:
        events.push(AutomationEvent(
            event='stop_delivery_pump_failed',
            automation_id=automation_id,
            message='The delivery pump failed to stop',
            level='error',
            details=exception
        ))
        raise Exception(f'The delivery pump failed to stop {exception}')


def wait_for_delivery_pump_pressure(timeout: int):
    automation_id = state.automation.automation_id
    start_time = time.time()
    while time.time() - start_time < timeout:
        delivery_pump_psi = plc.read(property='deliverypumpoutletpressure')
        details = {
            'plc_readings': [
                {
                    "panel": state.automation.settings.feed_string['plc']['settings']['href'],
                    "property": "deliverypumpoutletpressure",
                    "value": delivery_pump_psi,
                }
            ]
        }
        if delivery_pump_psi <= 1:
            events.push(AutomationEvent(
                event='mixing_bowl_empty_succeeded',
                automation_id=automation_id,
                message=f'The delivery pump outlet pressure hit {delivery_pump_psi} psi',
                level='info',
                details=details
            ))
            break
        update_automation_phase_times(phase_description=f"Emptying the mixing bowl. Wating for delivery pump to reach 0 PSI. Current pressure is {delivery_pump_psi} PSI")
        time.sleep(0.5)
    else:
        events.push(AutomationEvent(
            event='mixing_bowl_empty_failed',
            automation_id=automation_id,
            message=f'The delivery pump outlet pressure failed to reach 0 within the timeout of {timeout} seconds.',
            level='error',
            details=details
        ))
        raise Exception(f'The delivery pump outlet pressure failed to reach 0 within the timeout of {timeout} seconds.')


def turn_generator_off():
    automation_id = state.automation.automation_id
    try:
        response = plc.write(
            panel=config.controls_plc_url,
            property='userenablegenerator',
            value=0,
            timeout=0.5
        )
        plc_readings.update(PLCReading(
            panel=config.controls_plc_url,
            property='userenablegenerator',
            value=1
        ))
        events.push(AutomationEvent(
            event='stop_generator_succeeded',
            automation_id=automation_id,
            message='The generator has stopped',
            level='info',
            details=response
        ))
    except Exception as exception:
        events.push(AutomationEvent(
            event='stop_generator_failed',
            automation_id=automation_id,
            message='The generator failed to stop',
            level='error',
            details=exception
        ))
        raise Exception(f'The generator failed to stop {exception}')


def wait_for_loadbus_to_go_offline(timeout: int = 30):
    start_time = time.time()
    automation_id = state.automation.automation_id

    while time.time() - start_time < timeout:
        if stop_event.is_set():
            return
        
        loadbus_online = plc.read_from_controls_plc(property='genloadbusonline')
        if not loadbus_online:
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
                event='generator_loadbus_offline_succeeded',
                automation_id=automation_id,
                message='The generator loadbus has gone offline',
                level='info',
                details=details
            ))
            return

        update_automation_phase_times(phase_description=f"Turning off the generator")
        time.sleep(1)

    events.push(AutomationEvent(
        event='generator_loabus_offline_failed',
        automation_id=automation_id,
        message='The generator loadbus failed to go offline',
        level='error',
        details='The load bus did not go offline within the timeout period',
    ))
    raise Exception('The load bus did not go offline within the timeout period')