##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Viewlet tests

$Id: tests.py 39461 2005-10-15 10:45:13Z srichter $
"""
__docformat__ = 'restructuredtext'

import unittest
from Testing.ZopeTestCase import FunctionalDocFileSuite
from zope.app.testing import setup
from zope.interface import Interface
from zope.interface import implements
from zope.viewlet import interfaces
from OFS.SimpleItem import SimpleItem

class Content(SimpleItem):
    implements(Interface)

class UnitTestSecurityPolicy:
    """
        Stub out the existing security policy for unit testing purposes.
    """
    #
    #   Standard SecurityPolicy interface
    #
    def validate( self
                , accessed=None
                , container=None
                , name=None
                , value=None
                , context=None
                , roles=None
                , *args
                , **kw):
        return 1

    def checkPermission( self, permission, object, context) :
        return 1

class ILeftColumn(interfaces.IViewletManager):
    """Left column of my page."""

class INewColumn(interfaces.IViewletManager):
    """Left column of my page."""

class WeightBasedSorting(object):
    def sort(self, viewlets):
        return sorted(viewlets,
                      lambda x, y: cmp(x[1].weight, y[1].weight))

class Weather(object):
    weight = 0

class Stock(object):
    weight = 0
    def getStockTicker(self):
        return u'SRC $5.19'

class Sport(object):
    weight = 0
    def __call__(self):
        return u'Red Sox vs. White Sox'

def setUp(test):
    setup.placefulSetUp()

def tearDown(test):
    setup.placefulTearDown()

def test_suite():
    return unittest.TestSuite((
        FunctionalDocFileSuite('README.txt'),
        FunctionalDocFileSuite('directives.txt',
                     setUp=setUp, tearDown=tearDown
                     ),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
