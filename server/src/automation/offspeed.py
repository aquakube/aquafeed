import time
import logging
import threading

from clients import plc
from clients import state
from clients import events

from models.automation_event import AutomationEvent
from config import config

logger = logging.getLogger()

class OffSpeedHandler(threading.Thread):
    """
    Class to handle offspeed events for supply pumps, delivery pumps, and auger motors
    """

    def __init__(self):
        super().__init__(daemon=True, name=f"offspeed handler thread")
        self.stop_event = threading.Event()


    def stop(self):
        self.stop_event.set()


    def run(self):
        while not self.stop_event.is_set():
            logger.info("Offspeed handler running")
            self.check_supply_pump_offspeed()
            self.check_delivery_pump_offspeed()
            self.check_auger_offspeed()
            time.sleep(config.offspeed_polling_interval)


    def check_supply_pump_offspeed(self):
        try:
            feed_string = state.automation.settings.feed_string
            supply_pump_running = plc.read(property='userrunsupplypump')
            supply_pump_run_speed = plc.read(property='supplypumpspeedfeedback')
            suppy_pump_set_speed = plc.read(property='usersupplypumpspeeddemand')
            if supply_pump_running  and state.supply_pump_on_time is not None and time.time() - state.supply_pump_on_time > config.offspeed_startup_threshold and abs(supply_pump_run_speed - suppy_pump_set_speed) > feed_string['supplyPump']['settings']['offSpeedThreshold']:
                events.push(AutomationEvent(
                    event='supply_pump_off_speed_warning',
                    automation_id=state.automation.automation_id,
                    message=f'Supply pump is running at {supply_pump_run_speed}% but should be running at {suppy_pump_set_speed}%. Delta is {abs(supply_pump_run_speed - suppy_pump_set_speed)}%',
                    level='warning',
                    details={
                        "plc_readings": [
                            {
                                "panel": feed_string['plc']['settings']['href'],
                                "property": "userrunsupplypump",
                                "value": supply_pump_running,
                            },
                            {
                                "panel": feed_string['plc']['settings']['href'],
                                "property": "supplypumpspeedfeedback",
                                "value": supply_pump_run_speed,
                            },
                            {
                                "panel": feed_string['plc']['settings']['href'],
                                "property": "usersupplypumpspeeddemand",
                                "value": suppy_pump_set_speed,
                            }
                        ]
                    }
                ))
        except:
            logger.exception("Error in offspeed handler for supply pump check")



    def check_delivery_pump_offspeed(self):
        try:
            feed_string = state.automation.settings.feed_string
            delivery_pump_running = plc.read(property='userrundeliverypump')
            delivery_pump_run_speed = plc.read(property='deliverypumpspeedfeedback')
            delivery_pump_set_speed = plc.read(property='userdeliverypumpspeeddemand')
            if delivery_pump_running and state.delivery_pump_on_time is not None and time.time() - state.delivery_pump_on_time > config.offspeed_startup_threshold and abs(delivery_pump_run_speed - delivery_pump_set_speed) > feed_string['deliveryPump']['settings']['offSpeedThreshold']:
                events.push(AutomationEvent(
                    event='delivery_pump_off_speed_warning',
                    automation_id=state.automation.automation_id,
                    message=f'Delivery pump is running at {delivery_pump_run_speed}% but should be running at {delivery_pump_set_speed}%. Delta is {abs(delivery_pump_run_speed - delivery_pump_set_speed)}%',
                    level='warning',
                    details={
                        "plc_readings": [
                            {
                                "panel": feed_string['plc']['settings']['href'],
                                "property": "userrundeliverypump",
                                "value": delivery_pump_running,
                            },
                            {
                                "panel": feed_string['plc']['settings']['href'],
                                "property": "deliverypumpspeedfeedback",
                                "value": delivery_pump_run_speed,
                            },
                            {
                                "panel": feed_string['plc']['settings']['href'],
                                "property": "userdeliverypumpspeeddemand",
                                "value": delivery_pump_set_speed,
                            }
                        ]
                    }
                ))
        except:
            logger.exception("Error in offspeed handler for delivery pump check")


    def check_auger_offspeed(self):
        try:
            feed_string = state.automation.settings.feed_string
            auger_running = plc.read(property='userrunaugermotor')
            auger_run_speed = plc.read(property='augermotorspeedfeedback')
            auger_set_speed = plc.read(property='useraugermotorspeeddemand')
            if auger_running and state.auger_on_time is not None and time.time() - state.auger_on_time > config.offspeed_startup_threshold  and abs(auger_run_speed - auger_set_speed) > feed_string['augers'][0]['settings']['offSpeedThreshold']:
                events.push(AutomationEvent(
                    event='auger_off_speed_warning',
                    automation_id=state.automation.automation_id,
                    message=f'Auger is running at {auger_run_speed}% but should be running at {auger_set_speed}%. Delta is {abs(auger_run_speed - auger_set_speed)}%',
                    level='warning',
                    details={
                        "plc_readings": [
                            {
                                "panel": feed_string['plc']['settings']['href'],
                                "property": "userrunaugermotor",
                                "value": auger_running,
                            },
                            {
                                "panel": feed_string['plc']['settings']['href'],
                                "property": "augermotorspeedfeedback",
                                "value": auger_run_speed,
                            },
                            {
                                "panel": feed_string['plc']['settings']['href'],
                                "property": "useraugermotorspeeddemand",
                                "value": auger_set_speed,
                            }
                        ]
                    }
                ))
        except:
            logger.exception("Error in offspeed handler for auger check")