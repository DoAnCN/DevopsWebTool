# -*- coding:utf-8 -*-

import click
import os
from os.path import dirname, isdir
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
    if name:
        gc(name, _bg=True)
    else:
        gc()

    _set_info_for_php(name or url.split("/")[1].replace(".git",""))

    

def _set_info_for_php(proj_name, host='127.0.0.1'):
    log=logger('set info')
    dir = os.getcwd()+ '/' + proj_name

    if not isdir(dir):
        log.error('Can not find project')
    # while dir.split('/')[-1] != proj_name:
    #     dir = dirname(dir)
    #     if dir == '/' or dir == None:
    #         log.error('Can not find project')
    #         return

    dir += '/lib/db.php'
    with open(dir) as f:
        content = f.readlines()

    for i in range(len(content)):
        if '$host =' in content[i]:
            content[i] = '\t$host = \'{}\';\n'.format(host)
        if '$user =' in content[i]:
            content[i] = '\t$user = \'{}\';\n'.format(proj_name)
        if '$pass =' in content[i]:
            content[i] = '\t$pass = \'{}\';\n'.format(proj_name)
        if '$db =' in content[i]:
            content[i] = '\t$db = \'{}\';\n'.format(proj_name)

    with open(dir, "w") as f:
        f.writelines(content)