# -*- coding:utf-8 -*-

from ..webautotool.commmand import webautotool as cli
from ..webautotool.commmand.remote import remote
from ..webautotool.commmand.common import auto_update

assert auto_update
assert remote

if __name__ == '__main__':
    cli(obj={})