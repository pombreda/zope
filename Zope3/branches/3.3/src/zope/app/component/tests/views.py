##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""Views test.

$Id: views.py 26551 2004-07-15 07:06:37Z srichter $
"""
from zope.interface import Interface, implements, directlyProvides

class Request(object):

    def __init__(self, type):
        directlyProvides(self, type)

class IR(Interface):
    pass

class IV(Interface):
    def index():
        pass

class IC(Interface): pass

class V1(object):
    implements(IV)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def index(self):
        return 'V1 here'

    def action(self):
        return 'done'

class VZMI(V1):
    def index(self):
        return 'ZMI here'

class R1(object):

    def index(self):
        return 'R1 here'

    def action(self):
        return 'R done'

    def __init__(self, request):
        pass

    implements(IV)

class RZMI(R1):
    pass
