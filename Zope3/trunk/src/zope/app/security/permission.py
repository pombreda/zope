##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
"""Permissions

$Id: permission.py,v 1.12 2004/04/11 18:16:31 jim Exp $
"""
from zope.interface import implements
from zope.schema import Enumerated, Field
from zope.schema.interfaces import ValidationError
from zope.security.checker import CheckerPublic
from zope.app import zapi
from zope.app.security.interfaces import IPermission, IPermissionField


class Permission(object):
    implements(IPermission)

    def __init__(self, id, title="", description=""):
        self.id = id
        self.title = title
        self.description = description


def checkPermission(context, permission_id):
    """Check whether a given permission exists in the provided context."""
    if permission_id == CheckerPublic:
        return
    if not zapi.queryUtility(context, IPermission, name=permission_id):
        raise ValueError("Undefined permission id", permission_id)


class PermissionField(Enumerated, Field):
    """A field that represents a permission in a schema"""
    implements(IPermissionField)

    def _validate(self, value):
        if value is CheckerPublic:
            return
        super(PermissionField, self)._validate(value)
        if zapi.queryUtility(self.context, IPermission, name=value) is None:
            raise ValidationError("Unknown permission", value)
