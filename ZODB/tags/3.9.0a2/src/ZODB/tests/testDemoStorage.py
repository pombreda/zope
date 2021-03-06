##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
import unittest
import random
import transaction
from ZODB.DB import DB
from zope.testing import doctest
import ZODB.tests.util
import ZODB.utils
import ZODB.DemoStorage
from ZODB.tests import (
    BasicStorage,
    HistoryStorage,
    IteratorStorage,
    MTStorage,
    PackableStorage,
    RevisionStorage,
    StorageTestBase,
    Synchronization,
    )

class DemoStorageTests(
    StorageTestBase.StorageTestBase,
    BasicStorage.BasicStorage,
        
    HistoryStorage.HistoryStorage,
    IteratorStorage.ExtendedIteratorStorage,
    IteratorStorage.IteratorStorage,
    MTStorage.MTStorage,
    PackableStorage.PackableStorage,
    RevisionStorage.RevisionStorage,
    Synchronization.SynchronizedStorage,
    ):

    def setUp(self):
        StorageTestBase.StorageTestBase.setUp(self)
        self._storage = ZODB.DemoStorage.DemoStorage()

    def checkOversizeNote(self):
        # This base class test checks for the common case where a storage
        # doesnt support huge transaction metadata. This storage doesnt
        # have this limit, so we inhibit this test here.
        pass

    def checkLoadDelegation(self):
        # Minimal test of loadEX w/o version -- ironically
        db = DB(self._storage) # creates object 0. :)
        s2 = ZODB.DemoStorage.DemoStorage(base=self._storage)
        self.assertEqual(s2.load(ZODB.utils.z64, ''),
                         self._storage.load(ZODB.utils.z64, ''))

    def checkLengthAndBool(self):
        self.assertEqual(len(self._storage), 0)
        self.assert_(not self._storage)
        db = DB(self._storage) # creates object 0. :)
        self.assertEqual(len(self._storage), 1)
        self.assert_(self._storage)
        conn = db.open()
        for i in range(10):
            conn.root()[i] = conn.root().__class__()
        transaction.commit()
        self.assertEqual(len(self._storage), 11)
        self.assert_(self._storage)
        
    def checkLoadBeforeUndo(self):
        pass # we don't support undo yet
    checkUndoZombie = checkLoadBeforeUndo

    def checkPackWithMultiDatabaseReferences(self):
        pass # we never do gc
        
class DemoStorageWrappedBase(DemoStorageTests):

    def setUp(self):
        StorageTestBase.StorageTestBase.setUp(self)
        self._base = self._makeBaseStorage()
        self._storage = ZODB.DemoStorage.DemoStorage(base=self._base)

    def tearDown(self):
        self._base.close()
        StorageTestBase.StorageTestBase.tearDown(self)

    def _makeBaseStorage(self):
        raise NotImplementedError

class DemoStorageWrappedAroundMappingStorage(DemoStorageWrappedBase):

    def _makeBaseStorage(self):
        from ZODB.MappingStorage import MappingStorage
        return MappingStorage()

class DemoStorageWrappedAroundFileStorage(DemoStorageWrappedBase):

    def _makeBaseStorage(self):
        from ZODB.FileStorage import FileStorage
        return FileStorage('FileStorageTests.fs')
                       


def setUp(test):
    random.seed(0)
    ZODB.tests.util.setUp(test)

def testSomeDelegation():
    r"""
    >>> class S:
    ...     def __init__(self, name):
    ...         self.name = name
    ...     def registerDB(self, db):
    ...         print self.name, db
    ...     def close(self):
    ...         print self.name, 'closed'
    ...     sortKey = getSize = __len__ = history = getTid = None
    ...     tpc_finish = tpc_vote = tpc_transaction = None
    ...     _lock_acquire = _lock_release = lambda: None
    ...     getName = lambda self: 'S'
    ...     isReadOnly = tpc_transaction = None
    ...     supportsUndo = undo = undoLog = undoInfo = None
    ...     supportsTransactionalUndo = None
    ...     def new_oid(self):
    ...         return '\0' * 8
    ...     def tpc_begin(self, t, tid, status):
    ...         print 'begin', tid, status
    ...     def tpc_abort(self, t):
    ...         pass

    >>> from ZODB.DemoStorage import DemoStorage
    >>> storage = DemoStorage(base=S(1), changes=S(2))

    >>> storage.registerDB(1)
    2 1

    >>> storage.close()
    1 closed
    2 closed

    >>> storage.tpc_begin(1, 2, 3)
    begin 2 3
    >>> storage.tpc_abort(1)

    """

def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite('synchronized.txt'),
        doctest.DocTestSuite(
            setUp=setUp, tearDown=ZODB.tests.util.tearDown,
            ),
        doctest.DocFileSuite(
            'README.txt',
            setUp=setUp, tearDown=ZODB.tests.util.tearDown,
            ),
        ))




def test_suite():
    suite = unittest.TestSuite((
        doctest.DocTestSuite(
            setUp=setUp, tearDown=ZODB.tests.util.tearDown,
            ),
        doctest.DocFileSuite(
            '../DemoStorage.test',
            setUp=setUp, tearDown=ZODB.tests.util.tearDown,
            ),
        ))
    suite.addTest(unittest.makeSuite(DemoStorageTests, 'check'))
    suite.addTest(unittest.makeSuite(DemoStorageWrappedAroundFileStorage,
                                     'check'))
    suite.addTest(unittest.makeSuite(DemoStorageWrappedAroundMappingStorage,
                                     'check'))
    return suite
