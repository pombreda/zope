##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
$Id: test_traversers.py,v 1.1 2003/02/07 15:59:38 jim Exp $
"""
__metaclass__ = type

from unittest import TestCase, TestSuite, main, makeSuite
from zope.exceptions import NotFoundError
from zope.app.http.traversal import ContainerTraverser, ItemTraverser
from zope.publisher.browser import TestRequest
from zope.app.http.put import NullResource

class Items:

    def __init__(self, data):
        self.data = data

    def __getitem__(self, name):
        return self.data[name]

class Container(Items):

    def get(self, name, default=None):
        return self.data.get(name, default)
    

class TestContainer(TestCase):

    Container = Container
    Traverser = ContainerTraverser

    def testSubobject(self):
        container = self.Container({'foo': 42})
        request = TestRequest()
        traverser = self.Traverser(container, request)
        self.assertEqual(traverser.publishTraverse(request, 'foo'), 42)

    def testNotFound(self):
        container = self.Container({'foo': 42})
        request = TestRequest()
        traverser = self.Traverser(container, request)
        self.assertRaises(NotFoundError,
                          traverser.publishTraverse, request, 'bar')
    

    def testNull(self):
        container = self.Container({'foo': 42})
        request = TestRequest()
        request.method = 'PUT'
        traverser = self.Traverser(container, request)
        null = traverser.publishTraverse(request, 'bar')
        self.assertEqual(null.__class__, NullResource)
        self.assertEqual(null.container, container)
        self.assertEqual(null.name, 'bar')
        

class TestItem(TestContainer):

    Container = Items
    Traverser = ItemTraverser
    

def test_suite():
    return TestSuite((
        makeSuite(TestContainer),
        makeSuite(TestItem),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')
