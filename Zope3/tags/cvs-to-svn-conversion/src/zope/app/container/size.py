
##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
"""Adapters that give the size of an object.

$Id: size.py,v 1.5 2004/03/03 11:03:57 philikon Exp $
"""
from zope.app.i18n import ZopeMessageIDFactory as _
from zope.app.size.interfaces import ISized
from zope.interface import implements

__metaclass__ = type

class ContainerSized:

    implements(ISized)

    def __init__(self, container):
        self._container = container

    def sizeForSorting(self):
        """See ISized"""
        return ('item', len(self._container))

    def sizeForDisplay(self):
        """See ISized"""
        num_items = len(self._container)
        if num_items == 1:
            return _('1 item')
        size = _('${items} items')
        size.mapping = {'items': str(num_items)}
        return size
