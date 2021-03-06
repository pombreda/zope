##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" Unit tests for Event module.

$Id$
"""

import unittest
import Testing

from DateTime import DateTime

from Products.CMFCore.testing import ConformsToContent
from Products.CMFCore.tests.base.testcase import RequestTest


class TestEvent(ConformsToContent, unittest.TestCase):

    def _getTargetClass(self):
        from Products.CMFCalendar.Event import Event

        return Event

    def _makeOne(self, *args, **kw):
        return self._getTargetClass()(*args, **kw)

    def test_z3interfaces(self):
        from zope.interface.verify import verifyClass
        from Products.CMFCalendar.interfaces import IEvent
        from Products.CMFCalendar.interfaces import IMutableEvent

        verifyClass(IEvent, self._getTargetClass())
        verifyClass(IMutableEvent, self._getTargetClass())

    def test_new(self):
        event = self._makeOne('test')

        self.assertEqual( event.getId(), 'test' )
        self.failIf( event.Title() )

    def test_edit(self):
        # Year month and day were processed in the wrong order
        # Also see http://collector.zope.org/CMF/202
        event = self._makeOne('foo')
        event.edit( title='title'
                  , description='description'
                  , eventType=( 'eventType', )
                  , effectiveDay=1
                  , effectiveMo=5
                  , effectiveYear=1999
                  , expirationDay=31
                  , expirationMo=12
                  , expirationYear=1999
                  , start_time="00:00"
                  , startAMPM="AM"
                  , stop_time="11:59"
                  , stopAMPM="PM"
                  )

        self.assertEqual( event.Title(), 'title' )
        self.assertEqual( event.Description(), 'description' )
        self.assertEqual( event.Subject(), ( 'eventType', ), event.Subject() )
        self.assertEqual( event.effective_date, None )
        self.assertEqual( event.expiration_date, None )
        self.assertEqual( event.end(), DateTime('1999/12/31 23:59') )
        self.assertEqual( event.start(), DateTime('1999/05/01 00:00') )
        self.failIf( event.contact_name )

    def test_puke(self):
        event = self._makeOne('shouldPuke')

        self.assertRaises( DateTime.DateError
                         , event.edit
                         , effectiveDay=31
                         , effectiveMo=2
                         , effectiveYear=1999
                         , start_time="00:00"
                         , startAMPM="AM"
                         )


class EventPUTTests(RequestTest):

    def _makeOne(self, id, *args, **kw):
        from Products.CMFCalendar.Event import Event

        # NullResource.PUT calls the PUT method on the bare object!
        return Event(id, *args, **kw)

    def test_PutWithoutMetadata(self):
        self.REQUEST['BODY'] = ''
        d = self._makeOne('foo')
        d.PUT(self.REQUEST, self.RESPONSE)

        self.assertEqual( d.Title(), '' )
        self.assertEqual( d.Format(), 'text/plain' )
        self.assertEqual( d.Description(), '' )
        self.assertEqual( d.Subject(), () )
        self.assertEqual( d.Contributors(), () )
        self.assertEqual( d.EffectiveDate(), 'None' )
        self.assertEqual( d.ExpirationDate(), 'None' )
        self.assertEqual( d.Language(), '' )
        self.assertEqual( d.Rights(), '' )


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(TestEvent),
        unittest.makeSuite(EventPUTTests),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
