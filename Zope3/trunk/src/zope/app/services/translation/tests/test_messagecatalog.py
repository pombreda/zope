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
"""Test the generic persistent Message Catalog.

$Id: test_messagecatalog.py,v 1.3 2003/03/25 23:25:13 bwarsaw Exp $
"""
import unittest

from zope.interface.verify import verifyObject
from zope.app.services.translation.messagecatalog import MessageCatalog
from zope.app.interfaces.services.translation import ILocalMessageCatalog
from zope.i18n.tests.test_imessagecatalog import TestIMessageCatalog


# This is a mixin class -- don't add it to the suite
class TestILocalMessageCatalog:

    # This should be overwritten by every class that inherits this test
    def _getMessageCatalog(self):
        pass

    def _getUniqueIndentifier(self):
        pass

    def setUp(self):
        self._catalog = self._getMessageCatalog()
        assert verifyObject(ILocalMessageCatalog, self._catalog)

    def testGetFullMessage(self):
        catalog = self._catalog
        self.assertEqual(catalog.getFullMessage('short_greeting'),
                         {'domain': 'default',
                          'language': 'en',
                          'msgid': 'short_greeting',
                          'msgstr': 'Hello!',
                          'mod_time': 0})

    def testSetMessage(self):
        catalog = self._catalog
        catalog.setMessage('test', 'Test', 1)
        self.assertEqual(catalog.getFullMessage('test'),
                         {'domain': 'default',
                          'language': 'en',
                          'msgid': 'test',
                          'msgstr': 'Test',
                          'mod_time': 1})
        catalog.deleteMessage('test')

    def testDeleteMessage(self):
        catalog = self._catalog
        self.assertEqual(catalog.queryMessage('test'), None)
        catalog.setMessage('test', 'Test', 1)
        self.assertEqual(catalog.queryMessage('test'), 'Test')
        catalog.deleteMessage('test')
        self.assertEqual(catalog.queryMessage('test'), None)

    def testGetMessageIds(self):
        catalog = self._catalog
        ids = catalog.getMessageIds()
        ids.sort()
        self.assertEqual(ids, ['greeting', 'short_greeting'])

    def testGetMessages(self):
        catalog = self._catalog
        ids = catalog.getMessageIds()
        ids.sort()
        self.assertEqual(ids, ['greeting', 'short_greeting'])


class LocalMessageCatalogTest(unittest.TestCase,
                              TestIMessageCatalog,
                              TestILocalMessageCatalog):

    def setUp(self):
        TestIMessageCatalog.setUp(self)
        TestILocalMessageCatalog.setUp(self)

    def _getMessageCatalog(self):
        catalog = MessageCatalog('en', 'default')
        catalog.setMessage('short_greeting', 'Hello!', 0)
        catalog.setMessage('greeting', 'Hello $name, how are you?', 0)
        return catalog

    def _getUniqueIndentifier(self):
        return ('en', 'default')


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(LocalMessageCatalogTest))
    return suite
