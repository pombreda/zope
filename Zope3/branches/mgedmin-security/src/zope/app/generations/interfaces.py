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
"""Interfaces for experimental support for application database generations

$Id: interfaces.py,v 1.1 2004/04/22 18:51:07 jim Exp $
"""

import zope.interface

class GenerationError(Exception):
    """A database generation is invalid
    """

class GenerationTooHigh(GenerationError):
    """A database generation is higher than an application generation
    """

class GenerationTooLow(GenerationError):
    """A database generation is lower than an application minimum generation
    """

class UnableToEvolve(GenerationError):
    """A database can't evolve to an application minimum generation
    """


class ISchemaManager(zope.interface.Interface):
    """Manage schema evolution for an application."""

    minimum_generation = zope.interface.Attribute(
        "Minimum supported schema generation")

    generation = zope.interface.Attribute(
        "Current schema generation")

    def evolve(context, generation):
        """Evolve a database to the given schema generation.

        The database should be assumed to be at the schema
        generation one less than the given generation
        argument. In other words, the evolve method is only
        required to make one evolutionary step.

        The context argument has a connection attribute,
        providing a database connection to be used to change
        the database.  A context argument is passed rather than
        a connection to make it possible to provide additional
        information later, if it becomes necessary.
        """
