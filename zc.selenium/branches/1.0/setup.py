from setuptools import setup, find_packages

setup(
    name='zc.selenium',
    version='1.0.0',
    author='Zope Corporation',
    author_email='info@zope.com',
    url='http://svn.zope.org/zc.seleinum',
    description="Selenium integration for Zope 3",
    packages=find_packages('src'),
    package_dir = {'': 'src'},
    include_package_data=True,
    zip_safe=False,
    license='ZPL 2.1',
    namespace_packages = ['zc'],
    install_requires =[
        'zope.interface',
        'zope.component',
        'zope.publisher',
    ]
)
