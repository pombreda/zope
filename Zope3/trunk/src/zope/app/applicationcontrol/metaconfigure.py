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
""" Register ServerControl configuration directives.

$Id: metaconfigure.py,v 1.3 2003/07/31 21:37:18 srichter Exp $
"""

from zope.component import getUtility
from zope.app.interfaces.applicationcontrol import IServerControl
from zope.configuration.action import Action


def registerShutdownHook(_context, call, name, priority):
    """Register a shutdown hook with the current server control utility"""
    return [
        Action(
            discriminator = ('server-control:registerShutdownHook', name),
            callable = doRegisterShutdownHook,
            args = (_context, call, priority, name),
            )
        ]

def doRegisterShutdownHook(_context, call, priority, name):
    server_control = getUtility(_context, IServerControl)
    server_control.registerShutdownHook(_context.resolve(call), priority, name)
