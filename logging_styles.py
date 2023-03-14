import logging
import coloredlogs

DEFAULT_LOG_LEVEL = logging.DEBUG
DEFAULT_LOG_FORMAT = "%(asctime)s - [%(levelname)s] - %(filename)s - %(message)s"
DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
DEFAULT_FIELD_STYLES = {
    "asctime": {"color": "green"},
    "hostname": {"color": "magenta"},
    "levelname": {"bold": True, "color": 115},
    "name": {"color": "blue"},
}
# Boldだと色がつかない
DEFAULT_LEVEL_STYLES = {
    "debug": {"color": "green"},
    "info": {"color": "blue"},
    "warning": {"color": "yellow"},
    "error": {"color": "red"},
    "critical": {"color": "red"},
}

def set_default():
    coloredlogs.DEFAULT_LOG_LEVEL = DEFAULT_LOG_LEVEL
    coloredlogs.DEFAULT_LOG_FORMAT = DEFAULT_LOG_FORMAT
    coloredlogs.DEFAULT_DATE_FORMAT = DEFAULT_DATE_FORMAT
    coloredlogs.DEFAULT_FIELD_STYLES = DEFAULT_FIELD_STYLES
    coloredlogs.DEFAULT_LEVEL_STYLES = DEFAULT_LEVEL_STYLES
