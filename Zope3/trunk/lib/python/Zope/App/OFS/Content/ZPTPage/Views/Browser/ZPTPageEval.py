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
"""Define view component for ZPT page eval results.

$Id: ZPTPageEval.py,v 1.4 2002/11/12 17:30:09 stevea Exp $
"""

from Zope.Publisher.Browser.BrowserView import BrowserView

class ZPTPageEval(BrowserView):

    def index(self, REQUEST=None, **kw):
        """Call a Page Template"""

        template = self.context

        if REQUEST is not None:
            REQUEST.response.setHeader('content-type',
                                       template.content_type)

        return template.render(REQUEST, **kw)

