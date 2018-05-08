# -*- coding:utf-8 -*-

import click
from webautotool.commmand import webautotool as cli

@cli.command
@click.argument('url')
@click.pass_context
def start(url):
    print("")