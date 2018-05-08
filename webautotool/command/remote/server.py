# -*- coding: utf-8 -*-

import re
from sh import ssh, ErrorReturnCode_1

from webautotool.config.log import logger

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

    def execute(self, cmd, follow=False, print_follow=False):

        """
        Execute a command on the remote host
        follow allow to read stdout as an iterator
        """
        log = logger('execute command sh')
        if print_follow:
            result = self.ssh(*cmd, _iter=True, _err_to_out=follow)
            for line in result:
                print(line.strip())
        else:
            result = self.ssh(*cmd, _iter=False, _err_to_out=follow)
        # Pipe error output to stdout when following
        if not follow and result.stderr:
            '''
            Don't do this with follow, or it will stop output until the
            command is fully executed.
            '''
            log.debug(result.stderr)

        return result

    def check_remote_file(self, filepath):
        try:
            self.execute(['test', '-e', filepath])
            exists = True
        except ErrorReturnCode_1:
            exists = False
        return exists

    def git_clone(self, url, dest_dir, version='1.0'):
        log = logger('git clone')

        log.info("Clonning project from github")
        cmd = [
            'git clone',
            '--progress',
            url, dest_dir,
            '--branch', version
        ]
        self.execute(cmd)

    def git_pull(self, version='1.0', proj_path=None):
        log = logger('git pull')
        if not self.check_remote_file(proj_path):
            log.ERROR("Don't found directory of project")
            return
        log.info("Pulling project...")
        cmd = [
            'git',
            '-C',
            proj_path,
            'pull', 'origin',
            version
        ]
        self.execute(cmd)

    def create_db(self, php):
        log = logger('create database')
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
        log.info('Create database {}'.format(db_name))
        cmd = [
            'mysqladmin',
            'create', db_name
        ]
        self.execute(cmd)
        if self.check_remote_file('/opt/web/web-HOANGLAMMOC/db/son.sql'):
            log.info('Input already data to database')
            cmd = [
                'mysql',
                db_name, '<', '/opt/web/web-HOANGLAMMOC/db/son.sql'
            ]
            self.execute(cmd)
        
    def create_user(self,user, host, passwd):
        log = logger('create user')

        query = "CREATE USER \'{}\'@\'{}\' " \
                "IDENTIFIED BY \'{}\';".format(user, host, passwd)
        log.info("Create user database")
        cmd = [
            'mysql',
            '--execute=\"%s\"'% query
        ]
        self.execute(cmd)

    def grant_user(self, user, host, db_name):
        log = logger('grant user')
        log.info('Set grant all on database for user')
        query = "GRANT ALL ON {}.* TO '{}'@'{}'".format(db_name, user, host)
        print (query)
        cmd = [
            'mysql',
            '--execute=\'%s\'' % query
        ]
        self.execute(cmd)