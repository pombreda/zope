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
"""Unit test logic for setting up and tearing down basic infrastructure


$Id: placelesssetup.py,v 1.6 2003/06/05 12:03:19 stevea Exp $
"""

from zope.component.tests.placelesssetup \
    import PlacelessSetup as CAPlacelessSetup
from zope.app.component.tests.placelesssetup \
    import PlacelessSetup as ACAPlacelessSetup
from zope.app.event.tests.placelesssetup \
    import PlacelessSetup as EventPlacelessSetup
from zope.app.i18n.tests.placelesssetup \
    import PlacelessSetup as I18nPlacelessSetup
from zope.app.container.tests.placelesssetup \
    import PlacelessSetup as ContainerPlaclessSetup
from zope.app.security._protections import protect

class PlacelessSetup(CAPlacelessSetup,
                     ACAPlacelessSetup,
                     EventPlacelessSetup,
                     I18nPlacelessSetup,
                     ContainerPlaclessSetup
                     ):

    def setUp(self):
        CAPlacelessSetup.setUp(self)
        ContainerPlaclessSetup.setUp(self)
        ACAPlacelessSetup.setUp(self)
        EventPlacelessSetup.setUp(self)
        I18nPlacelessSetup.setUp(self)
        # Register app-specific security declarations
        protect()

ps = PlacelessSetup()
setUp = ps.setUp
tearDown = ps.tearDown
del ps
