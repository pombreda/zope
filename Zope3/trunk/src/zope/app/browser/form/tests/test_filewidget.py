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
$Id: test_filewidget.py,v 1.5 2003/05/22 22:50:09 jim Exp $
"""
import unittest

from StringIO import StringIO
from zope.app.browser.form.widget import FileWidget

from zope.app.browser.form.tests.test_browserwidget import BrowserWidgetTest

class FileWidgetTest(BrowserWidgetTest):

    _WidgetFactory = FileWidget

    def setUp(self):
        BrowserWidgetTest.setUp(self)

        file = StringIO('Foo Value')
        file.filename = 'test.txt'
        self._widget.request.form['field.foo'] = file

    def testProperties(self):
        self.assertEqual(self._widget.getValue('tag'), 'input')
        self.assertEqual(self._widget.getValue('type'), 'file')
        self.assertEqual(self._widget.getValue('cssClass'), '')
        self.assertEqual(self._widget.getValue('extra'), '')
        self.assertEqual(self._widget.getValue('default'), '')
        self.assertEqual(self._widget.getValue('displayWidth'), 20)
        self.assertEqual(self._widget.getValue('displayMaxWidth'), '')

    def testRender(self):
        value = 'Foo Value'
        self._widget.setData(value)
        check_list = ('type="file"', 'id="field.foo"', 'name="field.foo"',
                      'size="20"')

        self._verifyResult(self._widget(), check_list)
        check_list = ('type="hidden"',) + check_list[1:-1]
        self._verifyResult(self._widget.hidden(), check_list)
        check_list = ('style="color: red"',) + check_list
        self._widget.extra = 'style="color: red"'
        self._verifyResult(self._widget.hidden(), check_list)



def test_suite():
    return unittest.makeSuite(FileWidgetTest)

if __name__=='__main__':
    unittest.main(defaultTest='test_suite')
