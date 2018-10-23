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
    """
    Remote to server
    """
    if ctx.invoked_subcommand is None:
        ctx.invoke(deploy, *args, **kw)

@remote.command()
# @click.option('--user', '-u', default='ubuntu',
#               help='User name of server')
# @click.option('--address', '-a', default='127.0.0.1',
#               help='Ip address of server')
# @click.option('--instance-name', '-p', default='22',
#               help='Port number ssh')
# @click.option('--clone/--no-clone', '-c', is_flag=True, default=False,
#               help = "Accept clone source code from github")
@click.argument('instance_name')
@click.pass_context
def deploy(ctx, instance_name):

    log = logger('Deploy log')
    user = UserConfig()
    url = user.manager['manager']['url']

    api_get = '{0}/api/instances/{1}'.format(url, instance_name)
    response = requests.get(api_get)
    if requests.codes.ok:
        instance = response.json()
    if not instance['success']:
        log.error("Instance {0} not found on manager".format(instance_name))
        return
    s = Server(instance['data']['id_host'])
    try:
        deploy_cmd(s, instance, '1.0')
    except:
        raise

    api_put = '{}/api/instances/update'.format(url)
    data = {"id": "{0}".format(instance['data']['id']),
            "user": "{0}".format(s.user.manager['manager']['name']),
            "time" : "{0}".format(datetime.now()),
            "status": "RUNNING"}
    response = requests.put(api_put, data)
    if response.status_code == 200:
        log.info("Deploy done")
    else:
        log.info("Can not update into manager")
