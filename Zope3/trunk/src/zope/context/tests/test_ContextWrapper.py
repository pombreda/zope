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
"""XXX short summary goes here.

XXX longer description goes here.

$Id: test_ContextWrapper.py,v 1.1 2003/05/28 23:15:26 jim Exp $
"""

from zope.testing.doctestunit import DocTestSuite

def test_basic():
    """
    >>> from zope.security.checker import ProxyFactory, NamesChecker
    >>> checker = NamesChecker()
    >>> from zope.context import ContextWrapper, ContainmentIterator
    >>> from zope.context import getWrapperData

    >>> class C:
    ...    def __init__(self, name): self.name = name
    ...    def __repr__(self): return self.name

    >>> c1 = C('c1')

    >>> c2 = C('c2')
    >>> p2 = ProxyFactory(c2)
    >>> w2 = ContextWrapper(p2, c1, name=2)
    >>> int(type(w2) is type(p2))
    1
    >>> getWrapperData(w2)
    {'name': 2}
    
    >>> c3 = C('c3')
    >>> p3 = ProxyFactory(c3)
    >>> w3 = ContextWrapper(p3, w2, name=3)
    >>> int(type(w3) is type(p3))
    1
    >>> getWrapperData(w3)
    {'name': 3}

    >>> list(ContainmentIterator(w3))
    [c3, c2, c1]

    >>> w3x = ContextWrapper(w3, w2, name='x')
    >>> int(w3x is w3)
    1
    >>> getWrapperData(w3)
    {'name': 'x'}
    
    """

def test_suite(): return DocTestSuite()
if __name__ == '__main__': unittest.main()
