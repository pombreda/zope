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
"""Widget for selecting permissions.

$Id: permissionwidget.py,v 1.3 2003/01/21 21:22:00 jim Exp $
"""

from zope.app.interfaces.browser.form import IBrowserWidget
from zope.app.browser.form import widget
from zope.component import getService

class BaseWidget:

    def _convert(self, permission_id):
        if type(permission_id) is unicode:
            try:
                permission_id = permission_id.encode('ascii')
            except UnicodeError, v:
                raise ConversionError("Invalid textual data", v)

        return permission_id

class SinglePermissionWidget(BaseWidget, widget.BrowserWidget):

    def __call__(self):
        search_name = self.name + ".search"
        search_string = self.request.form.get(search_name, '')

        service = getService(self.context.context, "Permissions")
        permissions = [p.getId() for p in service.getPermissions()]
        permissions.sort()
        if search_string:
            permissions = [permission
                           for permission in permissions
                           if permission.find(search_string)!=-1]

        select_name = self.name
        selected = self._showData()

        options = ['<option value=\"\">---select permission---</option>']
        for permission in permissions:
            options.append('<option value="%s"%s>%s</option>'
                           % (permission,
                              permission == selected and ' selected' or '',
                              permission)
                           )


        search_field = '<input type="text" name="%s" value=\"%s\">' % (
            search_name, search_string)
        select_field = '<select name="%s">%s</select>'  % (
            select_name, ''.join(options))

        HTML = search_field + select_field
        return HTML

class DisplayWidget(BaseWidget, widget.DisplayWidget):
    pass
