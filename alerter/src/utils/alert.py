from enum import Enum


def floaty(value: str) -> float:
    if value is None or value == "None":
        return 0
    else:
        return float(value)


class SeverityCode(Enum):
    INFO = 1
    WARNING = 2
    CRITICAL = 3
    ERROR = 4


class Severity(Enum):
    INFO = 'INFO'
    WARNING = 'WARNING'
    CRITICAL = 'CRITICAL'
    ERROR = 'ERROR'
