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
$Id: test_xmlnavigationviews.py,v 1.10 2004/02/20 09:19:39 philikon Exp $
"""

from unittest import TestCase, TestLoader, TextTestRunner

from zope.interface import implements
from zope.pagetemplate.tests.util import check_xml
from zope.publisher.browser import TestRequest
from zope.publisher.interfaces.browser import IBrowserPublisher

from zope.app.tests import ztapi
from zope.app.content.file import File
from zope.app.traversing import traverse
from zope.app.services.tests.eventsetup import EventSetup
from zope.app.browser.skins.rotterdam.tests import util
from zope.app.browser.skins.rotterdam.xmlobject \
     import ReadContainerXmlObjectView
from zope.app.interfaces.container import IReadContainer
from zope.app.browser.skins.rotterdam.xmlobject import XmlObjectView

class TestXmlObject(EventSetup, TestCase):
    
    def setUp(self):
        super(TestXmlObject, self).setUp()

    def testXMLTreeViews(self):
        rcxov = ReadContainerXmlObjectView
        treeView = rcxov(self.folder1, TestRequest()).singleBranchTree
        check_xml(treeView(), util.read_output('test1.xml'))

        treeView = rcxov(self.folder1, TestRequest()).children
        check_xml(treeView(), util.read_output('test2.xml'))

        treeView = rcxov(self.folder1_1_1, TestRequest()).children
        check_xml(treeView(), util.read_output('test3.xml'))
        
        treeView = rcxov(self.rootFolder, TestRequest()).children
        check_xml(treeView(), util.read_output('test4.xml'))

        file1 = File()
        self.folder1_1_1["file1"] = file1
        self.file1 = traverse(self.rootFolder,
                              '/folder1/folder1_1/folder1_1_1/file1')

        class ReadContainerView(ReadContainerXmlObjectView):
            implements(IBrowserPublisher)
            def browserDefault(self, request):
                return self, ()
            def publishTraverse(self, request, name):
                raise NotFoundError(self, name, request)
            def __call__(self):
                return self.singleBranchTree()
            
        ztapi.browserView(IReadContainer, 'singleBranchTree.xml',
                          ReadContainerView)

        treeView = rcxov(self.folder1_1_1, TestRequest()).singleBranchTree
        check_xml(treeView(), util.read_output('test5.xml'))

        treeView = XmlObjectView(self.file1, TestRequest()).singleBranchTree
        check_xml(treeView(), util.read_output('test5.xml'))


def test_suite():
    loader = TestLoader()
    return loader.loadTestsFromTestCase(TestXmlObject)

if __name__=='__main__':
    TextTestRunner().run(test_suite())
