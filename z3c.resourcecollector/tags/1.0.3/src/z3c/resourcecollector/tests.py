##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
__docformat__ = "reStructuredText"

import os
import doctest
import unittest

from zope.testing import doctest

from zope.testing.doctestunit import DocFileSuite, DocTestSuite


def test_suite():
    return unittest.TestSuite(
        (DocFileSuite('zcml.txt',
                  optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                  ),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

