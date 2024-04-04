import time
import math
import threading

from models.automation_event import AutomationEvent
from config import f200_automation_settings, config
from models.plc_reading import PLCReading

import clients.events as events
import clients.plc as plc
import clients.state as state
import utility.plc_readings as plc_readings


stop_event = threading.Event()
""" stop flag initiated by operator """

timeout = None
""" the timout value for the automation once feed has been completed """

target_reached_time = None
""" the time when the feed quantity has been reached """

start_time = None
""" the start time of the main phase """


def initialize():

    global stop_event, timeout, target_reached_time, start_time

    # reset variables (safety measure becasue im using globals which is bad juju)
    timeout = None
    target_reached_time = None
    start_time = None

    if stop_event.is_set():
        return

    # initialize variables
    start_time = time.time()
    automation_id = state.automation.automation_id

    # send event that phase has changed
    events.push(AutomationEvent(
        event='automation_phase_changed',
        automation_id=state.automation.automation_id,
        message=f'Automation phase changed from "{state.automation.phase}" to "main"',
        level='info',
        details={
            'previous_phase': state.automation.phase,
            'current_phase': 'main',
        }
    ))
    state.automation.phase = 'main'
    state.automation.phase_percentage = 0
    state.automation.phase_description = 'Starting main phase'
    state.publish(state=state.automation)

    # Start the auger motor upon entering the main phase to begin feeding if not within pulse feeder range
    
    if state.automation.settings.feed_rate >= state.automation.settings.feed_string['augers'][0]['settings']['feedRate']['pulseThreshold']:
        state.automation.phase_description = 'Turning auger on'
        state.publish(state=state.automation)
        turn_auger_on()

    # Main phase control loop
    while True:

        # exit main phase if pumps are off (they should always be on unless EPO / user is controlling from HMI)
        supply_pump_running = plc.read(property='userrunsupplypump')
        delivery_pump_running = plc.read(property='userrundeliverypump')
        if not supply_pump_running or not delivery_pump_running:
            events.push(AutomationEvent(
                event='main_failed',
                automation_id=automation_id,
                message=f'The supply or delivery pump has stopped running',
                level='error',
                details={
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
                        }
                    ]
                }
            ))
            break

        # exit main phase if stop event is set
        if stop_event.is_set():
            break

        # exit main phase if feed completed grace period is over
        if feed_completed():
            events.push(AutomationEvent(
                event='main_succeeded',
                automation_id=automation_id,
                message=f'The main phase grace period has ended after {f200_automation_settings.timeout_main_phase_completed} seconds.',
                level='info',
                details={}
            ))
            break

        # exit main phase if feed timeout has been reached
        if feed_timeout():
            events.push(AutomationEvent(
                event='main_timeout',
                automation_id=automation_id,
                message=f'The main phase has timed out after exceeding the feed time limit of {state.automation.settings.time_limit} minutes.',
                level='info',
                details={}
            ))
            break

        # sleep for the control loop iterations
        time.sleep(f200_automation_settings.control_loop_sleep_period_main_phase)

        # calculate feed delivered
        auger_ticks = plc.read(property='augerticks')
        feed_constant = state.automation.settings.feed_string['calibrations']['ratio_of_ticks_per_kg']
        feed_delivered = auger_ticks / feed_constant

        # calculate feed rate actual
        auger_speed = plc.read(property='augermotorspeedfeedback')
        D = state.automation.settings.feed_string['calibrations']['feed_rate_actual_coefficients']['d']
        E = state.automation.settings.feed_string['calibrations']['feed_rate_actual_coefficients']['e']
        F = state.automation.settings.feed_string['calibrations']['feed_rate_actual_coefficients']['f']
        feed_rate = 0
        if auger_speed > 0:
            feed_rate = ((D * auger_speed**2) + (E * auger_speed) + F) * 60

        # read the current state of the system
        # feed_delivered = plc.read(property='feedquanititydelivered')
        # feed_rate = plc.read(property='feedrateactual')
        feed_target = plc.read(property='userfeedquantityrequested')
        auger_on = plc.read(property='userrunaugermotor')
        projected_time = plc.read(property='feedtimeestimate') * 60

        # update the automation state
        update_state(feed_rate, feed_delivered, feed_target, projected_time)

        # check if the feed quantity requested has been reached
        if feed_delivered >= feed_target and target_reached_time is None and timeout is None:
            # stop the auger
            turn_auger_off()
            # set the phase timeout variables to enter teardown phase unless operators updates feed quantity
            timeout = f200_automation_settings.timeout_main_phase_completed
            target_reached_time = time.time()
            # send event that the feed target has been reached
            events.push(AutomationEvent(
                event='feed_target_reached',
                automation_id=automation_id,
                message=f'The feed target of {feed_target} has been reached. Update the automation within {f200_automation_settings.timeout_main_phase_completed} seconds or the system will enter teardown phase.',
                level='info',
                details={
                    "plc_readings": [
                        {
                            "panel": state.automation.settings.feed_string['plc']['settings']['href'],
                            "property": "feedquanititydelivered",
                            "value": feed_delivered,
                        },
                        {
                            "panel": state.automation.settings.feed_string['plc']['settings']['href'],
                            "property": "userfeedquantityrequested",
                            "value": feed_target,
                        }
                    ]
                }
            ))
        # when feed is running check the mixing bowl and pump sensors are nominal
        if auger_on:
            # stop auger to prvent clogs
            # TODO: add flag to toggle this on based on the sensor set
            # stop_auger_if_water_level_low(minimum=f200_automation_settings.minimum_mixing_bowl_level_main_phase)
            stop_auger_if_delivery_pump_pressure_spiked(maximum=state.automation.settings.feed_string['deliveryPump']['settings']['psiThresholds']['max'])
            # check if feed is detected while auger is on
            # check_feed_detection(auger_is_turned_on=auger_on)

        # Pulse auger if running below the minimum feed rate for a simple feed.
        if state.automation.settings.feed_rate < state.automation.settings.feed_string['augers'][0]['settings']['feedRate']['pulseThreshold']:
            # Calculate pulse on and off times based on forumula (provided via HW team)
            pulse_on_time =  ((state.automation.settings.feed_rate / state.automation.settings.feed_string['augers'][0]['settings']['feedRate']['pulseThreshold']) / state.automation.settings.feed_string['augers'][0]['settings']['feedRate']['numberOfPulsesPerMinute']) * 60
            pulse_off_time = (60 / state.automation.settings.feed_string['augers'][0]['settings']['feedRate']['numberOfPulsesPerMinute']) - pulse_on_time

            if (time.time() % (pulse_on_time + pulse_off_time)) < pulse_on_time and not auger_on and not state.automation.paused:
                turn_auger_on()
            elif (time.time() % (pulse_on_time + pulse_off_time)) >= pulse_on_time and auger_on and not state.automation.paused:
                turn_auger_off()

    # Stop the auger when exiting main phase (safety net - it should be off already)
    state.automation.phase_description = 'Main phase completed. Turning auger off'
    state.publish(state=state.automation)
    turn_auger_off()
    # reset variables (safety measure becasue im using globals which is bad juju)
    timeout = None
    target_reached_time = None
    start_time = None


def feed_completed() -> bool:
    global timeout, target_reached_time
    return bool(
        timeout is not None 
        and target_reached_time is not None
        and time.time() - target_reached_time > timeout
    )


def feed_timeout() -> bool:
    global start_time
    return bool(
        start_time is not None
        and (time.time() - start_time) > (state.automation.settings.time_limit * 60)
    )


def reset_feed_completed_bits():
    global timeout, target_reached_time
    timeout = None
    target_reached_time = None


def turn_auger_on():
    automation_id = state.automation.automation_id
    try:
        response = plc.write(
            panel = state.automation.settings.feed_string['plc']['settings']['href'],
            property='userrunaugermotor',
            value=1,
            timeout = state.automation.settings.feed_string['plc']['settings']['timeout']
        )
        state.auger_on_time = time.time()
        plc_readings.update(PLCReading(
            panel=state.automation.settings.feed_string['plc']['settings']['href'],
            property='userrunaugermotor',
            value=1
        ))
        events.push(AutomationEvent(
            event='start_auger_succeeded',
            automation_id=automation_id,
            message='The auger has been started',
            level='info',
            details=response
        ))
    except Exception as exception:
        events.push(AutomationEvent(
            event='start_auger_failed',
            automation_id=automation_id,
            message='The auger failed to start',
            level='error',
            details=exception
        ))
        raise Exception(f'The auger failed to start {exception}')


def turn_auger_off():
    automation_id = state.automation.automation_id
    try:
        response = plc.write(
            panel = state.automation.settings.feed_string['plc']['settings']['href'],
            property='userrunaugermotor',
            value=0,
            timeout = state.automation.settings.feed_string['plc']['settings']['timeout']
        )
        plc_readings.update(PLCReading(
            panel=state.automation.settings.feed_string['plc']['settings']['href'],
            property='userrunaugermotor',
            value=0
        ))
        events.push(AutomationEvent(
            event='stop_auger_succeeded',
            automation_id=automation_id,
            message='The auger has been stopped',
            level='info',
            details=response
        ))
    except Exception as exception:
        events.push(AutomationEvent(
            event='stop_auger_failed',
            automation_id=automation_id,
            message='The auger failed to stop',
            level='error',
            details=exception
        ))
        raise Exception(f'The auger failed to stop {exception}')


def stop_auger_if_water_level_low(minimum: int) -> bool:
    mixing_bowl_level = plc.read(property='mixbwllevel')

    if mixing_bowl_level < minimum:
        # stop the auger to prevent a clog
        turn_auger_off()
        # enter automatic paused state
        state.automation.paused = True
        state.publish(state=state.automation)
        # send event that the auger has been stopped due to clog
        events.push(AutomationEvent(
            event='main_failed',
            automation_id=state.automation.automation_id,
            message=f'Main failed: The mixing bowl level is too low. Level: {mixing_bowl_level}. Stopping the auger to prevent clogging.',
            level='error',
            details={
                "plc_readings": [
                    {
                        "panel": state.automation.settings.feed_string['plc']['settings']['href'],
                        "property": "mixbwllevel",
                        "value": mixing_bowl_level,
                    },
                ]
            }
        ))


def stop_auger_if_delivery_pump_pressure_spiked(maximum: int) -> bool:
    deliverypumpoutletpressure = plc.read(property='deliverypumpoutletpressure')

    if deliverypumpoutletpressure > maximum:
        # stop the auger 
        turn_auger_off()
        # enter automatic paused state
        state.automation.paused = True
        state.publish(state=state.automation)
        # send event that the auger has been stopped due to clog
        events.push(AutomationEvent(
            event='delivery_pump_pressure_warning',
            automation_id=state.automation.automation_id,
            message=f'The delivery pump pressure spiked. Pressure: {deliverypumpoutletpressure}. Stopping the auger to prevent clogging.',
            level='error',
            details={
                'deliverypumpoutletpressure': deliverypumpoutletpressure
            }
        ))


def check_feed_detection(auger_is_turned_on: bool):
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

    if not feed_detected and auger_is_turned_on:
        events.push(AutomationEvent(
            event='main_warning',
            automation_id=automation_id,
            message=f'Main warning: The system detected no feed when the aguer is turned on.',
            level='warning',
            details=details
        ))


def update_state(feed_rate: int, feed_delivered: int, feed_target: int, projected_time: int):
    global start_time
    phase_elapsed_time = time.time() - start_time

    phase_percentage = 0
    if feed_target > 0:
        phase_percentage = math.floor((feed_delivered / feed_target) * 100)

    state.automation.feed_delivered = feed_delivered
    state.automation.feed_rate = feed_rate
    state.automation.phase_elapsed_time = phase_elapsed_time
    state.automation.phase_projected_time = projected_time
    state.automation.phase_percentage = phase_percentage
    state.automation.phase_description = f"Delivered {feed_delivered}kg of {feed_target}kg."
    if time.time() - state.last_publish_time > config.state_publish_interval:
        state.publish(state=state.automation)
        state.last_publish_time = time.time()
