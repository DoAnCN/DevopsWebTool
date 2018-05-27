# -*- coding:utf-8 -*-

import click
import sh
from sh import ErrorReturnCode
from webautotool.command import webautotool as cli
from webautotool.config.log import logger

@cli.group()
@click.pass_context
def web(ctx, *args, **kw):
    """
    Command use on local
    """
    if ctx.invoked_subcommand is None:
        ctx.invoke(start, *args, **kw)

@web.command()
@click.argument('url')
@click.option('--version', '-v', default='master', help='Version of project')
@click.option('--name', '-n', help='Set name for project when clone to local - '
                                   'Default name is the name on github/gitlab')
@click.pass_context
def start(ctx, url, version, name):
    log = logger("start")
    log.info("Checking url")

    try:
        sh.git('ls-remote', url)
    except ErrorReturnCode as e:
        if "not found" in str(e):
            log.error("Repository not found")
            return

    gc = sh.git.bake('clone', url, '-b', version)
    print ("==============", gc)
    if name:
        gc(name, _bg=True)
    else:
        gc()
