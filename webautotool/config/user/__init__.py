# -*- coding: utf-8 -*-

import yaml
from os.path import join, exists, expanduser

from webautotool.config.log import logger

class UserConfig(object):

    def __init__(self):
        log = logger("User log")
        config_name = '.{}'.format('manager')
        commandrc = join(expanduser('~'), config_name)
        if exists(commandrc):
            with open(commandrc, 'r') as commandrc_file:
                self.manager = yaml.load(commandrc_file) or {}
        if not self.manager:
            log.error(
                "Missing file .manager, please authentication Who you are?")
            return
