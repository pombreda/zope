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
"""Mutable Schema (as Utility) Views

$Id: schema.py,v 1.4 2003/09/21 17:31:11 jim Exp $
"""
from zope.app import zapi
from zope.app.browser.form.editview import EditView
from zope.app.form.utility import setUpEditWidgets
from zope.app.i18n import ZopeMessageIDFactory as _
from zope.app.interfaces.utilities.schema import IMutableSchema
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.publisher.browser import BrowserView
from zope.schema import getFieldNamesInOrder, getFieldsInOrder

class EditSchema(BrowserView):

    edit = ViewPageTemplateFile('edit.pt')
    errors = ()
    update_status = None

    def name(self):
        return self.context.getName()

    def fieldNames(self):
        return getFieldNamesInOrder(self.context)

    def fields(self):
        return [{'name': name,
                 'field': field,
                 'type': field.__class__.__name__}
                for name, field in getFieldsInOrder(self.context)]

    def update(self):
        status = ''
        container = zapi.getAdapter(self.context, IMutableSchema)

        if 'DELETE' in self.request:
            if not 'ids' in self.request:
                self.errors = (_("Must select a field to delete"),)
                status = _("An error occured.")
            for id in self.request.get('ids', []):
                container.removeField(id)

        self.update_status = status
        return status


class EditMutableSchema(EditView):

    def _get_schema(self):
        return self.context.mutableschema

    schema = property(_get_schema)

    def _setUpWidgets(self):
        adapted = zapi.getAdapter(self.context, self.schema)
        if adapted is not self.context:
            adapted.__parent__ = self.context
        setUpEditWidgets(self, self.schema, names=self.fieldNames,
                         content=self.adapted)
