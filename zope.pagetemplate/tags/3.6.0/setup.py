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
"""Setup for zope.pagetemplate package
"""
import os
from setuptools import setup, find_packages


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


setup(name='zope.pagetemplate',
      version='3.6.0',
      author='Zope Foundation and Contributors',
      author_email='zope-dev@zope.org',
      description='Zope Page Templates',
      long_description=(
          read('README.txt')
          + '\n\n' +
          'Detailed Documentation\n' +
          '----------------------'
          + '\n\n' +
          read('src', 'zope', 'pagetemplate', 'architecture.txt')
          + '\n\n' +
          read('src', 'zope', 'pagetemplate', 'readme.txt')
          + '\n\n' +
          read('CHANGES.txt')),
      keywords="zope3 page template",
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Environment :: Web Environment',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: Zope Public License',
          'Programming Language :: Python',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Topic :: Internet :: WWW/HTTP',
          'Framework :: Zope3'],
      url='http://pypi.python.org/pypi/zope.pagetemplate',
      license='ZPL 2.1',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      namespace_packages=['zope'],
      extras_require=dict(
          test=['zope.testing',
                'zope.proxy',
                'zope.security',
                ]),
      install_requires=['setuptools',
                        'zope.interface',
                        'zope.component',
                        'zope.security [untrustedpython]',
                        'zope.tales',
                        'zope.tal',
                        'zope.i18n',
                        'zope.i18nmessageid',
                        'zope.traversing',
                       ],
      include_package_data=True,
      zip_safe=False,
      )
