# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from webautotool import __version__

setup(
    name='webautotool',
    version=__version__,
    author=['Ly Hong Dat - 14520143','Do Minh Thien - 14520862'],
    author_email=['14520143@gm.email.com', '14520862@gm.uit.edu.vn'],
    description='Usual development commands used to manage websites are '
                'promgrammed by PHP',
    packages=find_packages(),
    install_requires=[
        'click>=6.0',
        'sh'
    ],
    entry_points='''
        [console_scripts]
        webautotool=webautotool.run:cli
    ''',
)