##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Helper base class that picks principal ids

$Id$
"""

from zope.app.container.contained import NameChooser


class IdPicker(NameChooser):
    """Helper base class that picks principal ids

    Add numbers to ids given by users to make them unique.
    """
        
    def chooseName(self, name, object):
        i = 0
        name = unicode(name)
        orig = name
        while (not name) or (name in self.context):
            i += 1
            name = orig+str(i)

        self.checkName(name, object)
        return name
    
