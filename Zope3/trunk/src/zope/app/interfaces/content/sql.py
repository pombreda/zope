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
$Id: sql.py,v 1.2 2002/12/25 14:12:59 jim Exp $
"""
import zope.schema

from zope.app.interfaces.rdb import ISQLCommand
from zope.component import getService
from zope.interface import Attribute
from zope.proxy.context import ContextProperty


class SQLConnectionName(zope.schema.TextLine):
    """SQL Connection Name"""

    def __allowed(self):
        """Note that this method works only if the Field is context wrapped."""
        connection_service = getService(self.context, "SQLDatabaseConnections")
        connections = connection_service.getAvailableConnections()
        return connections

    allowed_values = ContextProperty(__allowed)

class ISQLScript(ISQLCommand):
    """A persistent script that can execute SQL."""

    connectionName = SQLConnectionName(
        title=u"Connection Name",
        description=u"The Connection Name for the connection to be used.",
        required=False)

    arguments = zope.schema.BytesLine(
        title=u"Arguments",
        description=u"A set of attributes that can be used during the DTML "
                    u"rendering process to provide dynamic data.",
        required=False)

    source = zope.schema.Bytes(
        title=u"Source",
        description=u"The source of the page template.",
        required=True)

    def setArguments(arguments):
        """Processes the arguments (which could be a dict, string or whatever)
        to arguments as they are needed for the rendering process."""

    def getArguments():
        """Get the arguments. A method is preferred here, since some argument
        evaluation might be done."""

    def getArgumentsString():
        """This method returns the arguments string."""

    def setSource(source):
        """Save the source of the page template."""

    def getSource():
        """Get the source of the page template."""

    def getTemplate():
        """Get the SQL DTML Template object."""

    def setConnectionName(name):
        """Save the connection name for this SQL Script."""

    def getConnectionName():
        """Get the connection name for this SQL Script."""
