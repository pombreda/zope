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
"""Tests for catalog

Note that indexes &c already have test suites, we only have to check that
a catalog passes on events that it receives.

$Id$
"""
import unittest
import doctest

from zope.interface import implements
from zope.app.index.interfaces.field import IUIFieldCatalogIndex
from zope.app.catalog.interfaces.index import ICatalogIndex
from zope.index.interfaces import IInjection, ISimpleQuery
from zope.app.uniqueid.interfaces import IUniqueIdUtility
from zope.app.site.interfaces import ISite
from zope.app import zapi
from zope.app.tests import ztapi

from zope.app.catalog.catalog import Catalog
from zope.app.tests.placelesssetup import PlacelessSetup
from zope.component import getGlobalServices
from BTrees.IIBTree import IISet


class UniqueIdUtilityStub:
    """A stub for UniqueIdUtility."""
    implements(IUniqueIdUtility)

    def __init__(self):
        self.ids = {}
        self.objs = {}
        self.lastid = 0

    def _generateId(self):
        self.lastid += 1
        return self.lastid

    def register(self, ob):
        if ob not in self.ids:
            uid = self._generateId()
            self.ids[ob] = uid
            self.objs[uid] = ob
        else:
            return self.ids[ob]

    def unregister(self, ob):
        uid = self.ids[ob]
        del self.ids[ob]
        del self.objs[id]

    def getObject(self, uid):
        return self.objs[uid]

    def getId(self, ob):
        return self.ids[ob]

    def items(self):
        return [(id, lambda: obj) for id, obj in self.objs.items()]


class StubIndex:
    implements(ISimpleQuery, IInjection)

    def __init__(self, field_name, interface=None):
        self._field_name = field_name
        self.interface = interface
        self._notifies = []
        self.doc = {}

    def index_doc(self, docid, texts):
        self.doc[docid] = texts

    def unindex_doc(self, docid):
        raise

    def query(self, term, start=0, count=None):
        """TODO"""
###        termdict = self._getterms()
###        res = termdict.get(term, [])
###        return IISet(res)

class stoopid:
    def __init__(self, **kw):
        self.__dict__ = kw


class Test(PlacelessSetup, unittest.TestCase):

    def test_catalog_add_del_indexes(self):
        catalog = Catalog()
        index = StubIndex('author', None)
        catalog['author'] = index
        self.assertEqual(catalog.keys(), ['author'])
        index = StubIndex('title', None)
        catalog['title'] = index
        indexes = catalog.keys()
        indexes.sort()
        self.assertEqual(indexes, ['author', 'title'])
        del catalog['author']
        self.assertEqual(catalog.keys(), ['title'])

    def test_catalog_notification_passing(self):
        catalog = Catalog()
        catalog['author'] = StubIndex('author', None)
        catalog['title'] = StubIndex('title', None)
        catalog.notify(regEvt(None, None, 'reg1', 1))
        catalog.notify(regEvt(None, None, 'reg2', 2))
        catalog.notify(regEvt(None, None, 'reg3', 3))
        catalog.notify(unregEvt(None, None, 'unreg4', 4))
        catalog.notify(unregEvt(None, None, 'unreg5', 5))
        catalog.notify(modEvt(None, None, 'mod6', 6))
        for index in catalog.values():
            checkNotifies = index._notifies
            self.assertEqual(len(checkNotifies), 6)
            notifLocs = [ x.location for x in checkNotifies ]
            self.assertEqual(notifLocs, ['reg1', 'reg2', 'reg3', 
                                         'unreg4', 'unreg5','mod6' ])
            self.assertEqual(notifLocs, ['reg1', 'reg2', 'reg3', 
                                         'unreg4', 'unreg5','mod6' ])
        catalog.clearIndexes()
        for index in catalog.values():
            checkNotifies = index._notifies
            self.assertEqual(len(checkNotifies), 0)

    def _frob_uniqueidutil(self, ints=1, apes=1):
        uidutil = UniqueIdUtilityStub()
        ztapi.provideUtility(IUniqueIdUtility, uidutil)
        # whack some objects in our little objecthub
        if ints:
            for i in range(10):
                uidutil.register("<object %s>"%i)
        if apes:
            uidutil.register(stoopid(simiantype='monkey', name='bobo'))
            uidutil.register(stoopid(simiantype='monkey', name='bubbles'))
            uidutil.register(stoopid(simiantype='monkey', name='ginger'))
            uidutil.register(stoopid(simiantype='bonobo', name='ziczac'))
            uidutil.register(stoopid(simiantype='bonobo', name='bobo'))
            uidutil.register(stoopid(simiantype='punyhuman', name='anthony'))
            uidutil.register(stoopid(simiantype='punyhuman', name='andy'))
            uidutil.register(stoopid(simiantype='punyhuman', name='kev'))

    def test_updateindexes(self):
        "test a full refresh"
        self._frob_uniqueidutil()
        catalog = Catalog()
        catalog['author'] = StubIndex('author', None)
        catalog['title'] = StubIndex('author', None)
        catalog.updateIndexes()
        for index in catalog.values():
            checkNotifies = index._notifies
            self.assertEqual(len(checkNotifies), 18)
            notifLocs = [ x.location for x in checkNotifies ]
            notifLocs.sort()
            expected = [ "/%s"%(i+1) for i in range(18) ]
            expected.sort()
            self.assertEqual(notifLocs, expected)

    def test_basicsearch(self):
        "test the simple searchresults interface"
        self._frob_uniqueidutil(ints=0)
        catalog = Catalog()
        catalog['simiantype'] = StubIndex('simiantype', None)
        catalog['name'] = StubIndex('name', None)
        catalog.updateIndexes()
        res = catalog.searchResults(simiantype='monkey')
        names = [ x.name for x in res ]
        names.sort()
        self.assertEqual(len(names), 3)
        self.assertEqual(names, ['bobo', 'bubbles', 'ginger'])
        res = catalog.searchResults(name='bobo')
        names = [ x.simiantype for x in res ]
        names.sort()
        self.assertEqual(len(names), 2)
        self.assertEqual(names, ['bonobo', 'monkey'])
        res = catalog.searchResults(simiantype='punyhuman', name='anthony')
        self.assertEqual(len(res), 1)
        ob = iter(res).next()
        self.assertEqual((ob.name,ob.simiantype), ('anthony', 'punyhuman'))
        res = catalog.searchResults(simiantype='ape', name='bobo')
        self.assertEqual(len(res), 0)
        res = catalog.searchResults(simiantype='ape', name='mwumi')
        self.assertEqual(len(res), 0)
        self.assertRaises(ValueError, catalog.searchResults, 
                            simiantype='monkey', hat='beret')
        res = list(res)

def test_suite():
    import sys
    return unittest.TestSuite((
        unittest.makeSuite(Test),
###        doctest.DocTestSuite(sys.modules[__name__]),
        ))

if __name__ == "__main__":
    unittest.main()

