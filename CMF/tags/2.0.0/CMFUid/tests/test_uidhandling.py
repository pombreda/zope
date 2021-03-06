##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Test the unique id handling.

$Id$
"""

import unittest
import Testing

from Products.CMFCore.tests.base.dummy import DummyContent
from Products.CMFCore.tests.base.dummy import DummyFolder
from Products.CMFCore.tests.base.dummy import DummySite
from Products.CMFCore.tests.base.testcase import SecurityTest


class DummyUid:
    """A dummy uid that surely is of different type of the generated ones.
    """
    pass


class UniqueIdHandlerTests(SecurityTest):

    def _getTargetClass(self):
        from Products.CMFUid.UniqueIdHandlerTool import UniqueIdHandlerTool

        return UniqueIdHandlerTool

    def setUp(self):
        from Products.CMFCore.CatalogTool import CatalogTool
        from Products.CMFUid.UniqueIdAnnotationTool \
                import UniqueIdAnnotationTool
        from Products.CMFUid.UniqueIdGeneratorTool \
                import UniqueIdGeneratorTool
        SecurityTest.setUp(self)
        self.root._setObject('portal_catalog', CatalogTool())
        self.root._setObject('portal_uidgenerator', UniqueIdGeneratorTool())
        self.root._setObject('portal_uidannotation', UniqueIdAnnotationTool())
        self.root._setObject('portal_uidhandler', self._getTargetClass()())
        self.root._setObject('dummy', DummyContent(id='dummy'))
        self.root._setObject('dummy2', DummyContent(id='dummy2'))

    def test_z3interfaces(self):
        from zope.interface.verify import verifyClass
        from Products.CMFUid.interfaces import IUniqueIdBrainQuery
        from Products.CMFUid.interfaces import IUniqueIdHandler
        from Products.CMFUid.interfaces import IUniqueIdUnrestrictedQuery
        verifyClass(IUniqueIdHandler, self._getTargetClass())
        verifyClass(IUniqueIdBrainQuery, self._getTargetClass())
        verifyClass(IUniqueIdUnrestrictedQuery, self._getTargetClass())

    def test_getUidOfNotYetRegisteredObject(self):
        handler = self.root.portal_uidhandler
        dummy = self.root.dummy
        UniqueIdError = handler.UniqueIdError

        self.assertEqual(handler.queryUid(dummy, None), None)
        self.assertRaises(UniqueIdError, handler.getUid, dummy)

    def test_getInvalidUid(self):
        handler = self.root.portal_uidhandler
        dummy = self.root.dummy
        UniqueIdError = handler.UniqueIdError

        self.assertEqual(handler.queryObject(100, None), None)
        self.assertRaises(UniqueIdError, handler.getObject, 100)
        self.assertEqual(handler.unrestrictedQueryObject(100, None), None)
        self.assertRaises(UniqueIdError, handler.unrestrictedGetObject, 100)

        uid = handler.register(dummy)
        self.assertEqual(handler.queryObject(uid+1, None), None)
        self.assertRaises(UniqueIdError, handler.getObject, uid+1)
        self.assertEqual(handler.unrestrictedQueryObject(uid+1, None), None)
        self.assertRaises(UniqueIdError, handler.unrestrictedGetObject, uid+1)

    def test_getUidOfRegisteredObject(self):
        handler = self.root.portal_uidhandler
        dummy = self.root.dummy

        uid = handler.register(dummy)
        self.assertEqual(handler.getUid(dummy), uid)

    def test_getRegisteredObjectByUid(self):
        handler = self.root.portal_uidhandler
        dummy = self.root.dummy

        uid = handler.register(dummy)
        self.assertEqual(handler.getObject(uid), dummy)
        self.assertEqual(handler.unrestrictedGetObject(uid), dummy)

    def test_getUnregisteredObject(self):
        handler = self.root.portal_uidhandler
        dummy = self.root.dummy
        UniqueIdError = handler.UniqueIdError

        uid = handler.register(dummy)
        handler.unregister(dummy)
        self.assertEqual(handler.queryObject(uid, None), None)
        self.assertRaises(UniqueIdError, handler.getObject, uid)
        self.assertEqual(handler.unrestrictedQueryObject(uid, None), None)
        self.assertRaises(UniqueIdError, handler.unrestrictedGetObject, uid)

    def test_getUidOfUnregisteredObject(self):
        handler = self.root.portal_uidhandler
        dummy = self.root.dummy
        UniqueIdError = handler.UniqueIdError

        uid = handler.register(dummy)
        handler.unregister(dummy)
        self.assertEqual(handler.queryUid(dummy, None), None)
        self.assertRaises(UniqueIdError, handler.getUid, dummy)

    def test_reregisterObject(self):
        handler = self.root.portal_uidhandler
        dummy = self.root.dummy

        uid1_reg = handler.register(dummy)
        uid1_get = handler.getUid(dummy)
        uid2_reg = handler.register(dummy)
        uid2_get = handler.getUid(dummy)
        self.assertEqual(uid1_reg, uid2_reg)
        self.assertEqual(uid1_get, uid2_get)
        self.assertEqual(uid1_reg, uid1_get)

    def test_unregisterObjectWithoutUid(self):
        handler = self.root.portal_uidhandler
        dummy = self.root.dummy
        UniqueIdError = handler.UniqueIdError

        self.assertRaises(UniqueIdError, handler.unregister, dummy)

    def test_setNewUidByHandWithCheck(self):
        handler = self.root.portal_uidhandler
        dummy = self.root.dummy

        # registering and unregisterung a object just to get a free uid
        unused_uid = handler.register(dummy)
        handler.unregister(dummy)

        handler.setUid(dummy, unused_uid)

        result = handler.getUid(dummy)
        self.assertEqual(unused_uid, result)

    def test_setSameUidOnSameObjectWithCheck(self):
        handler = self.root.portal_uidhandler
        dummy = self.root.dummy

        uid = handler.register(dummy)

        # just setting the same uid another time is allowed
        handler.setUid(dummy, uid)

        result = handler.getUid(dummy)
        self.assertEqual(uid, result)

    def test_setExistingUidOnDifferentObjectWithCheckRaisesException(self):
        handler = self.root.portal_uidhandler
        dummy = self.root.dummy
        dummy2 = self.root.dummy2
        UniqueIdError = handler.UniqueIdError

        # registering and unregisterung a object just to get a free uid
        uid1_reg = handler.register(dummy)
        uid2_reg = handler.register(dummy2)

        self.assertRaises(UniqueIdError, handler.setUid, dummy2, uid1_reg)

    def test_setExistingUidOnDifferentObjectWithoutCheck(self):
        handler = self.root.portal_uidhandler
        dummy = self.root.dummy
        dummy2 = self.root.dummy2
        UniqueIdError = handler.UniqueIdError

        # registering and unregisterung a object just to get a free uid
        uid1_reg = handler.register(dummy)
        uid2_reg = handler.register(dummy2)

        # now lets double the unique id
        handler.setUid(dummy2, uid1_reg, check_uniqueness=False)

        # calling a getter returns one object and generates a log
        # we can't capture. So let's ask the catalog directly.
        catalog = self.root.portal_catalog
        result = catalog({handler.UID_ATTRIBUTE_NAME: uid1_reg})
        self.assertEqual(len(result), 2)

        # dummy2 shall not be reachable anymore by uid2_reg
        self.assertRaises(UniqueIdError, handler.getBrain, uid2_reg)

    def test_setNoneAsUidRaisesException(self):
        handler = self.root.portal_uidhandler
        dummy = self.root.dummy
        UniqueIdError = handler.UniqueIdError

        uid = handler.register(dummy)

        self.assertRaises(UniqueIdError, handler.setUid, dummy, None)

    def test_setArbitraryKindOfUidRaisesException(self):
        handler = self.root.portal_uidhandler
        dummy = self.root.dummy
        UniqueIdError = handler.UniqueIdError

        uid = handler.register(dummy)

        # As we don't know what kind of exception the implementation
        # throws lets check for all exceptions!
        # IMHO it makes sense here to catch exceptions in general here!
        self.assertRaises(Exception, handler.setUid, dummy, DummyUid())


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(UniqueIdHandlerTests),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
