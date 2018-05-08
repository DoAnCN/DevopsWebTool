# -*- coding:utf-8 -*-

import click
from DevopsWebTool.webautotool.config.log import logger
from DevopsWebTool.webautotool.command import webautotool as cli
from DevopsWebTool.webautotool.command.remote.server import Server
from DevopsWebTool.webautotool.command.remote.deploy_cmd import deploy_cmd

@cli.group()
@click.pass_context
def remote(ctx, *args, **kw):
    """
    Remote to server
    """
    if ctx.invoked_subcommand is None:
        ctx.invoke(deploy, *args, **kw)

@remote.command()
@click.option('--user', '-u', default='ubuntu',
              help='User name of server')
@click.option('--address', '-a', default='127.0.0.1',
              help='Ip address of server')
@click.option('--port', '-p', default='22',
              help='Port number ssh')
# @click.option('--clone/--no-clone', '-c', is_flag=True, default=False,
#               help = "Accept clone source code from github")
@click.argument('url')
@click.pass_context
def deploy(ctx, user, address, port, url):

    host = {
        'user': user,
        'address': address,
        'port': port,
    }
    s = Server(host)
    deploy_cmd(s, url, '1.0')

