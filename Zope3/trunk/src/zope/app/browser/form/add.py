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
$Id: add.py,v 1.25 2003/08/02 07:03:55 philikon Exp $
"""

import sys

from zope.schema.interfaces import ValidationError

from zope.app.interfaces.container import IAdding
from zope.app.event import publish
from zope.app.event.objectevent import ObjectCreatedEvent
from zope.app.interfaces.form import WidgetsError
from zope.app.form.utility import setUpWidgets, getWidgetsData
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.security.checker import defineChecker, NamesChecker
from zope.component import getAdapter
from zope.component.view import provideView
from zope.publisher.interfaces.browser import IBrowserPresentation
from zope.app.pagetemplate.simpleviewclass import SimpleViewClass
from zope.app.browser.form.submit import Update
from zope.app.browser.form.editview import EditView, normalize
from zope.app.publisher.browser.globalbrowsermenuservice \
     import menuItemDirective

class AddView(EditView):
    """Simple edit-view base class.

    Subclasses should provide a schema attribute defining the schema
    to be edited.
    """

    def _setUpWidgets(self):
        setUpWidgets(self, self.schema, names=self.fieldNames)

    def update(self):

        if self.update_status is not None:
            # We've been called before. Just return the previous result.
            return self.update_status

        if Update in self.request:

            self.update_status = ''
            try:
                data = getWidgetsData(self, self.schema,
                                      strict=True,
                                      names=self.fieldNames,
                                      set_missing=False)
                content = self.createAndAdd(data)
            except WidgetsError, errors:
                self.errors = errors
                self.update_status = u"An error occured."
                return self.update_status

            self.request.response.redirect(self.nextURL())

        return self.update_status

    def create(self, *args, **kw):
        """Do the actual instantiation.
        """
        return self._factory(*args, **kw)

    def createAndAdd(self, data):
        """Add the desired object using the data in the data argument.

        The data argument is a dictionary with the data entered in the form.
        """
        
        args = []
        if self._arguments:
            for name in self._arguments:
                args.append(data[name])

        kw = {}
        if self._keyword_arguments:
            for name in self._keyword_arguments:
                if name in data:
                    kw[str(name)] = data[name]

        content = self.create(*args, **kw)
        adapted = getAdapter(content, self.schema, context=self.context)

        errors = []

        for name in self._set_before_add:
            if name in data:
                field = self.schema[name]
                try:
                    field.set(adapted, data[name])
                except ValidationError:
                    errors.append(sys.exc_info()[1])

        if errors:
            raise WidgetsError(*errors)

        publish(self.context, ObjectCreatedEvent(content))

        content = self.add(content)

        adapted = getAdapter(content, self.schema)

        for name in self._set_after_add:
            if name in data:
                field = self.schema[name]
                try:
                    field.set(adapted, data[name])
                except ValidationError:
                    errors.append(sys.exc_info()[1])

        if errors:
            raise WidgetsError(*errors)

        return content

    def add(self, content):
        return self.context.add(content)

    def nextURL(self):

        return self.context.nextURL()


def AddViewFactory(name, schema, label, permission, layer,
                   template, default_template, bases, for_,
                   fields, content_factory, arguments,
                   keyword_arguments, set_before_add, set_after_add):

    class_  = SimpleViewClass(
        template,
        used_for = schema, bases = bases
        )

    class_.schema = schema
    class_.label = label
    class_.fieldNames = fields
    class_._factory = content_factory
    class_._arguments = arguments
    class_._keyword_arguments = keyword_arguments
    class_._set_before_add = set_before_add
    class_._set_after_add = set_after_add

    class_.generated_form = ViewPageTemplateFile(default_template)

    defineChecker(class_,
                  NamesChecker(
                    ("__call__", "__getitem__", "browserDefault"),
                    permission,
                    )
                  )

    provideView(for_, name, IBrowserPresentation, class_, layer)


def add(_context, name, schema, content_factory='', label='',
        permission = 'zope.Public', layer = "default",
        class_ = None, for_ = IAdding,
        template = None, fields=None, arguments=None, keyword_arguments=None,
        set_before_add=None, set_after_add=None,
        menu=None, title=None, description=''):

    # Handle menu attrs. We do this now to rather than later becaise
    # menuItemDirective expects a dotted name for for_. 
    if menu or title:
        if (not menu) or (not title):
            raise ValueError("If either menu or title are specified, "
                             "they must both be specified")
        menuItemDirective(
            _context, menu, for_, '@@' + name, title,
            permission=permission, description=description)

    for_, bases, template, fields = normalize(
        for_, schema, class_, template, 'add.pt', fields, AddView)

    leftover = fields

    if arguments:
        missing = [n for n in arguments if n not in fields]
        if missing:
            raise ValueError("Some arguments are not included in the form",
                             missing)
        optional = [n for n in arguments if not schema[n].required]
        if optional:
            raise ValueError("Some arguments are optional, use"
                             " keyword_arguments for them",
                             optional)
        leftover = [n for n in leftover if n not in arguments]

    if keyword_arguments:
        missing = [n for n in keyword_arguments if n not in fields]
        if missing:
            raise ValueError(
                "Some keyword_arguments are not included in the form",
                missing)
        leftover = [n for n in leftover if n not in keyword_arguments]

    if set_before_add:
        missing = [n for n in set_before_add if n not in fields]
        if missing:
            raise ValueError(
                "Some set_before_add are not included in the form",
                missing)
        leftover = [n for n in leftover if n not in set_before_add]

    if set_after_add:
        missing = [n for n in set_after_add if n not in fields]
        if missing:
            raise ValueError(
                "Some set_after_add are not included in the form",
                missing)
        leftover = [n for n in leftover if n not in set_after_add]

        set_after_add += leftover

    else:
        set_after_add = leftover

    _context.action(
        discriminator = ('view', for_, name, IBrowserPresentation, layer),
        callable = AddViewFactory,
        args = (name, schema, label, permission, layer, template, 'add.pt',
                bases, for_, fields, content_factory, arguments,
                keyword_arguments, set_before_add, set_after_add),
        )
