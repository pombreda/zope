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
$Id: test_floatwidget.py,v 1.2 2004/03/17 17:37:06 philikon Exp $
"""
import unittest, doctest
from zope.app.form.browser.tests.test_browserwidget import BrowserWidgetTest
from zope.app.form.interfaces import IInputWidget
from zope.app.form.browser import FloatWidget
from zope.app.form.interfaces import ConversionError, WidgetInputError
from zope.interface.verify import verifyClass

from zope.schema import Float


class FloatWidgetTest(BrowserWidgetTest):
    """Documents and tests the float widget.
        
        >>> verifyClass(IInputWidget, FloatWidget)
        True
    """

    _FieldFactory = Float
    _WidgetFactory = FloatWidget

    def test_hasInput(self):
        del self._widget.request.form['field.foo']
        self.failIf(self._widget.hasInput())
        # widget has input, even if input is an empty string
        self._widget.request.form['field.foo'] = u''
        self.failUnless(self._widget.hasInput())
        self._widget.request.form['field.foo'] = u'123'
        self.failUnless(self._widget.hasInput())

    def test_getInputValue(self):
        self._widget.request.form['field.foo'] = u''
        self.assertRaises(WidgetInputError, self._widget.getInputValue)
        self._widget.request.form['field.foo'] = u'123.45'
        self.assertEquals(self._widget.getInputValue(), 123.45)
        self._widget.request.form['field.foo'] = u'abc'
        self.assertRaises(ConversionError, self._widget.getInputValue)


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(FloatWidgetTest),
        doctest.DocTestSuite(),
        ))

if __name__=='__main__':
    unittest.main(defaultTest='test_suite')
