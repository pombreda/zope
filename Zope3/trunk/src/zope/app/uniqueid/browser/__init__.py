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
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""
Unique id utility views.

$Id$
"""
from zope.security.proxy import trustedRemoveSecurityProxy
from zope.app import zapi

class UniqueIdUtilityView:

    def len(self):
        return len(trustedRemoveSecurityProxy(self.context).refs)

    def populate(self):
        self.context.register(zapi.traverse(self.context, "/"))
        self.context.register(zapi.traverse(self.context, "/++etc++site"))

    def items(self):
        return [(uid, zapi.getPath(ref())) for uid, ref in self.context.items()]

