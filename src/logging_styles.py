import logging
import coloredlogs

DEFAULT_LOG_LEVEL = logging.DEBUG
DEFAULT_LOG_FORMAT = "%(asctime)s - [%(levelname)s] - %(filename)s - %(message)s"  # NOQA
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

formatter = coloredlogs.ColoredFormatter(
    fmt=DEFAULT_LOG_FORMAT,
    datefmt=DEFAULT_DATE_FORMAT,
    field_styles=DEFAULT_FIELD_STYLES,
    level_styles=DEFAULT_LEVEL_STYLES,
)


def getLogger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(DEFAULT_LOG_LEVEL)
    logger.addHandler(logging.StreamHandler())
    logger.handlers[0].setFormatter(formatter)
    return logger
