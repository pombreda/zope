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
$Id: testPasswordWidget.py,v 1.1 2002/07/16 15:15:55 srichter Exp $
"""
from unittest import TestCase, TestSuite, main, makeSuite
from Zope.App.Forms.Views.Browser.Widget import PasswordWidget

from testBrowserWidget import BrowserWidgetTest, Field


class PasswordWidgetTest(BrowserWidgetTest):
    
    def setUp(self):
        field = Field()
        request = {'field_foo': 'Foo Value'}
        self._widget = PasswordWidget(field, request)

    def testProperties(self):
        self.assertEqual(self._widget.getValue('tag'), 'input')
        self.assertEqual(self._widget.getValue('type'), 'password')
        self.assertEqual(self._widget.getValue('cssClass'), '')
        self.assertEqual(self._widget.getValue('hidden'), 0)
        self.assertEqual(self._widget.getValue('extra'), '')
        self.assertEqual(self._widget.getValue('default'), '')
        self.assertEqual(self._widget.getValue('displayWidth'), 20)
        self.assertEqual(self._widget.getValue('displayMaxWidth'), '')

    def testRender(self):
        value = 'Foo Value'
        check_list = ('type="password"', 'name="field_foo"',
                      'value="Foo Value"', 'size="20"')
        self._verifyResult(self._widget.render(value), check_list)
        check_list = ('type="hidden"',) + check_list[1:-1]
        self._verifyResult(self._widget.renderHidden(value), check_list)
        check_list = ('style="color: red"',) + check_list
        self._widget.extra = 'style="color: red"'
        self._verifyResult(self._widget.renderHidden(value), check_list)



def test_suite():
    return TestSuite((
        makeSuite(PasswordWidgetTest),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')
