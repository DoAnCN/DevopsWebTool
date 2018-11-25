# -*- coding: utf-8 -*-

import string
from random import choice
from sh import ssh, ErrorReturnCode_1

from webautotool.config.log import logger
# from webautotool.config.user import UserConfig


class Server(object):

    def __init__(self, host, userhost='web', timeout=60):
        log = logger("Server configuration ")
        # self.user =  UserConfig()
        if host:
            log.info('Configurating host')
            host_ssh = '%s@%s' % (userhost, host['ip'])
            self.ssh = ssh.bake( host_ssh, '-p', host['port'] or '22', '-A',
                                '-o', 'UserKnownHostsFile=/dev/null',
                                '-o', 'StrictHostKeyChecking=no',
                                '-o', 'BatchMode=yes',
                                '-o', 'PasswordAuthentication=no',
                                '-o', 'ConnectTimeout=%s' % timeout)
        else:
            log.error('No host to deploy')
            exit(0)


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

    def check_remote_file(self, filepath, follow=False):
        try:
            self.execute(['test', '-e', filepath], follow)
            exists = True
        except ErrorReturnCode_1:
            exists = False
        return exists

    def git_clone(self, url, dest_dir, version='1.0', follow=False):
        log = logger('git clone')

        log.info("Clonning project from github")
        cmd = [
            'git clone',
            '--progress',
            url, dest_dir,
            '--branch', version
        ]
        self.execute(cmd, follow)

    def git_pull(self, version='1.0', inst_path=None, follow=False):
        log = logger('git pull')
        if not self.check_remote_file(inst_path):
            log.ERROR("Don't found directory of project")
            return
        log.info("Pulling project...")
        cmd = [
            'git',
            '-C',
            inst_path,
            'pull', 'origin',
            version
        ]
        self.execute(cmd, follow)

    def create_db(self, proj_dir, db_name, instance_name, inst_type='i',
                  host='localhost', follow=False):
        config_php = proj_dir + "/lib/db.php"

        log = logger('create database')
        db_user = db_name

        log.info('Generate password')
        if inst_type == 'i':
            passwd = 'abc123ABC!!!'
        elif inst_type == 's':
            passwd = 'abc123ABC!@#'
        else:
            passwd = self.generate_passwd()

        log.info('Update file config connect between PHP and MySQL')
        cmd = ['sed', '-i',
               "\"s/\$host =/\$host = \'{0}\'\;/g;"
               "s/\$user =/\$user = \'{1}\'\;/g;"
               "s/\$pass =/\$pass = \'{2}\'\;/g;"
               "s/\$db =/\$db = \'{3}\'\;/g\"".format(host, db_user, passwd,
                                                      db_name),
               config_php]
        self.execute(cmd, follow)

        log.info('Create user database')
        self.create_user(db_user, host, passwd)

        log.info('Create database {}'.format(db_name))
        cmd = [
            'mysqladmin',
            'create', db_name
        ]
        self.execute(cmd, follow)

        log.info('Set grant all on database for user')
        self.grant_user(db_user, host, db_name)

        dir_input_db = '/opt/web/{0}/db/'.format(instance_name)
        log.info('Prepare database for importing')
        if inst_type != 'i':
            self.import_db(dir_input_db, db_name)

    def import_db(self, dir, db_name, follow=False):
        log = logger('Import database')
        if self.check_remote_file(dir):
            cmd = [
                'find', dir,
                '-name', '*.sql'
            ]
            list_db = self.execute(cmd, follow)
            log.info('Restore data to database')
            for db in list_db.split('\n'):
                if db:
                    cmd = [
                        'mysql', '--database',
                        db_name, '<', db
                    ]
                    self.execute(cmd, follow)

    def create_user(self,user, host, passwd, follow=False):
        log = logger('create user')

        query = "CREATE USER \'{}\'@\'{}\' " \
                "IDENTIFIED BY \'{}\';".format(user, host, passwd)
        log.debug("Create user database \n {}".format(query))
        cmd = [
            'mysql',
            '--execute=\"%s\"'% query
        ]
        self.execute(cmd, follow)

    def grant_user(self, user, host, db_name, follow=False):
        log = logger('grant user')
        query = "GRANT ALL ON {}.* TO '{}'@'{}'".format(db_name, user, host)
        log.debug('Set grant all on database for user \n{}'.format(query))
        cmd = [
            'mysql',
            '--execute=\'%s\'' % query
        ]
        self.execute(cmd, follow)

    def generate_passwd(self):
        alphabet = string.ascii_letters + string.digits
        passwd = ''.join(choice(alphabet) for _ in range(12))
        return passwd
