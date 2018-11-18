# -*- coding:utf-8 -*-

import click
import requests
from datetime import datetime

from webautotool.config.log import logger
from webautotool.config.user import UserConfig
from webautotool.command import webautotool as cli
from webautotool.command.remote.server import Server
from webautotool.command.remote.deploy_cmd import deploy_cmd


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
            s = Server(instance['host'])
            try:
                deploy_cmd(s, instance, '1.0')
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
