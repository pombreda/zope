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

$Id: components.py,v 1.6 2004/04/20 11:01:21 stevea Exp $
"""
__metaclass__ = type # All classes are new style when run with Python 2.2+

from zope.interface import Interface, Attribute, implements

class RecordingAdapter:

    def __init__(self):
        self.record = []

    def __call__(self, context):
        # Note that this sets the context rather than appending to the record
        # so as not to assume things about adapters being cached, if this
        # happens in the future.
        self.context = context
        return self

    def check(self, *args):
        record = self.record
        if len(args) != len(record):
            raise AssertionError('wrong number of entries in record',
                                 args, record)
        for arg, entry in zip(args, record):
            if arg != entry:
                raise AssertionError('record entry does not match',
                                     args, record)


class IApp(Interface):
    a = Attribute('test attribute')
    def f(): "test func"

class IContent(Interface): pass

class Content:
    implements(IContent)

class Comp:
    __used_for__ = IContent
    implements(IApp)

    def __init__(self, *args):
        # Ignore arguments passed to constructor
        pass

    a = 1
    def f(): pass

comp = Comp()
