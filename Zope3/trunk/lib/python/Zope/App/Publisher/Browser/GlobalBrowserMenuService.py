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

from IBrowserMenuService import IBrowserMenuService
from Zope.Configuration.Action import Action
from Interface.Registry.TypeRegistry import TypeRegistry
from Zope.Exceptions import DuplicationError, Unauthorized, Forbidden
from Zope.App.PageTemplate.Engine import Engine
from Zope.App.ZopePublication.Browser.PublicationTraverse \
     import PublicationTraverser

class GlobalBrowserMenuService:
    """Global Browser Menu Service
    """

    __implements__ = IBrowserMenuService

    def __init__(self):
        self._registry = {}

    _clear = __init__
        
    def menu(self, menu_id, title, description=''):
        # XXX we have nothing to do with the title and description. ;)

        if menu_id in self._registry:
            raise DuplicationError("Menu %s is already defined." % menu_id)

        self._registry[menu_id] = TypeRegistry()

    def menuItem(self, menu_id, interface,
                 action, title, description='', filter_string=None):

        registry = self._registry[menu_id]

        if filter_string:
            filter = Engine.compile(filter_string)
        else:
            filter = None

        data = registry.get(interface) or []
        data.append((action, title, description, filter))
        registry.register(interface, data)

    def getMenu(self, menu_id, object, request):
        registry = self._registry[menu_id]
        traverser = PublicationTraverser()

        result = []
        
        for items in registry.getAllForObject(object):
            for action, title, description, filter in items:
                if filter is not None:
                    
                    try:
                        include = filter(Engine.getContext(
                            context = object,
                            nothing = None))
                    except Unauthorized:
                        include = 0

                    if not include:
                        continue
   
                if action:
                    try:
                        v = traverser.traverseRelativeURL(
                            request, object, action)
                        # XXX
                        # tickle the security proxy's checker
                        # we're assuming that view pages are callable
                        # this is a pretty sound assumption
                        v.__call__
                    except (Unauthorized, Forbidden):
                        continue # Skip unauthorized or forbidden

                result.append({
                    'title': title,
                    'description': description,
                    'action': "%s" % action,
                    })
        
        return result

def menuDirective(_context, id, title, description=''):
    return [Action(
        discriminator = ('browser:menu', id),
        callable = globalBrowserMenuService.menu,
        args = (id, title, description),
        )]

def menuItemDirective(_context, menu, for_,
                      action, title, description='', filter=None):
    return menuItemsDirective(_context, menu, for_).menuItem(
        _context, action, title, description, filter)        

    
class menuItemsDirective:

    def __init__(self, _context, menu, for_):
        self.menu = menu
        self.interface = _context.resolve(for_)

    def menuItem(self, _context, action, title, description='', filter=None):
        return [Action(
            discriminator = ('browser:menuItem',
                             self.menu, self.interface, title),
            callable = globalBrowserMenuService.menuItem,
            args = (self.menu, self.interface,
                    action, title, description, filter),
            )]
        
    def __call__(self):
        return ()


globalBrowserMenuService = GlobalBrowserMenuService()

_clear = globalBrowserMenuService._clear

# Register our cleanup with Testing.CleanUp to make writing unit tests simpler.
from Zope.Testing.CleanUp import addCleanUp
addCleanUp(_clear)
del addCleanUp

__doc__ = GlobalBrowserMenuService.__doc__ + """

$Id: GlobalBrowserMenuService.py,v 1.4 2002/08/01 15:33:44 jim Exp $
"""
