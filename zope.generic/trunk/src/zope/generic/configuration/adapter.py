##############################################################################
#
# Copyright (c) 2005, 2006 Zope Corporation and Contributors.
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

"""
$Id$
"""

__docformat__ = 'restructuredtext'

from BTrees.OOBTree import OOBTree
import transaction
from UserDict import DictMixin

from zope.location import Location
from zope.location.interfaces import ILocation
from zope.component import adapts
from zope.event import notify
from zope.interface import implements

from zope.generic.face.api import getKeyface
from zope.generic.face.api import toDottedName
from zope.generic.face.api import toInterface

from zope.generic.configuration import IAttributeConfigurable
from zope.generic.configuration import IConfigurationType
from zope.generic.configuration import IConfigurations
from zope.generic.configuration.base import createConfiguration
from zope.generic.configuration.event import Configuration
from zope.generic.configuration.event import ObjectConfiguredEvent
from zope.generic.configuration.helper import configurationToDict



class AttributeConfigurations(DictMixin, Location):
    """Store configurations on an object within the __configurations__ attribute.

    """

    implements(IConfigurations)

    adapts(IAttributeConfigurable)

    def __init__(self, context):
        self.context = context

    def __nonzero__(self):
        return bool(getattr(self.context, '__configurations__', 0))

    def __conform__(self, keyface):
        configurations = getattr(self.context, '__configurations__', None)
        if configurations is None:
            return None

        else:
            return configurations.get(toDottedName(keyface), None)

    def __getitem__(self, keyface):
        configurations = getattr(self.context, '__configurations__', None)
        if configurations is None:
            raise KeyError(keyface)

        return configurations[toDottedName(keyface)]

    def keys(self):
        configurations = getattr(self.context, '__configurations__', None)
        if configurations is None:
            return []

        return [toInterface(iface) for iface in configurations.keys()]

    def update(self, keyfaced_or_keyface, data=None):
        """Update a configuration."""
        
        keyface = getKeyface(keyfaced_or_keyface)
        # feed by a configuration
        isconfig = False
        if keyface != keyfaced_or_keyface:
            data = keyfaced_or_keyface
            isconfig = True

        elif keyface.providedBy(data):
            isconfig = True

        try:
            current_config = self[keyface]
        except KeyError:
            # there is no existing configuration, try to set a new one
            self[keyface] = data
            return

        updated_data = {}
        existing_data = {}
        errors = []
        try:
            for name in keyface:
                field = keyface[name]
    
                # readonly attribute cannot be updated
                if field.readonly:
                    raise ValueError(name, 'Data is readonly.')
    
                if isconfig:
                    value = getattr(data, name, field.missing_value)
                # assume dict
                else:
                    try:
                        value = data[name]
                    except KeyError:
                        continue
                existing_value = getattr(current_config, name, field.missing_value)
                if value != existing_value:
                    existing_data[name] = existing_value
                    setattr(current_config, name, value)
                    updated_data[name] = value
    
            # notify update
            parent = self.__parent__
            if updated_data and ILocation.providedBy(parent) and parent.__parent__ is not None:
                notify(ObjectConfiguredEvent(parent, 
                    Configuration(keyface, updated_data)))

        except:
            # set the values back to the last valid configuration
            for name, value in existing_data.items():
                setattr(current_config, name, value)
            raise


    def __setitem__(self, keyface, value):
        # preconditions
        if not IConfigurationType.providedBy(keyface):
            raise KeyError('Interface key %s requires %s.' % 
                (keyface.__name__, IConfigurationType.__name__))

        if not (keyface.providedBy(value) or isinstance(value, dict)):
            raise ValueError('Value does not provide %s or is not a dictionary.' % keyface.__name__)

        # essentials
        try:
            configurations = self.context.__configurations__
        except AttributeError:
            configurations = self.context.__configurations__ = OOBTree()
        
        # avoid unintended overwrittings of a configuration
        key = toDottedName(keyface)
        if key in configurations:
            raise ValueError('Configuration is already provided %s.' % keyface.__name__)

        # set configuration or dictionary
        if keyface.providedBy(value):
            configurations[key] = value
        else:
            configurations[key] = createConfiguration(keyface, value)

        # notify setting
        parent = self.__parent__
        if ILocation.providedBy(parent) and parent.__parent__ is not None:
            if isinstance(value, dict):
                data = value
            else:
                data = configurationToDict(value, all=True)
            notify(ObjectConfiguredEvent(parent, 
                Configuration(keyface, data)))

    def __delitem__(self, keyface):
        try:
            configurations = self.context.__configurations__
        except AttributeError:
            raise KeyError(keyface)

        del configurations[toDottedName(keyface)]
        # notify deletion
        # notify setting
        parent = self.__parent__
        if ILocation.providedBy(parent) and parent.__parent__ is not None:
            notify(ObjectConfiguredEvent(parent, 
                Configuration(keyface, {})))
