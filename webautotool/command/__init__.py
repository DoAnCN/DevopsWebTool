# -*- coding:utf-8 -*-

import click

@click.group()
@click.option('--quite', '-1',is_flag=True , default=False,
              help='Skipping log output')
@click.option('--light/--full', '-l', default=False,
              help='Light execution will skipping long process like '
                   'auto-update and env-update ')
@click.option('--auto-update/--no-auto-update', default=False,
              help='Update of webautotool')
@click.option('--env-update/--no-env-update', default=True,
              help='Update virtual enviroment')
@click.pass_context
def webautotool(ctx,quite, light, auto_update, env_update):

    if light:
        auto_update = False
        env_update = False
    ctx.command.name
    # ctx.invoked_subcommand
