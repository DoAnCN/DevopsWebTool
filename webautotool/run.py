# -*- coding:utf-8 -*-

from webautotool.command import webautotool as cli
from webautotool.command.common import common
from webautotool.command.db import db
from webautotool.command.local import web
from webautotool.command.remote import remote

assert common
assert db
assert remote
assert web

if __name__ == '__main__':
    cli(obj={})