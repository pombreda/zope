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

Revision information:
$Id: test_contents.py,v 1.2 2002/12/25 14:12:30 jim Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite
from zope.app.tests.placelesssetup import PlacelessSetup
from zope.component.adapter import provideAdapter

from zope.app.interfaces.container import IZopeContainer
from zope.app.interfaces.container import IContainer
from zope.app.container.zopecontainer import ZopeContainerAdapter

from zope.app.event.tests.placelesssetup import getEvents
from zope.app.interfaces.event import IObjectRemovedEvent, IObjectModifiedEvent
from zope.interface import Interface
from zope.proxy.introspection import removeAllProxies


class BaseTestContentsBrowserView(PlacelessSetup):
    """Base class for testing browser contents.

    Subclasses need to define a method, '_TestView__newContext', that
    takes no arguments and that returns a new empty test view context.

    Subclasses need to define a method, '_TestView__newView', that
    takes a context object and that returns a new test view.
    """

    def setUp(self):
        PlacelessSetup.setUp(self)
        provideAdapter(IContainer, IZopeContainer, ZopeContainerAdapter)


    def testInfo(self):
        # Do we get the correct information back from ContainerContents?
        container = self._TestView__newContext()
        subcontainer = self._TestView__newContext()
        container.setObject( 'subcontainer', subcontainer )
        document = Document()
        container.setObject( 'document', document )

        fc = self._TestView__newView( container )
        info_list = fc.listContentInfo()

        self.assertEquals( len( info_list ), 2 )

        ids = map( lambda x: x['id'], info_list )
        self.assert_( 'subcontainer' in ids )

        objects = map( lambda x: x['object'], info_list )
        self.assert_( subcontainer in objects )

        urls = map( lambda x: x['url'], info_list )
        self.assert_( 'subcontainer' in urls )

        self.failIf( filter( None, map( lambda x: x['icon'], info_list ) ) )

    def testInfoWDublinCore(self):
        container = self._TestView__newContext()
        document = Document()
        container.setObject( 'document', document )

        from datetime import datetime
        from zope.app.interfaces.dublincore import IZopeDublinCore
        from zope.app.browser.container.contents \
            import formatTime, getSize
        class FauxDCAdapter:
            __implements__ = IZopeDublinCore

            def __init__(self, context):
                pass
            title = 'faux title'
            size = 1024
            created = datetime(2001, 1, 1, 1, 1, 1)
            modified = datetime(2002, 2, 2, 2, 2, 2)

        from zope.component.adapter \
             import provideAdapter
        provideAdapter(IDocument, IZopeDublinCore, FauxDCAdapter)

        fc = self._TestView__newView( container )
        info = fc.listContentInfo()[0]

        self.assertEqual(info['id'], 'document')
        self.assertEqual(info['url'], 'document')
        self.assertEqual(info['object'], document)
        self.assertEqual(info['title'], 'faux title')
        size,label=info['size']['size'],info['size']['label']
        self.assertEqual((size,label), getSize(FauxDCAdapter.size))
        self.assertEqual(info['created'], formatTime(FauxDCAdapter.created))
        self.assertEqual(info['modified'], formatTime(FauxDCAdapter.modified))

    def testObjectSize(self):
        from zope.app.browser.container.contents import getSize
        class SizeableObject:
            def __init__(self, size=0):
                self.size=size
            def getSize(self):
                return self.size
        self.assertEqual(getSize(SizeableObject(0)), (0, u'1 KB') )
        self.assertEqual(getSize(SizeableObject(2048)), (2048, u'2 KB') )
        self.assertEqual(getSize(SizeableObject(2000000)),(2000000,u'1.91 MB'))
        self.assertEqual(getSize(SizeableObject('bob')), (0,u'N/A'))
        self.assertEqual(getSize('dobbs'), (0,u'N/A'))


    def testRemove( self ):
        container = self._TestView__newContext()
        subcontainer = self._TestView__newContext()
        container.setObject('subcontainer', subcontainer)
        document = Document()
        container.setObject('document', document)
        document2 = Document()
        container.setObject('document2', document2)

        fc = self._TestView__newView( container )

        self.failIf(getEvents(IObjectModifiedEvent))
        self.failIf(getEvents(IObjectRemovedEvent))

        fc.removeObjects(['document2'])

        self.failUnless(
            getEvents(IObjectRemovedEvent,
                      filter =
                      lambda event:
                      removeAllProxies(event.object) == document2)
            )
        self.failUnless(
            getEvents(IObjectModifiedEvent,
                      filter =
                      lambda event:
                      removeAllProxies(event.object) == container)
            )

        info_list = fc.listContentInfo()

        self.assertEquals( len( info_list ), 2 )

        ids = map( lambda x: x['id'], info_list )
        self.assert_( 'subcontainer' in ids )

        objects = map( lambda x: x['object'], info_list )
        self.assert_( subcontainer in objects )

        urls = map( lambda x: x['url'], info_list )
        self.assert_( 'subcontainer' in urls )


class IDocument(Interface):
    pass

class Document:
    __implements__ = IDocument


class Test(BaseTestContentsBrowserView, TestCase):

    def _TestView__newContext(self):
        from zope.app.container.sample import SampleContainer
        return SampleContainer()

    def _TestView__newView(self, container):
        from zope.app.browser.container.contents import Contents
        from zope.publisher.browser import TestRequest
        return Contents(container, TestRequest())

def test_suite():
    return makeSuite(Test)

if __name__=='__main__':
    main(defaultTest='test_suite')
