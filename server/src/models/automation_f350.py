from dataclasses import dataclass


@dataclass(frozen=True)
class F350AutomationSettings:

    timeout_main_phase_completed: int = 120
    """
    The time in seconds to wait before exiting main phase after feed has been completed
    Feed is completed when feed delivered = feed requested
    This timeout is reset if the user updates the feed requested during this timeframe
    """

    flush_timeout_teardown_phase: int = 120
    """
    Time in seconds to wait for the pumps to flush during teardown phase
    Should be determined by the length of the output hose
    """

    control_loop_sleep_period_main_phase: int = 2
    """
    Time in seconds to sleep between each iteration of the main phase control loop
    """
