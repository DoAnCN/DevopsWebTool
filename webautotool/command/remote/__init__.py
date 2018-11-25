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
@click.option('--username', '-u', help='User name of system admin')
@click.option('--ip', '-i', default='127.0.0.1',
              help='Ip address of server')
@click.option('--port', '-p', default='22',
              help='Port number ssh')
@click.option('--clone/--no-clone', '-c', is_flag=True, default=False,
              help = 'Accept clone source code from github')
@click.argument('instance_name')
@click.pass_context
def deploy(ctx, username, ip, port, instance_name):
    """Deploy new project or just update source code"""
    log = logger('Deploy log')
    user = UserConfig()
    token = user.getToken()
    if token:
        head = {'Authorization': 'JWT {}'.format(token)}
        urlEmoi = user.manager['manager']['url']
        resource = 'api/instances/{0}'.format(instance_name)
        res = requests.get('{0}/{1}'.format(urlEmoi, resource), headers=head)

        if res.status_code == 404:
            log.error('Instance {0} not found on Emoi'.format(instance_name))
            return
        elif res.status_code == 200:
            instance = res.json()
            srv = Server(instance['host'])
            try:
                deploy_cmd(srv, instance, '1.0')
            except:
                raise

            data_update = {
                'usr_deployed': user.manager['manager']['username'],
                'latest_deploy': datetime.now()
            }

            resource = 'api/instances/{0}'.format(instance_name)
            res = requests.put('{0}/{1}'.format(urlEmoi, resource),
                               headers=head, data=data_update)
            if res.status_code == 200:
                log.info('The deployment process has been completed')
            else:
                log.warning('Cannot update user deployed instance {0} '
                            'or deployment time'.format(instance_name))

@remote.command()
@click.option('--ip', '-i', help='Agent\'s ip address')
@click.option('--url', '-u', default='http://127.0.0.1:55000',
              help='Wazuh manager\'s url')
@click.argument('agent_name')
@click.pass_context
def register(ctx, ip, url, agent_name):
    """Create trust relationship between Wazuh manager and agents."""
    log = logger('Register agents')
    user = UserConfig()
    token = user.getToken()
    if token:
        urlEmoi = user.manager['manager']['url']
        head = {'Authorization': 'JWT {}'.format(token)}
        resource = 'api/hosts/{0}'.format(agent_name)
        res = requests.get('{0}/{1}'.format(urlEmoi, resource), headers=head)
        if res.status_code == 404:
            log.error(
                'Hostname {0} not found on Emoi'.format(agent_name))
            return
        elif res.status_code == 200:
            host = res.json()
            if not ip:
                ip = host['ip']
            else:
                if host['ip'] != '':
                    data_update = {'ip': ip}
                    resource = 'api/hosts/{0}'.format(agent_name)
                    res = requests.put('{0}/{1}'.format(urlEmoi, resource),
                                       headers=head, data=data_update)
                    if res.status_code == 200:
                        log.info('Update succeeded')
                    else:
                        log.error('Something wrong '
                                  'when you update host\'s ip address')

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

        log.info('Update infomations')
        data_update = monitor.get_status(agent_name)
        resource = 'api/hosts/{0}'.format(agent_name)
        res = requests.put('{0}/{1}'.format(urlEmoi, resource),
                           headers=head, data=data_update)
        if res.status_code == 200:
            log.info(
                'The register agent process has been completed')
        else:
            log.warning(
                'Cannot update information about {0} host \n {1}'.format(
                    agent_name, res))
