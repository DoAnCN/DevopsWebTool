# -*- coding:utf-8 -*-

import os
import json
import time
import requests
from requests.auth import HTTPBasicAuth

from subprocess import PIPE, Popen
from webautotool.config.log import logger

class Monitor(object):

    def __init__(self, manager_url, server, verify=False):
        self.auth = HTTPBasicAuth('titi', 'tutu')  # default username and password
        self.base_url = manager_url
        self.verify = verify  # Use with self-signed certificates.
        self.server = server

    def add_agent(self, agent_name, agent_ip=None):
        # Thực hiện thêm agent trên manager thông qua API của manager
        log=logger("Add agent")
        if agent_ip:
            data_create = {'name': agent_name, 'ip': agent_ip}
            res = requests.post('{0}/{1}'.format(self.base_url, 'agents'),
                                data=data_create, auth=self.auth)
        else:
            data_create = {'name': agent_name}
            res = requests.post('{0}/{1}'.format(self.base_url, 'agents'),
                               data=data_create, auth=self.auth)

        if res.status_code == 200:
            agent_info = res.json()
            if agent_info['error'] == 0:
                agent_id = agent_info['data']['id']
                agent_key = agent_info['data']['key']
                return agent_id, agent_key
            else:
                log.error(agent_info['message'])
                exit()
        else:
            # msg = json.dumps(res, indent=4, sort_keys=True)
            code = "Status: {0} - {1}".format(
                res.status_code,requests.status_codes._codes[res.status_code])
            log.error("ERROR - ADD AGENT:\n{0}\n".format(code))
            exit()

    def execute(self, cmd_list, stdin=None):
        # Thực hiện lệnh trên chính server manager
        """Execute command on local host"""
        p = Popen(cmd_list, stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
        std_out, std_err = p.communicate(b'"{}".format(stdin)')
        return_code = p.returncode
        return std_out, std_err, return_code

    def import_agent(self, agent_key):
        # Import agent key được remote thực hiện từ server manager đến server agent
        log = logger('Import agent')
        cmd = ['yes', '|',
                '/var/ossec/bin/manage_agents',
                '-i', '\'{0}\''.format(agent_key)]
        i = self.server.execute(cmd)
        if 'Added' in i:
            log.info('Imported agent key')

    def restart_ossec(self):
        # Restart trình điều khiển của agent sau khi import key
        log = logger('Restart ossec')
        cmd = ["/var/ossec/bin/ossec-control", "restart"]
        self.server.execute(cmd)

    def get_status(self, agent_name):
        # Lấy các thông tin agent sau khi đăng ký
        log = logger('Get status agent')
        pending_count = 0
        if agent_name:
            res = requests.get(
                '{0}/{1}/{2}'.format(self.base_url, 'agents/name', agent_name),
                auth=self.auth )
            if res.status_code == 200:
                last_alive = None
                monitor = 'n'
                agent_info =  res.json()
                if agent_info['error'] == 0:
                    if 'Active' in agent_info['data']['status']:
                        monitor = 'a'
                    elif 'Pending' in agent_info['data']['status']:
                        # Thực hiện lại get_status sau 3 lần pending,
                        # nếu sau 3 lần (mỗi lần 5s) agent vẫn ở trạng thái pending
                        # thì update status trên wabmanager is_agents=False
                        if pending_count < 3:
                            time.sleep(5)
                            pending_count += 1
                            return self.get_status(agent_name)
                        monitor = 'p'
                        last_alive = agent_info['data']['lastKeepAlive']

                    if monitor == 'a':
                        return {
                            'monitor': monitor,
                            'date_add': agent_info['data']['dateAdd'],
                            'last_alive': agent_info['data']['lastKeepAlive'],
                            'os': agent_info['data']['os']['platform'] + ' ' +\
                                 agent_info['data']['os']['version'],
                        }
                    else:
                        return {
                            'monitor': monitor,
                            'date_add': agent_info['data']['dateAdd'],
                            'last_alive': last_alive,
                        }
                else:
                    log.error(agent_info['message'])
            else:
                # msg = json.dumps(res, indent=4, sort_keys=True)
                code = "Status: {0} - {1}".format(
                    res.status_code, requests.status_codes._codes[
                                                            res.status_code])
                log.error("ERROR - ADD AGENT:\n{0}\n".format(code))
                exit()
