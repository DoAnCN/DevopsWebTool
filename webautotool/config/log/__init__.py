# -*- coding: utf-8 -*-

import logging
import colorlog

formatter = colorlog.ColoredFormatter(
    '%(purple)s%(asctime)s '
    '%(log_color)s%(levelname)-4s%(reset)s '
    '%(white)s%(message)s',
    datefmt = '%Y-%m-%d %H:%M',
    reset = True,
    log_colors = {
        'CRITICAL': 'red',
        'DEBUG': 'cyan',
        'ERROR': 'red',
        'INFO': 'green',
        'WARNING': 'yellow',
    },
    secondary_log_colors={},
	style='%',
)


def init_logger(lv_debug):
    handler = colorlog.StreamHandler()
    handler.setFormatter(formatter)
    log = colorlog.getLogger()
    if lv_debug:
        log.setLevel(logging.DEBUG)
    else:
        log.setLevel(logging.INFO)
    log.addHandler(handler)


def logger(name):
    return colorlog.getLogger(name)

