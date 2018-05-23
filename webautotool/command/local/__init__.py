# -*- coding:utf-8 -*-

import click
import sh
from webautotool.commmand import webautotool as cli
from webautotool.config.log import logger

@cli.group()
@click.pass_context
def web(ctx, *args, **kw):
    """
    Command use on local
    """
    if ctx.invoked_subcommand is None:
        ctx.invoke(start, *args, **kw)

@web.command
@click.argument('url')
@click.option
@click.pass_context
def start(url):
    log = logger("start")
    log.info("Checking url")
    sh.git('ls-remote', url)
    