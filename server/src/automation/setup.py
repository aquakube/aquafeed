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
""" stop flag initiated by operator """

start_time = None
""" time when automation phase started"""

priming_time = None
""" time it took in seconds for the supply pump to prime """

def initialize():
    global start_time, stop_event, priming_time

    if stop_event.is_set():
        return

    start_time = time.time()
    priming_time = None

    # send event that phase has changed
    events.push(AutomationEvent(
        event='automation_phase_changed',
        automation_id=state.automation.automation_id,
        message=f'Automation phase changed from "{state.automation.phase}" to "setup"',
        level='info',
        details={
            'previous_phase': state.automation.phase,
            'current_phase': 'setup',
        }
    ))
    state.automation.phase = 'setup'
    state.automation.phase_percentage = 0
    state.automation.phase_description = 'Starting supply pump'
    state.publish(state=state.automation)

    # starts the supply pump
    run_supply_pump()

    if stop_event.is_set():
        return

    # wait for supply pump vacuum psi to reach -5 (this means the supply pump is primed)
    wait_on_supply_pump(
        supply_pump_primed_psi_threshold=state.automation.settings.feed_string['supplyPump']['settings']['psiThresholds']['primed'],
        timeout=state.automation.settings.feed_string['supplyPump']['settings']['primeTimeout']
    )

    if stop_event.is_set():
        return

    state.automation.phase_description = 'Filling mixing bowl'
    state.publish(state=state.automation)

    # sleep for half the time it takes to fill a mixing bowl to full capacity at max supply pump speed
    time.sleep(state.automation.settings.feed_string['mixingBowl']['settings']['fillTimeout'])

    state.automation.phase_description = 'Starting delivery pump'
    state.publish(state=state.automation)

    # starts the delivery pump
    run_delivery_pump()

    # drop the supply pump speed to the operating speed
    drop_supply_pump_speed(
        speed=state.automation.settings.feed_string['supplyPump']['settings']['runSpeed']
    )

    if stop_event.is_set():
        return

    # waits for the water level to reach the high sensor
    wait_on_stabilization(
        timeout=state.automation.settings.feed_string['mixingBowl']['settings']['stabilizationTimeout']
    )

    # setup phase succeeded
    events.push(AutomationEvent(
        event='setup_succeeded',
        automation_id=state.automation.automation_id,
        message=f'Setup succeeded: The system has stabilized after {state.automation.settings.feed_string["mixingBowl"]["settings"]["stabilizationTimeout"]} seconds',
        level='info',
        details={}
    ))


def update_automation_phase_times(phase_description: str = ''):
    global start_time, priming_time
    phase_elapsed_time = time.time() - start_time

    fill_mixing_bowl_time = state.automation.settings.feed_string['mixingBowl']['settings']['fillTimeout']
    stabilization_time = state.automation.settings.feed_string['mixingBowl']['settings']['stabilizationTimeout']
    phase_projected_time =  fill_mixing_bowl_time + stabilization_time

    # if priming was quick reduce the projected time by the actual priming time, otherwise use the default priming timeout time in calculation
    if priming_time is None:
        phase_projected_time += state.automation.settings.feed_string['supplyPump']['settings']['primeTimeout']
    if priming_time:
        phase_projected_time += priming_time

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


def run_supply_pump():
    automation_id = state.automation.automation_id
    try:
        response = plc.write(
            panel = state.automation.settings.feed_string['plc']['settings']['href'],
            property='userrunsupplypump',
            value=1,
            timeout = state.automation.settings.feed_string['plc']['settings']['timeout']
        )
        state.supply_pump_on_time = time.time()
        plc_readings.update(PLCReading(
            panel=state.automation.settings.feed_string['plc']['settings']['href'],
            property='userrunsupplypump',
            value=1
        ))
        events.push(AutomationEvent(
            event='start_supply_pump_succeeded',
            automation_id=automation_id,
            message='The supply pump has started',
            level='info',
            details=response
        ))
    except Exception as exception:
        events.push(AutomationEvent(
            event='start_supply_pump_failed',
            automation_id=automation_id,
            message='The supply pump failed to start',
            level='error',
            details=exception
        ))
        raise Exception(f'The supply pump failed to start {exception}')


def wait_on_supply_pump(supply_pump_primed_psi_threshold: int = -5, timeout: int = 120):
    global stop_event, priming_time
    automation_id = state.automation.automation_id
    start_time = time.time()
    while time.time() - start_time < timeout:
        # break out manually so the else clause doesn't run when user stops during this task of the setup phase
        if stop_event.is_set():
            break
        time.sleep(0.25)
        vacuum_psi = plc.read(property='supplypumpvacuumsensor')
        update_automation_phase_times(phase_description=f"Priming supply pump. Current vacuum pressure: {vacuum_psi} psi. Target vacuum pressure: {supply_pump_primed_psi_threshold} psi")
        details = {
            'plc_readings': [
                {
                    "panel": state.automation.settings.feed_string['plc']['settings']['href'],
                    "property": "supplypumpvacuumsensor",
                    "value": vacuum_psi,
                }
            ]
        }
        if vacuum_psi <= supply_pump_primed_psi_threshold:
            events.push(AutomationEvent(
                event='supply_pump_primed_succeeded',
                automation_id=automation_id,
                message=f'The supply pump has been primed and reached the expected vacuum pressure of {supply_pump_primed_psi_threshold} psi',
                level='info',
                details=details
            ))
            priming_time = time.time() - start_time
            break
    else:
        events.push(AutomationEvent(
            event='supply_pump_primed_failed',
            automation_id=automation_id,
            message=f'Setup failed: The supply pump failed to prime within the timeout of {timeout} seconds. The supply pump vacuum pressure should reach atleast {supply_pump_primed_psi_threshold} psi when primed',
            level='error',
            details=details
        ))
        raise Exception(f'Setup failed: The supply pump failed to prime within the timeout of {timeout} seconds. The supply pump vacuum pressure should reach atleast {supply_pump_primed_psi_threshold} psi when primed)')


def run_delivery_pump():
    automation_id = state.automation.automation_id
    try:
        response = plc.write(
            panel = state.automation.settings.feed_string['plc']['settings']['href'],
            property='userrundeliverypump',
            value=1,
            timeout = state.automation.settings.feed_string['plc']['settings']['timeout']
        )
        state.delivery_pump_on_time = time.time()
        plc_readings.update(PLCReading(
            panel=state.automation.settings.feed_string['plc']['settings']['href'],
            property='userrundeliverypump',
            value=1
        ))
        events.push(AutomationEvent(
            event='start_delivery_pump_succeeded',
            automation_id=automation_id,
            message='The delivery pump has started',
            level='info',
            details=response
        ))
    except Exception as exception:
        events.push(AutomationEvent(
            event='start_delivery_pump_failed',
            automation_id=automation_id,
            message='The delivery pump failed to start',
            level='error',
            details=exception
        ))
        raise Exception(f'The delivery pump failed to start {exception}')


def drop_supply_pump_speed(speed: int):
    automation_id = state.automation.automation_id
    try:
        response = plc.write(
            panel = state.automation.settings.feed_string['plc']['settings']['href'],
            property='usersupplypumpspeeddemand',
            value=speed,
            timeout = state.automation.settings.feed_string['plc']['settings']['timeout']
        )
        plc_readings.update(PLCReading(
            panel=state.automation.settings.feed_string['plc']['settings']['href'],
            property='usersupplypumpspeeddemand',
            value=speed
        ))
        events.push(AutomationEvent(
            event='operational_supply_pump_speed_succeeded',
            automation_id=automation_id,
            message=f'Dropped supply pump speed to {speed}%',
            level='info',
            details=response
        ))
    except Exception as exception:
        events.push(AutomationEvent(
            event='operational_supply_pump_speed_failed',
            automation_id=automation_id,
            message=f'Failed to drop supply pump speed to {speed}%',
            level='error',
            details=exception
        ))
        raise Exception(f'Failed to drop supply pump speed to {speed}%. {exception}')


def wait_on_stabilization(timeout: int):
    global stop_event
    start_time = time.time()
    while time.time() - start_time < timeout and not stop_event.is_set():
        update_automation_phase_times(phase_description=f"Waiting on mixing bowl to stabilize. Flushing system for {int(timeout - (time.time() - start_time))} seconds")
        time.sleep(1)
        # confirm_delivery_pump_pressure_within_expected_range(
        #     minimum=state.automation.settings.feed_string['deliveryPump']['settings']['psiThresholds']['min'],
        #     maximum=state.automation.settings.feed_string['deliveryPump']['settings']['psiThresholds']['max'],
        # )
        # confirm_supply_pump_pressure_within_expected_range(
        #     minimum=state.automation.settings.feed_string['supplyPump']['settings']['psiThresholds']['min'],
        #     maximum=state.automation.settings.feed_string['supplyPump']['settings']['psiThresholds']['max'],
        # )
        # confirm_no_feed_deteceted()


def confirm_delivery_pump_pressure_within_expected_range(minimum: int, maximum: int):
    automation_id = state.automation.automation_id

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

    if not (minimum < delivery_pump_psi < maximum):
        events.push(AutomationEvent(
            event='delivery_pump_pressure_warning',
            automation_id=automation_id,
            message=f'Setup warning: The delivery pump pressure is not within the expected range ({minimum}, {maximum})',
            level='warning',
            details=details
        ))



def confirm_supply_pump_pressure_within_expected_range(minimum: int, maximum: int):
    automation_id = state.automation.automation_id

    supply_pump_psi = plc.read(property='supplypumpvacuumsensor')

    details = {
        'plc_readings': [
            {
                "panel": state.automation.settings.feed_string['plc']['settings']['href'],
                "property": "supplypumpvacuumsensor",
                "value": supply_pump_psi,
            }
        ]
    }

    if not (minimum < supply_pump_psi < maximum):
        events.push(AutomationEvent(
            event='supply_pump_pressure_warning',
            automation_id=automation_id,
            message=f'Setup warning: The supply pump pressure is not within the expected range ({minimum}, {maximum})',
            level='warning',
            details=details
        ))



def confirm_no_feed_deteceted():
    
    automation_id = state.automation.automation_id

    feed_detected = plc.read(property='feedcapacitiveon')

    details = {
        'plc_readings': [
            {
                "panel": state.automation.settings.feed_string['plc']['settings']['href'],
                "property": "feedcapacitiveon",
                "value": feed_detected,
            }
        ]
    }

    if feed_detected:
        events.push(AutomationEvent(
            event='feed_detected_warning',
            automation_id=automation_id,
            message=f'The system detected feed when the aguer is stopped. Please check the sensor.',
            level='warning',
            details=details
        ))
