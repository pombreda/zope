##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Class Views

$Id: browser.py 29143 2005-02-14 22:43:16Z srichter $
"""
__docformat__ = 'restructuredtext'
import types
from zope.proxy import removeAllProxies
from zope.security.proxy import removeSecurityProxy

from zope.app import zapi
from zope.app.apidoc.interfaces import IDocumentationModule
from zope.app.apidoc.utilities import getPythonPath, getPermissionIds
from zope.app.apidoc.utilities import renderText, getFunctionSignature
from zope.app.traversing.interfaces import TraversalError


def getTypeLink(type):
    if type is types.NoneType:
        return None
    path = getPythonPath(type)
    return path.replace('.', '/')

class ClassDetails(object):
    """Represents the details of the class."""

    def getBases(self):
        """Get all bases of this class."""
        return self._listClasses(self.context.getBases())


    def getKnownSubclasses(self):
        """Get all known subclasses of this class."""
        entries = self._listClasses(self.context.getKnownSubclasses())
        entries.sort(lambda x, y: cmp(x['path'], y['path']))
        return entries

    def _listClasses(self, classes):
        """Prepare a list of classes for presentation."""
        info = []
        codeModule = zapi.getUtility(IDocumentationModule, "Code")
        for cls in classes:
            # We need to removeAllProxies because the security checkers for
            # zope.app.container.contained.ContainedProxy and
            # zope.app.i18n.messagecatalog.MessageCatalog prevent us from
            # accessing __name__ and __module__.
            unwrapped_cls = removeAllProxies(cls)
            path = getPythonPath(unwrapped_cls)
            try:
                klass = zapi.traverse(codeModule, path.replace('.', '/'))
                url = zapi.absoluteURL(klass, self.request)
            except TraversalError:
                # If one of the classes is implemented in C, we will not
                # be able to find it.
                url = None
            info.append({'path': path, 'url': url})
        return info


    def getBaseURL(self):
        """Return the URL for the API Documentation Tool."""
        m = zapi.getUtility(IDocumentationModule, "Code")
        return zapi.absoluteURL(zapi.getParent(m), self.request)


    def getInterfaces(self):
        """Get all implemented interfaces (as paths) of this class."""
        return map(getPythonPath, self.context.getInterfaces())


    def getAttributes(self):
        """Get all attributes of this class."""
        attrs = []
        # remove the security proxy, so that `attr` is not proxied. We could
        # unproxy `attr` for each turn, but that would be less efficient.
        #
        # `getPermissionIds()` also expects the class's security checker not
        # to be proxied.
        klass = removeSecurityProxy(self.context)
        for name, attr, iface in klass.getAttributes():
            entry = {'name': name,
                     'value': `attr`,
                     'type': type(attr).__name__,
                     'type_link': getTypeLink(type(attr)),
                     'interface': getPythonPath(iface)}
            entry.update(getPermissionIds(name, klass.getSecurityChecker()))
            attrs.append(entry)
        return attrs


    def getMethods(self):
        """Get all methods of this class."""
        methods = []
        # remove the security proxy, so that `attr` is not proxied. We could
        # unproxy `attr` for each turn, but that would be less efficient.
        #
        # `getPermissionIds()` also expects the class's security checker not
        # to be proxied.
        klass = removeSecurityProxy(self.context)
        for name, attr, iface in klass.getMethodDescriptors():
            entry = {'name': name,
                     'signature': "(...)",
                     'doc': renderText(attr.__doc__ or '',
                                       zapi.getParent(self.context).getPath()),
                     'interface': getPythonPath(iface)}
            entry.update(getPermissionIds(name, klass.getSecurityChecker()))
            methods.append(entry)
        for name, attr, iface in klass.getMethods():
            entry = {'name': name,
                     'signature': getFunctionSignature(attr),
                     'doc': renderText(attr.__doc__ or '',
                                       zapi.getParent(self.context).getPath()),
                     'interface': getPythonPath(iface)}
            entry.update(getPermissionIds(name, klass.getSecurityChecker()))
            methods.append(entry)
        return methods


    def getDoc(self):
        """Get the doc string of the class STX formatted."""
        return renderText(self.context.getDocString() or '',
                          zapi.getParent(self.context).getPath())

