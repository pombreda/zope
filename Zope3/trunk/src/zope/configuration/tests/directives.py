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
Test class for use by test modules

$Id: directives.py,v 1.4 2003/04/18 22:12:31 jim Exp $
"""

from zope.interface import directlyProvides, classProvides
from zope.configuration.interfaces import INonEmptyDirective
from zope.configuration.interfaces import ISubdirectiveHandler

protections=[]

count = 0

def _increment():
    global count
    count += 1

def increment(_context):
    return [(None, _increment, (), )]

class protectClass:

    classProvides(INonEmptyDirective)
    __implements__ = ISubdirectiveHandler

    def __init__(self, _context, name, permission=None, names=None):
        self._name=name
        self._permission=permission
        self._names=names
        self._children=[]
        self.__context = _context

    def __call__(self):
        if not self._children:
            p = self._name, self._permission, self._names
            d = self._name, self._names
            return [(d, protections.append, (p,))]
        else:
            return ()

    def protect(self, _context, permission=None, names=None):
        if permission is None: permission=self._permission
        if permission is None: raise 'no perm'
        p=self._name, permission, names
        d=self._name, names
        self._children.append(p)
        return [(d, protections.append, (p,))]

    def subsub(self, _context):
        #Dummy subdirective-with-subdirectives.  Define this and you
        #can define 'protect' subdirectives within it.  This lets
        #us excercise the subdirectives-of-subdirectives code.
        #If you put a protect inside a subsub, that'll set children,
        #so when the parser calls us, __call__ will return ().
        return self
    directlyProvides(subsub, INonEmptyDirective)

done = []

def doit(_context, name):
    return [('d', done.append, (name,))]

def clearDirectives():
    del protections[:]
    del done[:]

# Register our cleanup with Testing.CleanUp to make writing unit tests simpler.
from zope.testing.cleanup import addCleanUp
addCleanUp(clearDirectives)
del addCleanUp
