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
"""Keyword-index search interface

$Id$
"""
from zope.interface import Interface

class IKeywordQuerying(Interface):
    """Query over a set of keywords, seperated by white space."""

    def search(query, operator='and'):
        """Execute a search given by 'query' as a list/tuple of
           (unicode) strings against the index. 'operator' can be either
           'and' or 'or' to search for all keywords or any keyword. 

           Return an IISet of docids
        """
