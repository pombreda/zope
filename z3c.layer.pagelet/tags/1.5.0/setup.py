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
"""Setup"""

import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '1.5.0'

setup(
    name='z3c.layer.pagelet',
    version=version,
    author='Zope Foundation and Contributors',
    author_email='zope-dev@zope.org',
    description = "Pagelet layer setup for Zope3",
    long_description=(
        read('README.txt')
        + '\n\n' +
        '.. contents::'
        + '\n\n' +
        read('src', 'z3c', 'layer', 'pagelet', 'README.txt')
        + '\n\n' +
        read('src', 'z3c', 'layer', 'pagelet', 'login.txt')
        + '\n\n' +
        read('CHANGES.txt')
        ),
    keywords = "z3c pagelet layer zope zope3",
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
    url='http://pypi.python.org/pypi/z3c.layer.pagelet',
    license='ZPL 2.1',
    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages = ['z3c', 'z3c.layer'],
    extras_require = dict(
        test = [
            'zope.testbrowser',
            'zope.securitypolicy',
            'zope.app.testing',
            'zope.app.i18n',
            'zope.configuration>=3.5.0',
            'zope.component',
            'zope.app.authentication',
            'zope.principalregistry',
            ],
        ),
    install_requires = [
        'setuptools',
        'z3c.pagelet',
        'zope.app.publisher',
        'zope.authentication',
        'zope.browser>=1.2',
        'zope.configuration',
        'zope.traversing',
        'zope.viewlet',
        ],
    zip_safe = False,
)

