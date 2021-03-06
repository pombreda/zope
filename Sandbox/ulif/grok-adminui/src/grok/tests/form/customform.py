"""
A form view can completely override which fields are displayed by setting
form_fields manually:

  >>> grok.grok(__name__)

We only expect a single field to be present in the form, as we omitted 'size':

  >>> from zope import component
  >>> from zope.publisher.browser import TestRequest
  >>> request = TestRequest()
  >>> view = component.getMultiAdapter((Mammoth(), request), name='edit')
  >>> len(view.form_fields)
  1
  >>> [w.__name__ for w in view.form_fields]
  ['name']

"""

import grok
from zope import interface, schema

class IMammoth(interface.Interface):
    name = schema.TextLine(title=u"Name")
    size = schema.TextLine(title=u"Size", default=u"Quite normal")

class Mammoth(grok.Model):
    interface.implements(IMammoth)

class Edit(grok.EditForm):
    grok.context(Mammoth)

    form_fields = grok.Fields(IMammoth).omit('size')
