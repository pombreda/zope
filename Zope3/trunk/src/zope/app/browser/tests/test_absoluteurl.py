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
"""Test the AbsoluteURL view

Revision information:
$Id: test_absoluteurl.py,v 1.8 2003/04/28 13:14:20 mgedmin Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite
from zope.interface import Interface

from zope.app.tests.placelesssetup import PlacelessSetup
from zope.component import getService, getView
from zope.app.services.servicenames import Adapters, Views

from zope.i18n.interfaces import IUserPreferredCharsets

from zope.publisher.tests.httprequest import TestRequest
from zope.publisher.http import IHTTPRequest
from zope.publisher.http import HTTPCharsets
from zope.publisher.interfaces.browser import IBrowserPresentation
from zope.proxy.context import ContextWrapper


class IRoot(Interface): pass

class Root:
    __implements__ = IRoot

class TrivialContent(object):
    """Trivial content object, used because instances of object are rocks."""

class TestAbsoluteURL(PlacelessSetup, TestCase):

    def setUp(self):
        PlacelessSetup.setUp(self)
        from zope.app.browser.absoluteurl \
             import AbsoluteURL, SiteAbsoluteURL
        provideView=getService(None,Views).provideView
        provideView(None, 'absolute_url', IBrowserPresentation,
                    [AbsoluteURL])
        provideView(IRoot, 'absolute_url', IBrowserPresentation,
                    [SiteAbsoluteURL])
        provideAdapter = getService(None, Adapters).provideAdapter
        provideAdapter(IHTTPRequest, IUserPreferredCharsets, HTTPCharsets)

    def testBadObject(self):
        request = TestRequest()
        request.setViewType(IBrowserPresentation)
        view = getView(None, 'absolute_url', request)
        self.assertRaises(TypeError, view.__str__)

    def testNoContext(self):
        request = TestRequest()
        request.setViewType(IBrowserPresentation)
        view = getView(Root(), 'absolute_url', request)
        self.assertEqual(str(view), 'http://foobar.com')

    def testBasicContext(self):
        request = TestRequest()
        request.setViewType(IBrowserPresentation)

        content = ContextWrapper(TrivialContent(), Root(), name='a')
        content = ContextWrapper(TrivialContent(), content, name='b')
        content = ContextWrapper(TrivialContent(), content, name='c')
        view = getView(content, 'absolute_url', request)
        self.assertEqual(str(view), 'http://foobar.com/a/b/c')

        breadcrumbs = view.breadcrumbs()
        self.assertEqual(breadcrumbs,
                         ({'name':  '', 'url': 'http://foobar.com'},
                          {'name': 'a', 'url': 'http://foobar.com/a'},
                          {'name': 'b', 'url': 'http://foobar.com/a/b'},
                          {'name': 'c', 'url': 'http://foobar.com/a/b/c'},
                          ))

    def testContextWSideEffectsInMiddle(self):
        request = TestRequest()
        request.setViewType(IBrowserPresentation)

        content = ContextWrapper(TrivialContent(), Root(), name='a')
        content = ContextWrapper(TrivialContent(), content,
                                 name='.',
                                 side_effect_name="++skin++ZopeTop")
        content = ContextWrapper(TrivialContent(), content, name='b')
        content = ContextWrapper(TrivialContent(), content, name='c')
        view = getView(content, 'absolute_url', request)
        self.assertEqual(str(view), 'http://foobar.com/a/++skin++ZopeTop/b/c')

        breadcrumbs = view.breadcrumbs()
        self.assertEqual(breadcrumbs,
         ({'name':  '', 'url': 'http://foobar.com'},
          {'name': 'a', 'url': 'http://foobar.com/a/++skin++ZopeTop'},
          {'name': 'b', 'url': 'http://foobar.com/a/++skin++ZopeTop/b'},
          {'name': 'c', 'url': 'http://foobar.com/a/++skin++ZopeTop/b/c'},
          ))

    def testContextWSideEffectsInFront(self):
        request = TestRequest()
        request.setViewType(IBrowserPresentation)

        root = Root()
        content = ContextWrapper(root, root,
                                 name='.',
                                 side_effect_name="++skin++ZopeTop")
        content = ContextWrapper(TrivialContent(), content, name='a')
        content = ContextWrapper(TrivialContent(), content, name='b')
        content = ContextWrapper(TrivialContent(), content, name='c')
        view = getView(content, 'absolute_url', request)
        self.assertEqual(str(view), 'http://foobar.com/++skin++ZopeTop/a/b/c')

        breadcrumbs = view.breadcrumbs()
        self.assertEqual(breadcrumbs,
         ({'name':  '', 'url': 'http://foobar.com/++skin++ZopeTop'},
          {'name': 'a', 'url': 'http://foobar.com/++skin++ZopeTop/a'},
          {'name': 'b', 'url': 'http://foobar.com/++skin++ZopeTop/a/b'},
          {'name': 'c', 'url': 'http://foobar.com/++skin++ZopeTop/a/b/c'},
          ))

    def testVirtualHosting(self):
        request = TestRequest()
        request.setViewType(IBrowserPresentation)

        vh_root = TrivialContent()
        content = ContextWrapper(vh_root, Root(), name='a')
        request._vh_root = ContextWrapper(vh_root, Root(), name='a')
        content = ContextWrapper(TrivialContent(), content, name='b')
        content = ContextWrapper(TrivialContent(), content, name='c')
        view = getView(content, 'absolute_url', request)
        self.assertEqual(str(view), 'http://foobar.com/b/c')

        breadcrumbs = view.breadcrumbs()
        self.assertEqual(breadcrumbs,
         ({'name':  '', 'url': 'http://foobar.com'},
          {'name': 'b', 'url': 'http://foobar.com/b'},
          {'name': 'c', 'url': 'http://foobar.com/b/c'},
          ))

    def testVirtualHostingWithVHElements(self):
        request = TestRequest()
        request.setViewType(IBrowserPresentation)

        vh_root = TrivialContent()
        content = ContextWrapper(vh_root, Root(), name='a')
        request._vh_root = ContextWrapper(vh_root, Root(), name='a')
        content = ContextWrapper(TrivialContent(), content,
                                 name='.',
                                 side_effect_name="++vh++abc")
        content = ContextWrapper(TrivialContent(), content, name='b')
        content = ContextWrapper(TrivialContent(), content, name='c')
        view = getView(content, 'absolute_url', request)
        self.assertEqual(str(view), 'http://foobar.com/b/c')

        breadcrumbs = view.breadcrumbs()
        self.assertEqual(breadcrumbs,
         ({'name':  '', 'url': 'http://foobar.com'},
          {'name': 'b', 'url': 'http://foobar.com/b'},
          {'name': 'c', 'url': 'http://foobar.com/b/c'},
          ))

    def testVirtualHostingInFront(self):
        request = TestRequest()
        request.setViewType(IBrowserPresentation)

        root = Root()
        request._vh_root = ContextWrapper(root, root, name='')
        content = ContextWrapper(root, root,
                                 name='.',
                                 side_effect_name="++vh++abc")
        content = ContextWrapper(TrivialContent(), content, name='a')
        content = ContextWrapper(TrivialContent(), content, name='b')
        content = ContextWrapper(TrivialContent(), content, name='c')
        view = getView(content, 'absolute_url', request)
        self.assertEqual(str(view), 'http://foobar.com/a/b/c')

        breadcrumbs = view.breadcrumbs()
        self.assertEqual(breadcrumbs,
         ({'name':  '', 'url': 'http://foobar.com'},
          {'name': 'a', 'url': 'http://foobar.com/a'},
          {'name': 'b', 'url': 'http://foobar.com/a/b'},
          {'name': 'c', 'url': 'http://foobar.com/a/b/c'},
          ))


def test_suite():
    return makeSuite(TestAbsoluteURL)

if __name__=='__main__':
    main(defaultTest='test_suite')
