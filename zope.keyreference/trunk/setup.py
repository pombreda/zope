##############################################################################
#
# Copyright (c) 2006 Zope Foundation and Contributors.
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
# This package is developed by the Zope Toolkit project, documented here:
# http://docs.zope.org/zopetoolkit
# When developing and releasing this package, please follow the documented
# Zope Toolkit policies as described by this documentation.
##############################################################################
"""Setup for zope.keyreference package
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(name = 'zope.keyreference',
      version='4.0.0dev',
      author='Zope Foundation and Contributors',
      author_email='zope-dev@zope.org',
      description='Key References',
      long_description=(
          read('README.txt')
          + '\n\n' +
          'Detailed Documentation\n' +
          '----------------------\n'
          + '\n\n' +
          read('src', 'zope', 'keyreference', 'persistent.txt')
          + '\n\n' +
          read('CHANGES.txt')
          ),
      keywords = "zope3 key reference persistent",
      classifiers = [
          'Development Status :: 5 - Production/Stable',
          'Environment :: Web Environment',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: Zope Public License',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Topic :: Internet :: WWW/HTTP',
          'Framework :: Zope3'],
      url='http://pypi.python.org/pypi/zope.keyreference',
      license='ZPL 2.1',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['zope'],
      extras_require={'test': []},
      install_requires = ['setuptools',
                          'ZODB3',
                          'zope.component',
                          'zope.i18nmessageid',
                          'zope.interface',
                          'zope.schema',
                          ],
      include_package_data = True,
      zip_safe = False,
      )
