##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""Unit test for CacheConfiguration.

$Id: test_cacheconfiguration.py,v 1.13 2003/06/05 12:03:18 stevea Exp $
"""
__metaclass__ = type

from unittest import TestCase, main, makeSuite
from zope.app.context import ContextWrapper
from zope.app.interfaces.cache.cache import ICache
from zope.app.interfaces.cache.cache import ICachingService
from zope.app.interfaces.dependable import IDependable
from zope.app.interfaces.event import IObjectModifiedEvent
from zope.app.interfaces.services.configuration import Active, Unregistered
from zope.app.interfaces.services.configuration import IAttributeUseConfigurable
from zope.app.interfaces.services.configuration import IConfigurable
from zope.app.interfaces.services.service import ILocalService
from zope.app.services.cache import CacheConfiguration
from zope.app.services.configuration import ConfigurationRegistry
from zope.app.services.tests.placefulsetup import PlacefulSetup
from zope.app.tests import setup
from zope.app.traversing import traverse
from zope.context import ContextMethod
from zope.interface import implements

class DependableStub:

    implements(IDependable)

    def addDependent(self, location):
        pass

    def removeDependent(self, location):
        pass

    def dependents(self):
        pass


class TestCache(DependableStub):

    implements(ICache, IAttributeUseConfigurable)

    def invalidateAll(self):
        self.invalidated = True


class CachingServiceStub(DependableStub):

    implements(ICachingService, IConfigurable, ILocalService)

    def __init__(self):
        self.bindings = {}
        self.subscriptions = {}

    def queryConfigurationsFor(self, cfg, default=None):
        return self.queryConfigurations(cfg.name)
    queryConfigurationsFor = ContextMethod(queryConfigurationsFor)

    def queryConfigurations(self, name, default=None):
        registry = self.bindings.get(name, default)
        return ContextWrapper(registry, self)
    queryConfigurations = ContextMethod(queryConfigurations)

    def createConfigurationsFor(self, cfg):
        return self.createConfigurations(cfg.name)
    createConfigurationsFor = ContextMethod(createConfigurationsFor)

    def createConfigurations(self, name):
        try:
            registry = self.bindings[name]
        except KeyError:
            self.bindings[name] = registry = ConfigurationRegistry()
        return ContextWrapper(registry, self)
    createConfigurations = ContextMethod(createConfigurations)

    def subscribe(self, obj, event):
        self.subscriptions.setdefault(obj, []).append(event)

    def unsubscribe(self, obj, event):
        self.subscriptions.setdefault(obj, []).remove(event)

    def listSubscriptions(self, obj):
        return self.subscriptions.get(obj, [])


class TestConnectionConfiguration(PlacefulSetup, TestCase):

    def setUp(self):
        sm = PlacefulSetup.setUp(self, site=True)
        self.service = setup.addService(sm, 'Caching', CachingServiceStub())


        self.default = traverse(self.rootFolder,
                           '++etc++site/default')
        self.default.setObject('cch', TestCache())
        self.cch = traverse(self.default, 'cch')

        self.cm = self.default.getConfigurationManager()
        key = self.cm.setObject('',
                                CacheConfiguration('cache_name',
                                                   '/++etc++site/default/cch'))
        self.config = traverse(self.default.getConfigurationManager(), key)

    def tearDown(self):
        PlacefulSetup.tearDown(self)

    def test_getComponent(self):
        # This should be already tested by ComponentConfiguration tests, but
        # let's doublecheck
        self.assertEqual(self.config.getComponent(), self.cch)

    def test_status(self):
        self.assertEqual(self.config.status, Unregistered)
        self.config.status = Active
        self.assertEqual(self.config.status, Active)
        cr = self.service.queryConfigurations('cache_name')
        self.assertEqual(cr.active(), self.config)

    def test_activated(self):
        self.config.activated()
        self.assertEqual(self.service.listSubscriptions(self.cch),
                         [IObjectModifiedEvent])

    def test_deactivated(self):
        self.service.subscribe(self.cch, IObjectModifiedEvent)
        self.cch.invalidated = False
        self.config.deactivated()
        self.assertEqual(self.service.listSubscriptions(self.cch), [])
        self.failIf(not self.cch.invalidated,
                    "deactivation should call invalidateAll")


def test_suite():
    return makeSuite(TestConnectionConfiguration)


if __name__=='__main__':
    main(defaultTest='test_suite')
