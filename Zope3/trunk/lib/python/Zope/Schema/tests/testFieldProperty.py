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
$Id: testFieldProperty.py,v 1.2 2002/09/11 22:06:41 jim Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite

from Interface import Interface
from Zope.Schema import Float, Text, Bytes
from Zope.Schema.FieldProperty import FieldProperty
from Zope.Schema.Exceptions import ValidationError

class I(Interface):

    title = Text(description=u"Short summary", default=u'say something')
    weight = Float(min=0.0)
    code = Bytes(min_length=6, max_length=6, default='xxxxxx')

class C(object):

    title = FieldProperty(I['title'])
    weight = FieldProperty(I['weight'])
    code = FieldProperty(I['code'])

class Test(TestCase):

    def test(self):
        c = C()
        self.assertEqual(c.title, u'say something')
        self.assertEqual(c.weight, None)
        self.assertEqual(c.code, 'xxxxxx')
        self.assertRaises(ValidationError, setattr, c, 'title', 'foo')
        self.assertRaises(ValidationError, setattr, c, 'weight', 'foo')
        self.assertRaises(ValidationError, setattr, c, 'weight', -1.0)
        self.assertRaises(ValidationError, setattr, c, 'weight', 2)
        self.assertRaises(ValidationError, setattr, c, 'code', -1)
        self.assertRaises(ValidationError, setattr, c, 'code', 'xxxx')
        self.assertRaises(ValidationError, setattr, c, 'code', u'xxxxxx')

        c.title = u'c is good'
        c.weight = 10.0
        c.code = 'abcdef'

        self.assertEqual(c.title, u'c is good')
        self.assertEqual(c.weight, 10)
        self.assertEqual(c.code, 'abcdef')
        
        

def test_suite():
    return TestSuite((
        makeSuite(Test),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')
