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

Revision information: $Id: contents.py,v 1.13 2003/03/19 19:57:21 alga Exp $
"""
from zope.app.interfaces.container import IContainer, IZopeContainer
from zope.app.interfaces.dublincore import IZopeDublinCore
from zope.app.interfaces.size import ISized
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile

from zope.component import queryView, queryAdapter, getAdapter, getService
from zope.app.interfaces.services.principalannotation \
     import IPrincipalAnnotationService
from zope.publisher.browser import BrowserView
from zope.app.interfaces.traversing import IPhysicallyLocatable
from zope.app.traversing import traverse, getRoot, getPath
from zope.app.interfaces.copypastemove import IPrincipalClipboard
from zope.app.interfaces.container import IPasteTarget
from zope.app.interfaces.copypastemove import IObjectCopier
from zope.app.interfaces.copypastemove import IObjectMover

class Contents(BrowserView):

    __used_for__ = IContainer

    def _extractContentInfo(self, item):
        id, obj = item
        info = {}
        info['id'] = id
        info['object'] = obj

        info['url'] = id

        zmi_icon = queryView(obj, 'zmi_icon', self.request)
        if zmi_icon is None:
            info['icon'] = None
        else:
            info['icon'] = zmi_icon()

        dc = queryAdapter(obj, IZopeDublinCore)
        if dc is not None:
            title = dc.title
            if title:
                info['title'] = title

            created = dc.created
            if created is not None:
                info['created'] = formatTime(created)

            modified = dc.modified
            if modified is not None:
                info['modified'] = formatTime(modified)

        sized_adapter = queryAdapter(obj, ISized)
        if sized_adapter is not None:
            info['size'] = sized_adapter
        return info

    def renameObjects(self, ids, newids):
        """Given a sequence of tuples of old, new ids we rename"""
        container = getAdapter(self.context, IZopeContainer)
        for id, newid in zip(ids, newids):
            if newid != id:
                container.rename(id, newid)
        self.request.response.redirect('@@contents.html')

    def removeObjects(self, ids):
        """Remove objects specified in a list of object ids"""
        container = getAdapter(self.context, IZopeContainer)
        for id in ids:
            container.__delitem__(id)

        self.request.response.redirect('@@contents.html')

    def copyObjects(self, ids):
        """Copy objects specified in a list of object ids"""
        container_path = getPath(self.context)

        user = self.request.user
        annotationsvc = getService(self.context, 'PrincipalAnnotation')
        annotations = annotationsvc.getAnnotation(user)
        clipboard = getAdapter(annotations, IPrincipalClipboard)
        clipboard.clearContents()
        items = []
        for id in ids:
            items.append('%s/%s' % (container_path, id))
        clipboard.addItems('copy', items)

        self.request.response.redirect('@@contents.html')

    def cutObjects(self, ids):
        """move objects specified in a list of object ids"""
        container_path = getPath(self.context)

        user = self.request.user
        annotationsvc = getService(self.context, 'PrincipalAnnotation')
        annotations = annotationsvc.getAnnotation(user)
        clipboard = getAdapter(annotations, IPrincipalClipboard)
        clipboard.clearContents()
        items = []
        for id in ids:
            items.append('%s/%s' % (container_path, id))
        clipboard.addItems('cut', items)

        self.request.response.redirect('@@contents.html')

    def pasteObjects(self):
        """Iterate over clipboard contents and perform the
           move/copy operations"""
        container = self.context
        target = container

        user = self.request.user
        annotationsvc = getService(self.context, 'PrincipalAnnotation')
        annotations = annotationsvc.getAnnotation(user)
        clipboard = getAdapter(annotations, IPrincipalClipboard)
        items = clipboard.getContents()
        for item in items:
            obj = traverse(container, item['target'])
            if item['action'] == 'cut':
                getAdapter(obj, IObjectMover).moveTo(target)
                # XXX need to remove the item from the clipboard here
                # as it will not be available anymore from the old location
            elif item['action'] == 'copy':
                getAdapter(obj, IObjectCopier).copyTo(target)
            else:
                raise

        self.request.response.redirect('@@contents.html')

    def hasClipboardContents(self):
        """ interogates the PrinicipalAnnotation to see if
           clipboard contents exist """

        user = self.request.user

        annotationsvc = getService(self.context, 'PrincipalAnnotation')
        annotations = annotationsvc.getAnnotation(user)
        clipboard = getAdapter(annotations, IPrincipalClipboard)

        if clipboard.getContents():
            return True

        return False


    def listContentInfo(self):
        return map(self._extractContentInfo,
                   getAdapter(self.context, IZopeContainer).items())

    contents = ViewPageTemplateFile('main.pt')
    contentsMacros = contents

    rename = ViewPageTemplateFile('rename.pt')

    _index = ViewPageTemplateFile('index.pt')

    def index(self):
        if 'index.html' in self.context:
            self.request.response.redirect('index.html')
            return ''

        return self._index()

class JustContents(Contents):
    """Like Contents, but does't delegate to item named index.html
    """

    def index(self):
        return self._index()



# XXX L10N Below is prime material for localization.
# We are a touchpoint that should contact the personalization
# service so that users can see datetime and decimals

def formatTime(in_date):
    format='%m/%d/%Y'
    undefined=u'N/A'
    if hasattr(in_date, 'strftime'):
        return in_date.strftime(format)
    return undefined
