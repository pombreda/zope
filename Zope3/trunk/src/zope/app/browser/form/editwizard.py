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
$Id: editwizard.py,v 1.1 2003/07/12 06:18:40 Zen Exp $
"""

import logging
from UserDict import UserDict
from zope.interface import implements, classProvides
from zope.publisher.interfaces.browser import IBrowserPresentation
from zope.component import getAdapter
from zope.app.publisher.browser.globalbrowsermenuservice \
     import menuItemDirective, globalBrowserMenuService
from zope.configuration.action import Action
from zope.configuration.interfaces import INonEmptyDirective
from zope.configuration.interfaces import ISubdirectiveHandler
from zope.app.pagetemplate.simpleviewclass import SimpleViewClass
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from editview import normalize, EditViewFactory, EditView
from zope.security.checker import defineChecker, NamesChecker
from zope.app.context import ContextWrapper
from zope.component.view import provideView
from zope.app.form.utility import setUpEditWidgets, getWidgetsData
from submit import Next, Previous, Update
from zope.app.interfaces.form import WidgetsError

PaneNumber = 'CURRENT_PANE_IDX'

# TODO: Needs to be persistent aware for session (?)
class WizardStorage(dict):
    def __init__(self, fields, content):
        super(WizardStorage, self).__init__(self)
        for k in fields:
            self[k] = getattr(content,k)

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError, key

    def __setattr__(self, key, value):
        self[key] = value

class WizardEditView(EditView):

    def _setUpWidgets(self):
        adapted = getAdapter(self.context, self.schema)
        if adapted is not self.context:
            adapted = ContextWrapper(adapted, self.context, name='(adapted)')
        self.adapted = adapted

        if self.use_session:
            raise NotImplementedError, 'use_storage'
        else:
            self.storage = WizardStorage(self.fieldNames, adapted)

        # Add all our widgets as attributes on this view
        setUpEditWidgets(
            self, self.schema, names=self.fieldNames, content=self.storage
            )

    def widgets(self):
        return [getattr(self, name+'_widget') 
            for name in self.currentPane().names
            ]

    _current_pane_idx = 0

    def currentPane(self):
        return self.panes[self._current_pane_idx]

    _update_called = 0

    def update(self):
        '''
        if not pane submitted, 
            current_pane = 0
        else
            if current_pane is valid:
                if submit == 'Next':
                    current_pane += 1
                elif submit == 'Previous':
                    current_pane -= 1
                elif submit == 'Submit':
                    apply_changes()
                    return redirect(next_pane())
        assert current_pane > 0
        assert current_pane < len(self.panes())
        display current_pane
        '''
        if self._update_called:
            return
        self._update_called = 1

        # Determine the current pane
        if PaneNumber in self.request:
            self._current_pane_idx = int(self.request[PaneNumber])
            assert self._current_pane_idx >= 0
            assert self._current_pane_idx < len(self.panes)
        else:
            # First page
            self._current_pane_idx = 0
            self.errors = []
            self.label = self.currentPane().label
            self._choose_buttons()
            return

        # Validate the current pane, and set self.errors
        try:
            if self.use_session:
                names = self.currentPane().names
            else:
                names = self.fieldNames
            #data = getWidgetsData(
            #    self, self.schema, strict=False, set_missing=True, 
            #    names=names, exclude_readonly=True
            #    )
            data = getWidgetsData(
                self, self.schema, strict=True, set_missing=True, 
                names=names, exclude_readonly=True
                )
            valid = 1
            self.errors = []
        except WidgetsError, errors:
            self.errors = errors
            valid = 0
            data = getWidgetsData(
                self, self.schema, strict=False, set_missing=True,
                names=names, exclude_readonly=True, do_not_raise=True
                )
            logging.fatal('data is %r' % (data,))
            self.storage.update(data)
            for k,v in self.storage.items():
                getattr(self,k).setData(v)

        else:
            self.storage.update(data)

            if Next in self.request:
                self._current_pane_idx += 1
                assert self._current_pane_idx < len(self.panes)
            elif Previous in self.request:
                self._current_pane_idx -= 1
                assert self._current_pane_idx >= 0
            elif Update in self.request:
                self.apply_update(self.storage)

        # Set last_pane flag - last_pane always gets a submit button
        if self._current_pane_idx == len(self.panes) - 1:
            self.last_pane = True
        else:
            self.last_pane = False

        # Set the current label
        self.label = self.currentPane().label

        self._choose_buttons()

    def _choose_buttons(self):
        # TODO: show_submit should be true if all fields on every pane 
        # except the current one are valid
        self.show_submit = 1 

        self.show_next = (self._current_pane_idx < len(self.panes) - 1)

        self.show_previous = self._current_pane_idx > 0


    def renderHidden(self):
        ''' Render state as hidden fields. Also render hidden fields to 
            propagate self.storage if we are not using the session to do this.
        '''
        olist = []
        out = olist.append
        out('<input class="hiddenType" type="hidden" name="%s" value="%d" />'%(
            PaneNumber, self._current_pane_idx
            ))

        if self.use_session:
            ''.join(olist)

        current_fields = self.currentPane().names
        for k in self.fieldNames:
            if k not in current_fields:
                widget = getattr(self, k)
                out(widget.hidden())
        return ''.join(olist)


class Pane:
    def __init__(self, field_names, label):
        self.names = field_names
        self.label = label


class EditWizardDirective:

    classProvides(INonEmptyDirective)
    implements(ISubdirectiveHandler)

    def __init__(self, _context, name, schema, permission, 
                 for_=None, class_=None, template=None, layer='default',
                 menu=None, title='Edit', use_session='yes'):
        self.name = name
        self.permission = permission
        self.title = title
        self.layer = layer
        self.menu = menu

        if use_session == 'yes':
            self.use_session = True
        elif use_session == 'no':
            self.use_session = False
        else:
            raise ValueError('Invalid value %r for use_session'%(use_session,))

        if menu:
            actions = menuItemDirective(
                _context, menu, for_ or schema, '@@' + name, title,
                permission=permission)
        else:
            actions = []

        schema, for_, bases, template, fields = normalize(
            _context, schema, for_, class_, template, 'editwizard.pt', 
            fields=None, omit=None, view=WizardEditView
            )

        self.schema = schema
        self.for_ = for_
        self.bases = bases
        self.template = template
        self.all_fields = fields

        self.panes = []
        self.actions = actions

    def pane(self, _context, fields, label=''):
        # TODO: Maybe accept a default of None for fields, meaning 'all 
        # remaining fields
        fields = [str(f) for f in fields.split(' ')]
        # TODO: unittest validation
        for f in fields:
            if f not in self.all_fields:
                raise ValueError(
                    'Field name is not in schema', 
                    name, self.schema
                    )
        self.panes.append(Pane(fields, label))
        return []

    def __call__(self):
        self.actions.append(
            Action(
                discriminator=(
                    'view', self.for_, self.name, IBrowserPresentation, 
                    self.layer
                    ),
                callable=EditWizardViewFactory,
                args=(
                    self.name, self.schema, self.permission, self.layer, 
                    self.panes, self.all_fields, self.template, 'editwizard.pt',
                    self.bases, self.for_, self.menu, u'', self.use_session
                    )
                )
            )
        return self.actions

def EditWizardViewFactory(name, schema, permission, layer,
                    panes, fields, template, default_template, bases, for_, 
                    menu=u'', usage=u'', use_session=True):
    # XXX What about the __implements__ of the bases?
    class_ = SimpleViewClass(template, used_for=schema, bases=bases)
    class_.schema = schema
    class_.panes = panes
    class_.fieldNames = fields
    class_.use_session = use_session

    class_.generated_form = ViewPageTemplateFile(default_template)

    class_.usage = usage or (
        menu and globalBrowserMenuService.getMenuUsage(menu))

    defineChecker(class_,
                  NamesChecker(("__call__", "__getitem__", "browserDefault"),
                               permission))

    provideView(for_, name, IBrowserPresentation, class_, layer)


