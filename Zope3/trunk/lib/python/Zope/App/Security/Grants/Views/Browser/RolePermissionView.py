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

$Id: RolePermissionView.py,v 1.3 2002/06/25 10:30:24 efge Exp $
"""

import time
from Zope.App.PageTemplate import ViewPageTemplateFile
from Zope.Publisher.Browser.BrowserView import BrowserView
from Zope.ComponentArchitecture import getService, getAdapter
from Zope.App.Security.IRolePermissionManager import IRolePermissionManager
from Zope.App.Security.Grants.PermissionRoles import PermissionRoles
from Zope.App.Security.Grants.RolePermissions import RolePermissions
from Zope.App.Security.Settings import Unset, Allow, Deny

class RolePermissionView(BrowserView):

    index = ViewPageTemplateFile('manage_access.pt')
    manage_permissionForm = ViewPageTemplateFile('manage_permissionForm.pt')
    manage_roleForm = ViewPageTemplateFile('manage_roleForm.pt')

    def roles(self):
        roles = getattr(self, '_roles', None)
        if roles is None:
            roles = self._roles = getService(
                self.context, 'RoleService'
                ).getRoles()
        return roles

    def permissions(self):
        permissions = getattr(self, '_permissions', None)
        if permissions is None:
            permissions = self._permissions = getService(
                self.context, 'PermissionService'
                ).getPermissions()
        return permissions

    def availableSettings(self, noacquire=0):
        aq = {'id': Unset.getName(), 'shorttitle': ' ', 'title': 'Acquire'}
        rest = [{'id': Allow.getName(), 'shorttitle': '+', 'title': 'Allow'},
                {'id': Deny.getName(), 'shorttitle': '-', 'title': 'Deny'},
                ]
        if noacquire:
            return rest
        else:
            return [aq]+rest

    def permissionRoles(self):
        context = self.context
        roles = self.roles()
        return [PermissionRoles(permission, context, roles)
                for permission in self.permissions()]

    def permissionForID(self, pid):
        context = self.context
        roles = self.roles()
        perm = getService(context, 'PermissionService'
                          ).getPermission(pid)
        return PermissionRoles(perm, context, roles)

    def roleForID(self, rid):
        context = self.context
        permissions = self.permissions()
        role = getService(context, 'RoleService'
                          ).getRole(rid)
        return RolePermissions(role, context, permissions)

    def action(self, REQUEST, testing=None):
        roles       = [r.getId() for r in self.roles()]
        permissions = [p.getId() for p in self.permissions()]
        prm         = getAdapter(self.context, IRolePermissionManager)
        for ip in range(len(permissions)):
            rperm = REQUEST.get("p%s" % ip)
            if rperm not in permissions: continue
            for ir in range(len(roles)):
                rrole = REQUEST.get("r%s" % ir)
                if rrole not in roles: continue
                setting = REQUEST.get("p%sr%s" % (ip, ir), None)
                if setting is not None:
                    if setting == Unset.getName():
                        prm.unsetPermissionFromRole(rperm, rrole)
                    elif setting == Allow.getName():
                        prm.grantPermissionToRole(rperm, rrole)
                    elif setting == Deny.getName():
                        prm.denyPermissionToRole(rperm, rrole)
                    else:
                        raise ValueError("Incorrect setting: %s" % setting)

        if not testing:
            return self.index( REQUEST,
                message="Settings changed at %s" % time.ctime(time.time())
                )

    def update_permission(self, REQUEST, permission_id,
                          settings=(), testing=None):
        prm = getAdapter(self.context, IRolePermissionManager)
        roles = self.roles()
        rperm = permission_id
        for ir in range(len(roles)):
            rrole = roles[ir].getId()
            setting = settings[ir]
            if setting == Unset.getName():
                prm.unsetPermissionFromRole(rperm, rrole)
            elif setting == Allow.getName():
                prm.grantPermissionToRole(rperm, rrole)
            elif setting == Deny.getName():
                prm.denyPermissionToRole(rperm, rrole)
            else:
                raise ValueError("Incorrect setting: %s" % setting)

        if not testing:
            return self.index(REQUEST,
                              message="Settings changed at %s"
                                  % time.ctime(time.time())
                              )

    def update_role(self, REQUEST, role_id, testing=None):
        prm = getAdapter(self.context, IRolePermissionManager)
        allowed = REQUEST.get(Allow.getName(), ())
        denied = REQUEST.get(Deny.getName(), ())
        for permission in self.permissions():
            rperm = permission.getId()
            if rperm in allowed and rperm in denied:
                raise ValueError("Incorrect setting for %s" % rperm)
            if rperm in allowed:
                prm.grantPermissionToRole(rperm, role_id)
            elif rperm in denied:
                prm.denyPermissionToRole(rperm, role_id)
            else:
                prm.unsetPermissionFromRole(rperm, role_id)

        if not testing:
            return self.index(REQUEST,
                              message="Settings changed at %s"
                                  % time.ctime(time.time())
                              )

