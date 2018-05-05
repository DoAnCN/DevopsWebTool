# -*- coding:utf-8 -*-

from webautotool.command import webautotool as cli
from webautotool.command.remote import remote
from webautotool.command.common import auto_update

assert auto_update
assert remote

if __name__ == '__main__':
    cli(obj={})