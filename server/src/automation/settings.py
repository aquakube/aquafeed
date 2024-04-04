from models.automation_state import AutomationSettings
from models.plc_reading import PLCReading

import clients.plc as plc
import clients.state as state

def update_settings(settings: AutomationSettings, on_update: bool = False) -> 'list[PLCReading]':


    # fetch settings from the feed string configuration
    panel = state.automation.settings.feed_string['plc']['settings']['href']
    supply_pump_setup_speed = state.automation.settings.feed_string['supplyPump']['settings']['setupSpeed']
    delivery_pump_run_speed = state.automation.settings.feed_string['deliveryPump']['settings']['runSpeed']
    ratio_of_ticks_per_kg = state.automation.settings.feed_string['calibrations']['ratio_of_ticks_per_kg']

    a = state.automation.settings.feed_string['calibrations']['auger_run_speed_coefficients']['a']
    b = state.automation.settings.feed_string['calibrations']['auger_run_speed_coefficients']['b']
    c = state.automation.settings.feed_string['calibrations']['auger_run_speed_coefficients']['c']
    feed_rate_pulse_threshold = state.automation.settings.feed_string['augers'][0]['settings']['feedRate']['pulseThreshold']


    readings = [
        # set feed rate
        PLCReading(
            panel,
            property='userfeedraterequested',
            value=settings.feed_rate
        ),
        # set feed limit
        PLCReading(
            panel,
            property='userfeedquantityrequested',
            value=settings.feed_limit
        ),
        # set auger mode
        PLCReading(
            panel,
            property='augermotorfeedrateorhz',
            value=1
        ),
        # set auger speed
        PLCReading(
            panel,
            property='useraugermotorspeeddemand',
            # calculates the auger speed based on the feed rate
            # there is minimum auger speed defined in % throttle given our determined minimum feed rate of X KG/MIN
            # this minimum feed rage value will vary per system according to its feed string specs
            value=int(
                max(
                    min((a*(settings.feed_rate/60)**2) + (b*(settings.feed_rate/60)) + c, 100),
                    min((a*feed_rate_pulse_threshold**2) + (b*feed_rate_pulse_threshold) + c, 100),
                )
            )
        )
    ]

    if not on_update:
        readings.extend([
            # set supply pump speed
            PLCReading(
                panel,
                property='usersupplypumpspeeddemand',
                value=supply_pump_setup_speed
            ),
            # set delivery pump speed
            PLCReading(
                panel,
                property='userdeliverypumpspeeddemand',
                value=delivery_pump_run_speed
            ),
            # set feed calibration
            PLCReading(
                panel,
                property='userfeedconstantrequested',
                value=ratio_of_ticks_per_kg
            ),
        ])

    settings = [
        *readings,
        *settings.plc_readings,
    ]

    # update the PLC with the new settings
    for setting in settings:
        plc.write(setting. panel, setting.property, setting.value, timeout=state.automation.settings.feed_string['plc']['settings']['timeout'])

    return settings
