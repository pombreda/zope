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
""" Define Zope\'s default security policy

$Id: ZopeSecurityPolicy.py,v 1.5 2002/07/16 23:41:17 jim Exp $
"""
__version__='$Revision: 1.5 $'[11:-2]

from Zope.ComponentArchitecture import queryAdapter
from Zope.Proxy.ContextWrapper import ContainmentIterator
from Zope.Exceptions import Unauthorized, Forbidden
from Zope.Security.ISecurityPolicy import ISecurityPolicy
from Zope.App.Security.IRolePermissionManager \
     import IRolePermissionManager, IRolePermissionMap
from Zope.App.Security.IPrincipalPermissionManager \
    import IPrincipalPermissionManager, IPrincipalPermissionMap
from Zope.App.Security.IPrincipalRoleManager \
    import IPrincipalRoleManager, IPrincipalRoleMap
from Zope.App.Security.IRolePermissionManager import IRolePermissionManager
from Zope.App.Security.Registries.PermissionRegistry import permissionRegistry 
from Zope.App.Security.Registries.PrincipalRegistry import principalRegistry 
from Zope.App.Security.Registries.RoleRegistry import roleRegistry
from Zope.App.Security.Grants.Global.PrincipalPermissionManager \
     import principalPermissionManager 
from Zope.App.Security.Grants.Global.RolePermissionManager \
     import rolePermissionManager 
from Zope.App.Security.Grants.Global.PrincipalRoleManager \
     import principalRoleManager
from Zope.App.Security.Settings import Allow, Deny

getPermissionsForPrincipal = \
                principalPermissionManager.getPermissionsForPrincipal
getPermissionsForRole      = rolePermissionManager.getPermissionsForRole
getRolesForPrincipal       = principalRoleManager.getRolesForPrincipal

globalContext=object()

class ZopeSecurityPolicy:

    __implements__ = ISecurityPolicy

    def __init__(self, ownerous=1, authenticated=1):
        """
            Two optional keyword arguments may be provided:

            ownerous -- Untrusted users can create code
                (e.g. Python scripts or templates),
                so check that code owners can access resources.
                The argument must have a truth value.
                The default is true.

            authenticated -- Allow access to resources based on the
                privaledges of the authenticated user.  
                The argument must have a truth value.
                The default is true.

                This (somewhat experimental) option can be set
                to false on sites that allow only public
                (unauthenticated) access. An anticipated
                scenario is a ZEO configuration in which some
                clients allow only public access and other
                clients allow full management.
        """
        
        self._ownerous=ownerous
        self._authenticated=authenticated

    def checkPermission(self, permission, object, context):
        # XXX We aren't really handling multiple principals yet

        # mapping from principal to set of roles
        principals = { context.user : {'Anonymous': Allow} }
        
        role_permissions = {}
        remove = {}
        orig = object

        # Look for placeless grants first.

        # get placeless principal permissions
        for principal in principals:
            for permission, setting in getPermissionsForPrincipal(principal):
                if setting is Deny:
                    return 0
                assert setting is Allow
                remove[principal] = 1


        # Clean out removed principals
        if remove:
            for principal in remove:
                del principals[principal]
            if principals:
                # not done yet
                remove.clear()
            else:
                # we've eliminated all the principals
                return 1


        # get placeless principal roles
        for principal in principals:
            roles = principals[principal]
            for role, setting in getRolesForPrincipal(principal):
                assert setting in (Allow, Deny)
                if role not in roles:
                    roles[role] = setting

        for perm, role, setting in (
            rolePermissionManager.getRolesAndPermissions()):
            assert setting in (Allow, Deny)
            if role not in role_permissions:
                role_permissions[role] = {perm: setting}
            else:
                if perm not in role_permissions[role]:
                    role_permissions[role][perm] = setting

        # Get principal permissions based on roles
        for principal in principals:
            roles = principals[principal]
            for role in roles:
                if role in role_permissions:
                    if permission in role_permissions[role]:
                        setting = role_permissions[role][permission]
                        if setting is Deny:
                            return 0
                        remove[principal] = 1


        # Clean out removed principals
        if remove:
            for principal in remove:
                del principals[principal]
            if principals:
                # not done yet
                remove.clear()
            else:
                # we've eliminated all the principals
                return 1


        # Look for placeful grants
        for object in ContainmentIterator(orig):

            # Copy specific principal permissions
            prinper = queryAdapter(object, IPrincipalPermissionMap)
            if prinper is not None:
                for principal in principals:
                    for permission, setting in (
                        prinper.getPermissionsForPrincipal(principal)):

                        if setting is Deny:
                            return 0

                        assert setting is Allow
                        remove[principal] = 1

            # Clean out removed principals
            if remove:
                for principal in remove:
                    del principals[principal]
                if principals:
                    # not done yet
                    remove.clear()
                else:
                    # we've eliminated all the principals
                    return 1
                
            # Collect principal roles
            prinrole = queryAdapter(object, IPrincipalRoleMap)
            if prinrole is not None:
                for principal in principals:
                    roles = principals[principal]
                    for role, setting in (
                        prinrole.getRolesForPrincipal(principal)):
                        assert setting in (Allow, Deny)
                        if role not in roles:
                            roles[role] = setting

            # Collect role permissions
            roleper = queryAdapter(object, IRolePermissionMap)
            if roleper is not None:
                for perm, role, setting in roleper.getRolesAndPermissions():
                    assert setting in (Allow, Deny)
                    if role not in role_permissions:
                        role_permissions[role] = {perm: setting}
                    else:
                        if perm not in role_permissions[role]:
                            role_permissions[role][perm] = setting

            # Get principal permissions based on roles
            for principal in principals:
                roles = principals[principal]
                for role in roles:
                    if role in role_permissions:
                        if permission in role_permissions[role]:
                            setting = role_permissions[role][permission]
                            if setting is Deny:
                                return 0
                            remove[principal] = 1

            # Clean out removed principals
            if remove:
                for principal in remove:
                    del principals[principal]
                if principals:
                    # not done yet
                    remove.clear()
                else:
                    # we've eliminated all the principals
                    return 1

        return 0 # deny by default


def permissionsOfPrincipal(principal, object):
    permissions = {}
    roles = {'Anonymous': Allow} # Everyone has anonymous
    role_permissions = {}
    orig = object

    # Make two passes.

    # First, collect what we know about the principal:


    # get placeless principal permissions
    for permission, setting in getPermissionsForPrincipal(principal):
        if permission not in permissions:
            permissions[permission] = setting

    # get placeless principal roles
    for role, setting in getRolesForPrincipal(principal):
        if role not in roles:
            roles[role] = setting

    # get placeful principal permissions and roles
    for object in ContainmentIterator(orig):

        # Copy specific principal permissions
        prinper = queryAdapter(object, IPrincipalPermissionMap)
        if prinper is not None:
            for permission, setting in prinper.getPermissionsForPrincipal(
                principal):
                if permission not in permissions:
                    permissions[permission] = setting

        # Collect principal roles
        prinrole = queryAdapter(object, IPrincipalRoleMap)
        if prinrole is not None:
            for role, setting in prinrole.getRolesForPrincipal(principal):
                if role not in roles:
                    roles[role] = setting

    # Second, update permissions using principal 

    for perm, role, setting in (
        rolePermissionManager.getRolesAndPermissions()):
        if role in roles and perm not in permissions:
            permissions[perm] = setting

    for object in ContainmentIterator(orig):

        # Collect role permissions
        roleper = queryAdapter(object, IRolePermissionMap)
        if roleper is not None:
            for perm, role, setting in roleper.getRolesAndPermissions():
                if role in roles and perm not in permissions:
                    permissions[perm] = setting



    result = [permission
              for permission in permissions
              if permissions[permission] is Allow]

    return result



zopeSecurityPolicy=ZopeSecurityPolicy()

