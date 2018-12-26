# -*- coding: utf-8 -*-

import base64
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
                commandrc_file = commandrc_file.read().split('\n')
                data = ''
                for contennt in commandrc_file:
                    data += base64.b64decode(contennt).decode()
                self.manager = yaml.load(data) or {}
        if not self.manager:
            log.error(
                "Missing file .manager, please authentication Who you are?")
            return

    def getToken(self, user_name):
        log = logger('Get token')
        url = self.manager['url']
        try:
            api_auth = '{0}/api/auth/token/'.format(url)
            data_auth = {
                'username': user_name,
                'password': self.manager['manager'][user_name] if user_name in self.manager['manager'] else log.error('You have no permission to execute command')
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
        except OSError as err:
            log.warning("Cannot access to web manager\n {0}".format(err))
            return None
