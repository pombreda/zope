##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Factory-related Tests

$Id: test_factory.py,v 1.2 2004/03/09 12:40:07 srichter Exp $
"""
import unittest
from zope.interface import Interface, implements

from zope.component import createObject, getFactoryInterfaces, getFactoriesFor
from zope.component.interfaces import IFactory
from zope.component.utility import utilityService
from zope.component.factory import Factory
from placelesssetup import PlacelessSetup

class IKlass(Interface):
    pass

class Klass(object):
    implements(IKlass)

    def __init__(self, *args, **kw):
        self.args = args
        self.kw = kw


class TestFactory(unittest.TestCase):

    def setUp(self):
        self._factory = Factory(Klass, 'Klass', 'Klassier')

    def testCall(self):
        kl = self._factory(3, foo=4)
        self.assert_(isinstance(kl, Klass))
        self.assertEqual(kl.args, (3, ))
        self.assertEqual(kl.kw, {'foo': 4})

    def testTitleDescription(self):
        self.assertEqual(self._factory.title, 'Klass')
        self.assertEqual(self._factory.description, 'Klassier')

    def testGetInterfaces(self):
        self.assertEqual(self._factory.getInterfaces(), [IKlass])
        
    
class TestFactoryZAPIFunctions(PlacelessSetup, unittest.TestCase):

    def setUp(self):
        super(TestFactoryZAPIFunctions, self).setUp()
        self.factory = Factory(Klass, 'Klass', 'Klassier')
        utilityService.provideUtility(IFactory, self.factory, 'klass')

    def testCreateObject(self):
        kl = createObject(None, 'klass', 3, foo=4)
        self.assert_(isinstance(kl, Klass))
        self.assertEqual(kl.args, (3, ))
        self.assertEqual(kl.kw, {'foo': 4})

    def testGetFactoryInterfaces(self):
        self.assertEqual(getFactoryInterfaces(None, 'klass'), [IKlass])

    def testGetFactoriesFor(self):
        self.assertEqual(getFactoriesFor(None, IKlass),
                         [('klass', self.factory)])
        

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(TestFactory),
        unittest.makeSuite(TestFactoryZAPIFunctions)
        ))

if __name__=='__main__':
    unittest.main(defaultTest='test_suite')

