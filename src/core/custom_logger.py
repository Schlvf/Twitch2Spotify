import logging
import sys


def reset_color():
    return "\x1b[0m"


def get_text_color(color):
    colors = {
        "black": "\x1b[30;49;1m",
        "red": "\x1b[31;49;1m",
        "green": "\x1b[32;49;1m",
        "yellow": "\x1b[33;49;1m",
        "blue": "\x1b[34;49;1m",
        "magenta": "\x1b[35;49;1m",
        "cyan": "\x1b[36;49;1m",
        "white": "\x1b[37;49;1m",
    }
    return colors[color]


def get_bg_color(color):
    colors = {
        "w_black": "\x1b[30;47;1m",
        "w_red": "\x1b[37;41;1m",
        "w_green": "\x1b[37;42;1m",
        "w_yellow": "\x1b[37;43;1m",
        "w_blue": "\x1b[37;44;1m",
        "w_magenta": "\x1b[37;45;1m",
        "w_cyan": "\x1b[37;46;1m",
        "w_white": "\x1b[37;40;1m",
    }
    return colors[color]


def get_color_by_level(level):
    levels = {
        "DEBUG": "w_black",
        "INFO": "w_green",
        "WARN": "w_yellow",
        "ERR": "w_red",
        "CRIT": "w_red",
    }
    color = levels[level]

    return get_bg_color(color)


class CustomFormatter(logging.Formatter):
    """Please use this side for the colors https://ansi.gabebanks.net/"""

    """Base format -> '%(asctime)s - %(name)s - %(levelname)s - %(message)-60s (%(filename)s:%(lineno)d)'"""

    field_date = get_text_color("magenta") + "%(asctime)s" + reset_color()
    field_name = get_bg_color("w_blue") + "%(name)s" + reset_color()
    field_msg = "%(message)-60s"
    field_file = get_text_color("yellow") + "(%(filename)s:%(lineno)d)" + reset_color()

    head = field_date + " - " + field_name + " - "
    tail = " - " + field_msg + " - " + field_file

    # format = "%(asctime)s - %(name)s - %(levelname)s - %(message)-60s (%(filename)s:%(lineno)d)"

    FORMATS = {
        logging.DEBUG: (
            head + get_color_by_level("DEBUG") + "%(levelname)s" + reset_color() + tail
        ),
        logging.INFO: (
            head + get_color_by_level("INFO") + "%(levelname)s" + reset_color() + tail
        ),
        logging.WARNING: (
            head + get_color_by_level("WARN") + "%(levelname)s" + reset_color() + tail
        ),
        logging.ERROR: (
            head + get_color_by_level("ERR") + "%(levelname)s" + reset_color() + tail
        ),
        logging.CRITICAL: (
            head + get_color_by_level("CRIT") + "%(levelname)s" + reset_color() + tail
        ),
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


def get_logger_level(level):
    levels = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }

    return levels[level]


def get_logger_instance(name, level):
    logger = logging.getLogger(name)
    logger.setLevel(get_logger_level(level))
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(CustomFormatter())
    logger.addHandler(handler)

    return logger
