##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Interfaces for stateful workflow.

$Id: interfaces.py,v 1.1 2004/04/24 23:18:24 srichter Exp $
"""
from zope.interface import Interface

class IContentFilterAdapter(Interface):

    def filterListByState(objList, state, workflow='default'):
        """Filter a list of objects according to given workflow and state

        objList  ... list of objects
        state    ... name of a state (of the given workflow) in which the result
                      objects must be
        workflow ... name of a workflow to which result objects must be attached
        """

    def filterObjectByState(object, state, workflow='default'):
        """Filter an object according to the given workflow and state."""


