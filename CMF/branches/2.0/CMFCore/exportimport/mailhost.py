##############################################################################
#
# Copyright (c) 2005 Zope Foundation and Contributors.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Mailhost setup handlers.

$Id$
"""

from Products.GenericSetup.utils import exportObjects
from Products.GenericSetup.utils import importObjects

from Products.CMFCore.utils import getToolByName


def importMailHost(context):
    """Import mailhost settings from an XML file.
    """
    site = context.getSite()
    tool = getToolByName(site, 'MailHost')

    importObjects(tool, '', context)

def exportMailHost(context):
    """Export mailhost settings as an XML file.
    """
    site = context.getSite()
    tool = getToolByName(site, 'MailHost', None)
    if tool is None:
        logger = context.getLogger('mailhost')
        logger.info('Nothing to export.')
        return

    exportObjects(tool, '', context)
