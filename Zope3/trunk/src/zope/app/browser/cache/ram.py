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
"""RAMCache view

$Id: ram.py,v 1.4 2003/09/21 17:30:21 jim Exp $
"""
from zope.app.publisher.browser import BrowserView
from zope.app.interfaces.cache.ram import IRAMCache

class RAMCacheView(BrowserView):

    __used_for__ = IRAMCache

    def action(self, maxEntries=None, maxAge=None, cleanupInterval=None):
        self.context.update(maxEntries, maxAge, cleanupInterval)
        self.request.response.redirect('.')
