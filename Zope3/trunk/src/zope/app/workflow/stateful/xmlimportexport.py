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
"""Stateful ProcessDefinition XML Import/Export handlers

$Id: xmlimportexport.py,v 1.12 2004/03/08 12:06:25 srichter Exp $
"""
from xml.sax import parse
from xml.sax.handler import ContentHandler

from zope.configuration.name import resolve
from zope.interface import implements
from zope.proxy import removeAllProxies
from zope.security.checker import CheckerPublic
from zope.security.proxy import trustedRemoveSecurityProxy

from zope.app import zapi
from zope.app.dublincore.interfaces import IZopeDublinCore
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.app.security.interfaces import IPermission 
from zope.app.workflow.interfaces.stateful import IStatefulProcessDefinition
from zope.app.workflow.interfaces import IProcessDefinitionImportHandler
from zope.app.workflow.interfaces import IProcessDefinitionExportHandler
from zope.app.workflow.stateful.definition import State, Transition


# basic implementation for a format-checker
class XMLFormatChecker(ContentHandler):

    def __init__(self):
        self.__valid = False

    def startElement(self, name, attrs):
        if name == 'workflow' and attrs.get('type',None) == 'StatefulWorkflow':
            self.__valid = True

    def endElement(self, name):
        pass

    def isValid(self):
        return self.__valid


class XMLStatefulImporter(ContentHandler):
    def __init__(self, context, encoding='latin-1'):
        self.context = context
        self.encoding = encoding

    def startElement(self, name, attrs):
        handler = getattr(self, 'start' + name.title().replace('-', ''), None)
        if not handler:
            raise ValueError, 'Unknown element %s' % name

        handler(attrs)

    def endElement(self, name):
        handler = getattr(self, 'end' + name.title().replace('-', ''), None)
        if handler:
            handler()

    def noop(*args):
        pass

    startStates = noop
    startTransitions = noop
    startPermissions = noop

    def startWorkflow(self, attrs):
        dc = IZopeDublinCore(self.context)
        dc.title = attrs.get('title', u'')

    def startSchema(self, attrs):
        name = attrs['name'].encode(self.encoding).strip()
        if name:
            self.context.relevantDataSchema = resolve(name)

    def startPermission(self, attrs):
        perms = trustedRemoveSecurityProxy(self.context.schemaPermissions)
        fieldName = attrs.get('for')
        type = attrs.get('type')
        perm_id = attrs.get('id')
        if perm_id == 'zope.Public':
            perm = CheckerPublic
        elif perm_id == '':
            perm = None
        else:
            perm = zapi.getUtility(None, IPermission, perm_id)
        if not fieldName in perms.keys():
            perms[fieldName] = (CheckerPublic, CheckerPublic)
        if type == u'get':
            perms[fieldName] = (perm, perms[fieldName][1])
        if type == u'set':
            perms[fieldName] = (perms[fieldName][0], perm)

    def startState(self, attrs):
        encoding = self.encoding
        name  = attrs['name'].encode(encoding)
        if name == 'INITIAL':
            state = self.context.getState('INITIAL')
            dc = IZopeDublinCore(state)
            dc.title = attrs.get('title', u'')
        else:
            state = State()
            dc = IZopeDublinCore(state)
            dc.title = attrs.get('title', u'')
            self.context.addState(name, state)

    def startTransition(self, attrs):
        encoding = self.encoding
        name = attrs['name'].encode(encoding)
        permission = attrs.get('permission', '').encode(encoding)
        if permission == 'zope.Public':
            permission = CheckerPublic
        trans = Transition(
                source = attrs['sourceState'].encode(encoding),
                destination = attrs['destinationState'].encode(encoding),
                condition = attrs.get('condition', '').encode(encoding),
                script = attrs.get('script', '').encode(encoding),
                permission = permission,
                triggerMode = attrs['triggerMode'].encode(encoding)
                )
        dc = IZopeDublinCore(trans)
        dc.title = attrs.get('title', u'')
        self.context.addTransition(name, trans)


class XMLImportHandler(object):
    implements(IProcessDefinitionImportHandler)

    # XXX Implementation needs more work !!
    # check if xml-data can be imported and represents a StatefulPD
    def canImport(self, context, data):
        checker = XMLFormatChecker()
        parse(data, checker)
        return (bool(IStatefulProcessDefinition.providedBy(context)) 
                and checker.isValid())

    def doImport(self, context, data):
        # XXX Manually clean ProcessDefinition ??
        context.clear()
        parse(data, XMLStatefulImporter(context))


class XMLExportHandler(object):
    implements(IProcessDefinitionExportHandler)

    template = ViewPageTemplateFile('xmlexport_template.pt')

    def doExport(self, context, process_definition):
        # XXX Not really nice to fake a BrowserView here ....
        self.request = None
        self.process_definition = process_definition
        self.context = context
        return self.template()

    def getDefinition(self):
        return self.process_definition

    def getDublinCore(self, obj):
        return IZopeDublinCore(obj)

    def getPermissionId(self, permission):
        if isinstance(permission, str):
            return permission
        if permission is CheckerPublic:
            return 'zope.Public'
        if permission is None:
            return ''
        return removeAllProxies(permission).id

    def getSchemaPermissions(self):
        info = []
        perms = self.getDefinition().schemaPermissions
        for field, (getPerm, setPerm) in perms.items():
            info.append({'fieldName': field,
                         'type': 'get',
                         'id': self.getPermissionId(getPerm)})
            info.append({'fieldName': field,
                         'type': 'set',
                         'id': self.getPermissionId(setPerm)})
        return info

    def relevantDataSchema(self):
        schema = self.getDefinition().relevantDataSchema
        if schema is None:
            return 'None'
        return schema.__module__ + '.' + schema.getName()
