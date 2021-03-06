"""
A permission has to be defined first (using grok.Permission for example)
before it can be used in grok.require() in an XMLRPC class.

  >>> grok.grok(__name__)
  Traceback (most recent call last):
  GrokError: Undefined permission 'doesnt.exist' in <class
  'grok.tests.security.missing_permission_xmlrpc.MissingPermission'>. Use
  grok.Permission first.

"""

import grok
import zope.interface

class MissingPermission(grok.XMLRPC):
    grok.context(zope.interface.Interface)
    grok.require('doesnt.exist')

    def foo(self):
        pass

