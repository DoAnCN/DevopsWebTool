# -*- coding: utf-8 -*-

import yaml
import requests
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

    def getToken(self):
        log = logger('Get token')
        url = self.manager['manager']['url']

        api_auth = '{0}/api/auth/token/'.format(url)
        data_auth = {
            'username': self.manager['manager']['username'],
            'password': self.manager['manager']['passwd']
        }
        response = requests.post(api_auth, data=data_auth)
        if response.status_code == 400:
            content = response.json()
            if 'non_field_errors' in content:
                log.error(content['non_field_errors'][0])
                log.warning('Username/password incorrect')
            if 'username' in content and 'required' in content['username'][
                0] or \
                    'password' in content and 'required' in \
                    content['password'][0]:
                log.error('Missing username or password')
            return
        if response.status_code == 200:
            return response.json()['token']
