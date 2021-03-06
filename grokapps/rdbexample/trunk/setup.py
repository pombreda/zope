from setuptools import setup, find_packages

version = '0.0'

setup(name='rdbexample',
      version=version,
      description="",
      long_description="""\
""",
      # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[], 
      keywords="",
      author="",
      author_email="",
      url="",
      license="ZPL",
      package_dir={'': 'src'},
      packages=find_packages('src'),
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        'grok',
                        'grokui.admin',
                        'z3c.testsetup',
                        'grokcore.startup',
                        'z3c.saconfig',
                        'megrok.rdb >= 0.10',
                        # Add extra requirements here
                        ],
      entry_points = """
      [console_scripts]
      rdbexample-debug = grokcore.startup:interactive_debug_prompt
      rdbexample-ctl = grokcore.startup:zdaemon_controller
      [paste.app_factory]
      main = grokcore.startup:application_factory
      """,
      )
