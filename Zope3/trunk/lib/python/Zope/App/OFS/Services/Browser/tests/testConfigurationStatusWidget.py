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
"""XXX short summary goes here.

XXX longer description goes here.

$Id: testConfigurationStatusWidget.py,v 1.2 2002/11/30 18:35:55 jim Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite
from Zope.Publisher.Browser.BrowserRequest import TestRequest
from Zope.App.OFS.Services.ConfigurationInterfaces import ConfigurationStatus
from Zope.App.OFS.Services.Browser.ConfigurationStatusWidget \
     import ConfigurationStatusWidget
from Interface import Interface


class Test(TestCase):

    def test_call(self):
        field = ConfigurationStatus(__name__="status")
        request = TestRequest()
        widget = ConfigurationStatusWidget(field, request)
        widget.setPrefix("f")

        text = ' '.join(widget().split())
        self.assertEqual(
            text,
            '<input type="radio" name="f.status" value="Unregistered" checked>'
            ' Unregistered<br />'
            '<input type="radio" name="f.status" value="Registered">'
            ' Registered<br />'
            '<input type="radio" name="f.status" value="Active">'
            ' Active'
            )
        
        request.form['f.status'] = u'Registered'
        text = ' '.join(widget().split())
        self.assertEqual(
            text,
            '<input type="radio" name="f.status" value="Unregistered">'
            ' Unregistered<br />'
            '<input type="radio" name="f.status" value="Registered" checked>'
            ' Registered<br />'
            '<input type="radio" name="f.status" value="Active">'
            ' Active'
            )

        widget.setData(u"Active")
        text = ' '.join(widget().split())
        self.assertEqual(
            text,
            '<input type="radio" name="f.status" value="Unregistered">'
            ' Unregistered<br />'
            '<input type="radio" name="f.status" value="Registered">'
            ' Registered<br />'
            '<input type="radio" name="f.status" value="Active" checked>'
            ' Active'
            )

        widget.setData(u"Unregistered")
        text = ' '.join(widget().split())
        self.assertEqual(
            text,
            '<input type="radio" name="f.status" value="Unregistered" checked>'
            ' Unregistered<br />'
            '<input type="radio" name="f.status" value="Registered">'
            ' Registered<br />'
            '<input type="radio" name="f.status" value="Active">'
            ' Active'
            )


def test_suite():
    return TestSuite((
        makeSuite(Test),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')
