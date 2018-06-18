# -*- coding: utf-8 -*-

from random import choice
import string
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

    def create_db(self, php, proj_name, host='127.0.0.1'):
        log = logger('create database')

        if proj_name:
            db_user = db_name = proj_name
        log.info('Generate password')
        passwd = self.generate_passwd()
        log.info('Update file config connect between PHP and MySQL')
        cmd = ['sed', '-i', "\"s/\$host =/\$host = \'{}\'\;/g;"
                              "s/\$user =/\$user = \'{}\'\;/g;"
                              "s/\$pass =/\$pass = \'{}\'\;/g;"
                              "s/\$db =/\$db = \'{}\'\;/g\"".format(host, db_user,
                                                    passwd, db_name), php]
        self.execute(cmd)
        log.info('Create user database')
        self.create_user(db_user, host, passwd)
        log.info('Create database {}'.format(db_name))
        cmd = [
            'mysqladmin',
            'create', db_name
        ]
        self.execute(cmd)
        log.info('Set grant all on database for user')
        self.grant_user(db_user, host, db_name)
        dir_input = '/opt/web/{}/db/'.format(proj_name)
        if self.check_remote_file(dir_input):
            cmd = [
                'find', dir_input,
                '-name', '*.sql'
            ]
            list_db = self.execute(cmd)
            log.info('Restore data to database')
            for db in list_db.split('\n'):
                if db:
                    cmd = [
                        'mysql', '--database',
                        db_name, '<', db.decode('UTF-8')
                    ]
                    self.execute(cmd)

    def create_user(self,user, host, passwd):
        log = logger('create user')

        query = "CREATE USER \'{}\'@\'{}\' " \
                "IDENTIFIED BY \'{}\';".format(user, host, passwd)
        log.debug("Create user database \n {}".format(query))
        cmd = [
            'mysql',
            '--execute=\"%s\"'% query
        ]
        self.execute(cmd)

    def grant_user(self, user, host, db_name):
        log = logger('grant user')
        query = "GRANT ALL ON {}.* TO '{}'@'{}'".format(db_name, user, host)
        log.debug('Set grant all on database for user \n{}'.format(query))
        cmd = [
            'mysql',
            '--execute=\'%s\'' % query
        ]
        self.execute(cmd)

    def generate_passwd(self):
        alphabet = string.ascii_letters + string.digits
        passwd = ''.join(choice(alphabet) for _ in range(12))
        return passwd