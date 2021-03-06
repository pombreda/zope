import unittest

import zope
import zope.component

from zope.testing import doctest, doctestunit
from zope.app.testing import ztapi
from zope.app.testing.setup import placefulSetUp, placefulTearDown
from zope.app.file import File
from zope.app.folder import rootFolder

from zope.interface import classImplements
from zope.app import zapi

from zorg.live.testing import livePageSetUp
from zorg.comment.testing import commentSetUp
from zorg.comment import IAttributeAnnotableComments


def buildTestFile() :
    """ Returns a file that is located in a site. """
    root = rootFolder()
    root[u"file.txt"] = File()
    return root[u"file.txt"]
    
    
def setUpBrowserTests(test) :

    placefulSetUp()
    commentSetUp()
    livePageSetUp()
     
def tearDownBrowserTests(test) :

    placefulTearDown()
    


def test_suite():
    optionflags = doctest.NORMALIZE_WHITESPACE+doctest.ELLIPSIS
    globs = {'zope': zope,
             'zapi': zope.app.zapi,
             'pprint': doctestunit.pprint,
             'TestRequest': zope.publisher.browser.TestRequest}
 
    return unittest.TestSuite((
        doctest.DocFileSuite('README.txt', 
                                setUp=setUpBrowserTests, 
                                tearDown=tearDownBrowserTests,
                                globs=globs,
                                optionflags=optionflags
                             ),
                             
        doctest.DocTestSuite("zorg.live.demo.comment.comment", 
                                setUp=setUpBrowserTests, 
                                tearDown=tearDownBrowserTests,
                                optionflags=optionflags
                             ),
                             
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
