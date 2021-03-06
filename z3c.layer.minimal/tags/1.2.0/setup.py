#!python
##############################################################################
#
# Copyright (c) 2007-2009 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Setup

$Id: setup.py 313 2007-05-22 15:33:41Z srichter $
"""
import os
import xml.sax.saxutils
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '1.2.0'

setup(
    name = 'z3c.layer.minimal',
    version = version,
    author='Zope Foundation and Contributors',
    author_email = "zope-dev@zope.org",
    description = "Minimal layer setup for Zope3",
    long_description=(
        read('README.txt')
        + '\n\n' +
        '.. contents::\n'
        + '\n\n' +
        read('src', 'z3c', 'layer', 'minimal', 'README.txt')
        + '\n\n' +
        read('CHANGES.txt')
        ),
    keywords = "z3c minimal layer zope zope3",
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Framework :: Zope3'],
    url='http://pypi.python.org/pypi/z3c.layer.minimal',
    license='ZPL 2.1',
    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages = ['z3c', 'z3c.layer'],
    extras_require = dict(
        test = [
            'zope.app.testing',
            'zope.app.zcmlfiles',
            'zope.securitypolicy',
            'zope.testbrowser',
            ],
        ),
    install_requires = [
        'setuptools',
        'zope.app.http',
        'zope.app.publisher',
        'zope.configuration',
        'zope.traversing',
        ],
    zip_safe = False,
)

