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

$Id: testMessageCatalog.py,v 1.3 2002/06/12 18:38:58 srichter Exp $
"""
import unittest

from Zope.I18n.MessageCatalog import MessageCatalog
from testIMessageCatalog import TestIMessageCatalog


class MessageCatalogTest(TestIMessageCatalog):


    def _getMessageCatalog(self):
        catalog = MessageCatalog('en', 'default')
        catalog.setMessage('short_greeting', 'Hello!')
        catalog.setMessage('greeting', 'Hello $name, how are you?')
        return catalog
    
    def _getUniqueIndentifier(self):
        return ('en', 'default')


    def testSetMessage(self):
        catalog = self._catalog
        catalog.setMessage('new', 'New Test')
        self.assertEqual(catalog.getMessage('new'), 'New Test')


    def testGetMessageIds(self):
        catalog = self._catalog
        ids = catalog.getMessageIds()
        ids.sort()
        self.assertEqual(ids, ['greeting', 'short_greeting'])


def test_suite():
    loader=unittest.TestLoader()
    return loader.loadTestsFromTestCase(MessageCatalogTest)

if __name__=='__main__':
    unittest.TextTestRunner().run(test_suite())
