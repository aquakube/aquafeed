from dataclasses import dataclass

from models.plc_reading import PLCReading


@dataclass
class AutomationSettings:

    feed_rate: int
    """
    The feed rate in kilograms/min.
    """

    feed_limit: int
    """
    The feed limit in kilograms.
    """

    time_limit: int
    """
    The time limit in minutes.
    """

    feed_string: dict
    """
    The feed string configuration.
    """

    plc_readings: list[PLCReading]
    """
    The PLC readings that are set on startup
    """


@dataclass
class AutomationState:

    automation_id: str

    phase: str

    paused: bool

    start_time: float

    end_time: float

    elapsed_time: int

    phase_elapsed_time: int

    phase_percentage: int

    feed_delivered: int

    feed_rate: int

    epo: bool

    settings: AutomationSettings
    """
    automation settings that are
    utilized by the automation.
    """

    phase_description: str

    readings: dict
