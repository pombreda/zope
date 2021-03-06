##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################
"""Default View Tests

$Id$
"""
import unittest
from zope.testing.cleanup import cleanUp
from zope.testing.doctestunit import DocTestSuite

def cleanUpDoc(args):
    cleanUp()

def test_suite():
    return DocTestSuite('zope.publisher.defaultview',
            setUp=cleanUpDoc, tearDown=cleanUpDoc)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
