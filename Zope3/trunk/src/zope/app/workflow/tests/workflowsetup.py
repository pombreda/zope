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
"""
Setup for Placeful Worfklow Tests
Revision information:
$Id: workflowsetup.py,v 1.7 2004/01/14 22:55:29 chrism Exp $
"""

from zope.component import getService, getServiceManager
from zope.app.services.servicenames import Permissions
from zope.app.services.servicenames import Authentication, Workflows

from zope.app.interfaces.security import IAuthenticationService
from zope.app.interfaces.security import IPermissionService
from zope.app.security.registries.principalregistry import principalRegistry
from zope.app.security.registries.permissionregistry import permissionRegistry

from zope.app.services.tests.placefulsetup import PlacefulSetup
from zope.app.interfaces.annotation import IAttributeAnnotatable

from zope.app.workflow.service import WorkflowService

from zope.interface import implements

from zope.app.tests import setup

from zope.app import zapi

class WorkflowServiceForTests(WorkflowService):

    implements(IAttributeAnnotatable)


class WorkflowSetup(PlacefulSetup):

    def setUp(self):
        self.root_sm = getServiceManager(None)

        self.sm = PlacefulSetup.setUp(self, site=True)
        self.service = setup.addService(self.sm, Workflows,
                                        WorkflowServiceForTests())
        self.default = zapi.traverse(self.sm, "default")
        self.cm = self.default.getRegistrationManager()

        self.sm1 = self.makeSite('folder1')
        self.service1 = setup.addService(self.sm1, Workflows,
                                         WorkflowServiceForTests())
        self.default1 = zapi.traverse(self.sm1, "default")
        self.cm1 = self.default1.getRegistrationManager()

    def setupAuthService(self):
        self.root_sm.defineService(Authentication, IAuthenticationService)
        self.root_sm.provideService(Authentication, principalRegistry)
        return getService(self.rootFolder, Authentication)

    def setupPermissionService(self):
        self.root_sm.defineService(Permissions, IPermissionService)
        self.root_sm.provideService(Permissions, permissionRegistry)
        return getService(self.rootFolder, Permissions)

