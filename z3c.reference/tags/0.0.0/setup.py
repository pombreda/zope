#!python
from setuptools import setup, find_packages

setup (
    name='z3c.reference',
    version='0.0.0a1',
    author = "Lovely Systems",
    author_email = "office@lovelysystems.com",
    description = "Reference",
    license = "ZPL 2.1",
    keywords = "zope3 web20 zope reference",
    url = 'svn://svn.zope.org/repos/main/z3c.reference',
    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages = ['z3c'],
    extras_require = dict(
        test = ['zope.app.testing',
                'zope.testing',]
        ),
    install_requires = [
        'ZODB3',
        'zc.resourcelibrary',
        'zope.app.component',
        'zope.app.file',
        'zope.app.form',
        'zope.app.keyreference',
        'zope.cachedescriptors',
        'zope.dublincore',
        'zope.interface',
        'zope.location',
        'zope.schema',
        'zope.traversing'
        ],
    dependency_links = ['http://download.zope.org/distribution']
    )
