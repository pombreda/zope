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
"""Define view component for event service control.

$Id: error.py,v 1.8 2004/02/09 02:09:01 anthony Exp $
"""
from zope.app.services.error import ILocalErrorReportingService
from zope.publisher.browser import BrowserView
from zope.app import zapi
from zope.app.services.servicenames import ErrorLogging

class EditErrorLog:
    __used_for__ = ILocalErrorReportingService

    def updateProperties(self, keep_entries, copy_to_zlog=None,
                         ignored_exceptions=None):
        errorLog = self.context
        if copy_to_zlog is None:
            copy_to_zlog = 0
        errorLog.setProperties(keep_entries, copy_to_zlog, ignored_exceptions)
        return self.request.response.redirect('@@configure.html')


class ErrorRedirect(BrowserView):

    def action(self):
        err = zapi.getService(self, ErrorLogging)
        url = str(zapi.getView(err, 'absolute_url', self.request))
        url = url + "/@@SelectedManagementView.html"
        self.request.response.redirect(url)
