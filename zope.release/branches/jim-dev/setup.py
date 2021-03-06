##############################################################################
#
# Copyright (c) 2007 Zope Corporation and Contributors.
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
"""Setup for ``zope.release`` project"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(name='zope.release',
      version = '0',
      author='Zope Corporation and Contributors',
      author_email='zope-dev@zope.org',
      description='Zope Release and Known-Good-Set (KGS) Support',
      long_description=(
          read('README.txt')
          + '\n\n' +
          read('src', 'zope', 'release', 'README.txt')
          + '\n\n' +
          read('CHANGES.txt')
          ),
      keywords = "zope3 setuptools egg kgs release",
      classifiers = [
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: Zope Public License',
          'Programming Language :: Python',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Topic :: Internet :: WWW/HTTP',
          'Framework :: Zope3'],
      url='http://pypi.python.org/pypi/zope.release',
      license='ZPL 2.1',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['zope'],
      extras_require = dict(
          test=['zope.testing']),
      install_requires=[
          'setuptools',
          'zc.buildout',
          'zc.lockfile',
          'zope.kgs',
          ],
      entry_points = dict(console_scripts=[
          'upload = zope.release.upload:main',
          'update-tree = zope.release.tree:main',
          'update-index = zope.release.update:main',
          ]),
      include_package_data = True,
      zip_safe = False,
      )
