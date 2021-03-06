##########################################################################
# zopyx.convert2 - XSL-FO related functionalities
#
# (C) 2007, 2008 ZOPYX Ltd & Co. KG, Tuebingen, Germany
##########################################################################

import os
from setuptools import setup, find_packages


CLASSIFIERS = [
    'Programming Language :: Python',
]

version = '2.1.0'

desc = unicode(file('README.txt').read().strip(), 'utf-8')
changes = file('CHANGES.txt').read().strip()
long_description = desc + '\n\nChanges:\n========\n\n' + changes


setup(name='zopyx.convert2',
      version=version,
      license='ZPL (see LICENSE.txt)',
      author='Andreas Jung',
      author_email='info@zopyx.com',
      maintainer='Andreas Jung',
      maintainer_email='info@zopyx.com',
      classifiers=CLASSIFIERS,
      url='http://pypi.python.org/pypi/zopyx.convert2',
      description='A Python interface for the conversion of HTML to PDF, RTF, DOCX, WML and ODT) - belongs to zopyx.smartprintng.core',
      long_description=long_description,
      packages=['zopyx', 'zopyx.convert2'],
      package_dir = {'': 'src'},
      include_package_data = True,
      test_suite='nose.collector',
      zip_safe=False,
      install_requires=['setuptools', 'elementtree', 'BeautifulSoup<=3.0.9999'],
      namespace_packages=['zopyx'],
      entry_points={'console_scripts': ['html-convert = zopyx.convert2.cli:main',]},
      )
