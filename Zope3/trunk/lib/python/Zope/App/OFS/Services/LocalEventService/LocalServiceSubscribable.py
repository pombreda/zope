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
"""

Revision information:
$Id: LocalServiceSubscribable.py,v 1.5 2002/09/06 02:14:31 poster Exp $
"""

from Zope.Exceptions import NotFoundError
from Zope.Event.ISubscriptionAware import ISubscriptionAware
from Zope.Event.IEvent import IEvent
from Zope.ContextWrapper import ContextMethod
from Zope.Proxy.ProxyIntrospection import removeAllProxies
from Zope.Proxy.ContextWrapper import ContextWrapper
from LocalSubscribable import LocalSubscribable
from Persistence import Persistent
from Zope.App.ComponentArchitecture.NextService import getNextService

class LocalServiceSubscribable(LocalSubscribable, Persistent):
    """a local mix-in for services"""
    
    _serviceName = None # replace me
    
    def unsubscribe(wrapped_self,
                    subscriber,
                    event_type = None,
                    filter = None):
        # might be wrapped, might not
        subscriber = removeAllProxies(subscriber) 
        
        clean_self = removeAllProxies(wrapped_self)
        wrapped_subscriber = ContextWrapper(subscriber, wrapped_self)
        
        for subscriber_index in range(len(clean_self._subscribers)):
            sub = clean_self._subscribers[subscriber_index]
            if sub[0] == subscriber:
                ev_set = sub[1]
                break
        else:
            # raise NotFoundError(subscriber)
            getNextService(
                wrapped_self, clean_self._serviceName).unsubscribe(
                    subscriber, event_type, filter)
            return
        
        
        do_alert = ISubscriptionAware.isImplementedBy(subscriber)
        
        if event_type:
            ev_type = event_type
            if event_type is IEvent:
                ev_type = None # handle optimization
            if ev_type not in ev_set:
                getNextService(
                    wrapped_self, clean_self._serviceName).unsubscribe(
                    subscriber, event_type, filter)
            else:
                subscriptions = clean_self._registry.get(ev_type)
                try:
                    subscriptions.remove((subscriber, filter))
                except ValueError:
                    raise NotFoundError(subscriber, event_type, filter)
                if do_alert:
                    wrapped_subscriber.unsubscribedFrom(
                        wrapped_self, event_type, filter)
                if len(ev_set) == 1:
                    for sub in subscriptions:
                        if sub[0] == subscriber:
                            break
                    else:
                        del clean_self._subscribers[subscriber_index]
        else:
            for ev_type in ev_set:
                subscriptions = clean_self._registry.get(ev_type)
                subs = subscriptions[:]
                subscriptions[:] = []
                for sub in subs:
                    if sub[0] == subscriber: # deleted (not added back)
                        if do_alert:
                            wrapped_subscriber.unsubscribedFrom(
                                wrapped_self, ev_type or IEvent, sub[1])
                            # IEvent switch is to make optimization
                            # transparent
                    else: # kept (added back)
                        subscriptions.append(sub)
            del clean_self._subscribers[subscriber_index]
            getNextService(
                wrapped_self, clean_self._serviceName).unsubscribe(
                    subscriber, event_type, filter)
        clean_self._p_changed = 1 #trigger persistence
    
    unsubscribe = ContextMethod(unsubscribe)
    
    def listSubscriptions(wrapped_self, subscriber, event_type = None):
        # might be wrapped, might not
        subscriber = removeAllProxies(subscriber) 
        
        clean_self = removeAllProxies(wrapped_self)
        result = LocalSubscribable.listSubscriptions(
            clean_self, subscriber, event_type)
        result.extend(getNextService(
            wrapped_self, clean_self._serviceName).listSubscriptions(
                subscriber, event_type))
        return result
    
    listSubscriptions = ContextMethod(listSubscriptions)
