##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Location framework

$Id: location.py,v 1.2 2003/09/21 17:32:25 jim Exp $
"""

from zope.interface import Interface, Attribute
from zope import schema

class ILocation(Interface):
    """Objects that have a structural location
    """

    __parent__ = Attribute("The parent in the location hierarchy")

    __name__ = schema.TextLine(
        __doc__=
        """The name within the parent

        The parent can be traversed with this name to get the object.
        """)
