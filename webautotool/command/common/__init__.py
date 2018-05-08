# -*- coding:utf-8 -*-

import click
import os

from DevopsWebTool.webautotool.command import webautotool as cli

@cli.group()
@click.pass_context
def common(ctx, *args, **kw):
    """
    Utils commands
    """
    if ctx.invoked_subcommand is None:
        ctx.invoke(auto_update, *args, **kw)

@common.command()
@click.pass_context
def auto_update(ctx):
    """
    Auto update webautotool
    """
    pack = 'git+ssh://git@github.com/DoAnCN/DevopsWebTool.git@1.0#egg=DevopsWebTool'
    os.system('pip install -U -e {}'.format(pack))
