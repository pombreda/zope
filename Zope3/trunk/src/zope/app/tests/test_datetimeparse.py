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
import unittest
from zope.app.datetimeutils import parse, time, DateTimeError

class Test(unittest.TestCase):

    def testParse(self):
        from zope.app.datetimeutils import parse

        self.assertEqual(parse('1999 12 31')[:6],
                         (1999, 12, 31, 0, 0, 0))
        self.assertEqual(parse('1999 12 31 EST'),
                         (1999, 12, 31, 0, 0, 0, 'EST'))
        self.assertEqual(parse('Dec 31, 1999')[:6],
                         (1999, 12, 31, 0, 0, 0))
        self.assertEqual(parse('Dec 31 1999')[:6],
                         (1999, 12, 31, 0, 0, 0))
        self.assertEqual(parse('Dec 31 1999')[:6],
                         (1999, 12, 31, 0, 0, 0))
        self.assertEqual(parse('1999/12/31 1:2:3')[:6],
                         (1999, 12, 31, 1, 2, 3))
        self.assertEqual(parse('1999-12-31 1:2:3')[:6],
                         (1999, 12, 31, 1, 2, 3))
        self.assertEqual(parse('1999-12-31T01:02:03')[:6],
                         (1999, 12, 31, 1, 2, 3))
        self.assertEqual(parse('1999-31-12 1:2:3')[:6],
                         (1999, 12, 31, 1, 2, 3))
        self.assertEqual(parse('1999-31-12 1:2:3.456')[:5],
                         (1999, 12, 31, 1, 2))
        self.assertEqual(int(parse('1999-31-12 1:2:3.456')[5]*1000+.000001),
                         3456)
        self.assertEqual(parse('1999-12-31T01:02:03.456')[:5],
                         (1999, 12, 31, 1, 2))
        self.assertEqual(int(parse('1999-12-31T01:02:03.456')[5]*1000+.000001),
                         3456)
        self.assertEqual(parse('Tue, 24 Jul 2001 09:41:03 -0400'),
                         (2001, 7, 24, 9, 41, 3, '-0400'))
        self.assertEqual(parse('1999-12-31T01:02:03.456-12')[6], '-1200')
        self.assertEqual(parse('1999-12-31T01:02:03.456+0030')[6], '+0030')
        self.assertEqual(parse('1999-12-31T01:02:03.456-00:30')[6], '-0030')

    def testTime(self):
        from time import gmtime
        from zope.app.datetimeutils import time
        self.assertEqual(gmtime(time('1999 12 31 GMT'))[:6],
                         (1999, 12, 31, 0, 0, 0))
        self.assertEqual(gmtime(time('1999 12 31 EST'))[:6],
                         (1999, 12, 31, 5, 0, 0))
        self.assertEqual(gmtime(time('1999 12 31 -0500'))[:6],
                         (1999, 12, 31, 5, 0, 0))
        self.assertEqual(gmtime(time('1999-12-31T00:11:22Z'))[:6],
                         (1999, 12, 31, 0, 11, 22))
        self.assertEqual(gmtime(time('1999-12-31T01:11:22+01:00'))[:6],
                         (1999, 12, 31, 0, 11, 22))

    def testBad(self):
        from zope.app.datetimeutils import time, DateTimeError
        self.assertRaises(DateTimeError, parse, '1999')
        self.assertRaises(DateTimeError, parse, '1999-31-12 1:2:63.456')
        self.assertRaises(DateTimeError, parse, '1999-31-13 1:2:3.456')
        self.assertRaises(DateTimeError, parse, '1999-2-30 1:2:3.456')
        self.assertRaises(DateTimeError, parse, 'April 31, 1999 1:2:3.456')

    def testLeap(self):
        from zope.app.datetimeutils import time, DateTimeError
        self.assertRaises(DateTimeError, parse, '1999-2-29 1:2:3.456')
        self.assertRaises(DateTimeError, parse, '1900-2-29 1:2:3.456')
        self.assertEqual(parse('2000-02-29 1:2:3')[:6],
                         (2000, 2, 29, 1, 2, 3))
        self.assertEqual(parse('2004-02-29 1:2:3')[:6],
                         (2004, 2, 29, 1, 2, 3))

    def test_tzoffset(self):
        from zope.app.datetimeutils import _tzoffset
        self.assertEqual(_tzoffset('-0400', None), -4*60*60)
        self.assertEqual(_tzoffset('-0030', None), -30*60)
        self.assertEqual(_tzoffset('+0200', None), 2*60*60)
        self.assertEqual(_tzoffset('EET', None), 2*60*60)

    def testParseDatetimetz(self):
        from datetime import datetime
        from zope.app.datetimeutils import parseDatetimetz, tzinfo
        self.assertEqual(parseDatetimetz('1999-12-31T01:02:03.037-00:30'),
                         datetime(1999, 12, 31, 1, 2, 3, 37000, tzinfo(-30)))

def test_suite():
    loader=unittest.TestLoader()
    return loader.loadTestsFromTestCase(Test)

if __name__=='__main__':
    unittest.TextTestRunner().run(test_suite())
