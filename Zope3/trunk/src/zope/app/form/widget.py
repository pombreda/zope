##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""
$Id: widget.py,v 1.8 2003/08/13 21:28:34 garrett Exp $
"""
import traceback
from warnings import warn
from zope.app.interfaces.form import IWidget
from zope.component.interfaces import IViewFactory
from zope.interface import implements

__metaclass__ = type

class Widget:
    """Mix-in class providing some functionality common accross view types
    """
    implements(IWidget)

    _prefix = 'field.'
    _data_marker = object()
    _data = _data_marker

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.name = self._prefix + context.__name__

    # See IWidget
    propertyNames = []

    def getValue(self, name):
        'See IWidget'
        if name in self.propertyNames:
            return getattr(self, name, None)

    def setPrefix(self, prefix):
        if not prefix.endswith("."):
            prefix += '.'
        self._prefix = prefix
        self.name = prefix + self.context.__name__

    def setData(self, value):
        if traceback.extract_stack()[-2][2] != 'setRenderedValue':
            warn("setData is deprecated - use setRenderedValue",
                DeprecationWarning, 2)
        
        # XXX - move this implementation to setRenderedValue when 
        # deprecation is removed

        self._data = value

    def setRenderedValue(self, value):
        self.setData(value)

    def hasInput(self):
        raise TypeError("hasInput has not been implemented")

    def hasValidInput(self):
        raise TypeError("hasValidInput has not been implemented")
    
    def getInputValue(self):
        raise TypeError("getInputValue has not been implemented")

    def validate(self):
        raise TypeError("validate has not been implemented")

    def applyChanges(self, content):
        raise TypeError("applyChanges has not been implemented")

    title = property(lambda self: self.context.title)
    description = property(lambda self: self.context.description)

    required = property(lambda self: self.context.required)

# XXX CustomWidget *should* be called CustomWidgetFactory
class CustomWidget:
    """Custom Widget."""
    implements(IViewFactory)

    def __init__(self, *args, **kw):
        self._widget_factory = args[0]
        if len(args) > 1:
            self.args = args[1:]
        else:
            self.args = ()
        self.kw = kw

    def __call__(self, context, request):
        args = (context, request) + self.args
        instance = self._widget_factory(*args)
        for item in self.kw.items():
            setattr(instance, item[0], item[1])
        return instance

