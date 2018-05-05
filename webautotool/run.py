# -*- coding:utf-8 -*-

from DevopsWebTool.webautotool.command import webautotool as cli
from DevopsWebTool.webautotool.command.remote import remote
from DevopsWebTool.webautotool.command.common import auto_update

assert auto_update
assert remote

if __name__ == '__main__':
    cli(obj={})