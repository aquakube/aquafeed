from dataclasses import dataclass

@dataclass
class AutomationEvent:

    event: str
    """
    The event type.
    """

    automation_id: str
    """
    The uuid of the automation.
    """

    message: str
    """
    A human readable message that can be displayed on a UI
    """

    level: str
    """
    Level of info, warning, error, that can be used to
    determine how to display the message.
    """

    details: dict
    """
    A dictionary of additional details that can be used 
    to provide more information about the event.
    """
