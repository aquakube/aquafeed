from models.plc_reading import PLCReading

import clients.state as state

def update(reading: PLCReading):
    """
    Update the list of readings that have been written to the PLC and publish the updated state for consumers
    """
    plc_readings = state.automation.settings.plc_readings
    for plc_reading in plc_readings:
        if plc_reading.panel == reading.panel and plc_reading.property == reading.property:
            plc_reading.value = reading.value
            break
    else:
        plc_readings.append(reading)
    state.automation.settings.plc_readings = plc_readings
    state.publish(state=state.automation)