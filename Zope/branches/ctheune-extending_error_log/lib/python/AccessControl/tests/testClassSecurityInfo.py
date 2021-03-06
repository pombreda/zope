##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################
""" Unit tests for ClassSecurityInfo.
"""

import unittest


class ClassSecurityInfoTests(unittest.TestCase):


    def _getTargetClass(self):

        from AccessControl.SecurityInfo import ClassSecurityInfo
        return ClassSecurityInfo

    def test_SetPermissionDefault(self):

        # Test setting default roles for permissions.

        import Globals  # XXX: avoiding import cycle
        from App.class_init import default__class_init__
        from ExtensionClass import Base

        ClassSecurityInfo = self._getTargetClass()

        # Setup a test class with default role -> permission decls.
        class Test(Base):
            """Test class
            """
            __ac_roles__ = ('Role A', 'Role B', 'Role C')

            meta_type = "Test"

            security = ClassSecurityInfo()

            security.setPermissionDefault(
                'Test permission',
                ('Manager', 'Role A', 'Role B', 'Role C')
                )

            security.declareProtected('Test permission', 'foo')
            def foo(self, REQUEST=None):
                """ """
                pass

        # Do class initialization.
        default__class_init__(Test)

        # Now check the resulting class to see if the mapping was made
        # correctly. Note that this uses carnal knowledge of the internal
        # structures used to store this information!
        object = Test()
        imPermissionRole = object.foo__roles__
        self.failUnless(len(imPermissionRole) == 4)

        for item in ('Manager', 'Role A', 'Role B', 'Role C'):
            self.failUnless(item in imPermissionRole)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ClassSecurityInfoTests))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
