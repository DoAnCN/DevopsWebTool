# -*- coding:utf-8 -*-

import click
import requests
import time
from datetime import datetime

from webautotool.config.log import logger
from webautotool.config.user import UserConfig
from webautotool.command import webautotool as cli
from webautotool.command.remote.server import Server
from webautotool.command.remote.deploy_cmd import deploy_cmd
from webautotool.command.remote.monitor import Monitor


@cli.group()
@click.pass_context
def remote(ctx, *args, **kw):
    """Remote to server"""
    if ctx.invoked_subcommand is None:
        ctx.invoke(deploy, *args, **kw)

@remote.command()
@click.option('--ip', '-i', help='Ip address of server')
@click.option('--port', '-p', default='22',
              help='Port number ssh')
@click.option('--clone/--no-clone', '-c', is_flag=True, default=False,
              help = 'Just execute clone project from github if clone=True')
@click.option('--url', '-u', help='Repository url that can use to clone'
                                  ' the project')
@click.option('--project_name', '-P', help='Name of project')
@click.option('--db_name', '-d', help='Name of database')
@click.option('--project_ver', '-v', help='Project\'s version')
@click.option('--type', '-t', help='Instance\'s type' )
@click.argument('instance_name')
@click.argument('user_name')
@click.pass_context
def deploy(ctx, ip, port, instance_name, url, project_name, db_name,
           project_ver, type, clone, user_name):
    """Deploy new project or just update source code"""
    log = logger('Deploy log')

    user = UserConfig()
    token = user.getToken(user_name)
    instance = {}
    urlWebManager = user.manager['url']
    if token:
        head = {'Authorization': 'JWT {}'.format(token)}
        resource = 'api/instances/{0}'.format(instance_name)
        res = requests.get('{0}/{1}'.format(urlWebManager, resource), headers=head)

        if res.status_code == 404:
            log.error('Instance {0} not found on WebManager'.format(instance_name))
            return
        elif res.status_code == 200:
            instance = res.json()
    else:
        if ip and port and url and project_ver:
            instance = {'name': instance_name,
                        'project': {'name': project_name or
                                            instance_name.split('_')[0],
                                    'url': url},
                        'db_name': db_name or instance_name,
                        'project_ver' : {"version": project_ver},
                        'type': type or instance_name.split('_')[-1][0],}
            host = {'ip': ip, 'port': port}
        else:
            log.error('Not enough information to execute command')
            exit()
    try:
        srv = Server(instance['host'] if 'host' in instance else host)
        deploy_cmd(srv, instance, clone)

        if token:
            data_update = {
                'usr_deployed': user_name,
                'latest_deploy': datetime.now()
            }
            head = {'Authorization': 'JWT {}'.format(token)}
            resource = 'api/instances/{0}'.format(instance_name)
            res = requests.put('{0}/{1}'.format(urlWebManager, resource),
                               headers=head, data=data_update)
            if res.status_code == 200:
                log.info('The deployment process has been completed')
            else:
                log.warning('Cannot update user deployed instance {0} '
                            'or deployment time'.format(instance_name))
    except OSError as err:
        log.error(err)

@remote.command()
@click.option('--ip', '-i', help='Agent\'s ip address')
@click.option('--port', '-p', help='Agent\'s ssh port', default=22)
@click.option('--url', '-u', default='http://127.0.0.1:55000',
              help='Wazuh manager\'s url')
@click.argument('agent_name')
@click.argument('user_name')
@click.pass_context
def register(ctx, ip, port, url, user_name, agent_name):
    """Create trust relationship between Wazuh manager and agents."""
    log = logger('Register agents')
    user = UserConfig()
    token = user.getToken(user_name)
    urlWebManager = user.manager['url']
    if token:
        head = {'Authorization': 'JWT {}'.format(token)}
        resource = 'api/hosts/{0}'.format(agent_name)
        res = requests.get('{0}/{1}'.format(urlWebManager, resource), headers=head)
        if res.status_code == 404:
            log.error(
                'Hostname {0} not found on WebManager'.format(agent_name))
            return
        elif res.status_code == 200:
            host = res.json()
            if not ip:
                ip = host['ip']
            else:
                if host['ip'] != '':
                    data_update = {'ip': ip}
                    resource = 'api/hosts/{0}'.format(agent_name)
                    res = requests.put('{0}/{1}'.format(urlWebManager, resource),
                                       headers=head, data=data_update)
                    if res.status_code == 200:
                        log.info('Update succeeded')
                    else:
                        log.error('Something wrong '
                                  'when you update host\'s ip address')
    else:
        if ip and port:
            host = {'ip': ip, 'port': port}
        else:
            log.error('Not enough information to execute command')
            exit()
    try:
        srv = Server(host, userhost="root")
        monitor = Monitor(manager_url=url, server=srv)

        log.info('Adding agent {0} to manager'.format(agent_name))
        agent_id, agent_key = monitor.add_agent(agent_name, ip)

        log.info('Agent {0} had id {1}'.format(agent_name, agent_id))
        log.info('Importing agent key')
        monitor.import_agent(agent_key)

        log.info('Restarting ossec')
        monitor.restart_ossec()

        time.sleep(5) # Đợi 5s cho quá trình restart trình điều khiển của agent hoàn tất

        if token:
            head = {'Authorization': 'JWT {}'.format(token)}
            log.info('Update infomations')
            data_update = monitor.get_status(agent_name)
            resource = 'api/hosts/{0}'.format(agent_name)
            res = requests.put('{0}/{1}'.format(urlWebManager, resource),
                               headers=head, data=data_update)
            if res.status_code == 200:
                log.info(
                    'The register agent process has been completed')
            else:
                log.warning(
                    'Cannot update information about {0} host \n {1}'.format(
                        agent_name, res))
    except OSError as err:
        log.error(err)

@remote.command()
@click.option('--name', '-n', help='Database name')
@click.option('--type', '-t', help='Type of instance', default='i')
@click.option('--ip', '-i', help='Ip address of server')
@click.option('--port', '-p', default='22',
              help='Port number ssh')
@click.option('--createuser/--no-createuser', is_flag=True, default=False,
              help = 'Accept to create new user manage database')
@click.argument('instance_name')
@click.argument('user_name')
@click.pass_context
def createDB(ctx, name, type, ip, port, createuser, instance_name, user_name):
    """Create empty database for instance"""
    log = logger('Create empty database log')
    print(createDB)
    user = UserConfig()
    token = user.getToken(user_name)
    instance = {}
    if token:
        head = {'Authorization': 'JWT {}'.format(token)}
        urlWebManager = user.manager['url']
        resource = 'api/instances/{0}'.format(instance_name)
        res = requests.get('{0}/{1}'.format(urlWebManager, resource), headers=head)

        if res.status_code == 404:
            log.error('Instance {0} not found on WebManager'.format(instance_name))
            return
        elif res.status_code == 200:
            instance = res.json()
    else:
        if ip and port:
            instance = {'name': instance_name,
                        'db_name': name or instance_name,
                        'type': type or instance_name.split('_')[-1][0], }
            host = {'ip': ip, 'port': port}
        else:
            log.error('Not enough information to execute command')
            exit()
    try:
        srv = Server(instance['host'] if 'host' in instance else host)
        dest_dir = '/opt/web/{}'.format(instance_name)
        srv.create_db(dest_dir, instance['db_name'], instance_name,
                      instance['type'], createuser)
        log.info(
            'Create new database has been completed')
    except OSError as err:
        log.error(err)

@remote.command()
@click.option('--name', '-n', help='Database name')
@click.option('--ip', '-i', help='Ip address of server')
@click.option('--port', '-p', default='22',
              help='Port number ssh')
@click.argument('instance_name')
@click.argument('user_name')
@click.pass_context
def importDB(ctx, name, ip, port, instance_name, user_name):
    """Create empty database for instance"""
    log = logger('Create empty database log')

    user = UserConfig()
    token = user.getToken(user_name)
    instance = {}
    if token:
        head = {'Authorization': 'JWT {}'.format(token)}
        urlWebManager = user.manager['url']
        resource = 'api/instances/{0}'.format(instance_name)
        res = requests.get('{0}/{1}'.format(urlWebManager, resource), headers=head)

        if res.status_code == 404:
            log.error('Instance {0} not found on WebManager'.format(instance_name))
            return
        elif res.status_code == 200:
            instance = res.json()
    else:
        if ip and port:
            instance = {'name': instance_name,
                        'db_name': name or instance_name,}
            host = {'ip': ip, 'port': port}
        else:
            log.error('Not enough information to execute command')
            exit()
    try:
        srv = Server(instance['host'] if 'host' in instance else host)
        dest_dir = '/opt/web/{}'.format(instance_name)
        srv.import_db(dest_dir, instance['db_name'], follow=False)
        log.info(
            'Import database has been completed')
    except OSError as err:
        log.error(err)
