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
"""Setting up an environment for testing context-dependent objects

$Id: setup.py,v 1.12 2004/02/24 16:51:13 philikon Exp $
"""

import zope.component
from zope.app import zapi
from zope.app.tests import ztapi
from zope.interface import classImplements

#------------------------------------------------------------------------
# Annotations
from zope.app.attributeannotations import AttributeAnnotations
from zope.app.interfaces.annotation import IAnnotations
from zope.app.interfaces.annotation import IAttributeAnnotatable
def setUpAnnotations():
    ztapi.provideAdapter(IAttributeAnnotatable, IAnnotations,
                         AttributeAnnotations)

#------------------------------------------------------------------------
# Dependencies
from zope.app.dependable import Dependable
from zope.app.interfaces.dependable import IDependable
def setUpDependable():
    ztapi.provideAdapter(IAttributeAnnotatable, IDependable,
                         Dependable)

#------------------------------------------------------------------------
# Traversal
from zope.app.browser.absoluteurl import SiteAbsoluteURL, AbsoluteURL
from zope.app.container.traversal import ContainerTraversable
from zope.app.interfaces.container import ISimpleReadContainer
from zope.app.interfaces.traversing import IContainmentRoot
from zope.app.interfaces.traversing import IPhysicallyLocatable
from zope.app.interfaces.traversing import ITraverser, ITraversable
from zope.app.traversing.adapters import DefaultTraversable
from zope.app.traversing.adapters import Traverser, RootPhysicallyLocatable
from zope.app.location import LocationPhysicallyLocatable
from zope.app.traversing.namespace import etc, provideNamespaceHandler

def setUpTraversal():
    ztapi.provideAdapter(None, ITraverser, Traverser)
    ztapi.provideAdapter(None, ITraversable, DefaultTraversable)

    ztapi.provideAdapter(
        ISimpleReadContainer, ITraversable, ContainerTraversable)
    ztapi.provideAdapter(
        None, IPhysicallyLocatable, LocationPhysicallyLocatable)
    ztapi.provideAdapter(
        IContainmentRoot, IPhysicallyLocatable, RootPhysicallyLocatable)

    # set up etc namespace
    provideNamespaceHandler("etc", etc)

    ztapi.browserView(None, "absolute_url", AbsoluteURL)
    ztapi.browserView(IContainmentRoot, "absolute_url", SiteAbsoluteURL)

#------------------------------------------------------------------------
# Use registration
from zope.app.interfaces.services.registration import IAttributeRegisterable
from zope.app.interfaces.services.registration import IRegistered
from zope.app.services.registration import Registered
def setUpRegistered():
    ztapi.provideAdapter(IAttributeRegisterable, IRegistered,
                         Registered)


#------------------------------------------------------------------------
# Placeful setup
from zope.app.component.hooks import getServiceManager_hook
from zope.app.tests.placelesssetup import setUp as placelessSetUp
from zope.app.tests.placelesssetup import tearDown as placelessTearDown
def placefulSetUp(site=False):
    placelessSetUp()
    zope.component.getServiceManager.sethook(getServiceManager_hook)
    setUpAnnotations()
    setUpDependable()
    setUpTraversal()
    setUpRegistered()

    if site:
        site = rootFolder()
        createServiceManager(site)
        return site

def placefulTearDown():
    placelessTearDown()
    zope.component.getServiceManager.reset()


from zope.app.folder import Folder, rootFolder

def buildSampleFolderTree():
    # set up a reasonably complex folder structure
    #
    #     ____________ rootFolder ____________
    #    /                                    \
    # folder1 __________________            folder2
    #   |                       \             |
    # folder1_1 ____           folder1_2    folder2_1
    #   |           \            |            |
    # folder1_1_1 folder1_1_2  folder1_2_1  folder2_1_1

    root = rootFolder()
    root['folder1'] = Folder()
    root['folder1']['folder1_1'] = Folder()
    root['folder1']['folder1_1']['folder1_1_1'] = Folder()
    root['folder1']['folder1_1']['folder1_1_2'] = Folder()
    root['folder1']['folder1_2'] = Folder()
    root['folder1']['folder1_2']['folder1_2_1'] = Folder()
    root['folder2'] = Folder()
    root['folder2']['folder2_1'] = Folder()
    root['folder2']['folder2_1']['folder2_1_1'] = Folder()

    return root


from zope.app.services.service import ServiceManager
from zope.app.interfaces.services.service import ISite
def createServiceManager(folder):
    if not ISite.isImplementedBy(folder):
        folder.setSiteManager(ServiceManager(folder))

    return zapi.traverse(folder, "++etc++site")

from zope.app.services.service import ServiceRegistration
from zope.app.interfaces.services.registration import ActiveStatus

def addService(servicemanager, name, service, suffix=''):
    """Add a service to a service manager

    This utility is useful for tests that need to set up services.
    """
    default = zapi.traverse(servicemanager, 'default')
    default[name+suffix] = service
    path = "%s/default/%s" % (zapi.getPath(servicemanager), name+suffix)
    registration = ServiceRegistration(name, path, default)
    key = default.getRegistrationManager().addRegistration(registration)
    zapi.traverse(default.getRegistrationManager(), key).status = ActiveStatus
    return zapi.traverse(servicemanager, path)

from zope.app.services.utility import UtilityRegistration

def addUtility(servicemanager, name, iface, utility, suffix=''):
    """Add a utility to a service manager

    This utility is useful for tests that need to set up utilities.
    """
    folder_name = name + suffix
    default = zapi.traverse(servicemanager, 'default')
    default[folder_name] = utility
    path = "%s/default/%s" % (zapi.getPath(servicemanager), folder_name)
    registration = UtilityRegistration(name, iface, path)
    key = default.getRegistrationManager().addRegistration(registration)
    zapi.traverse(default.getRegistrationManager(), key).status = ActiveStatus
    return zapi.traverse(servicemanager, path)

from zope.component import getServiceManager
from zope.app.interfaces.services.hub import IObjectHub
from zope.app.interfaces.services.event import ISubscriptionService
from zope.app.services.event import EventService
from zope.app.services.hub import ObjectHub
from zope.app.interfaces.services.utility import ILocalUtilityService
from zope.app.services.utility import LocalUtilityService
from zope.app.services.servicenames import HubIds
from zope.app.services.servicenames import EventPublication, EventSubscription
from zope.app.services.servicenames import Utilities
def createStandardServices(folder, hubids=None):
    '''Create a bunch of standard placeful services

    Well, uh, 3
    '''
    sm = createServiceManager(folder)
    defineService = getServiceManager(None).defineService

    defineService(EventSubscription, ISubscriptionService)

    # EventPublication service already defined by
    # zope.app.events.tests.PlacelessSetup

    defineService(HubIds, IObjectHub)

    # EventService must be IAttributeAnnotatable so that it can support
    # dependencies.
    classImplements(EventService, IAttributeAnnotatable)
    events = EventService()
    addService(sm, EventPublication, events)
    addService(sm, EventSubscription, events, suffix='sub')
    if hubids is None:
        hubids = ObjectHub()

    addService(sm, HubIds, hubids)

