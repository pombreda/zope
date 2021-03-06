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
"""Zope 3 Component Architecture

$Id$
"""
import sys
import types

from zope.interface import Interface
from zope.interface import implementedBy
from zope.interface import providedBy

from zope.component.interfaces import IComponentArchitecture
from zope.component.interfaces import IComponentRegistrationConvenience
from zope.component.interfaces import IFactory
from zope.component.interfaces import ComponentLookupError
from zope.component.interfaces import IComponentLookup
from zope.component._declaration import adaptedBy
from zope.component._declaration import adapter
from zope.component._declaration import adapts

# Use the C implementation in zope.hookable, if available;  fall back
# to our Python version if not.
try:
    from zope.hookable import hookable
except ImportError:
    from zope.component.hookable import hookable

# getSiteManager() returns a component registry.  Although the term
# "site manager" is deprecated in favor of "component registry",
# the old term is kept around to maintain a stable API.
base = None
@hookable
def getSiteManager(context=None):
    global base
    if context is None:
        if base is None:
            from zope.component.globalregistry import base
        return base
    else:
        # Use the global site manager to adapt context to `IComponentLookup`
        # to avoid the recursion implied by using a local `getAdapter()` call.
        try:
            return IComponentLookup(context)
        except TypeError, error:
            raise ComponentLookupError(*error.args)

# Adapter API

def getAdapterInContext(object, interface, context):
    adapter = queryAdapterInContext(object, interface, context)
    if adapter is None:
        raise ComponentLookupError(object, interface)
    return adapter

def queryAdapterInContext(object, interface, context, default=None):
    conform = getattr(object, '__conform__', None)
    if conform is not None:
        try:
            adapter = conform(interface)
        except TypeError:
            # We got a TypeError. It might be an error raised by
            # the __conform__ implementation, or *we* may have
            # made the TypeError by calling an unbound method
            # (object is a class).  In the later case, we behave
            # as though there is no __conform__ method. We can
            # detect this case by checking whether there is more
            # than one traceback object in the traceback chain:
            if sys.exc_info()[2].tb_next is not None:
                # There is more than one entry in the chain, so
                # reraise the error:
                raise
            # This clever trick is from Phillip Eby
        else:
            if adapter is not None:
                return adapter

    if interface.providedBy(object):
        return object

    return getSiteManager(context).queryAdapter(object, interface, '', default)

def getAdapter(object, interface=Interface, name=u'', context=None):
    adapter = queryAdapter(object, interface, name, None, context)
    if adapter is None:
        raise ComponentLookupError(object, interface, name)
    return adapter

def queryAdapter(object, interface=Interface, name=u'', default=None,
                 context=None):
    if context is None:
        return adapter_hook(interface, object, name, default)
    return getSiteManager(context).queryAdapter(object, interface, name,
                                                default)

def getMultiAdapter(objects, interface=Interface, name=u'', context=None):
    adapter = queryMultiAdapter(objects, interface, name, context=context)
    if adapter is None:
        raise ComponentLookupError(objects, interface, name)
    return adapter

def queryMultiAdapter(objects, interface=Interface, name=u'', default=None,
                      context=None):
    try:
        sitemanager = getSiteManager(context)
    except ComponentLookupError:
        # Oh blast, no site manager. This should *never* happen!
        return default

    return sitemanager.queryMultiAdapter(objects, interface, name, default)

def getAdapters(objects, provided, context=None):
    try:
        sitemanager = getSiteManager(context)
    except ComponentLookupError:
        # Oh blast, no site manager. This should *never* happen!
        return []
    return sitemanager.getAdapters(objects, provided)

def subscribers(objects, interface, context=None):
    try:
        sitemanager = getSiteManager(context)
    except ComponentLookupError:
        # Oh blast, no site manager. This should *never* happen!
        return []
    return sitemanager.subscribers(objects, interface)

def handle(*objects):
    sitemanager = getSiteManager(None)
    # iterating over subscribers assures they get executed
    for ignored in sitemanager.subscribers(objects, None):
        pass

#############################################################################
# Register the component architectures adapter hook, with the adapter hook
# registry of the `zope.inteface` package. This way we will be able to call
# interfaces to create adapters for objects. For example, `I1(ob)` is
# equvalent to `getAdapterInContext(I1, ob, '')`.
@hookable
def adapter_hook(interface, object, name='', default=None):
    try:
        sitemanager = getSiteManager()
    except ComponentLookupError:
        # Oh blast, no site manager. This should *never* happen!
        return None
    return sitemanager.queryAdapter(object, interface, name, default)

import zope.interface.interface
zope.interface.interface.adapter_hooks.append(adapter_hook)
#############################################################################


# Utility API

def getUtility(interface, name='', context=None):
    utility = queryUtility(interface, name, context=context)
    if utility is not None:
        return utility
    raise ComponentLookupError(interface, name)

def queryUtility(interface, name='', default=None, context=None):
    return getSiteManager(context).queryUtility(interface, name, default)

def getUtilitiesFor(interface, context=None):
    return getSiteManager(context).getUtilitiesFor(interface)


def getAllUtilitiesRegisteredFor(interface, context=None):
    return getSiteManager(context).getAllUtilitiesRegisteredFor(interface)


_marker = object()

def queryNextUtility(context, interface, name='', default=None):
    """Query for the next available utility.

    Find the next available utility providing `interface` and having the
    specified name. If no utility was found, return the specified `default`
    value.
    """
    sm = getSiteManager(context)
    bases = sm.__bases__
    for base in bases:
        util = base.queryUtility(interface, name, _marker)
        if util is not _marker:
            return util
    return default


def getNextUtility(context, interface, name=''):
    """Get the next available utility.

    If no utility was found, a `ComponentLookupError` is raised.
    """
    util = queryNextUtility(context, interface, name, _marker)
    if util is _marker:
        raise zope.component.interfaces.ComponentLookupError(
              "No more utilities for %s, '%s' have been found." % (
                  interface, name))
    return util


# Factories

def createObject(__factory_name, *args, **kwargs):
    context = kwargs.pop('context', None)
    return getUtility(IFactory, __factory_name, context)(*args, **kwargs)

def getFactoryInterfaces(name, context=None):
    return getUtility(IFactory, name, context).getInterfaces()

def getFactoriesFor(interface, context=None):
    utils = getSiteManager(context)
    for (name, factory) in utils.getUtilitiesFor(IFactory):
        interfaces = factory.getInterfaces()
        try:
            if interfaces.isOrExtends(interface):
                yield name, factory
        except AttributeError:
            for iface in interfaces:
                if iface.isOrExtends(interface):
                    yield name, factory
                    break
