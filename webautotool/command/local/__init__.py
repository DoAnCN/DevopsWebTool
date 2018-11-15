# -*- coding:utf-8 -*-

import click
import os
from os.path import dirname, isdir
import sh
from sh import ErrorReturnCode
import requests

from webautotool.command import webautotool as cli
from webautotool.config.log import logger
from webautotool.config.user import UserConfig
from webautotool.command.local.monitor import Monitor


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
    """Build project on local"""
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

@web.command()
@click.option('--ip', '-i', help='Agent\'s ip address')
@click.option('--url', '-u', default='http://127.0.0.1:55000',
              help='Manager\'s url')
@click.argument('agent_name')
@click.pass_context
def register(ctx, ip, url, agent_name):
    """Create trust relationship between Wazuh manager and agents."""
    log = logger('Register agents')
    user = UserConfig()
    token = user.getToken()
    if token:
        urlEmoi = user.manager['manager']['url']
        head = {'Authorization': 'JWT {}'.format(token)}
        resource = '/api/instances/{0}'.format(agent_name)
        res = requests.get('{0}/{1}'.format(urlEmoi, resource), headers=head)
        if res.status_code == 404:
            log.error(
                'Hostname {0} not found on Emoi'.format(agent_name))
            return
        elif res.status_code == 200:
            host = res.json()
            if not ip:
                ip = host['ip']
            else:
                if host['ip'] != '':
                    data_update = {'ip': ip}
                    resource = '/api/instances/{0}'.format(agent_name)
                    res = requests.put('{0}/{1}'.format(urlEmoi, resource),
                                       headers=head, data=data_update)
                    if res.status_code == 200:
                        log.info('Update succeeded')
                    else:
                        log.error('Something wrong '
                                  'when you update host\'s ip address')
        monitor = Monitor(url)
        log.info('Adding agent {0} to manager'.format(agent_name))
        agent_id, agent_key = monitor.add_agent(agent_name, ip)
        log.info('Agent {0} had id {1}'.format(agent_name, agent_id))
        log.info('Importing agent key')
        monitor.import_key(agent_key)
        log.info('Restarting ossec')
        monitor.restart_ossec()