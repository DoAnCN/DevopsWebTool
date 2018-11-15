# -*- coding:utf-8 -*-

import os
import json
import requests
from requests.auth import HTTPBasicAuth

from subprocess import PIPE, Popen
from webautotool.config.log import logger

class Monitor(object):

    def __init__(self, base_url, verify=False):
        self.auth = HTTPBasicAuth('foo', 'bar')  # default username and password
        self.base_url = base_url
        self.verify = verify  # Use with self-signed certificates.

    def add_agent(self, agent_name, agent_ip=None):
        log=logger("Add agent")
        if agent_ip:
            data_create = {'name': agent_name, 'ip': agent_ip}
            res = requests.post('{0}/{1}'.format(self.base_url, 'agents'),
                                data=data_create)
        else:
            data_create = {'name': agent_name}
            res = requests.post('{0}/{1}'.format(self.base_url, 'agents'),
                               data=data_create)

        if res.status_code == 200 and res.response['error'] == 0:
            r_id = res['data']['id']
            r_key = res['data']['key']
            return r_id, r_key
        else:
            msg = json.dumps(res, indent=4, sort_keys=True)
            code = "Status: {0} - {1}".format(
                res.status_code,requests.status_codes._codes[res.status_code])
            log.error("ERROR - ADD AGENT:\n{0}\n{1}".format(code, msg))
            exit()

    def execute(self, cmd_list, stdin=None):
        """Execute command on local host"""
        p = Popen(cmd_list, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        std_out, std_err = p.communicate(stdin)
        return_code = p.returncode
        return std_out, std_err, return_code

    def import_agent(self, agent_key):
        log = logger('Import agent')
        cmd = "/var/ossec/bin/manage_agents"
        std_out, std_err, r_code = self.execute([cmd, "-i", agent_key], "y\n\n")
        if r_code != 0:
            log.error("ERROR - IMPORT KEY:{0}".format(std_err))
            exit()

    def restart_ossec(self):
        log = logger('Restart ossec')
        cmd = "/var/ossec/bin/ossec-control"
        std_out, std_err, r_code = self.execute([cmd, "restart"])
        restarted = False

        for line_output in std_out.split(os.linesep):
            if "Completed." in line_output:
                restarted = True
                break

        if not restarted:
            log.error("ERROR - RESTARTING OSSEC:{0}".format(std_err))
            exit()
