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
"""Tests creator annotation.

$Id: test_creatorannotator.py,v 1.11 2004/03/13 15:21:15 srichter Exp $
"""
from unittest import TestCase, TestSuite, main, makeSuite
from zope.app.site.tests.placefulsetup import PlacefulSetup
from zope.testing.cleanup import CleanUp

from zope.interface import Interface, implements
from zope.app.tests import ztapi

from zope.app.dublincore.creatorannotator import CreatorAnnotator
from zope.app.dublincore.interfaces import IZopeDublinCore
from zope.app.security.interfaces import IPrincipal
from zope.app.event.interfaces import IEvent
from zope.security.management import noSecurityManager, newSecurityManager

class IDummyContent(Interface):
    pass

class DummyEvent:
    implements(IEvent)

class DummyDCAdapter(object):

    __used_for__ = IDummyContent
    implements(IZopeDublinCore)

    def _getcreator(self):
        return self.context.creators

    def _setcreator(self, value):
        self.context.creators = value
    creators = property(_getcreator,_setcreator,None,"Adapted Creators")

    def __init__(self, context):
        self.context = context
        self.creators = context.creators


class DummyDublinCore:

    implements(IDummyContent)

    creators = ()

class DummyPrincipal:
    implements(IPrincipal)

    def __init__(self, id, title, description):
        self.id = id
        self.title = title
        self.description = description


class Test(PlacefulSetup, TestCase, CleanUp):

    def setUp(self):
        PlacefulSetup.setUp(self)
        ztapi.provideAdapter(IDummyContent, IZopeDublinCore, DummyDCAdapter)
        noSecurityManager()

    def tearDown(self):
        noSecurityManager()
        PlacefulSetup.tearDown(self)

    def test_creatorannotation(self):

        # Create stub event and DC object
        event = DummyEvent()
        data = DummyDublinCore()
        event.object = data

        good_author = DummyPrincipal('goodauthor', 'the good author',
                                     'this is a very good author')

        bad_author = DummyPrincipal('badauthor', 'the bad author',
                                    'this is a very bad author')

        # Check what happens if no user is there
        noSecurityManager()
        CreatorAnnotator.notify(event)
        self.assertEqual(data.creators,())

        # Let the bad edit it first
        security = newSecurityManager(bad_author)
        CreatorAnnotator.notify(event)

        self.failIf(len(data.creators) != 1)
        self.failUnless(bad_author.id in data.creators)

        # Now let the good edit it
        security = newSecurityManager(good_author)
        CreatorAnnotator.notify(event)

        self.failIf(len(data.creators) != 2)
        self.failUnless(good_author.id in data.creators)
        self.failUnless(bad_author.id in data.creators)

        # Let the bad edit it again
        security = newSecurityManager(bad_author)
        CreatorAnnotator.notify(event)

	# Check that the bad author hasn't been added twice.
        self.failIf(len(data.creators) != 2)
        self.failUnless(good_author.id in data.creators)
        self.failUnless(bad_author.id in data.creators)

def test_suite():
    return TestSuite((
        makeSuite(Test),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')
