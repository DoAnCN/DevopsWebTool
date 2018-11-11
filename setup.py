# -*- coding: utf-8 -*-

import os
from setuptools import setup, find_packages
from setuptools.command.install import install
from webautotool import __version__

class createLoginFile(install):
    def run(self):
        # with open('manager.j2') as f: content = f.read()
        path = os.environ['HOME']
        print("=====================")
        os.system('echo \"{0}\" > {1}/.manager'.format("ffffffffffffffffffff", path))
        install.run(self)

setup(
    name='webautotool',
    version=__version__,
    author=['Ly Hong Dat - 14520143','Do Minh Thien - 14520862'],
    author_email=['14520143@gm.email.com', '14520862@gm.uit.edu.vn'],
    description='Usual development commands used to manage websites are '
                'promgrammed by PHP',
    cmdclass={'install': createLoginFile},
    packages=find_packages(),
    install_requires=[
        'click>=6.0',
        'colorlog',
        'sh',
        'requests',
        'pyyaml'
    ],
    entry_points='''
        [console_scripts]
        webautotool=webautotool.run:cli
    ''',
)