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
"""
$Id: IDBITypeInfo.py,v 1.3 2002/08/12 15:07:30 alga Exp $
"""
from Interface import Interface
from Interface.Attribute import Attribute

class IDBITypeInfo(Interface):
    """Database adapter specific information"""
    
    paramstyle = Attribute("""
        String constant stating the type of parameter marker formatting
        expected by the interface. Possible values are [2]:

       'qmark' = Question mark style, e.g. '...WHERE name=?'
       'numeric' = Numeric, positional style, e.g. '...WHERE name=:1'
       'named' = Named style, e.g. '...WHERE name=:name'
       'format' = ANSI C printf format codes, e.g. '...WHERE name=%s'
       'pyformat' = Python extended format codes, e.g. '...WHERE name=%(name)s'
       """)

    threadsafety = Attribute("""
        Integer constant stating the level of thread safety the interface
        supports. Possible values are:

            0 = Threads may not share the module.
            1 = Threads may share the module, but not connections.
            2 = Threads may share the module and connections.
            3 = Threads may share the module, connections and cursors.

        Sharing in the above context means that two threads may use a resource
        without wrapping it using a mutex semaphore to implement resource
        locking. Note that you cannot always make external resources thread
        safe by managing access using a mutex: the resource may rely on global
        variables or other external sources that are beyond your control.
        """)

    def getConverter(type):
        """Return a converter function for field type matching key"""
