================
Source Factories
================

Source factories are used to simplify the creation of sources for certain
standard cases.

Sources split up the process of providing input fields with choices for users
into several components: a context binder, a source class, a terms class, and a
term class.

This is the correct abstraction and will fit many complex cases very well. To
reduce the amount of work to do for some standard cases, the source factories
allow users to define only the business relevant code for getting a list of
values, getting a token and a title to display.


Simple case
-----------

In the most simple case, you only have to provide a method that returns a list
of values and derive from `BasicSourceFactory`::

  >>> import zc.sourcefactory.basic
  >>> class MyStaticSource(zc.sourcefactory.basic.BasicSourceFactory):
  ...     def getValues(self):
  ...         return ['a', 'b', 'c']

When calling the source factory, we get a source::

  >>> source = MyStaticSource()
  >>> import zope.schema.interfaces
  >>> zope.schema.interfaces.ISource.providedBy(source)
  True

The values match our `getValues`-method of the factory::

  >>> list(source)
  ['a', 'b', 'c']
  >>> 'a' in source
  True
  >>> len(source)
  3


Contextual sources
------------------

Sometimes we need context to determine the values. In this case, the
`getValues`-method gets a parameter `context`.

Let's assume we have a small object containing data to be used by the source::

  >>> class Context(object):
  ...      values = []

  >>> import zc.sourcefactory.contextual
  >>> class MyDynamicSource(
  ...     zc.sourcefactory.contextual.BasicContextualSourceFactory):
  ...     def getValues(self, context):
  ...         return context.values

When instanciating, we get a ContextSourceBinder::

  >>> binder = MyDynamicSource()
  >>> zope.schema.interfaces.IContextSourceBinder.providedBy(binder)
  True

Binding it to a context, we get a source::

  >>> context = Context()
  >>> source = binder(context)
  >>> zope.schema.interfaces.ISource.providedBy(source)
  True

  >>> list(source)
  []

Modifying the context also modifies the data in the source::

  >>> context.values = [1,2,3,4]
  >>> list(source)
  [1, 2, 3, 4]
  >>> 1 in source
  True
  >>> len(source)
  4


Filtering
---------

Additional to providing the `getValues`-method you can also provide a
`filterValue`-method that will allow you to reduce the items from the list,
piece by piece.

This is useful if you want to have more specific sources (by subclassing) that
share the same basic origin of the data but have different filters applied to
it::

  >>> class FilteringSource(zc.sourcefactory.basic.BasicSourceFactory):
  ...     def getValues(self):
  ...         return xrange(1,20)
  ...     def filterValue(self, value):
  ...         return value % 2
  >>> source = FilteringSource()
  >>> list(source)
  [1, 3, 5, 7, 9, 11, 13, 15, 17, 19]

Subclassing modifies the filter, not the original data::

  >>> class OtherFilteringSource(FilteringSource):
  ...     def filterValue(self, value):
  ...         return not value % 2
  >>> source = OtherFilteringSource()
  >>> list(source)
  [2, 4, 6, 8, 10, 12, 14, 16, 18]

The "in" operator gets applied also to filtered values::

  >>> 2 in source
  True
  >>> 3 in source
  False

The "len" also gets applied to filtered values::

  >>> len(source)
  9


Scaling
-------

Sometimes the number of items available through a source is very large.  So
large that you only want to access them if absolutely neccesary.  One such
occasion is with truth-testing a source.  By default Python will call
__nonzero__ to get the boolean value of an object, but if that isn't available
__len__ is called to see what it returns.  That might be very expensive, so we
want to make sure it isn't called.

  >>> class MyExpensiveSource(zc.sourcefactory.basic.BasicSourceFactory):
  ...     def getValues(self):
  ...         yield 'a'
  ...         raise RuntimeError('oops, iterated too far')

  >>> source = MyExpensiveSource()

  >>> bool(source)
  True


Simple case
-----------

In the most simple case, you only have to provide a method that returns a list
of values and derive from `BasicSourceFactory`::

  >>> import zc.sourcefactory.basic
  >>> class MyStaticSource(zc.sourcefactory.basic.BasicSourceFactory):
  ...     def getValues(self):
  ...         return ['a', 'b', 'c']

When calling the source factory, we get a source::

  >>> source = MyStaticSource()
  >>> import zope.schema.interfaces
  >>> zope.schema.interfaces.ISource.providedBy(source)
  True

The values match our `getValues`-method of the factory::

  >>> list(source)
  ['a', 'b', 'c']
  >>> 'a' in source
  True
  >>> len(source)
  3

WARNING about the standard adapters for ITerms
----------------------------------------------

The standard adapters for ITerms are only suitable if the value types returned
by your `getValues` function are homogenous. Mixing integers, persistent
objects, strings, and unicode within one source may create non-unique tokens.
In this case, you have to provide a custom `getToken`-method to provide unique
and unambigous tokens.
