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
"""Hooks for getting and setting a site in the thread global namespace.

$Id$
"""
import zope.component
from zope.component import getService
from zope.component.interfaces import IServiceService
from zope.app.site.interfaces import ISite
from zope.component.service import serviceManager
from zope.component.exceptions import ComponentLookupError
from zope.proxy import removeAllProxies
from zope.security.proxy import trustedRemoveSecurityProxy
from zope.app.traversing.interfaces import IContainmentRoot
from zope.app.location.interfaces import ILocation
from zope.app.location import locate
from zope.component.servicenames import Presentation
from zope.interface import Interface
from zope.component.servicenames import Adapters
import warnings
import zope.thread

class read_property(object):
    def __init__(self, func):
        self.func = func

    def __get__(self, inst, cls):
        if inst is None:
            return self

        return self.func(inst)

class SiteInfo(zope.thread.local):
    site = None
    services = serviceManager

    def adapter_hook(self):
        services = self.services
        adapters = services.getService(Adapters)
        adapter_hook = adapters.adapter_hook
        self.adapter_hook = adapter_hook
        return adapter_hook
    
    adapter_hook = read_property(adapter_hook)

siteinfo = SiteInfo()

def setSite(site=None):
    if site is None:
        services = serviceManager
    else:
        site = trustedRemoveSecurityProxy(site)
        services = site.getSiteManager()

    siteinfo.site = site
    siteinfo.services = services
    try:
        del siteinfo.adapter_hook
    except AttributeError:
        pass
    
def getSite():
    return siteinfo.site
    
def getServices_hook(context=None):

    if context is None:
        return siteinfo.services

    # Deprecated support for a context that isn't adaptable to
    # IServiceService.  Return the default service manager.
    try:
        return trustedRemoveSecurityProxy(IServiceService(context,
                                                          serviceManager))
    except ComponentLookupError:
        return serviceManager

def adapter_hook(interface, object, name='', default=None):
    try:
        return siteinfo.adapter_hook(interface, object, name, default)
    except ComponentLookupError:
        return default
    
def queryView(object, name, request, default=None,
              providing=Interface, context=None):
    views = getService(Presentation, context)
    view = views.queryView(object, name, request, default=default,
                           providing=providing)
    if ILocation.providedBy(view):
        locate(view, object, name)

    return view


def setHooks():
    # Hook up a new implementation of looking up views.
    zope.component.getServices.sethook(getServices_hook)
    zope.component.adapter_hook.sethook(adapter_hook)
    zope.component.queryView.sethook(queryView)

def resetHooks():
    # Reset hookable functions to original implementation.
    zope.component.getServices.reset()
    zope.component.adapter_hook.reset()
    zope.component.queryView.reset()
    
