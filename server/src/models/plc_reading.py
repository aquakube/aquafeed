from dataclasses import dataclass

@dataclass
class PLCReading:

    panel: str
    """
    The PLC panel the setting is associated with.
    'mccp', 'blcp', 'f2cp', etc.
    """

    property: str
    """
    The PLC reading the setting is associated with.
    'feedSystemLockout', 'feedString1Fault', etc.
    """

    value: int
