# -*- coding: utf-8 -*-

from logging import log
from sh import ssh, ErrorReturnCode
import re


class Server(object):

    def __init__(self, host, timeout=60):
        print ("------------", host)
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

    def execute(self, *cmd):
        result = self.ssh(*cmd, _iter=False, _err_to_out=False)
        return result

    def check_remote_file(self, filepath):
        try:
            self.execute(['test', '-e', filepath])
            exists = True
        except ErrorReturnCode:
            exists = False
        return exists

    def git_clone(self, url, dest_dir):
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
        cmd = [
            'mysqladmin',
            '-u', 'root',
            '--password=1',
            'create', db_name
        ]
        self.execute(cmd)
        self.grant_user(db_user, host, db_name)
        cmd = [
            'mysql',
            '-u', 'root',
            '--password=1',
            db_name, '<', '/opt/web/web-HOANGLAMMOC/db/son.sql'
        ]
        self.execute(cmd)
        
    def create_user(self,user, host, passwd):
        query = "CREATE USER \'{}\'@\'{}\' " \
                "IDENTIFIED BY \'{}\';".format(user, host, passwd)
        print(query)
        cmd = [
            'mysql',
            '-u', 'root',
            '--password=1',
            '--execute=\"%s\"'% query
        ]
        self.execute(cmd)

    def grant_user(self, user, host, db_name):
        query = "GRANT ALL ON {}.* TO '{}'@'{}'".format(db_name, user, host)
        print (query)
        cmd = [
            'mysql',
            '-u', 'root',
            '--password=1',
            '--execute=\'%s\'' % query
        ]
        self.execute(cmd)