# -*- coding:utf-8 -*-

import click
import os
from os.path import isfile
import subprocess

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
@click.argument('database')
@click.option('--password', prompt=True, hide_input=True,
              confirmation_prompt=True,
              help="Password for database")
@click.option('--user', '-u',
              help='Database use (Use the username same name of the project)')
@click.pass_context
def create(ctx, name, password, user):
    '''Create empty database'''
    log = logger('Create database')
    if not isfile('/opt/web/.my.cnf'):
        log.error('Missing configuration file of mysql')
        return
    # Đợi khi có website sẽ thay thông tin project trên web
    if not user:
        user = 'project_name'
    _create_user(user, password)
    if not name:
        name =  'project_name'
    _create_db(name, user)

@db.command()
@click.option('--path', '-p', help='Path of sql file')
@click.argument('database')
@click.pass_context
def restore(ctx, path, database):
    '''Restore database from file .sql'''
    log = logger('restore database')
    # Đợi khi có website sẽ thay thông tin project trên web
    if not path:
        os.mkdir('/opt/web/db_bk/{}'.format('project_name'))
        path = '/opt/web/db_bk/{}/{}.sql'.format('project_name', 'project_name')

    _restore(path, database)


def _create_db(name, user='web'):
    log = logger('create database')

    log.info('Creating database {}'.format(name))

    cmd = ['/usr/bin/mysqladmin', 'create', name]
    ex = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = ex.communicate()
    if 'database exists' in error.decode('UTF-8'):
        log.warning('Database \"{}\" already exists'.format(name))
        if click.confirm('Do you want drop and create one new?'):
            _drop_db(name)
            log.info('Creating new empty database')
            _create_db(name)
    _grant_user(name, user)

def _drop_db(name):
    log = logger('drop database')
    cmd = ['/usr/bin/mysqladmin', 'drop', '-f', name]
    log.info('Dropping database \"{}\" '.format(name))
    subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    log.info('Dropped database \"{}\"'.format(name))


def _create_user(user, passwd):
    log = logger('create user')

    query = "CREATE USER \'{}\'@\'{}\' " \
            "IDENTIFIED BY \'{}\';".format(user, '127.0.0.1', passwd)
    log.info("Creating user database")
    cmd = [
        'mysql',
        '--execute=\"%s\"' % query
    ]
    subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def _grant_user(db_name, user):
    log = logger('grant user')
    log.info('Set grant all on database for user')
    query = "GRANT ALL ON {}.* TO '{}'@'{}'".format(db_name, user, '127.0.0.1')
    cmd = [
        'mysql',
        '--execute=\'%s\'' % query
    ]
    subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def _restore(path, db_name):
    log = logger('Query restore')

    if not isfile(path):
        log.warning('Could not find backup file or not existed')
        return

    cmd = [
        'mysql', '--database', db_name, '<', [path]
    ]
    subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)



