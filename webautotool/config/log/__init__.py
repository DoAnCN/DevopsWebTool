# -*- coding: utf-8 -*-

import colorlog
import logging
import re

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
    log = colorlog.getLogger()
    log = disable_loggers(log)
    level = logging.DEBUG if lv_debug else logging.INFO
    log_handler = colorlog.StreamHandler()
    log_handler.setFormatter(formatter)
    log.setLevel(level)
    log.addHandler(log_handler)


def logger(name):
    return colorlog.getLogger(name)


# Tạm thời chưa giải quyết được vấn đề dư log của sh
def disable_loggers(log):
    log_disabled = ['requests\.', 'urllib3', 'paramiko',
                    'process', 'stream', 'command', 'sh\.']
    log.manager.disable_pattern = re.compile('^' + '|'.join(log_disabled))
    return log

