from setuptools import setup, find_packages

_description = (
    "Script that creates a Grok project directory, installs Grok, the Grok "
    "Toolkit and the Zope Toolkit and sets up a complete skeleton for "
    "a new Grok web application."
    )

long_description = (
    "===========\n"
    "Grokproject\n"
    "===========\n"
    "\n"
    "%s\n"
    "\n"
    ".. contents::\n"
    "\n"
    "Description\n"
    "===========\n"
    "\n" +
    open('README.txt').read() +
    '\n' +
    open('CHANGES.txt').read()
    ) % _description

setup(
    name='grokproject',
    version='2.2.1',
    author='Grok Team',
    author_email='grok-dev@zope.org',
    url='http://grok.zope.org',
    download_url='http://pypi.python.org/pypi/grokproject',
    description=_description,
    long_description=long_description,
    license='ZPL',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=['PasteScript>=1.6'],
    extras_require=dict(tests=['zope.testing',]),
    test_suite='tests.test_suite',
    entry_points={
        'console_scripts': ['grokproject = grokproject:main'],
        'paste.paster_create_template': ['grok = grokproject:GrokProject']},
    )
