import time
import logging
import traceback
from dataclasses import asdict

from models.automation_event import AutomationEvent

import clients.events as events
import clients.state as state
import clients.plc as plc

import automation.preflight as preflight
import automation.setup as setup
import automation.main as main
import automation.teardown as teardown
from automation.offspeed import OffSpeedHandler
from automation.reading import ReadingHandler
from config import config

def initialize():
    automation_id = state.automation.automation_id

    try:

        # start offspeed handler
        offspeed_handler = OffSpeedHandler()
        offspeed_handler.start()

        # start reading handler
        reading_handler = ReadingHandler()
        reading_handler.start()

        # reset feed system on startup
        feed_system_reset()

        # enter the preflight phase
        preflight.initialize()

        # enter the setup phase
        setup.initialize()

        # enter the main phase
        main.initialize()

        # enter the teardown phase
        teardown.initialize()

    except Exception as e:
        logging.exception('An error occurred while running the automation')

        # send automation failed event
        events.push(AutomationEvent(
            event='automation_failed',
            automation_id=automation_id,
            message='Automation failed',
            level='error',
            details={
                "error": str(e),
                "traceback": traceback.format_exc(),
            }
        ))

    finally:
        # stop offspeed handler
        offspeed_handler.stop()

        # update the automation state for the elapsed and end times
        state.automation.end_time = time.time()
        state.automation.elapsed_time = state.automation.end_time - state.automation.start_time
        state.automation.phase = 'completed'
        state.automation.phase_description = ''
        state.publish(state=state.automation)

        # send automation completed event
        events.push(AutomationEvent(
            event='automation_completed',
            automation_id=automation_id,
            message='Automation completed',
            level='info',
            details={
                "automation": asdict(state.automation),
            }
        ))

        # join the offspeed handler thread
        offspeed_handler.join()

        # reset the stop events
        reset()

        # safety measure
        shutdown_all_pumps()

        # reset feed system on shutdown
        feed_system_reset()

        # turn off generator
        turn_generator_off()

        # stop reading handler
        reading_handler.stop()


def stop():
    """ sets stop flag for all phases """
    preflight.stop_event.set()
    setup.stop_event.set()
    main.stop_event.set()


def reset():
    """ resets stop flag for all phases """
    preflight.stop_event.clear()
    setup.stop_event.clear()
    main.stop_event.clear()
    teardown.stop_event.clear()


def shutdown_all_pumps():
    """ shuts down all pumps """
    panel = state.automation.settings.feed_string['plc']['settings']['href']
    timeout = state.automation.settings.feed_string['plc']['settings']['timeout']
    plc.write(panel=panel, property='userrunsupplypump', value=0, timeout=timeout)
    plc.write(panel=panel, property='userrundeliverypump', value=0, timeout=timeout)
    plc.write(panel=panel, property='userrunaugermotor', value=0, timeout=timeout)


def feed_system_reset():
    panel = state.automation.settings.feed_string['plc']['settings']['href']
    timeout = state.automation.settings.feed_string['plc']['settings']['timeout']
    plc.write(panel=panel, property='userfeedreset', value=1, timeout=timeout)
    time.sleep(0.5)
    plc.write(panel=panel, property='userfeedreset', value=0, timeout=timeout)


def turn_generator_off():
    plc.write(
        panel=config.controls_plc_url,
        property='userenablegenerator',
        value=0,
        timeout=0.5,
    )