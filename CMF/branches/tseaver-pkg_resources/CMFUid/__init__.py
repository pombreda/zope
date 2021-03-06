##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Unique id generation and handling.

$Id$
"""

cmfuid_globals = globals()

def initialize(context):

    from Products.CMFCore.utils import ToolInit
    from Products.GenericSetup import EXTENSION
    from Products.GenericSetup import profile_registry

    import UniqueIdAnnotationTool
    import UniqueIdGeneratorTool
    import UniqueIdHandlerTool

    tools = ( UniqueIdAnnotationTool.UniqueIdAnnotationTool
            , UniqueIdGeneratorTool.UniqueIdGeneratorTool
            , UniqueIdHandlerTool.UniqueIdHandlerTool
            )

    ToolInit( 'CMF Unique Id Tool'
            , tools=tools
            , icon='tool.gif'
            ).initialize(context)

    profile_registry.registerProfile( 'default'
                                     , 'CMFUid'
                                     , 'Adds UID support.'
                                     , 'profiles/default'
                                     , 'CMFUid'
                                     , EXTENSION
                                     )
