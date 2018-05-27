# -*- coding:utf-8 -*-

import click
import os.path
import sh

from webautotool.command import webautotool as cli
from webautotool.config.log import logger

@cli.group()
@click.pass_context
def db(ctx, *args, **kw):
    """
    Utils commands
    """
    if ctx.invoked_subcommand is None:
        ctx.invoke(create, *args, **kw)

@db.command ()
@click.option('--name', '-n', default='Default', help='Database name')
@click.option('--password', prompt=True, hide_input=True,
              confirmation_prompt=True)
@click.option('--user', '-u', help='Database user')
@click.pass_context
def create(ctx, name, password, user):
    _create(name)

def _create(name):
    log = logger('create database')
    if not os.path.isfile('~/.my.conf'):
        log.error('Missing configuration file of mysql')
        return
    # cmd = ['mysql', '-e', '\"CREATE DATABASE {} '
    #            'DEFAULT CHARACTER SET utf8 '
    #            'COLLATE utf8_unicode_ci;\"'.format(name)]
    sh.Command('mysql', '-e', '\"CREATE DATABASE {} '
               'DEFAULT CHARACTER SET utf8 '
               'COLLATE utf8_unicode_ci;\"'.format(name))
