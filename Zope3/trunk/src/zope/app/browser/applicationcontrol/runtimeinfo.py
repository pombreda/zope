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
"""Define runtime information view component for Application Control

$Id: runtimeinfo.py,v 1.3 2003/04/08 20:35:25 gotcha Exp $
"""

from zope.publisher.browser import BrowserView
from zope.app.interfaces.applicationcontrol.runtimeinfo import IRuntimeInfo
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.component import getAdapter
from zope.component import ComponentLookupError


class RuntimeInfoView(BrowserView):

    def runtimeInfo(self):
        formatted = {}  # will contain formatted runtime information

        try:
            runtime_info = getAdapter(self.context, IRuntimeInfo)
            formatted['ZopeVersion'] = runtime_info.getZopeVersion()
            formatted['PythonVersion'] = runtime_info.getPythonVersion()
            formatted['PythonPath'] = runtime_info.getPythonPath()
            formatted['SystemPlatform'] = " ".join(runtime_info.getSystemPlatform())
            formatted['CommandLine'] = " ".join(runtime_info.getCommandLine())
            formatted['ProcessId'] = runtime_info.getProcessId()

            # make a unix "uptime" uptime format
            uptime = runtime_info.getUptime()
            days = int(uptime / (60*60*24))
            uptime = uptime - days * (60*60*24)

            hours = int(uptime / (60*60))
            uptime = uptime - hours * (60*60)

            minutes = int(uptime / 60)
            uptime = uptime - minutes * 60

            seconds = uptime
            # XXX Uptime still to be localized
            formatted['Uptime'] = "%s%02d:%02d:%02d" % (
                ((days or "") and "%d days, " % days), hours, minutes, seconds)

        except ComponentLookupError:
            # XXX We avoid having errors in the ApplicationController,
            # because all those things need to stay accessible.
            # Everybody ok with that?
            formatted['ZopeVersion'] = "N/A"
            formatted['PythonVersion'] = "N/A"
            formatted['PythonPath'] = "N/A"
            formatted['SystemPlatform'] = "N/A"
            formatted['CommandLine'] = "N/A"
            formatted['ProcessId'] = "N/A"
            formatted['Uptime'] = "N/A"
            formatted['Hint'] = "Could not retrieve runtime information."


        return formatted

    index = ViewPageTemplateFile('runtimeinfo.pt')
