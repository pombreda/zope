##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Interfaces for session service."""

import re
from zope.interface import Interface
from zope import schema
from zope.i18n import MessageIDFactory
from zope.app.interfaces.container import IContainer

_ = MessageIDFactory("zope")

# XXX: These mapping interfaces should probably live somewhere like 
# zope.interface.common.mapping, but there are already similar but less
# useful ones defined there.
_missing = []
class IReadMapping(Interface):
    ''' Mapping methods for retrieving data '''
    def __getitem__(key): 'Return a value'
    def __contains__(key): 'True if there is a value for key'
    def get(key, default=_missing):
        'Return a value, or default if key not found'

class IWriteMapping(Interface):
    ''' Mapping methods for changing data '''
    def __delitem__(key): 'Delete a value'
    def __setitem__(key): 'Set a value'

class IIterableMapping(Interface):
    ''' Mapping methods for listing keys and values ''' 
    def __len__(key): 'Number of items in the IMapping'
    def __iter__(): 'Iterate over all the keys'
    def keys(): 'Return a sequence of the keys'
    def items(): 'Return a sequence of the (key, value) tuples'
    def values(): 'Return a sequence of the values'

class IFullMapping(IReadMapping, IWriteMapping, IIterableMapping):
    ''' Full mapping interface '''


class IBrowserIdManager(Interface):
    ''' Manages sessions - fake state over multiple browser requests. '''

    def getBrowserId(request):
        ''' Return the IBrowserId for the given request.

            If the request doesn't have an attached sessionId a new one will
            be generated.

            This will do whatever is possible to do the HTTP request to ensure
            the session id will be preserved. Depending on the specific
            method, further action might be necessary on the part of the user.
            See the documentation for the specific implementation and its
            interfaces.
        '''


    """ XXX: Want this
    def invalidate(browser_id):
        ''' Expire the browser_id, and remove any matching ISessionData data 
        '''
    """


class ICookieBrowserIdManager(IBrowserIdManager):
    ''' Manages sessions using a cookie '''

    namespace = schema.TextLine(
            title=_('Cookie Name'),
            description=_(
                "Name of cookie used to maintain state. "
                "Must be unique to the site domain name, and only contain "
                "ASCII letters, digits and '_'"
                ),
            required=True,
            min_length=1,
            max_length=30,
            constraint=re.compile("^[\d\w_]+$").search,
            )

    cookieLifeSeconds = schema.Int(
            title=_('Cookie Lifetime'),
            description=_(
                "Number of seconds until the browser expires the cookie. "
                "Leave blank to never expire the cookie. Set to 0 to expire "
                "the cookie when the browser is quit."
                ),
            min=0,
            required=False,
            default=None,
            missing_value=None,
            )


class IBrowserId(Interface):
    ''' A unique ID representing a session '''
    def __str__(): '''as a unique ASCII string'''


class ISessionDataContainer(IReadMapping, IWriteMapping):
    ''' Stores data objects for sessions. The object implementing this
        interface is responsible for expiring data as it feels appropriate.

        Used like:
            session_data_container[browser_id][product_id][key] = value

        Attempting to access a key that does not exist will raise a KeyError.
    '''
    timeout = schema.Int(
            title=_(u"Timeout"),
            description=_("Number of seconds before inactive data is removed"),
            default=3600,
            required=True,
            min=1,
            )


class ISession(IFullMapping):
    ''' To access bits of data within an ISessionDataContainer, we
        need to know the browser_id, the product_id, and the actual key.
        An ISession is a wrapper around an ISessionDataContainer that
        simplifies this by storing the browser_id and product_id enabling
        access using just the key.
    '''
    def __init__(session_data_container, browser_id, product_id):
        ''' Construct an ISession '''

