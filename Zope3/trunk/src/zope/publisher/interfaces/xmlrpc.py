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
"""Interfaces for the XMLRPC publisher.

$Id: xmlrpc.py,v 1.6 2004/03/19 20:26:44 srichter Exp $
"""
from zope.publisher.interfaces import IPublication
from zope.publisher.interfaces import IPublishTraverse
from zope.publisher.interfaces.http import IHTTPRequest


class IXMLRPCPublisher(IPublishTraverse):
    """XML-RPC Publisher"""


class IXMLRPCPublication(IPublication):
    """Object publication framework."""

    def getDefaultTraversal(request, ob):
        """Get the default published object for the request

        Allows a default view to be added to traversal.
        Returns (ob, steps_reversed).
        """

class IXMLRPCRequest(IHTTPRequest):
    """XML-RPC Request
    """
