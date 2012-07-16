# -*- coding:utf-8 -*-
from distutils.core import setup

setup(
    name = 'elementflow',
    version = '0.3.0',
    author = 'Ivan Sagalaev',
    author_email = 'Maniac@SoftwareManiacs.Org',
    package_dir = {'': 'src'},
    py_modules = ['elementflow'],
    url = 'https://launchpad.net/elementflow',
    license = 'LICENSE.txt',
    description = 'Python library for generating XML as a stream without first building a tree in memory.',
    long_description = open('README.md').read(),
)
