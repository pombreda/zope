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
$Id: permissionroles.py,v 1.2 2004/03/05 18:39:07 srichter Exp $
"""

from zope.component import getAdapter
from zope.interface import implements

from zope.app.interfaces.security import IPermission
from zope.app.security.settings import Unset
from zope.app.securitypolicy.interfaces import IRolePermissionManager

class PermissionRoles:

    implements(IPermission)

    def __init__(self, permission, context, roles):
        self._permission = permission
        self._context    = context
        self._roles      = roles

    def getId(self):
        return self._permission.getId()

    def getTitle(self):
        return self._permission.getTitle()

    def getDescription(self):
        return self._permission.getDescription()

    def roleSettings(self):
        """
        Returns the list of setting names of each role for this permission.
        """
        prm = getAdapter(self._context, IRolePermissionManager)
        proles = prm.getRolesForPermission(self._permission.getId())
        settings = {}
        for role, setting in proles:
            settings[role] = setting.getName()
        nosetting = Unset.getName()
        return [settings.get(role.id, nosetting) for role in self._roles]
