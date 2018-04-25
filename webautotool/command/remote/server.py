# -*- coding: utf-8 -*-

import logging
from sh import ssh, ErrorReturnCode, ErrorReturnCode_1
import re


class Server(object):

    def __init__(self, host, timeout=60):
        self.user = host["user"]
        self.address = host["address"]
        self.port = host["port"]
        host_ssh = '%s@%s' % (self.user, self.address)
        self.ssh = ssh.bake( host_ssh, '-p', self.port, '-A',
                            '-o', 'UserKnownHostsFile=/dev/null',
                            '-o', 'StrictHostKeyChecking=no',
                            '-o', 'BatchMode=yes',
                            '-o', 'PasswordAuthentication=no',
                            '-o', 'ConnectTimeout=%s' % timeout)

    def execute(self, *cmd, follow=False):

        result = self.ssh(*cmd, _iter=True, _err_to_out=False)

        if not follow and result.stderr:
            '''
            Don't do this with follow, or it will stop output until the
            command is fully executed.
            '''
            logging.debug(result.stderr)
        return result

    def check_remote_file(self, filepath):
        try:
            self.execute(['test', '-e', filepath])
            exists = True
        except ErrorReturnCode_1:
            exists = False
        return exists

    def git_clone(self, url, dest_dir):
        logging.info("Clonning project from github")
        cmd = [
            'git clone', '--progress', url, dest_dir
        ]
        self.execute(cmd)

    def create_db(self, php):
        cmd = [
            'cat', php
        ]
        php_content = self.execute(cmd)
        reg = r'\$(?P<variable>\w+)\s*=\s*"?\'?(?P<value>[^"\';]+)"?\'?;'
        rg = re.compile(reg, re.IGNORECASE | re.DOTALL)
        arg = rg.findall(php_content.stdout.decode('utf-8'))
        for var, val in arg:
            if var == 'pass':
                passwd = val
            if var == 'db':
                db_name = val
            if var == 'user':
                db_user = val
            if var == 'host':
                host = val
        self.create_user(db_user, host, passwd)
        self.grant_user(db_user, host, db_name)
        cmd = [
            'mysqladmin',
            'create', db_name
        ]
        self.execute(cmd)
        cmd = [
            'mysql',
            db_name, '<', '/opt/web/web-HOANGLAMMOC/db/son.sql'
        ]
        self.execute(cmd)
        
    def create_user(self,user, host, passwd):
        query = "CREATE USER \'{}\'@\'{}\' " \
                "IDENTIFIED BY \'{}\';".format(user, host, passwd)
        print(query)
        cmd = [
            'mysql',
            '--execute=\"%s\"'% query
        ]
        self.execute(cmd)

    def grant_user(self, user, host, db_name):
        query = "GRANT ALL ON {}.* TO '{}'@'{}'".format(db_name, user, host)
        print (query)
        cmd = [
            'mysql',
            '--execute=\'%s\'' % query
        ]
        self.execute(cmd)