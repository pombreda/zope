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

$Id: test_editconfiguration.py,v 1.2 2002/12/25 14:12:38 jim Exp $
"""
__metaclass__ = type

from unittest import TestCase, TestSuite, main, makeSuite
from zope.interface import Interface
from zope.app.browser.services.service \
     import EditConfiguration
from zope.publisher.browser import TestRequest
from zope.app.tests.placelesssetup import PlacelessSetup
from zope.publisher.interfaces.browser import IBrowserPresentation
from zope.component.view import provideView
from zope.component.adapter import provideAdapter
from zope.publisher.browser import BrowserView
from zope.app.event.tests.placelesssetup import getEvents
from zope.app.interfaces.event import IObjectRemovedEvent
from zope.app.interfaces.event import IObjectModifiedEvent
from zope.app.interfaces.container import IContainer
from zope.app.interfaces.container import IZopeContainer
from zope.app.container.zopecontainer import ZopeContainerAdapter

class Container(dict):
    __implements__ = IContainer

class I(Interface):
    pass

class C:
    __implements__ = I


class Test(PlacelessSetup, TestCase):

    def test_remove_objects(self):

        provideAdapter(IContainer, IZopeContainer, ZopeContainerAdapter)

        c1 = C()
        c2 = C()
        c7 = C()
        d = Container({'1': c1, '2': c2, '7': c7})

        view = EditConfiguration(d, TestRequest())
        view.remove_objects(['2', '7'])
        self.assertEqual(d, {'1': c1})

        self.failUnless(
            getEvents(IObjectRemovedEvent,
                      filter = lambda event: event.object == c2),
            )
        self.failUnless(
            getEvents(IObjectRemovedEvent,
                      filter = lambda event: event.object == c7)
            )
        self.failUnless(
            getEvents(IObjectModifiedEvent,
                      filter = lambda event: event.object == d)
            )

    def test_configInfo(self):

        class V(BrowserView):
            def setPrefix(self, p):
                self._prefix = p

        provideView(I, 'ItemEdit', IBrowserPresentation, V)

        c1 = C()
        c2 = C()
        c7 = C()
        d = Container({'1': c1, '2': c2, '7': c7})

        view = EditConfiguration(d, TestRequest())

        info = view.configInfo()
        self.assertEqual(len(info), 3)
        self.assertEqual(info[0]['key'], '1')
        self.assertEqual(info[1]['key'], '2')
        self.assertEqual(info[2]['key'], '7')
        self.assertEqual(info[0]['view'].__class__, V)
        self.assertEqual(info[0]['view'].context, c1)
        self.assertEqual(info[0]['view']._prefix, 'config1')
        self.assertEqual(info[1]['view'].__class__, V)
        self.assertEqual(info[1]['view'].context, c2)
        self.assertEqual(info[1]['view']._prefix, 'config2')
        self.assertEqual(info[2]['view'].__class__, V)
        self.assertEqual(info[2]['view'].context, c7)
        self.assertEqual(info[2]['view']._prefix, 'config7')

def test_suite():
    return TestSuite((
        makeSuite(Test),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')
