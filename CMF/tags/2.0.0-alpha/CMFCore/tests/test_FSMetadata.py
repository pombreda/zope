##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" Unit tests for FSMetadata module.

$Id$
"""
from unittest import TestSuite, makeSuite, main
import Testing
import Zope2
Zope2.startup()

from test_FSSecurity import FSSecurityBase


class FSMetadata(FSSecurityBase):

    def _checkProxyRoles(self, obj, roles):
        # Test proxy roles on the object
        for role in roles:
            if not obj.manage_haveProxy(role):
                raise 'Object does not have the "%s" role' % role

    def test_basicPermissions(self):
        # Test basic FS permissions
        # check it has a title
        assert(self.ob.fake_skin.test6.title == 'Test object')
        self._checkSettings(
            self.ob.fake_skin.test6,
            'Access contents information',
            1,
            ['Manager','Anonymous'])
        self._checkSettings(
            self.ob.fake_skin.test6,
            'View management screens',
            0,
            ['Manager'])
        self._checkProxyRoles(
            self.ob.fake_skin.test6,
            ['Manager', 'Anonymous'])

    def test_basicPermissionsOnImage(self):
        # Test basic FS permissions on Image
        test_image = getattr(self.ob.fake_skin, 'test_image.gif')
        assert(test_image.title == 'Test image')
        self._checkSettings(
            test_image,
            'Access contents information',
            1,
            ['Manager','Anonymous'])
        self._checkSettings(
            test_image,
            'View management screens',
            0,
            ['Manager'])

    def test_basicPermissionsOnFile(self):
        # Test basic FS permissions on File
        test_file = getattr(self.ob.fake_skin, 'test_file.swf')
        assert(test_file.title == 'Test file')
        self._checkSettings(
            test_file,
            'Access contents information',
            1,
            ['Manager','Anonymous'])
        self._checkSettings(
            test_file,
            'View management screens',
            0,
            ['Manager'])

    def test_proxy(self):
        # Test roles
        ob = self.ob.fake_skin.test_dtml
        self._checkProxyRoles(ob, ['Manager', 'Anonymous'])


def test_suite():
    return TestSuite((
        makeSuite(FSMetadata),
        ))

if __name__ == '__main__':
    main(defaultTest='test_suite')
