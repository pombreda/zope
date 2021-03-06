WSGI Middleware for Managing ZODB Database Connections
======================================================

The zc.zodbwsgi provides middleware for managing connections to a ZODB
database. It combines several features into a single middleware
component:

- database configuration
- database initialization
- connection management
- optional transaction management
- optional request retry on conflict errors (using repoze.retry)

It is designed to work with paste deployment and provides a
"filter_app_factory" entry point, named "main".

A number of configuration options are provided. Option values are
strings.

configuration
   A required ZConfig formatted ZODB database configuration

   If multiple databases are defined, they will define a
   multi-database. Connections will be to the first defined database.

initializer
   An optional database initialization function of the form
   ``module:expression``

key
   An optional name of a WSGI environment key for database connections

   This defaults to "zodb.connection".

transaction_management
   An optional flag (either "true" or "false") indicating whether the
   middleware manages transactions

   Transaction management is enabled by default.

transaction_key
   An optional name of a WSGI environment key for transaction managers

   This defaults to "transaction.manager". The key will only be
   present if transaction management is enabled.

retry
   An optional retry count

   The default is "3", indicating that requests will be retried up to
   3 times.  Use "0" to disable retries.

   Note that when retry is not "0", request bodies will be buffered.

Let's look at some examples.

First we define an demonstration "application" that we can pass to our
factory::

    import transaction, ZODB.POSException
    from sys import stdout

    class demo_app:
        def __init__(self, default):
            pass
        def __call__(self, environ, start_response):
            start_response('200 OK', [('content-type', 'text/html')])
            root = environ['zodb.connection'].root()
            path = environ['PATH_INFO']
            if path == '/inc':
                root['x'] = root.get('x', 0) + 1
                if 'transaction.manager' in environ:
                    environ['transaction.manager'].get().note('path: %r' % path)
                else:
                    transaction.commit() # We have to commit our own!
            elif path == '/conflict':
                print >>stdout, 'Conflict!'
                raise ZODB.POSException.ConflictError

            return [repr(root)]

.. -> src

   >>> import zc.zodbwsgi.tests
   >>> exec(src, zc.zodbwsgi.tests.__dict__)

Now, we'll define our application factory using a paste deployment
configuration::

   [app:main]
   paste.app_factory = zc.zodbwsgi.tests:demo_app
   filter-with = zodb

   [filter:zodb]
   use = egg:zc.zodbwsgi
   configuration =
      <zodb>
        <demostorage>
        </demostorage>
      </zodb>

.. -> src

    >>> open('paste.ini', 'w').write(src)

Here, for demonstration purposes, we used an in-memory demo storage.

Now, we'll create an application with paste:

    >>> import paste.deploy, os
    >>> app = paste.deploy.loadapp('config:'+os.path.abspath('paste.ini'))

The resulting applications has a database attribute (mainly for
testing) with the created database.
Being newly initialized, the database is empty:

    >>> conn = app.database.open()
    >>> conn.root()
    {}

Let's do an "increment" request.

    >>> import webtest
    >>> testapp = webtest.TestApp(app)
    >>> testapp.get('/inc')
    <200 OK text/html body="{'x': 1}">

Now, if we look at the database, we see that there's now data in the
root object:

    >>> conn.sync()
    >>> conn.root()
    {'x': 1}

We can supply a database initialization function using the initializer
option.  Let's define an initialization function::

    import transaction

    def initialize_demo_db(db):
        conn = db.open()
        conn.root()['x'] = 100
        transaction.commit()
        conn.close()

.. -> src

   >>> exec(src, zc.zodbwsgi.tests.__dict__)

and update our paste configuration to use it::

   [app:main]
   paste.app_factory = zc.zodbwsgi.tests:demo_app
   filter-with = zodb

   [filter:zodb]
   use = egg:zc.zodbwsgi
   configuration =
      <zodb>
        <demostorage>
        </demostorage>
      </zodb>

   initializer = zc.zodbwsgi.tests:initialize_demo_db

.. -> src

    >>> open('paste.ini', 'w').write(src)

Now, when we use the application, we see the impact of the
initializer:

    >>> app = paste.deploy.loadapp('config:'+os.path.abspath('paste.ini'))
    >>> testapp = webtest.TestApp(app)
    >>> testapp.get('/inc')
    <200 OK text/html body="{'x': 101}">

.. Our application updated transaction meta data when called under
   transaction control.

    >>> app.database.history(conn.root()._p_oid, 1)[0]['description']
    "path: '/inc'"

Sometimes, you may not want the middleware to control transactions.
You might do this if your application used multiple databases,
including non-ZODB databases [#multidb]_.  You can suppress
transaction management by supplying a value of "false" for the
transaction_management option::

   [app:main]
   paste.app_factory = zc.zodbwsgi.tests:demo_app
   filter-with = zodb

   [filter:zodb]
   use = egg:zc.zodbwsgi
   configuration =
      <zodb>
        <demostorage>
        </demostorage>
      </zodb>

   initializer = zc.zodbwsgi.tests:initialize_demo_db
   transaction_management = false

.. -> src

    >>> open('paste.ini', 'w').write(src)
    >>> app = paste.deploy.loadapp('config:'+os.path.abspath('paste.ini'))
    >>> testapp = webtest.TestApp(app)
    >>> testapp.get('/inc')
    <200 OK text/html body="{'x': 101}">

    >>> app.database.history('\0'*8, 1)[0]['description']
    ''

By default, zc.zodbwsgi adds ``repoze.retry`` middleware to retry requests
when there are conflict errors:

    >>> import ZODB.POSException
    >>> app = paste.deploy.loadapp('config:'+os.path.abspath('paste.ini'))
    >>> testapp = webtest.TestApp(app)
    >>> try: testapp.get('/conflict')
    ... except ZODB.POSException.ConflictError: pass
    ... else: print 'oops'
    Conflict!
    Conflict!
    Conflict!
    Conflict!

Here we can see that the request was retried 3 times.

We can suppress this by supplying a value of "0" for the retry option::

   [app:main]
   paste.app_factory = zc.zodbwsgi.tests:demo_app
   filter-with = zodb

   [filter:zodb]
   use = egg:zc.zodbwsgi
   configuration =
      <zodb>
        <demostorage>
        </demostorage>
      </zodb>

   retry = 0

.. -> src

    >>> open('paste.ini', 'w').write(src)

Now, if we run the app, the request won't be retried:

    >>> app = paste.deploy.loadapp('config:'+os.path.abspath('paste.ini'))
    >>> testapp = webtest.TestApp(app)
    >>> try: testapp.get('/conflict')
    ... except ZODB.POSException.ConflictError: pass
    ... else: print 'oops'
    Conflict!

.. Other tests of corner cases:

  ::

    class demo_app:
        def __init__(self, default):
            pass
        def __call__(self, environ, start_response):
            start_response('200 OK', [('content-type', 'text/html')])
            root = environ['connection'].root()
            path = environ['PATH_INFO']
            if path == '/inc':
                root['x'] = root.get('x', 0) + 1
                environ['manager'].get().note('path: %r' % path)

            return [repr(root)]

  .. -> src

   >>> exec(src, zc.zodbwsgi.tests.__dict__)

  ::

   [app:main]
   paste.app_factory = zc.zodbwsgi.tests:demo_app
   filter-with = zodb

   [filter:zodb]
   use = egg:zc.zodbwsgi
   configuration =
      <zodb>
        <demostorage>
        </demostorage>
      </zodb>

   key = connection
   transaction_key = manager

  .. -> src

    >>> open('paste.ini', 'w').write(src)
    >>> app = paste.deploy.loadapp('config:'+os.path.abspath('paste.ini'))
    >>> testapp = webtest.TestApp(app)
    >>> testapp.get('/inc')
    <200 OK text/html body="{'x': 1}">


Changes
=======

0.1.0 (2010-02-16)
------------------

Initial release



.. [#multidb] If you want to use multiple ZODB databases, you can
   simply define them in your configuration option.  Just make sure to
   give them names.  When you want to access a database, use the
   ``get_connection`` method on the connection in the environment::

      foo_conn = environ['zodb.connection'].get_connection('foo')
