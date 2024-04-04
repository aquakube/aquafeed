import time
import logging
import threading

from clients import plc
from clients import state

logger = logging.getLogger()


class ReadingHandler(threading.Thread):
    """
    Class to handle routine reading of important PLC values for operators
    """

    def __init__(self):
        super().__init__(daemon=True, name=f"reading handler thread")
        self.stop_event = threading.Event()

    def stop(self):
        self.stop_event.set()

    def run(self):
        while not self.stop_event.is_set():
            try:
                # logger.info("Reading handler running")

                prev_readings = dict(state.automation.readings)

                state.automation.readings['supplypumpvacuumsensor'] = plc.read(property='supplypumpvacuumsensor')
                state.automation.readings['deliverypumpoutletpressure'] = plc.read(property='deliverypumpoutletpressure')

                state.automation.readings['userrunsupplypump'] = plc.read(property='userrunsupplypump')
                state.automation.readings['supplypumpspeedfeedback'] = plc.read(property='supplypumpspeedfeedback')
                state.automation.readings['usersupplypumpspeeddemand'] = plc.read(property='usersupplypumpspeeddemand')

                state.automation.readings['userrundeliverypump'] = plc.read(property='userrundeliverypump')
                state.automation.readings['deliverypumpspeedfeedback'] = plc.read(property='deliverypumpspeedfeedback')
                state.automation.readings['userdeliverypumpspeeddemand'] = plc.read(property='userdeliverypumpspeeddemand')

                state.automation.readings['userrunaugermotor'] = plc.read(property='userrunaugermotor')
                state.automation.readings['augermotorspeedfeedback'] = plc.read(property='augermotorspeedfeedback')
                state.automation.readings['useraugermotorspeeddemand'] = plc.read(property='useraugermotorspeeddemand')

                state.publish(state=state.automation)
                # self.publish_on_change(prev=prev_readings, current=state.automation.readings)

                # TODO: update read plc client function to handle multiple panels
                # state.automation.readings['userenablegenerator'] = plc.read(property='userenablegenerator')

                time.sleep(0.5)
            except:
                logger.exception("An error occurred in reading handler")

    def publish_on_change(self, prev: dict, current: dict):
        """
        Publish the current state of the automation if any of the readings have changed
        """
        for key in current:
            # logger.info(f"{key} prev: {prev.get(key)} current: {current.get(key)}")
            if prev.get(key) != current.get(key):
                logger.info(f"Publishing state due to change in {key}")
                state.publish(state=state.automation)
                return
