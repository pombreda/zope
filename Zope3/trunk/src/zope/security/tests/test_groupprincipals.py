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
"""Groups folder tests.

$Id: tests_groupprincipals.py 27237 2004-10-12 10:49:00 mriya3 $
"""


import unittest
from zope.testing.doctest import DocFileSuite

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(DocFileSuite('groups_principals.txt'))
    return suite
        
    
