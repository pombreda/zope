import os
import unittest
from zope.testing import doctest

from zope.app.testing.functional import FunctionalTestSetup, getRootFolder
from zope.app.testing import functional

ftesting_zcml = os.path.join(os.path.dirname(__file__), 'ftesting.zcml')
TestLayer = functional.ZCMLLayer(
                       ftesting_zcml, __name__, 'TestLayer')


optionflags = doctest.NORMALIZE_WHITESPACE + doctest.ELLIPSIS
extraglobs = dict(getRootFolder=getRootFolder)

def setUp(test):
    FunctionalTestSetup().setUp()

def tearDown(test):
    FunctionalTestSetup().tearDown()

def test_suite():
    suite = unittest.TestSuite()
    dottedname = 'mars.view.ftests.%s'
    for name in ['layout', 'template', 'pagelet']:
        test = doctest.DocTestSuite(
                    dottedname % name, setUp=setUp, extraglobs=extraglobs,
                    tearDown=tearDown, optionflags=optionflags)
        test.layer = TestLayer
        suite.addTest(test)
    return suite
