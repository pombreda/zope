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
"""XXX short summary goes here.

XXX longer description goes here.

$Id: iregistry.py,v 1.2 2003/09/21 17:31:13 jim Exp $
"""
from zope.app.interfaces.services.registration import IRegistry
from zope.interface.verify import verifyObject

class TestingIRegistry:
    """Base class for testing implementors of IRegistry

    Subclasses must implement:

      - createTestingRegistry()
        that returns a new registry object with no registrations.

        This registration object must be in the context of something
        that is not None.

      - createTestingRegistration()
        that returns a registration object.

    """

    def _assertInContext(self, ob, parent):
        """Assert that we have the proper context

        The container of ob must be the parent, and the parent must
        have some context.

        """
        self.assertEqual(ob.__parent__, parent)
        self.failIf(ob.__parent__.__parent__ is None)

    def test_implements_IRegistry(self):
        verifyObject(IRegistry, self.createTestingRegistry())

    def test_queryRegistrationsFor_no_config(self):
        registry = self.createTestingRegistry()
        registration = self.createTestingRegistration()
        self.failIf(registry.queryRegistrationsFor(registration))

        self.assertEqual(
            registry.queryRegistrationsFor(registration, 42),
            42)

    def test_createRegistrationsFor(self):
        registry = self.createTestingRegistry()
        registration = self.createTestingRegistration()
        stack = registry.createRegistrationsFor(registration)

        self.assertEqual(stack.__parent__, registry)

        # If we call it again, we should get the same object
        self.assertEqual(registry.createRegistrationsFor(registration),
                         stack)

        self._assertInContext(stack, registry)

        return stack

    def test_queryRegistrationsFor(self):
        registry = self.createTestingRegistry()
        registration = self.createTestingRegistration()

        cstack = registry.createRegistrationsFor(registration)


        stack = registry.queryRegistrationsFor(registration)
        self.assertEqual(stack, cstack)
        self._assertInContext(stack, registry)

        stack = registry.queryRegistrationsFor(registration, 42)
        self.assertEqual(stack, cstack)
        self._assertInContext(stack, registry)
